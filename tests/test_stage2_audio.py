"""
Tests for Stage 2: Audio Synthesis (Fallback Mode)
"""
import pytest
import asyncio
from pathlib import Path
from src.stages.stage2_audio import synthesize_audio_segments, _generate_silent_wav
from src.config import config


class TestStage2Audio:
    @pytest.mark.asyncio
    async def test_synthesize_audio_segments(self, sample_manifest, temp_output_dir):
        """Test audio segment generation"""
        # Use temp directory
        config.paths.raw_audio_dir = temp_output_dir

        manifest = await synthesize_audio_segments(sample_manifest)

        # Verify manifest updated with audio paths
        for action in manifest.actions:
            assert action.audio_segment_file is not None
            audio_path = Path(action.audio_segment_file)
            assert audio_path.exists()
            assert audio_path.suffix == '.wav'

    @pytest.mark.asyncio
    async def test_audio_file_duration(self, sample_manifest, temp_output_dir):
        """Test that generated audio files have reasonable duration"""
        import wave

        config.paths.raw_audio_dir = temp_output_dir
        manifest = await synthesize_audio_segments(sample_manifest)

        for action in manifest.actions:
            with wave.open(action.audio_segment_file, 'r') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)

                # Duration should be between 3-10 seconds
                assert 3.0 <= duration <= 10.0

    def test_generate_silent_wav(self, temp_output_dir):
        """Test silent WAV file generation"""
        output_path = temp_output_dir / "test_silent.wav"
        duration = 5.0

        _generate_silent_wav(output_path, duration)

        assert output_path.exists()

        # Verify WAV format
        import wave
        with wave.open(str(output_path), 'r') as wav:
            assert wav.getnchannels() == 1  # Mono
            assert wav.getsampwidth() == 2  # 16-bit
            assert wav.getframerate() == 44100  # 44.1kHz

            # Check duration
            frames = wav.getnframes()
            actual_duration = frames / 44100.0
            assert abs(actual_duration - duration) < 0.1  # Within 0.1s
