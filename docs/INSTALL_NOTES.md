# Installation Notes

## Fixed Dependency Conflicts (2025-10-31)

### Issues Found:
1. **asyncio==3.4.3** - Shouldn't be installed; it's part of Python stdlib
2. **librosa==0.10.2** - Conflicts with OpenVoice's requirement of librosa==0.9.1

### Changes Made:
- Removed `asyncio` from requirements (it's built into Python)
- Changed `librosa==0.10.2` to let OpenVoice control the version (it needs 0.9.1)
- Loosened version pins from `==` to `>=` where safe to avoid future conflicts

### Installation Order:
```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies (fixed requirements.txt)
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Convert voice sample
ffmpeg -i standardized_audio/Sage_voiceToTrain_webApp_01.m4a -ar 44100 -ac 1 voice_sample.wav
```

## Expected Installation Time
- pip install: 5-10 minutes (PyTorch is large)
- playwright install: 2-3 minutes
- Voice conversion: 10 seconds

## Verification
```bash
# Check key packages
python -c "from playwright.sync_api import sync_playwright; print('Playwright: OK')"
python -c "import openai; print('OpenAI: OK')"
python -c "import torch; print('PyTorch: OK')"
python -c "import git; print('GitPython: OK')"

# Check Playwright browsers
playwright --version

# Check voice sample
ls -lh voice_sample.wav
```

## Known Issues
- OpenVoice V2 needs manual setup after pip install completes
- Voice sample must be in root directory as `voice_sample.wav`
- Some packages may show dependency warnings (safe to ignore if installation completes)
