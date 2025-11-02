"""
Tests for data models
"""
import pytest
from src.models import (
    TechStack, ActionType, ProjectMetadata, Action,
    TutorialMetadata, ActionManifest
)


class TestTechStack:
    def test_tech_stack_values(self):
        """Test TechStack enum values"""
        assert TechStack.REACT.value == "react"
        assert TechStack.FASTAPI.value == "fastapi"
        assert TechStack.UNKNOWN.value == "unknown"


class TestActionType:
    def test_action_type_values(self):
        """Test ActionType enum values"""
        assert ActionType.GOTO.value == "goto"
        assert ActionType.CLICK.value == "click"
        assert ActionType.WAIT.value == "wait"


class TestProjectMetadata:
    def test_to_dict(self):
        """Test ProjectMetadata serialization"""
        metadata = ProjectMetadata(
            tech_stack=TechStack.REACT,
            setup_commands=["npm install"],
            start_command="npm start",
            default_port=3000,
            entry_points=["/", "/about"],
            readme_summary="Test app",
            key_features=["Feature 1"],
            repo_path="/tmp/test",
            repo_url="https://github.com/test/repo"
        )

        data = metadata.to_dict()
        assert data['tech_stack'] == 'react'
        assert data['default_port'] == 3000
        assert len(data['setup_commands']) == 1


class TestAction:
    def test_action_to_dict(self):
        """Test Action serialization"""
        action = Action(
            action_id="test_1",
            action_type=ActionType.CLICK,
            narration_text="Click the button",
            selector="button.submit",
            pre_action_delay_ms=500,
            post_action_delay_ms=1000
        )

        data = action.to_dict()
        assert data['action_id'] == "test_1"
        assert data['action_type'] == "click"
        assert data['selector'] == "button.submit"

    def test_action_from_dict(self):
        """Test Action deserialization"""
        data = {
            'action_id': 'test_1',
            'action_type': 'click',
            'narration_text': 'Test narration',
            'selector': 'button',
            'fill_text': None,
            'pre_action_delay_ms': 500,
            'post_action_delay_ms': 1000
        }

        action = Action.from_dict(data)
        assert action.action_id == 'test_1'
        assert action.action_type == ActionType.CLICK
        assert action.selector == 'button'


class TestTutorialMetadata:
    def test_tutorial_metadata_defaults(self):
        """Test TutorialMetadata default values"""
        metadata = TutorialMetadata(
            title="Test Tutorial",
            target_url="http://localhost:3000"
        )

        assert metadata.video_resolution == "1920x1080"

    def test_tutorial_metadata_roundtrip(self):
        """Test TutorialMetadata serialization roundtrip"""
        original = TutorialMetadata(
            title="Test",
            target_url="http://localhost:8000",
            video_resolution="1280x720"
        )

        data = original.to_dict()
        restored = TutorialMetadata.from_dict(data)

        assert restored.title == original.title
        assert restored.target_url == original.target_url
        assert restored.video_resolution == original.video_resolution


class TestActionManifest:
    def test_manifest_roundtrip(self, sample_manifest):
        """Test ActionManifest serialization roundtrip"""
        data = sample_manifest.to_dict()
        restored = ActionManifest.from_dict(data)

        assert restored.tutorial_metadata.title == sample_manifest.tutorial_metadata.title
        assert len(restored.actions) == len(sample_manifest.actions)
        assert restored.actions[0].action_type == sample_manifest.actions[0].action_type

    def test_manifest_has_project_metadata(self, sample_manifest):
        """Test manifest includes project metadata"""
        data = sample_manifest.to_dict()
        assert 'project_metadata' in data
        assert data['project_metadata']['tech_stack'] == 'react'
