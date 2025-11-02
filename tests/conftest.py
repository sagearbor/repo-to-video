"""
Pytest configuration and fixtures
"""
import pytest
import sys
from pathlib import Path
import shutil
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_manifest():
    """Create a sample action manifest for testing"""
    from src.models import ActionManifest, TutorialMetadata, Action, ActionType, ProjectMetadata, TechStack

    project_metadata = ProjectMetadata(
        tech_stack=TechStack.REACT,
        setup_commands=["npm install"],
        start_command="npm start",
        default_port=3000,
        entry_points=["/"],
        readme_summary="A sample React application",
        key_features=["Feature 1", "Feature 2"],
        repo_path="/tmp/sample-repo",
        repo_url="https://github.com/user/sample-repo"
    )

    tutorial_metadata = TutorialMetadata(
        title="Sample Tutorial",
        target_url="http://localhost:3000",
        video_resolution="1920x1080"
    )

    actions = [
        Action(
            action_id="step_1",
            action_type=ActionType.GOTO,
            narration_text="Welcome to this tutorial on React application.",
            pre_action_delay_ms=500,
            post_action_delay_ms=2000
        ),
        Action(
            action_id="step_2",
            action_type=ActionType.WAIT,
            selector="body",
            narration_text="The application has loaded successfully.",
            pre_action_delay_ms=500,
            post_action_delay_ms=1500
        ),
        Action(
            action_id="step_3",
            action_type=ActionType.CLICK,
            selector="button",
            narration_text="Let's click this button to see what happens.",
            pre_action_delay_ms=500,
            post_action_delay_ms=2000
        )
    ]

    manifest = ActionManifest(
        tutorial_metadata=tutorial_metadata,
        actions=actions,
        project_metadata=project_metadata
    )

    return manifest


@pytest.fixture
def test_repo_path():
    """Path to test repository"""
    return Path(__file__).parent.parent / "temp_repos" / "context-aware-ai-training"


@pytest.fixture(autouse=True)
def setup_directories():
    """Ensure all required directories exist before each test"""
    config.paths.ensure_directories()
