#!/usr/bin/env python3
"""
Test script for Stage 0 (Repository Analysis & Manifest Generation)
"""
import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.stages.stage0_analyze import analyze_and_generate_manifest
from src.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def test_stage0():
    """Test Stage 0 with the test repository"""
    # Test repo path
    repo_path = Path(__file__).parent / "temp_repos" / "context-aware-ai-training"
    repo_url = "https://github.com/sagearbor/context-aware-ai-training"

    if not repo_path.exists():
        logger.error(f"Test repository not found at {repo_path}")
        logger.error("Please clone it first: git clone https://github.com/sagearbor/context-aware-ai-training temp_repos/context-aware-ai-training")
        return False

    try:
        # Validate configuration
        is_valid, error = config.validate()
        if not is_valid:
            logger.error(f"Configuration validation failed: {error}")
            return False

        logger.info("="*80)
        logger.info("TESTING STAGE 0: Repository Analysis & Manifest Generation")
        logger.info("="*80)

        # Run Stage 0
        project_metadata, manifest = await analyze_and_generate_manifest(repo_path, repo_url)

        # Display results
        logger.info("\n" + "="*80)
        logger.info("PROJECT METADATA")
        logger.info("="*80)
        logger.info(f"Tech Stack: {project_metadata.tech_stack.value}")
        logger.info(f"Default Port: {project_metadata.default_port}")
        logger.info(f"Start Command: {project_metadata.start_command}")
        logger.info(f"Setup Commands: {', '.join(project_metadata.setup_commands[:3])}")
        logger.info(f"Entry Points: {', '.join(project_metadata.entry_points[:3])}")
        logger.info(f"README Summary: {project_metadata.readme_summary[:200]}...")
        logger.info(f"Key Features: {len(project_metadata.key_features)} features")

        logger.info("\n" + "="*80)
        logger.info("ACTION MANIFEST")
        logger.info("="*80)
        logger.info(f"Tutorial Title: {manifest.tutorial_metadata.title}")
        logger.info(f"Target URL: {manifest.tutorial_metadata.target_url}")
        logger.info(f"Number of Actions: {len(manifest.actions)}")

        logger.info("\nActions:")
        for i, action in enumerate(manifest.actions, 1):
            logger.info(f"  {i}. {action.action_type.value.upper()}: {action.narration_text[:60]}...")
            if action.selector:
                logger.info(f"     Selector: {action.selector}")

        # Save manifest to output
        config.paths.ensure_directories()
        manifest_path = config.paths.output_dir / "action_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest.to_dict(), f, indent=2)

        logger.info(f"\n✓ Manifest saved to: {manifest_path}")

        logger.info("\n" + "="*80)
        logger.info("STAGE 0 TEST: PASSED ✓")
        logger.info("="*80)

        return True

    except Exception as e:
        logger.error(f"\n✗ Stage 0 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_stage0())
    sys.exit(0 if success else 1)
