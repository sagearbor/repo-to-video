"""
Configuration management for the video generator
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load environment variables
load_dotenv()

@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration"""
    api_key: str
    endpoint: str
    deployment: str
    api_version: str

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            api_key=os.getenv('AZURE_OPENAI_API_KEY', ''),
            endpoint=os.getenv('AZURE_OPENAI_ENDPOINT', ''),
            deployment=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-5-nano'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2025-03-01-preview')
        )

    def is_configured(self) -> bool:
        """Check if all required fields are set"""
        return bool(self.api_key and self.endpoint and self.deployment)


@dataclass
class PathConfig:
    """Project path configuration"""
    root_dir: Path
    output_dir: Path
    raw_videos_dir: Path
    raw_audio_dir: Path
    standardized_videos_dir: Path
    standardized_audio_dir: Path
    temp_repos_dir: Path

    @classmethod
    def default(cls):
        """Create default path configuration"""
        root = Path(__file__).parent.parent
        return cls(
            root_dir=root,
            output_dir=root / 'output',
            raw_videos_dir=root / 'raw_videos',
            raw_audio_dir=root / 'raw_audio',
            standardized_videos_dir=root / 'standardized_videos',
            standardized_audio_dir=root / 'standardized_audio',
            temp_repos_dir=root / 'temp_repos'
        )

    def ensure_directories(self):
        """Create all directories if they don't exist"""
        for dir_path in [
            self.output_dir,
            self.raw_videos_dir,
            self.raw_audio_dir,
            self.standardized_videos_dir,
            self.standardized_audio_dir,
            self.temp_repos_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class VideoConfig:
    """Video processing configuration"""
    default_resolution: str = "1920x1080"
    default_fps: int = 30
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    default_port: int = 8000

    @property
    def width(self) -> int:
        return int(self.default_resolution.split('x')[0])

    @property
    def height(self) -> int:
        return int(self.default_resolution.split('x')[1])


@dataclass
class Config:
    """Main configuration object"""
    azure_openai: AzureOpenAIConfig
    paths: PathConfig
    video: VideoConfig

    @classmethod
    def load(cls):
        """Load configuration from environment"""
        return cls(
            azure_openai=AzureOpenAIConfig.from_env(),
            paths=PathConfig.default(),
            video=VideoConfig()
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration
        Returns: (is_valid, error_message)
        """
        if not self.azure_openai.is_configured():
            return False, "Azure OpenAI configuration is incomplete. Check your .env file."

        return True, None


# Global configuration instance
config = Config.load()
