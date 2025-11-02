# Testing OpenVoice V2 Voice Cloning Integration

This document provides instructions for testing the complete video generation pipeline with OpenVoice V2 voice cloning.

## Prerequisites

All dependencies should already be installed:
- ✅ OpenVoice V2 with all dependencies
- ✅ MeloTTS text-to-speech engine
- ✅ Model checkpoints in `checkpoints_v2/`
- ✅ Voice sample: `voice_sample.wav`

## Quick Verification

Before testing, verify OpenVoice V2 is working:

```bash
python -c "
import openvoice
from openvoice.api import ToneColorConverter
from melo.api import TTS
import torch
print('✓ OpenVoice V2 ready')
print(f'✓ Device: {\"cuda\" if torch.cuda.is_available() else \"cpu\"}')
"
```

Expected output:
```
✓ OpenVoice V2 ready
✓ Device: cpu
```

## Test the Full Pipeline

### Option 1: Quick Test (Context-Aware AI Training Repo)

This is the repo you've been using for development:

```bash
python generate_tutorial.py \
  https://github.com/sagearbor/context-aware-ai-training \
  --voice-sample voice_sample.wav \
  --skip-clone
```

**Note:** You'll need to manually start the dev server when prompted.

### Option 2: Test with Different Repository

```bash
# Clone a new repo
python generate_tutorial.py \
  https://github.com/user/your-test-repo \
  --voice-sample voice_sample.wav

# Or use any local repository
python generate_tutorial.py \
  /path/to/local/repo \
  --voice-sample voice_sample.wav \
  --skip-clone
```

## Expected Output

### Stage 0: Repository Analysis
```
Stage 0: Repository Analysis
✓ Detected technology stack: React
✓ Generated action manifest with 8 actions
```

### Stage 1: Video Capture
```
Stage 1: Video Capture
Recording action 1/8: Navigate to homepage
Recording action 2/8: Click login button
...
✓ Captured 8 video segments
```

### Stage 2: Audio Synthesis (WITH VOICE CLONING)
```
Stage 2: Audio Synthesis with OpenVoice V2
Using voice sample: voice_sample.wav
Using device: cpu
Loading ToneColorConverter model...
✓ ToneColorConverter loaded
Extracting speaker embedding from voice sample...
✓ Speaker embedding extracted
Initializing MeloTTS for English...
✓ MeloTTS initialized
Synthesizing segment 1/8
  Text: 'Welcome to this tutorial on the context-aware AI training...'
✓ Generated: segment_000.wav
Synthesizing segment 2/8
  Text: 'First, we'll navigate to the login page...'
✓ Generated: segment_001.wav
...
✓ Generated 8 audio segments with voice cloning
```

### Stage 3: Standardization
```
Stage 3: Asset Standardization
Converting video segments to MP4...
Converting audio segments to AAC...
✓ Standardized 8 video and 8 audio segments
```

### Stage 4: Assembly
```
Stage 4: Video Assembly
Concatenating 8 video segments...
Concatenating 8 audio segments...
Merging video and audio tracks...
✓ Final video: output/tutorial_YYYYMMDD_HHMMSS.mp4
```

## Verification Steps

1. **Check Audio Quality**
   ```bash
   # Play a generated audio segment
   ffplay raw_audio/segment_000.wav

   # Compare with voice sample
   ffplay voice_sample.wav
   ```

   The cloned voice should match the characteristics of your voice sample.

2. **Check Video Output**
   ```bash
   # Play final video
   ffplay output/tutorial_*.mp4
   ```

   Video should have:
   - ✓ Narration in cloned voice
   - ✓ Screen recordings of UI interactions
   - ✓ Synchronized audio and video

3. **Inspect Logs**
   ```bash
   # Check for any errors or warnings
   grep -i "error\|warning" video_generator.log
   ```

## Troubleshooting

### Issue: "OpenVoice V2 not available"
**Solution:** Verify installation:
```bash
pip list | grep -i "openvoice\|melotts"
```

### Issue: "Voice sample not found"
**Solution:** Verify voice sample exists:
```bash
ls -lh voice_sample.wav
file voice_sample.wav  # Should show: WAVE audio
```

### Issue: "Base speaker embedding not found"
**Solution:** Verify checkpoints are extracted:
```bash
ls -lh checkpoints_v2/base_speakers/ses/
ls -lh checkpoints_v2/converter/
```

### Issue: Silent audio instead of voice cloning
**Check logs for:**
- Missing dependencies
- Missing voice sample path
- Checkpoint loading errors

**Common fixes:**
```bash
# Re-verify OpenVoice installation
python -c "from openvoice.api import ToneColorConverter; print('OK')"

# Check voice sample format (must be WAV)
ffprobe voice_sample.wav
```

### Issue: CUDA out of memory
**Solution:** The code automatically falls back to CPU. If you see this, it's normal on systems without GPU.

## Performance Notes

**Expected processing times (CPU mode):**
- Stage 0 (Analysis): ~30-60 seconds
- Stage 1 (Capture): ~5-10 seconds per action
- **Stage 2 (Voice Cloning): ~10-20 seconds per action** ⭐
- Stage 3 (Standardization): ~2-5 seconds per segment
- Stage 4 (Assembly): ~10-30 seconds

**Total time for 8 actions: ~5-10 minutes**

Voice cloning is the most time-intensive stage but produces the highest quality results.

## Fallback Behavior

If OpenVoice V2 fails for any reason, the system automatically falls back to silent audio:

```
Stage 2: Audio Synthesis (Silent Fallback Mode)
Audio files will be silent placeholders
Generated silent audio (5.0s): segment_000.wav
```

This ensures the pipeline always completes successfully.

## Success Criteria

✅ All stages complete without errors
✅ Final video exists in `output/` directory
✅ Audio uses cloned voice (not silent)
✅ Voice characteristics match `voice_sample.wav`
✅ Video and audio are synchronized

## Next Steps After Testing

1. **Try different voice samples:**
   ```bash
   # Record a new voice sample
   ffmpeg -f alsa -i default -t 30 my_voice.wav

   # Use it for generation
   python generate_tutorial.py URL --voice-sample my_voice.wav
   ```

2. **Test with different repositories:**
   - React apps
   - Vue apps
   - Python Flask/FastAPI apps
   - Static HTML sites

3. **Optimize settings:**
   - Adjust speech speed in `stage2_audio.py` (currently 1.0)
   - Customize video resolution in `src/config.py`
   - Modify narration timing in manifest generation

## Support

If you encounter issues:
1. Check logs in `video_generator.log`
2. Verify all dependencies: `pip list | grep -E "openvoice|melo|torch"`
3. Review error messages for specific guidance
4. Test individual stages separately

---

**OpenVoice V2 Integration Status:** ✅ COMPLETE
**Last Updated:** 2025-11-02
**Version:** MVP with full voice cloning support
