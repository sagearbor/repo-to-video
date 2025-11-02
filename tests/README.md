# Test Suite for repo-to-video

Comprehensive test suite for the GitHub tutorial video generator.

## Running Tests

### Quick Start

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_models.py

# Run specific test class
python -m pytest tests/test_models.py::TestAction

# Run specific test
python -m pytest tests/test_models.py::TestAction::test_action_to_dict
```

### Using the Test Runner Script

```bash
# Run all tests
./run_tests.sh

# Run with coverage report
./run_tests.sh --coverage

# Run only fast tests
./run_tests.sh --fast

# Verbose output
./run_tests.sh --verbose
```

## Test Organization

- **test_models.py** - Tests for data models (ActionManifest, ProjectMetadata, etc.)
- **test_config.py** - Tests for configuration management
- **test_analyzers.py** - Tests for technology stack detection
- **test_stage2_audio.py** - Tests for audio synthesis (silent fallback mode)
- **test_integration.py** - Integration tests for multi-stage pipelines
- **test_stage0_manual.py** - Manual test script for Stage 0 with real repository

## Test Fixtures

See `conftest.py` for available fixtures:

- `temp_output_dir` - Temporary directory for test outputs
- `sample_manifest` - Pre-configured ActionManifest for testing
- `test_repo_path` - Path to the cloned test repository
- `setup_directories` - Auto-creates required directories before each test

## Test Coverage

Current test coverage: **25 tests, 100% passing**

Areas covered:
- ✅ Data model serialization/deserialization
- ✅ Configuration validation
- ✅ Technology stack detection
- ✅ Stage 0: Repository analysis and manifest generation
- ✅ Stage 2: Audio synthesis (silent fallback)
- ✅ Integration: Multi-stage pipelines

## Writing New Tests

### Example Unit Test

```python
import pytest
from src.models import Action, ActionType

def test_action_creation():
    """Test creating an Action"""
    action = Action(
        action_id="test_1",
        action_type=ActionType.CLICK,
        narration_text="Click the button"
    )

    assert action.action_id == "test_1"
    assert action.action_type == ActionType.CLICK
```

### Example Async Test

```python
import pytest
from src.stages.stage2_audio import synthesize_audio_segments

@pytest.mark.asyncio
async def test_audio_generation(sample_manifest):
    """Test audio segment generation"""
    manifest = await synthesize_audio_segments(sample_manifest)

    assert len(manifest.actions) > 0
    for action in manifest.actions:
        assert action.audio_segment_file is not None
```

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -r requirements-no-openvoice.txt
pip install pytest pytest-asyncio

# Run tests
python -m pytest tests/ -v --tb=short
```

## Troubleshooting

### Test Repository Not Found

If integration tests fail with "Test repository not cloned":

```bash
cd temp_repos
git clone https://github.com/sagearbor/context-aware-ai-training.git
```

### Permission Errors

Ensure all test directories are writable:

```bash
chmod -R u+w output/ raw_videos/ raw_audio/ standardized_*
```

### Azure OpenAI Tests

Integration tests for Stage 0 require valid Azure OpenAI credentials in `.env`:

```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-5-nano
AZURE_OPENAI_API_VERSION=2025-03-01-preview
```
