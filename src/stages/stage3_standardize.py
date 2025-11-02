"""
Stage 3: Asset Standardization
Normalizes all video and audio assets to uniform format for concatenation
"""
import subprocess
import os
from ..config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


def standardize_assets() -> None:
    """
    Normalize all assets to uniform format for fast concatenation
    Critical for performance - FFmpeg concat demuxer requires identical formats
    """
    logger.info("Stage 3: Asset Standardization")

    # Ensure output directories exist
    config.paths.standardized_videos_dir.mkdir(exist_ok=True)
    config.paths.standardized_audio_dir.mkdir(exist_ok=True)

    # Standardize videos
    video_files = list(config.paths.raw_videos_dir.glob('*.webm'))
    logger.info(f"Standardizing {len(video_files)} video files...")

    for video_file in video_files:
        output_path = config.paths.standardized_videos_dir / video_file.with_suffix('.mp4').name

        try:
            subprocess.run([
                'ffmpeg', '-y',
                '-i', str(video_file),
                '-c:v', config.video.video_codec,
                '-c:a', config.video.audio_codec,
                '-s', config.video.default_resolution,
                '-r', str(config.video.default_fps),
                str(output_path)
            ], check=True, capture_output=True)

            logger.info(f"✓ Standardized video: {output_path.name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to standardize {video_file.name}: {e.stderr.decode()}")

    # Standardize audio
    audio_files = list(config.paths.raw_audio_dir.glob('*.wav'))
    logger.info(f"Standardizing {len(audio_files)} audio files...")

    for audio_file in audio_files:
        output_path = config.paths.standardized_audio_dir / audio_file.with_suffix('.aac').name

        try:
            subprocess.run([
                'ffmpeg', '-y',
                '-i', str(audio_file),
                '-c:a', config.video.audio_codec,
                str(output_path)
            ], check=True, capture_output=True)

            logger.info(f"✓ Standardized audio: {output_path.name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to standardize {audio_file.name}: {e.stderr.decode()}")

    logger.info("Asset standardization complete")
