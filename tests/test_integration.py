"""
Integration tests for the full pipeline
"""
import pytest
import asyncio
import json
from pathlib import Path
from src.stages.stage0_analyze import analyze_and_generate_manifest
from src.stages.stage2_audio import synthesize_audio_segments
from src.config import config


class TestIntegration:
    @pytest.mark.asyncio
    async def test_stage0_with_test_repo(self, test_repo_path):
        """Test Stage 0 with actual test repository"""
        if not test_repo_path.exists():
            pytest.skip("Test repository not cloned")

        repo_url = "https://github.com/sagearbor/context-aware-ai-training"
        metadata, manifest = await analyze_and_generate_manifest(test_repo_path, repo_url)

        # Verify metadata
        assert metadata is not None
        assert metadata.tech_stack is not None
        assert metadata.default_port > 0

        # Verify manifest
        assert manifest is not None
        assert len(manifest.actions) > 0
        assert manifest.tutorial_metadata.title is not None

    @pytest.mark.asyncio
    async def test_stage0_and_stage2_pipeline(self, test_repo_path, temp_output_dir):
        """Test Stages 0 and 2 together"""
        if not test_repo_path.exists():
            pytest.skip("Test repository not cloned")

        # Override audio output path
        config.paths.raw_audio_dir = temp_output_dir

        # Stage 0: Analyze and generate manifest
        repo_url = "https://github.com/sagearbor/context-aware-ai-training"
        metadata, manifest = await analyze_and_generate_manifest(test_repo_path, repo_url)

        # Stage 2: Generate audio segments
        manifest_with_audio = await synthesize_audio_segments(manifest)

        # Verify audio files created
        for action in manifest_with_audio.actions:
            assert action.audio_segment_file is not None
            assert Path(action.audio_segment_file).exists()

    def test_manifest_serialization(self, sample_manifest):
        """Test that manifests can be saved and loaded"""
        manifest_data = sample_manifest.to_dict()

        # Simulate saving to JSON
        json_str = json.dumps(manifest_data, indent=2)

        # Reload from JSON
        from src.models import ActionManifest
        reloaded_data = json.loads(json_str)
        reloaded_manifest = ActionManifest.from_dict(reloaded_data)

        # Verify data integrity
        assert reloaded_manifest.tutorial_metadata.title == sample_manifest.tutorial_metadata.title
        assert len(reloaded_manifest.actions) == len(sample_manifest.actions)
