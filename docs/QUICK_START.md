# Quick Start Guide

## Running Tests

```bash
# Run all tests (recommended)
python -m pytest tests/ -v

# Quick test (summary only)
python -m pytest tests/ -q

# Run specific test file
python -m pytest tests/test_models.py -v

# Use the test runner script
./run_tests.sh

# With coverage report
./run_tests.sh --coverage
```

## Check Progress

```bash
# Overall progress
python checklist.py progress

# Next immediate steps
python checklist.py next

# Current blockers
python checklist.py blockers

# Known issues
python checklist.py issues
```

## Test Individual Stages

### Stage 0 (Repository Analysis)
```bash
# Comprehensive test with real repository
python tests/test_stage0_manual.py

# Or use pytest
python -m pytest tests/test_stage0_manual.py -v
```

### Stage 2 (Audio Synthesis - Silent Fallback)
```bash
python -m pytest tests/test_stage2_audio.py -v
```

## Generate Tutorial Video (Full Pipeline)

**Note:** Requires manually starting the dev server

```bash
# Basic usage with test repo
python generate_tutorial.py https://github.com/sagearbor/context-aware-ai-training

# Skip cloning if repo already exists
python generate_tutorial.py https://github.com/sagearbor/context-aware-ai-training --skip-clone

# Custom output directory
python generate_tutorial.py https://github.com/user/repo --output ./my_videos/
```

## Development Workflow

1. **Make changes to code**
2. **Run tests to verify:**
   ```bash
   python -m pytest tests/ -v
   ```
3. **Test specific stage if needed:**
   ```bash
   python tests/test_stage0_manual.py
   ```
4. **Update checklist:**
   ```bash
   python checklist.py note "What you did"
   # Then manually update DEVELOPER_CHECKLIST.yaml
   ```

## Common Issues

### Tests Failing
```bash
# Ensure all dependencies installed
pip install -r requirements-no-openvoice.txt
pip install pytest pytest-asyncio

# Ensure test repo cloned
cd temp_repos
git clone https://github.com/sagearbor/context-aware-ai-training.git
cd ..
```

### Permission Errors
```bash
chmod -R u+w output/ raw_videos/ raw_audio/ standardized_*
```

### Azure OpenAI Configuration
Ensure `.env` file has valid credentials:
```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-5-nano
AZURE_OPENAI_API_VERSION=2025-03-01-preview
```

## File Structure

```
repo-to-video/
├── src/                    # Source code
│   ├── analyzers/         # Tech stack detection
│   ├── stages/            # Pipeline stages 0-4
│   ├── utils/             # Utilities
│   ├── config.py          # Configuration
│   └── models.py          # Data models
├── tests/                 # Test suite (26 tests)
│   ├── test_models.py     # Model tests
│   ├── test_config.py     # Config tests
│   ├── test_analyzers.py  # Analyzer tests
│   ├── test_stage2_audio.py
│   ├── test_integration.py
│   └── test_stage0_manual.py
├── output/                # Final videos
├── raw_videos/           # Recorded segments
├── raw_audio/            # Generated audio
├── standardized_*/       # Processed assets
└── temp_repos/           # Cloned repositories
```

## Test Coverage Summary

- ✅ **26 tests, 100% passing**
- ✅ Data models (11 tests)
- ✅ Configuration (8 tests)
- ✅ Technology detection (2 tests)
- ✅ Audio generation (3 tests)
- ✅ Integration (4 tests)

## Next Steps

1. **Test end-to-end pipeline** with manual dev server
2. **Test Stages 3 and 4** (standardization and assembly)
3. **Add more integration tests** for different tech stacks
4. **Consider system TTS** as better audio fallback
5. **Phase 2:** OpenVoice V2 integration and auto server management

## Getting Help

- Read `SESSION_SUMMARY.md` for recent changes
- Check `DEVELOPER_CHECKLIST.yaml` for detailed status
- See `CLAUDE.md` for development guidelines
- Review `README.md` for project overview
- Test documentation: `tests/README.md`

## Quick Health Check

```bash
# Verify everything is working
python checklist.py progress && \
python -m pytest tests/ -q && \
echo "✅ All systems operational!"
```
