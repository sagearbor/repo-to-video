"""
Stage 1: Tutorial Video Capture (alternative to web app capture)
Captures screenshots of tutorial content for documentation/tutorial repositories
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Page
from ..models import ActionManifest, Action, ActionType
from ..config import config
from ..utils.logger import get_logger
from ..utils.tutorial_parser import TutorialParser, TutorialStructure

logger = get_logger(__name__)


async def capture_tutorial_screenshots(manifest: ActionManifest) -> ActionManifest:
    """
    Capture screenshots of tutorial content using GitHub's web interface

    Args:
        manifest: Action manifest with tutorial steps

    Returns:
        Updated manifest with screenshot file paths
    """
    logger.info("Stage 1: Tutorial Screenshot Capture")

    # Get repo info from manifest
    repo_url = manifest.tutorial_metadata.target_url
    if not repo_url.startswith('https://github.com/'):
        logger.error("Tutorial mode requires GitHub repository URL")
        raise ValueError("Tutorial mode requires GitHub repository URL")

    # Extract owner/repo from URL
    parts = repo_url.rstrip('/').split('/')
    owner = parts[-2]
    repo = parts[-1]

    width, height = map(int, manifest.tutorial_metadata.video_resolution.split('x'))

    # Create screenshots directory
    screenshots_dir = config.paths.raw_videos_dir.parent / 'raw_screenshots'
    screenshots_dir.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': width, 'height': height}
        )
        page = await context.new_page()

        try:
            for i, action in enumerate(manifest.actions):
                logger.info(f"Capturing screenshot {i+1}/{len(manifest.actions)}: {action.action_id}")

                # Get file path from action metadata (stored in selector field)
                file_path = action.selector

                if not file_path:
                    logger.warning(f"No file path for action {action.action_id}, skipping")
                    continue

                # Construct GitHub URL for the file
                if file_path.endswith('.md'):
                    # For markdown files, use GitHub's rendered view
                    github_url = f"https://github.com/{owner}/{repo}/blob/main/{file_path}"
                elif file_path.endswith('.py'):
                    # For Python files, use GitHub's code view
                    github_url = f"https://github.com/{owner}/{repo}/blob/main/{file_path}"
                else:
                    # Generic file view
                    github_url = f"https://github.com/{owner}/{repo}/blob/main/{file_path}"

                try:
                    # Navigate to the file
                    await page.goto(github_url, wait_until='networkidle', timeout=30000)

                    # Wait for content to load
                    await asyncio.sleep(2)

                    # Scroll to show more content if needed
                    if action.action_type == ActionType.SCROLL:
                        await page.evaluate('window.scrollBy(0, window.innerHeight * 0.8)')
                        await asyncio.sleep(1)

                    # Take screenshot
                    screenshot_name = f"screenshot_{i:03d}.png"
                    screenshot_path = screenshots_dir / screenshot_name

                    await page.screenshot(path=str(screenshot_path), full_page=False)

                    # Update manifest with screenshot path
                    manifest.actions[i].video_segment_file = str(screenshot_path)

                    logger.info(f"✓ Captured screenshot: {screenshot_path}")

                except Exception as e:
                    logger.warning(f"Failed to capture screenshot for {file_path}: {e}")
                    # Create a placeholder action
                    continue

        finally:
            await browser.close()

    logger.info(f"Screenshot capture complete. Captured {len([a for a in manifest.actions if a.video_segment_file])} screenshots.")
    return manifest


async def capture_tutorial_screenshots_vscode(manifest: ActionManifest, repo_path: Path) -> ActionManifest:
    """
    Alternative: Capture screenshots using VS Code Web (vscode.dev)

    Args:
        manifest: Action manifest with tutorial steps
        repo_path: Path to local repository

    Returns:
        Updated manifest with screenshot file paths
    """
    logger.info("Stage 1: Tutorial Screenshot Capture (VS Code Web)")

    repo_url = manifest.tutorial_metadata.target_url
    if not repo_url.startswith('https://github.com/'):
        logger.error("Tutorial mode requires GitHub repository URL")
        raise ValueError("Tutorial mode requires GitHub repository URL")

    width, height = map(int, manifest.tutorial_metadata.video_resolution.split('x'))

    # Create screenshots directory
    screenshots_dir = config.paths.raw_videos_dir.parent / 'raw_screenshots'
    screenshots_dir.mkdir(exist_ok=True)

    # Construct vscode.dev URL
    vscode_url = f"https://vscode.dev/{repo_url}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': width, 'height': height}
        )
        page = await context.new_page()

        try:
            # Navigate to vscode.dev
            logger.info(f"Opening repository in VS Code Web: {vscode_url}")
            await page.goto(vscode_url, wait_until='networkidle', timeout=60000)

            # Wait for VS Code to fully load
            await asyncio.sleep(5)

            for i, action in enumerate(manifest.actions):
                logger.info(f"Capturing screenshot {i+1}/{len(manifest.actions)}: {action.action_id}")

                file_path = action.selector

                if not file_path:
                    logger.warning(f"No file path for action {action.action_id}, skipping")
                    continue

                try:
                    # Open file using Command Palette (Ctrl+P)
                    await page.keyboard.press('Control+P')
                    await asyncio.sleep(0.5)

                    # Type filename
                    await page.keyboard.type(file_path)
                    await asyncio.sleep(0.5)

                    # Press Enter to open
                    await page.keyboard.press('Enter')
                    await asyncio.sleep(2)

                    # Scroll if needed
                    if action.action_type == ActionType.SCROLL:
                        await page.keyboard.press('PageDown')
                        await asyncio.sleep(1)

                    # Take screenshot
                    screenshot_name = f"screenshot_{i:03d}.png"
                    screenshot_path = screenshots_dir / screenshot_name

                    await page.screenshot(path=str(screenshot_path), full_page=False)

                    # Update manifest with screenshot path
                    manifest.actions[i].video_segment_file = str(screenshot_path)

                    logger.info(f"✓ Captured screenshot: {screenshot_path}")

                except Exception as e:
                    logger.warning(f"Failed to capture screenshot for {file_path}: {e}")
                    continue

        finally:
            await browser.close()

    logger.info(f"Screenshot capture complete. Captured {len([a for a in manifest.actions if a.video_segment_file])} screenshots.")
    return manifest


def create_tutorial_manifest_from_parsed(
    tutorials: list,
    repo_url: str,
    title: str = "Tutorial Walkthrough"
) -> ActionManifest:
    """
    Create an ActionManifest from parsed tutorial structures

    Args:
        tutorials: List of TutorialStructure objects
        repo_url: Repository URL
        title: Video title

    Returns:
        ActionManifest ready for capture
    """
    from ..models import TutorialMetadata

    actions = []
    action_id = 1

    for tutorial in tutorials:
        for step in tutorial.steps:
            # Create action for each step
            # Use GOTO for navigation, SCROLL for longer content
            action_type = ActionType.SCROLL if action_id > 1 else ActionType.GOTO

            action = Action(
                action_id=f"action_{action_id:03d}",
                action_type=action_type,
                narration_text=step.narration_text,
                selector=tutorial.file_path,  # Store file path in selector
                pre_action_delay_ms=1000,
                post_action_delay_ms=3000
            )

            actions.append(action)
            action_id += 1

            # Add extra scroll actions for steps with lots of code
            if len(step.code_snippets) > 1:
                scroll_action = Action(
                    action_id=f"action_{action_id:03d}",
                    action_type=ActionType.SCROLL,
                    narration_text=f"Let's look at the code examples for {step.heading}",
                    selector=tutorial.file_path,
                    pre_action_delay_ms=1000,
                    post_action_delay_ms=3000
                )
                actions.append(scroll_action)
                action_id += 1

    # Limit to reasonable number of actions
    if len(actions) > 30:
        logger.warning(f"Too many actions ({len(actions)}), limiting to first 30")
        actions = actions[:30]

    metadata = TutorialMetadata(
        title=title,
        target_url=repo_url,
        video_resolution="1920x1080"
    )

    manifest = ActionManifest(
        tutorial_metadata=metadata,
        actions=actions
    )

    logger.info(f"Created tutorial manifest with {len(actions)} actions")
    return manifest
