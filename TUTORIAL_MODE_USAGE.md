# Tutorial Mode - Quick Usage Guide

## What is Tutorial Mode?

Tutorial mode automatically detects repositories that contain tutorials or documentation (like `context-aware-ai-training`) and generates videos by:
1. Taking screenshots of tutorial files on GitHub
2. Converting screenshots to video segments with fade transitions
3. Synthesizing voice narration from tutorial content
4. Assembling everything into a final tutorial video

No manual server setup required - it just works!

## Quick Start

### 1. Test with context-aware-ai-training

```bash
# Already cloned in temp_repos/
python generate_tutorial.py \
  https://github.com/user/context-aware-ai-training \
  --skip-clone
```

### 2. Test with voice cloning

```bash
python generate_tutorial.py \
  https://github.com/user/context-aware-ai-training \
  --skip-clone \
  --voice-sample voice_sample.wav
```

### 3. Test with a new tutorial repo

```bash
python generate_tutorial.py \
  https://github.com/fastapi/fastapi-tutorial
```

## How Detection Works

A repo is detected as a tutorial if:
- ✅ Has `tutorials/` or `docs/` directory
- ✅ Has 3+ markdown files
- ❌ Does NOT have web server code (no Flask/FastAPI/Node.js server)

Examples:
- ✅ `context-aware-ai-training` - Has tutorials/ dir, no server
- ✅ `fastapi/fastapi-tutorial` - Has docs/ dir with tutorials
- ❌ `react-starter-app` - Has package.json with "start" script (web app mode)

## Expected Output

```
Stage 0: Repository Analysis
  ✓ Detected: tutorial
  ✓ Tutorial mode detected
  ✓ Tutorial files: 11
  ✓ Parsed 11 tutorial structures
  ✓ Created manifest with 30 actions

Stage 1: Tutorial Screenshot Capture
  📸 Capturing screenshots of tutorial content...
  ✓ Captured screenshot: screenshot_000.png
  ✓ Captured screenshot: screenshot_001.png
  ...
  ✓ Captured 30 screenshots

Stage 2: Audio Synthesis
  🎤 Using voice sample: voice_sample.wav
  ✓ Synthesized 30 audio segments

Stage 3: Asset Standardization
  ⚙️  Converting screenshots to video segments...
  ✓ Converted screenshot to video: segment_000.mp4
  ✓ Converted screenshot to video: segment_001.mp4
  ...
  ✓ Screenshot-to-video conversion complete

Stage 4: Video Assembly
  🎬 Assembling final video...
  ✓ Concatenated 30 video segments
  ✓ Merged audio track
  ✓ Final video: output/tutorial.mp4

✅ SUCCESS!
📹 Video: /home/scb2/PROJECTS/gitRepos-wsl/repo-to-video/output/tutorial.mp4
```

## Differences from Web App Mode

| Feature | Tutorial Mode | Web App Mode |
|---------|---------------|--------------|
| Detection | tutorials/ or docs/ dir | package.json, requirements.txt, etc. |
| Setup | None required | May need npm install, pip install |
| Server | Not needed | Must be running on localhost |
| Capture | GitHub screenshots | Playwright browser recording |
| Duration | 5 sec/screenshot | Variable based on actions |
| Actions | GOTO, SCROLL | GOTO, CLICK, FILL, HOVER, WAIT |

## File Locations

After running, you'll find:

```
output/
├── action_manifest.json        # Generated manifest
├── tutorial.mp4                # Final video

raw_screenshots/
├── screenshot_000.png
├── screenshot_001.png
└── ...

standardized_videos/
├── segment_000.mp4
├── segment_001.mp4
└── ...

raw_audio/
├── audio_000.wav
├── audio_001.wav
└── ...
```

## Customization

### Adjust video duration per screenshot

Edit `/home/scb2/PROJECTS/gitRepos-wsl/repo-to-video/src/stages/stage3_standardize.py`:

```python
# Line 100: Change '-t', '5' to different duration
'-t', '10',  # 10 seconds per screenshot
```

### Change fade transition duration

```python
# Line 104: Adjust fade frames (30 frames = 1 second at 30fps)
'-vf', 'fade=in:0:60,fade=out:240:60',  # 2-second fades
```

### Adjust action limit

Edit `/home/scb2/PROJECTS/gitRepos-wsl/repo-to-video/src/stages/stage1_tutorial_capture.py`:

```python
# Line 169: Change action limit
if len(actions) > 50:  # Limit to 50 instead of 30
    logger.warning(f"Too many actions ({len(actions)}), limiting to first 50")
    actions = actions[:50]
```

### Change screenshot method

By default, uses GitHub web interface. To use VS Code Web instead:

Edit `/home/scb2/PROJECTS/gitRepos-wsl/repo-to-video/generate_tutorial.py` line 131:

```python
# Change from:
manifest = await capture_tutorial_screenshots(manifest)

# To:
from src.stages.stage1_tutorial_capture import capture_tutorial_screenshots_vscode
manifest = await capture_tutorial_screenshots_vscode(manifest, repo_path)
```

## Troubleshooting

### "Not a tutorial repository" error

**Problem:** Repo not detected as tutorial

**Solution:** Check that:
1. Repo has `tutorials/` or `docs/` directory
2. Directory has at least 3 markdown files
3. Repo doesn't have server code (package.json with "start" script, server.py, etc.)

### "Tutorial mode requires GitHub repository URL" error

**Problem:** Screenshot capture requires GitHub URL

**Solution:** Use a valid GitHub URL:
```bash
# ✅ Good
python generate_tutorial.py https://github.com/user/repo

# ❌ Bad
python generate_tutorial.py /local/path/to/repo
```

### Screenshots are blank

**Problem:** GitHub page not loaded before screenshot

**Solution:** Increase wait time in `stage1_tutorial_capture.py` line 73:
```python
await asyncio.sleep(2)  # Change to 5 for slower connections
```

### FFmpeg conversion fails

**Problem:** Missing FFmpeg or codec support

**Solution:** Install FFmpeg with libx264:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## Example Repositories to Test

Good candidates for tutorial mode:

1. **context-aware-ai-training** (already in temp_repos/)
   - 11 tutorial files (md + py)
   - Well-structured with clear steps

2. **fastapi/fastapi-tutorial**
   - Comprehensive API framework tutorials
   - Multiple docs/ files

3. **python-guide-docs**
   - Python best practices
   - Many markdown tutorials

4. **javascript-algorithms**
   - Algorithm explanations
   - Code + markdown

5. **machine-learning-for-beginners**
   - Microsoft tutorial series
   - Step-by-step lessons

## Next Steps

1. Run full pipeline on context-aware-ai-training
2. Review generated video for quality
3. Adjust screenshot duration if needed
4. Test with other tutorial repositories
5. Experiment with voice samples
6. Customize fade transitions

## Tips for Best Results

1. **Choose repos with clear structure**: Numbered tutorials work best (01_, 02_, etc.)
2. **Use good voice sample**: 10+ seconds, clear audio, WAV format
3. **Check tutorial content**: Shorter steps = better screenshots
4. **Review manifest**: Check `output/action_manifest.json` to see what will be captured
5. **Test incremental**: Run Stage 0 first to verify detection before full pipeline

## Support

For issues or questions:
1. Check logs in console output
2. Review `TUTORIAL_MODE_IMPLEMENTATION.md` for technical details
3. Check `output/action_manifest.json` to debug manifest issues
4. Verify FFmpeg with: `ffmpeg -version`
5. Test Playwright with: `playwright install chromium`
