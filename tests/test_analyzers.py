"""
Tests for technology stack analyzers
"""
import pytest
import asyncio
from pathlib import Path
from src.analyzers.detector import detect_tech_stack
from src.models import TechStack


class TestAnalyzers:
    @pytest.mark.asyncio
    async def test_detect_test_repo(self, test_repo_path):
        """Test detection with actual test repository"""
        if not test_repo_path.exists():
            pytest.skip("Test repository not cloned")

        metadata = await detect_tech_stack(test_repo_path)

        assert metadata is not None
        assert metadata.tech_stack is not None
        assert metadata.start_command is not None
        assert metadata.default_port > 0

    @pytest.mark.asyncio
    async def test_detect_nonexistent_repo(self):
        """Test detection with nonexistent repository raises exception"""
        fake_path = Path("/nonexistent/path/to/repo")

        # Should raise an exception for nonexistent path
        with pytest.raises(Exception, match="Unable to detect technology stack"):
            await detect_tech_stack(fake_path)
