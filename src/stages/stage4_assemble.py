"""
Stage 4: Video Assembly
Concatenates video segments and syncs with audio to create final video
"""
import subprocess
import os
from pathlib import Path
from ..models import ActionManifest
from ..config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


def assemble_final_video(manifest: ActionManifest, output_path: str = None) -> Path:
    """
    Use FFmpeg to concatenate, add transitions, overlays, and sync audio

    Args:
        manifest: Action manifest with file paths
        output_path: Output path for final video

    Returns:
        Path to final video
    """
    logger.info("Stage 4: Video Assembly")

    if output_path is None:
        output_path = config.paths.output_dir / 'tutorial.mp4'
    else:
        output_path = Path(output_path)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary directory for concat lists
    temp_dir = config.paths.root_dir
    video_list_path = temp_dir / 'video_list.txt'
    audio_list_path = temp_dir / 'audio_list.txt'

    # Step 1: Create concat list for videos
    logger.info("Creating video concat list...")
    with open(video_list_path, 'w') as f:
        for action in manifest.actions:
            if action.video_segment_file:
                video_file = action.video_segment_file.replace('.webm', '.mp4')
                video_file = video_file.replace('raw_videos', 'standardized_videos')
                video_path = Path(video_file)

                if video_path.exists():
                    f.write(f"file '{video_path.absolute()}'\n")
                else:
                    logger.warning(f"Video file not found: {video_path}")

    # Step 2: Concatenate videos (fast, lossless)
    concatenated_video = temp_dir / 'concatenated_video.mp4'
    logger.info("Concatenating videos...")

    try:
        subprocess.run([
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(video_list_path),
            '-c', 'copy',
            str(concatenated_video)
        ], check=True, capture_output=True)

        logger.info(f"✓ Videos concatenated: {concatenated_video}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Video concatenation failed: {e.stderr.decode()}")
        raise

    # Step 3: Create concat list for audio (if audio exists)
    audio_files_exist = any(
        action.audio_segment_file and Path(action.audio_segment_file).exists()
        for action in manifest.actions
    )

    if audio_files_exist:
        logger.info("Creating audio concat list...")
        with open(audio_list_path, 'w') as f:
            for action in manifest.actions:
                if action.audio_segment_file:
                    audio_file = action.audio_segment_file.replace('.wav', '.aac')
                    audio_file = audio_file.replace('raw_audio', 'standardized_audio')
                    audio_path = Path(audio_file)

                    if audio_path.exists():
                        f.write(f"file '{audio_path.absolute()}'\n")

        # Step 4: Concatenate audio
        concatenated_audio = temp_dir / 'concatenated_audio.aac'
        logger.info("Concatenating audio...")

        try:
            subprocess.run([
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(audio_list_path),
                '-c', 'copy',
                str(concatenated_audio)
            ], check=True, capture_output=True)

            logger.info(f"✓ Audio concatenated: {concatenated_audio}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Audio concatenation failed: {e.stderr.decode()}")
            concatenated_audio = None

        # Step 5: Merge video + audio
        if concatenated_audio and concatenated_audio.exists():
            logger.info("Merging video and audio...")

            try:
                subprocess.run([
                    'ffmpeg', '-y',
                    '-i', str(concatenated_video),
                    '-i', str(concatenated_audio),
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-map', '0:v:0',
                    '-map', '1:a:0',
                    '-shortest',
                    str(output_path)
                ], check=True, capture_output=True)

                logger.info(f"✓ Final video created: {output_path}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Video+audio merge failed: {e.stderr.decode()}")
                raise
        else:
            # No audio, just copy video
            logger.info("No audio to merge, copying video...")
            subprocess.run([
                'ffmpeg', '-y',
                '-i', str(concatenated_video),
                '-c', 'copy',
                str(output_path)
            ], check=True, capture_output=True)

    else:
        # No audio files, just use video
        logger.info("No audio files found, using video only...")
        subprocess.run([
            'ffmpeg', '-y',
            '-i', str(concatenated_video),
            '-c', 'copy',
            str(output_path)
        ], check=True, capture_output=True)

    logger.info(f"✅ Final video created: {output_path}")
    return output_path
