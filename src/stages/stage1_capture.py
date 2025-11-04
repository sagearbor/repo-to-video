"""
Stage 1: Video Capture
Captures video segments using Playwright based on the action manifest
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext
from ..models import ActionManifest, ActionType
from ..config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


async def capture_video_segments(manifest: ActionManifest) -> ActionManifest:
    """
    Execute action manifest and record one video per action

    Args:
        manifest: Action manifest with steps to record

    Returns:
        Updated manifest with video_segment_file paths
    """
    logger.info("Stage 1: Video Capture")

    project_url = manifest.tutorial_metadata.target_url
    width, height = map(int, manifest.tutorial_metadata.video_resolution.split('x'))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        try:
            # Keep track of the page for non-goto actions
            current_page = None

            for i, action in enumerate(manifest.actions):
                logger.info(f"Recording action {i+1}/{len(manifest.actions)}: {action.action_id}")

                # Create NEW context for each action to ensure clean video segmentation
                # Using correct Playwright API: record_video_dir and record_video_size
                context = await browser.new_context(
                    record_video_dir=str(config.paths.raw_videos_dir),
                    record_video_size={'width': width, 'height': height},
                    viewport={'width': width, 'height': height}
                )

                page = await context.new_page()

                # Navigate if it's a goto action or first action
                if action.action_type == ActionType.GOTO or i == 0:
                    await page.goto(project_url, wait_until='networkidle', timeout=30000)
                else:
                    # For non-goto actions, navigate to maintain state
                    await page.goto(project_url, wait_until='networkidle', timeout=30000)

                # Pre-action delay
                await asyncio.sleep(action.pre_action_delay_ms / 1000)

                # Execute action
                try:
                    await _execute_action(page, action)
                except Exception as e:
                    logger.warning(f"Action execution failed: {e}. Continuing anyway.")

                # Post-action delay
                await asyncio.sleep(action.post_action_delay_ms / 1000)

                # Close context to finalize video (this triggers video save)
                await context.close()

                # After closing, the video is saved by Playwright
                # Get the video path and rename it to our standard format
                video_path = await page.video.path()

                # Rename to segment_XXX.webm format
                segment_name = f"segment_{i:03d}.webm"
                final_path = config.paths.raw_videos_dir / segment_name

                # Move the Playwright-generated video to our standardized name
                import shutil
                shutil.move(video_path, final_path)

                manifest.actions[i].video_segment_file = str(final_path)

                logger.info(f"✓ Recorded segment: {final_path}")

        finally:
            await browser.close()

    logger.info(f"Video capture complete. Recorded {len(manifest.actions)} segments.")
    return manifest


async def _execute_action(page: Page, action):
    """Execute a single action"""

    if action.action_type == ActionType.GOTO:
        # Already handled in main loop
        pass

    elif action.action_type == ActionType.CLICK:
        if action.selector:
            await page.click(action.selector, timeout=5000)

    elif action.action_type == ActionType.FILL:
        if action.selector and action.fill_text:
            await page.fill(action.selector, action.fill_text, timeout=5000)

    elif action.action_type == ActionType.SCROLL:
        if action.selector:
            # Use parameterized evaluation to prevent injection
            await page.evaluate("""
                (selector) => {
                    document.querySelector(selector)?.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            """, action.selector)

    elif action.action_type == ActionType.HOVER:
        if action.selector:
            await page.hover(action.selector, timeout=5000)

    elif action.action_type == ActionType.WAIT:
        if action.selector:
            try:
                await page.wait_for_selector(action.selector, timeout=5000)
            except:
                # If selector doesn't exist, just wait
                await asyncio.sleep(1)
