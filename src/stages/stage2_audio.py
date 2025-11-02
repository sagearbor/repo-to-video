"""
Stage 2: Audio Synthesis
Synthesizes narration audio using OpenVoice V2 voice cloning
"""
from pathlib import Path
from typing import Optional
import wave
import numpy as np
import os
import tempfile
from ..models import ActionManifest
from ..config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Try to import OpenVoice V2
try:
    import torch
    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter
    from melo.api import TTS
    OPENVOICE_AVAILABLE = True
    logger.info("OpenVoice V2 available for voice cloning")
except ImportError as e:
    OPENVOICE_AVAILABLE = False
    logger.warning(f"OpenVoice V2 not available: {e}")
    logger.warning("Will use silent audio fallback")


async def synthesize_audio_segments(
    manifest: ActionManifest,
    voice_sample_path: Optional[str] = None
) -> ActionManifest:
    """
    Generate audio segments for each action using OpenVoice V2 voice cloning.

    Args:
        manifest: Action manifest with narration text
        voice_sample_path: Path to voice sample WAV file for cloning

    Returns:
        Updated manifest with audio_segment_file paths
    """
    # Ensure output directory exists
    config.paths.ensure_directories()

    if OPENVOICE_AVAILABLE and voice_sample_path:
        return await _synthesize_with_openvoice(manifest, voice_sample_path)
    else:
        if not OPENVOICE_AVAILABLE:
            logger.warning("OpenVoice V2 not installed - using silent fallback")
        elif not voice_sample_path:
            logger.warning("No voice sample provided - using silent fallback")
        return await _synthesize_silent_fallback(manifest)


async def _synthesize_with_openvoice(
    manifest: ActionManifest,
    voice_sample_path: str
) -> ActionManifest:
    """
    Synthesize audio using OpenVoice V2 voice cloning.

    Args:
        manifest: Action manifest with narration text
        voice_sample_path: Path to reference voice sample

    Returns:
        Updated manifest with audio file paths
    """
    logger.info("Stage 2: Audio Synthesis with OpenVoice V2")
    logger.info(f"Using voice sample: {voice_sample_path}")

    # Verify voice sample exists
    if not Path(voice_sample_path).exists():
        logger.error(f"Voice sample not found: {voice_sample_path}")
        logger.warning("Falling back to silent audio")
        return await _synthesize_silent_fallback(manifest)

    # Initialize device
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    # Initialize ToneColorConverter
    ckpt_converter = 'checkpoints_v2/converter'
    if not Path(ckpt_converter).exists():
        logger.error(f"Checkpoint directory not found: {ckpt_converter}")
        logger.warning("Falling back to silent audio")
        return await _synthesize_silent_fallback(manifest)

    try:
        logger.info("Loading ToneColorConverter model...")
        tone_color_converter = ToneColorConverter(
            f'{ckpt_converter}/config.json',
            device=device
        )
        tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
        logger.info("✓ ToneColorConverter loaded")

        # Extract target speaker embedding from voice sample
        logger.info("Extracting speaker embedding from voice sample...")
        target_se, _ = se_extractor.get_se(
            voice_sample_path,
            tone_color_converter,
            vad=True  # Voice Activity Detection
        )
        logger.info("✓ Speaker embedding extracted")

        # Initialize MeloTTS for English synthesis
        logger.info("Initializing MeloTTS for English...")
        tts_model = TTS(language='EN_NEWEST', device=device)
        speaker_ids = tts_model.hps.data.spk2id

        # Load base speaker embedding
        base_speaker_path = 'checkpoints_v2/base_speakers/ses/en-newest.pth'
        if not Path(base_speaker_path).exists():
            # Try default speaker
            base_speaker_path = 'checkpoints_v2/base_speakers/ses/en-default.pth'

        if not Path(base_speaker_path).exists():
            logger.error("Base speaker embedding not found")
            return await _synthesize_silent_fallback(manifest)

        source_se = torch.load(base_speaker_path, map_location=device)
        logger.info("✓ MeloTTS initialized")

        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Generate audio for each action
            for i, action in enumerate(manifest.actions):
                output_path = config.paths.raw_audio_dir / f"segment_{i:03d}.wav"
                temp_source_path = temp_path / f"source_{i:03d}.wav"

                logger.info(f"Synthesizing segment {i+1}/{len(manifest.actions)}")
                logger.debug(f"  Text: '{action.narration_text[:60]}...'")

                try:
                    # Step 1: Generate speech with MeloTTS
                    tts_model.tts_to_file(
                        action.narration_text,
                        speaker_ids['EN-Newest'],  # Use newest English voice
                        str(temp_source_path),
                        speed=1.0
                    )

                    # Step 2: Apply tone color conversion to match reference voice
                    tone_color_converter.convert(
                        audio_src_path=str(temp_source_path),
                        src_se=source_se,
                        tgt_se=target_se,
                        output_path=str(output_path),
                        message="Generated by repo-to-video"
                    )

                    # Update manifest with audio file path
                    manifest.actions[i].audio_segment_file = str(output_path)
                    logger.info(f"✓ Generated: segment_{i:03d}.wav")

                except Exception as e:
                    logger.error(f"Error generating segment {i}: {e}")
                    logger.warning("Creating silent placeholder for this segment")
                    _generate_silent_wav(output_path, duration_seconds=5.0)
                    manifest.actions[i].audio_segment_file = str(output_path)

        logger.info(f"✓ Generated {len(manifest.actions)} audio segments with voice cloning")
        return manifest

    except Exception as e:
        logger.error(f"OpenVoice V2 synthesis failed: {e}")
        logger.warning("Falling back to silent audio")
        return await _synthesize_silent_fallback(manifest)


async def _synthesize_silent_fallback(manifest: ActionManifest) -> ActionManifest:
    """
    Generate silent audio segments as fallback.

    Args:
        manifest: Action manifest

    Returns:
        Updated manifest with silent audio file paths
    """
    logger.info("Stage 2: Audio Synthesis (Silent Fallback Mode)")
    logger.info("Audio files will be silent placeholders")

    for i, action in enumerate(manifest.actions):
        output_path = config.paths.raw_audio_dir / f"segment_{i:03d}.wav"

        # Duration based on narration text length (rough estimate: 150 words per minute)
        words = len(action.narration_text.split())
        duration_seconds = max(3.0, min(10.0, words / 2.5))  # 3-10 seconds

        _generate_silent_wav(output_path, duration_seconds)

        logger.info(f"Generated silent audio ({duration_seconds:.1f}s): segment_{i:03d}.wav")
        logger.debug(f"  Narration: '{action.narration_text[:60]}...'")

        # Update manifest with audio file path
        manifest.actions[i].audio_segment_file = str(output_path)

    logger.info(f"Generated {len(manifest.actions)} silent audio segments")
    return manifest


def _generate_silent_wav(output_path: Path, duration_seconds: float, sample_rate: int = 44100):
    """
    Generate a silent WAV file.

    Args:
        output_path: Path to save the WAV file
        duration_seconds: Duration of the silent audio
        sample_rate: Sample rate in Hz (default 44.1kHz)
    """
    # Create silent audio data
    num_samples = int(duration_seconds * sample_rate)
    silent_data = np.zeros(num_samples, dtype=np.int16)

    # Write WAV file
    with wave.open(str(output_path), 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(silent_data.tobytes())
