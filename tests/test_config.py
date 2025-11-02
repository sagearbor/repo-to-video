"""
Tests for configuration management
"""
import pytest
from pathlib import Path
from src.config import Config, AzureOpenAIConfig, PathConfig, VideoConfig


class TestAzureOpenAIConfig:
    def test_is_configured_true(self):
        """Test is_configured returns True when all fields set"""
        config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test.openai.azure.com/",
            deployment="gpt-5-nano",
            api_version="2025-03-01-preview"
        )
        assert config.is_configured() is True

    def test_is_configured_false(self):
        """Test is_configured returns False when fields missing"""
        config = AzureOpenAIConfig(
            api_key="",
            endpoint="https://test.openai.azure.com/",
            deployment="gpt-5-nano",
            api_version="2025-03-01-preview"
        )
        assert config.is_configured() is False


class TestPathConfig:
    def test_default_paths_exist(self):
        """Test default path configuration creates valid paths"""
        config = PathConfig.default()

        assert config.root_dir.exists()
        assert isinstance(config.output_dir, Path)
        assert isinstance(config.raw_videos_dir, Path)
        assert isinstance(config.raw_audio_dir, Path)

    def test_ensure_directories(self, temp_output_dir):
        """Test directory creation"""
        config = PathConfig(
            root_dir=temp_output_dir,
            output_dir=temp_output_dir / 'output',
            raw_videos_dir=temp_output_dir / 'raw_videos',
            raw_audio_dir=temp_output_dir / 'raw_audio',
            standardized_videos_dir=temp_output_dir / 'std_videos',
            standardized_audio_dir=temp_output_dir / 'std_audio',
            temp_repos_dir=temp_output_dir / 'repos'
        )

        config.ensure_directories()

        assert config.output_dir.exists()
        assert config.raw_videos_dir.exists()
        assert config.raw_audio_dir.exists()


class TestVideoConfig:
    def test_resolution_parsing(self):
        """Test video resolution width/height parsing"""
        config = VideoConfig(default_resolution="1920x1080")

        assert config.width == 1920
        assert config.height == 1080

    def test_custom_resolution(self):
        """Test custom resolution"""
        config = VideoConfig(default_resolution="1280x720")

        assert config.width == 1280
        assert config.height == 720


class TestConfig:
    def test_config_validation_success(self):
        """Test config validation with valid settings"""
        azure_config = AzureOpenAIConfig(
            api_key="test-key",
            endpoint="https://test.openai.azure.com/",
            deployment="gpt-5-nano",
            api_version="2025-03-01-preview"
        )

        config = Config(
            azure_openai=azure_config,
            paths=PathConfig.default(),
            video=VideoConfig()
        )

        is_valid, error = config.validate()
        assert is_valid is True
        assert error is None

    def test_config_validation_failure(self):
        """Test config validation with invalid settings"""
        azure_config = AzureOpenAIConfig(
            api_key="",  # Missing key
            endpoint="https://test.openai.azure.com/",
            deployment="gpt-5-nano",
            api_version="2025-03-01-preview"
        )

        config = Config(
            azure_openai=azure_config,
            paths=PathConfig.default(),
            video=VideoConfig()
        )

        is_valid, error = config.validate()
        assert is_valid is False
        assert error is not None
