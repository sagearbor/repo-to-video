#!/usr/bin/env python3
"""
GitHub Tutorial Video Generator - Master Orchestrator
Generates professional video tutorials from any GitHub repository
"""
import asyncio
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.utils.logger import setup_logger, get_logger
from src.utils.git_utils import clone_repository
from src.utils.file_utils import write_json
from src.stages import (
    analyze_and_generate_manifest,
    capture_video_segments,
    synthesize_audio_segments,
    standardize_assets,
    assemble_final_video
)

logger = setup_logger('video_generator')


async def generate_tutorial(
    github_url: str,
    voice_sample_path: str = None,
    output_dir: str = None,
    skip_clone: bool = False
):
    """
    Main pipeline orchestration

    Args:
        github_url: GitHub repository URL
        voice_sample_path: Path to voice sample for cloning
        output_dir: Output directory for final video
        skip_clone: Skip cloning if repo already exists
    """
    print("🚀 GitHub Tutorial Video Generator")
    print("=" * 70)

    # Validate configuration
    is_valid, error = config.validate()
    if not is_valid:
        logger.error(f"Configuration error: {error}")
        sys.exit(1)

    # Ensure directories exist
    config.paths.ensure_directories()

    # Set output directory
    if output_dir:
        config.paths.output_dir = Path(output_dir)
        config.paths.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Stage 0: Analyze Repository
        logger.info("")
        logger.info("📦 Stage 0: Repository Analysis")
        logger.info("-" * 70)

        if not skip_clone:
            logger.info(f"Cloning repository: {github_url}")
            repo_path = await asyncio.to_thread(clone_repository, github_url)
        else:
            # Use existing repo
            from src.utils.git_utils import get_repo_name
            repo_name = get_repo_name(github_url)
            repo_path = config.paths.temp_repos_dir / repo_name
            logger.info(f"Using existing repository: {repo_path}")

        logger.info("Analyzing project structure...")
        project_metadata, manifest = await analyze_and_generate_manifest(repo_path, github_url)

        logger.info(f"✓ Detected: {project_metadata.tech_stack.value}")
        logger.info(f"✓ Port: {project_metadata.default_port}")
        logger.info(f"✓ Start command: {project_metadata.start_command}")

        # Save manifest
        manifest_path = config.paths.output_dir / 'action_manifest.json'
        write_json(manifest_path, manifest.to_dict())
        logger.info(f"✓ Saved manifest: {manifest_path}")

        # Stage 1: Capture Video Segments
        logger.info("")
        logger.info("📹 Stage 1: Video Capture")
        logger.info("-" * 70)
        logger.info("⚠️  This stage requires the application to be running!")
        logger.info(f"   Please start the application manually:")
        logger.info(f"   cd {repo_path}")
        for cmd in project_metadata.setup_commands:
            logger.info(f"   {cmd}")
        logger.info(f"   {project_metadata.start_command}")
        logger.info("")

        proceed = input("Press Enter when the application is running, or 'q' to quit: ")
        if proceed.lower() == 'q':
            logger.info("Aborted by user")
            sys.exit(0)

        manifest = await capture_video_segments(manifest)
        logger.info(f"✓ Captured {len(manifest.actions)} video segments")

        # Save updated manifest
        write_json(manifest_path, manifest.to_dict())

        # Stage 2: Synthesize Audio
        logger.info("")
        logger.info("🎤 Stage 2: Audio Synthesis")
        logger.info("-" * 70)

        if voice_sample_path:
            logger.info(f"Using voice sample: {voice_sample_path}")
            manifest = await synthesize_audio_segments(manifest, voice_sample_path)
        else:
            logger.warning("No voice sample provided. Skipping audio synthesis.")
            logger.info("To add audio, provide --voice-sample path")

        # Save updated manifest
        write_json(manifest_path, manifest.to_dict())

        # Stage 3: Standardize Assets
        logger.info("")
        logger.info("⚙️  Stage 3: Asset Standardization")
        logger.info("-" * 70)

        standardize_assets()
        logger.info("✓ Assets standardized")

        # Stage 4: Assemble Final Video
        logger.info("")
        logger.info("🎬 Stage 4: Video Assembly")
        logger.info("-" * 70)

        final_video_path = config.paths.output_dir / 'tutorial.mp4'
        final_video = assemble_final_video(manifest, str(final_video_path))

        logger.info("")
        logger.info("✅ SUCCESS!")
        logger.info("=" * 70)
        logger.info(f"📹 Video: {final_video}")
        logger.info(f"📄 Manifest: {manifest_path}")
        logger.info(f"📁 Output directory: {config.paths.output_dir}")

    except KeyboardInterrupt:
        logger.warning("\n\nProcess interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate video tutorials from GitHub repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python generate_tutorial.py https://github.com/user/repo

  # With voice cloning
  python generate_tutorial.py https://github.com/user/repo --voice-sample voice.wav

  # Custom output directory
  python generate_tutorial.py https://github.com/user/repo --output ./my_videos

  # Skip cloning (use existing repo)
  python generate_tutorial.py https://github.com/user/repo --skip-clone
        """
    )

    parser.add_argument(
        'github_url',
        help='GitHub repository URL'
    )

    parser.add_argument(
        '--voice-sample',
        '-v',
        help='Path to voice sample file (WAV, 10+ seconds) for voice cloning'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Output directory for generated video (default: ./output)'
    )

    parser.add_argument(
        '--skip-clone',
        action='store_true',
        help='Skip cloning, use existing repository in temp_repos/'
    )

    args = parser.parse_args()

    # Run async main
    asyncio.run(generate_tutorial(
        github_url=args.github_url,
        voice_sample_path=args.voice_sample,
        output_dir=args.output,
        skip_clone=args.skip_clone
    ))


if __name__ == "__main__":
    main()
