"""
Stage 0: Repository Analysis & Manifest Generation
Analyzes the repository and generates an action manifest using AI
"""
import json
from pathlib import Path
from typing import Optional
from openai import AzureOpenAI
from ..models import ProjectMetadata, ActionManifest
from ..config import config
from ..utils.logger import get_logger
from ..analyzers import detect_tech_stack

logger = get_logger(__name__)


async def analyze_and_generate_manifest(
    repo_path: Path,
    repo_url: str = ""
) -> tuple[ProjectMetadata, ActionManifest]:
    """
    Analyze repository and generate action manifest

    Args:
        repo_path: Path to the repository
        repo_url: Original repository URL

    Returns:
        Tuple of (ProjectMetadata, ActionManifest)
    """
    logger.info("Stage 0: Repository Analysis & Manifest Generation")

    # Step 1: Detect tech stack
    logger.info("Detecting technology stack...")
    project_metadata = await detect_tech_stack(repo_path)

    if not project_metadata:
        raise Exception("Failed to detect technology stack")

    project_metadata.repo_url = repo_url

    logger.info(f"Detected: {project_metadata.tech_stack.value}")
    logger.info(f"Port: {project_metadata.default_port}")
    logger.info(f"Start command: {project_metadata.start_command}")

    # Step 2: Generate action manifest using AI
    logger.info("Generating action manifest with Azure OpenAI...")
    manifest = await generate_manifest_with_ai(project_metadata)

    logger.info(f"Generated manifest with {len(manifest.actions)} actions")

    return project_metadata, manifest


async def generate_manifest_with_ai(project_metadata: ProjectMetadata) -> ActionManifest:
    """
    Generate action manifest using Azure OpenAI

    Args:
        project_metadata: Project metadata from analysis

    Returns:
        ActionManifest
    """
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=config.azure_openai.api_key,
        api_version=config.azure_openai.api_version,
        azure_endpoint=config.azure_openai.endpoint
    )

    # Create prompt
    prompt = _create_manifest_prompt(project_metadata)

    # Call Azure OpenAI
    try:
        response = client.chat.completions.create(
            model=config.azure_openai.deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating video tutorial scripts. You generate structured JSON action manifests that define how to demonstrate web applications."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=4000  # Updated for newer API versions
            # Note: temperature removed as gpt-5-nano only supports default value
        )

        # Parse response
        response_text = response.choices[0].message.content
        if not response_text:
            raise ValueError("Azure OpenAI returned empty response")

        response_text = response_text.strip()
        logger.debug(f"Azure OpenAI response length: {len(response_text)} characters")

        # Extract JSON from response (handle markdown code blocks)
        json_text = response_text
        if '```json' in response_text:
            json_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            json_text = response_text.split('```')[1].split('```')[0].strip()

        if not json_text:
            raise ValueError(f"Could not extract JSON from response: {response_text[:200]}")

        manifest_data = json.loads(json_text)

        # Convert to ActionManifest
        manifest = ActionManifest.from_dict(manifest_data)
        manifest.project_metadata = project_metadata

        return manifest

    except Exception as e:
        logger.error(f"Failed to generate manifest with AI: {e}")
        logger.info("Falling back to default manifest")
        return _create_default_manifest(project_metadata)


def _create_manifest_prompt(project_metadata: ProjectMetadata) -> str:
    """Create prompt for manifest generation"""

    features_str = '\n'.join([f"- {feature}" for feature in project_metadata.key_features[:10]])

    prompt = f"""
You are generating a video tutorial script for a web application.

PROJECT DETAILS:
- Technology: {project_metadata.tech_stack.value}
- Description: {project_metadata.readme_summary}
- Key Features:
{features_str}
- Entry Points: {', '.join(project_metadata.entry_points)}

TASK:
Generate a JSON "Action Manifest" that defines 5-10 key demonstration steps for this application.
Each step should show a meaningful user interaction or feature.

The manifest must follow this schema:
{{
  "tutorial_metadata": {{
    "title": "Tutorial title here (be specific about the app)",
    "target_url": "http://localhost:{project_metadata.default_port}",
    "video_resolution": "1920x1080"
  }},
  "actions": [
    {{
      "action_id": "step_1",
      "action_type": "goto",
      "selector": null,
      "narration_text": "Welcome to this tutorial on [app name]. Let's explore its key features.",
      "fill_text": null,
      "pre_action_delay_ms": 500,
      "post_action_delay_ms": 2000
    }},
    {{
      "action_id": "step_2",
      "action_type": "wait",
      "selector": "body",
      "narration_text": "The application has loaded, showing the main interface with all available features.",
      "fill_text": null,
      "pre_action_delay_ms": 500,
      "post_action_delay_ms": 1500
    }}
  ]
}}

SUPPORTED ACTION TYPES:
- goto: Navigate to the URL (always first action)
- wait: Wait for element to appear (use "body" or main container)
- click: Click an element (provide CSS selector)
- fill: Fill a form field (provide selector and fill_text)
- scroll: Scroll to element (provide selector)
- hover: Hover over element (provide selector)

IMPORTANT GUIDELINES:
1. First action MUST be "goto" to navigate to the application
2. Second action should usually be "wait" to let the page load
3. Use GENERIC selectors that are likely to exist (e.g., "button", "input[type='text']", "a", "nav", ".container")
4. Make narration natural, informative, and match what's happening on screen
5. Don't assume specific element IDs/classes unless they're very common
6. Focus on demonstrating the KEY features from the project description
7. Use appropriate delays: 500ms pre-action, 1500-2000ms post-action for viewing
8. Keep it simple - better to show fewer things well than many things poorly

EXAMPLE FLOW:
1. Navigate to app (goto)
2. Wait for page load (wait for "body")
3. Show main feature (click or interaction)
4. Fill form if relevant (fill)
5. Submit or navigate (click)
6. Show results (wait)

Return ONLY valid JSON, no additional text or explanation.
"""

    return prompt


def _create_default_manifest(project_metadata: ProjectMetadata) -> ActionManifest:
    """Create a default manifest as fallback"""
    from ..models import TutorialMetadata, Action, ActionType

    tutorial_metadata = TutorialMetadata(
        title=f"{project_metadata.tech_stack.value.title()} Application Tutorial",
        target_url=f"http://localhost:{project_metadata.default_port}",
        video_resolution="1920x1080"
    )

    # Create simple default actions
    actions = [
        Action(
            action_id="step_1",
            action_type=ActionType.GOTO,
            narration_text=f"Welcome to this tutorial on the {project_metadata.tech_stack.value} application. Let's explore its features.",
            pre_action_delay_ms=500,
            post_action_delay_ms=2000
        ),
        Action(
            action_id="step_2",
            action_type=ActionType.WAIT,
            selector="body",
            narration_text="The application has loaded successfully. Here's the main interface.",
            pre_action_delay_ms=500,
            post_action_delay_ms=2000
        ),
        Action(
            action_id="step_3",
            action_type=ActionType.WAIT,
            selector="body",
            narration_text="This application showcases modern web development practices and provides a clean user experience.",
            pre_action_delay_ms=500,
            post_action_delay_ms=3000
        )
    ]

    manifest = ActionManifest(
        tutorial_metadata=tutorial_metadata,
        actions=actions,
        project_metadata=project_metadata
    )

    return manifest
