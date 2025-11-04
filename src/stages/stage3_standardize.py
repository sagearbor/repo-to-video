"""
Stage 3: Asset Standardization
Normalizes all video and audio assets to uniform format for concatenation
"""
import subprocess
import os
from pathlib import Path
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

    # Check for screenshots first (tutorial mode)
    screenshots_dir = config.paths.raw_videos_dir.parent / 'raw_screenshots'
    if screenshots_dir.exists():
        screenshot_files = list(screenshots_dir.glob('*.png'))
        if screenshot_files:
            logger.info(f"Converting {len(screenshot_files)} screenshots to video segments...")
            _convert_screenshots_to_videos(screenshot_files)
            return

    # Standardize videos (web app mode)
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


def _convert_screenshots_to_videos(screenshot_files: list) -> None:
    """
    Convert PNG screenshots to video segments using FFmpeg

    Args:
        screenshot_files: List of screenshot file paths

    Each screenshot becomes a 5-second video segment with fade transitions
    """
    logger.info("Converting screenshots to video segments (tutorial mode)")

    for i, screenshot_file in enumerate(screenshot_files):
        output_path = config.paths.standardized_videos_dir / f"segment_{i:03d}.mp4"

        try:
            # Convert static image to 5-second video with fade in/out
            # Using the loop filter to create video from single image
            subprocess.run([
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', str(screenshot_file),
                '-c:v', config.video.video_codec,
                '-t', '5',  # 5 seconds per screenshot
                '-pix_fmt', 'yuv420p',
                '-s', config.video.default_resolution,
                '-r', str(config.video.default_fps),
                '-vf', 'fade=in:0:30,fade=out:120:30',  # Fade in first 30 frames, fade out last 30 frames
                str(output_path)
            ], check=True, capture_output=True)

            logger.info(f"✓ Converted screenshot to video: {output_path.name}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to convert {screenshot_file.name}: {e.stderr.decode()}")

    # Also standardize audio if present
    audio_files = list(config.paths.raw_audio_dir.glob('*.wav'))
    if audio_files:
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

    logger.info("Screenshot-to-video conversion complete")
