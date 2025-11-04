"""
Data models for the video generator
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class TechStack(str, Enum):
    """Supported technology stacks"""
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NEXTJS = "nextjs"
    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    RAILS = "rails"
    PHP = "php"
    GO = "go"
    RUST = "rust"
    STATIC_HTML = "static_html"
    TUTORIAL = "tutorial"
    UNKNOWN = "unknown"


class ActionType(str, Enum):
    """Supported action types for video capture"""
    GOTO = "goto"
    CLICK = "click"
    FILL = "fill"
    SCROLL = "scroll"
    HOVER = "hover"
    WAIT = "wait"


@dataclass
class ProjectMetadata:
    """Metadata about the analyzed project"""
    tech_stack: TechStack
    setup_commands: List[str]
    start_command: str
    default_port: int
    entry_points: List[str]
    readme_summary: str
    key_features: List[str]
    repo_path: str
    repo_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'tech_stack': self.tech_stack.value,
            'setup_commands': self.setup_commands,
            'start_command': self.start_command,
            'default_port': self.default_port,
            'entry_points': self.entry_points,
            'readme_summary': self.readme_summary,
            'key_features': self.key_features,
            'repo_path': self.repo_path,
            'repo_url': self.repo_url
        }


@dataclass
class Action:
    """Single action in the tutorial manifest"""
    action_id: str
    action_type: ActionType
    narration_text: str
    selector: Optional[str] = None
    fill_text: Optional[str] = None
    pre_action_delay_ms: int = 500
    post_action_delay_ms: int = 2000
    video_segment_file: Optional[str] = None
    audio_segment_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'action_id': self.action_id,
            'action_type': self.action_type.value if isinstance(self.action_type, ActionType) else self.action_type,
            'selector': self.selector,
            'narration_text': self.narration_text,
            'fill_text': self.fill_text,
            'pre_action_delay_ms': self.pre_action_delay_ms,
            'post_action_delay_ms': self.post_action_delay_ms,
            'video_segment_file': self.video_segment_file,
            'audio_segment_file': self.audio_segment_file
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Create from dictionary"""
        action_type = data.get('action_type', 'goto')
        if isinstance(action_type, str):
            action_type = ActionType(action_type)

        return cls(
            action_id=data['action_id'],
            action_type=action_type,
            narration_text=data['narration_text'],
            selector=data.get('selector'),
            fill_text=data.get('fill_text'),
            pre_action_delay_ms=data.get('pre_action_delay_ms', 500),
            post_action_delay_ms=data.get('post_action_delay_ms', 2000),
            video_segment_file=data.get('video_segment_file'),
            audio_segment_file=data.get('audio_segment_file')
        )


@dataclass
class TutorialMetadata:
    """Metadata for the tutorial video"""
    title: str
    target_url: str
    video_resolution: str = "1920x1080"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'target_url': self.target_url,
            'video_resolution': self.video_resolution
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TutorialMetadata':
        """Create from dictionary"""
        return cls(
            title=data['title'],
            target_url=data['target_url'],
            video_resolution=data.get('video_resolution', '1920x1080')
        )


@dataclass
class ActionManifest:
    """Complete action manifest for video generation"""
    tutorial_metadata: TutorialMetadata
    actions: List[Action]
    project_metadata: Optional[ProjectMetadata] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'tutorial_metadata': self.tutorial_metadata.to_dict(),
            'actions': [action.to_dict() for action in self.actions]
        }
        if self.project_metadata:
            result['project_metadata'] = self.project_metadata.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionManifest':
        """Create from dictionary"""
        tutorial_metadata = TutorialMetadata.from_dict(data['tutorial_metadata'])
        actions = [Action.from_dict(action_data) for action_data in data['actions']]

        project_metadata = None
        if 'project_metadata' in data:
            pm_data = data['project_metadata']
            project_metadata = ProjectMetadata(
                tech_stack=TechStack(pm_data['tech_stack']),
                setup_commands=pm_data['setup_commands'],
                start_command=pm_data['start_command'],
                default_port=pm_data['default_port'],
                entry_points=pm_data['entry_points'],
                readme_summary=pm_data['readme_summary'],
                key_features=pm_data['key_features'],
                repo_path=pm_data['repo_path'],
                repo_url=pm_data.get('repo_url', '')
            )

        return cls(
            tutorial_metadata=tutorial_metadata,
            actions=actions,
            project_metadata=project_metadata
        )
