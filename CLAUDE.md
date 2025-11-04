<document>
<improved_claude_md>

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an autonomous video tutorial generator that takes any GitHub repository with a web frontend and produces professional tutorial videos with AI-generated narration. The system analyzes the repository, generates an action plan, records segmented video demonstrations, synthesizes voice narration, and assembles the final video.

The system supports three video capture modes:
1. **Manual Mode**: User starts the dev server, pipeline captures video
2. **Auto-Start Mode** (`--auto-start`): Automatically starts and manages dev server
3. **External URL Mode** (`--url`): Captures from already-running websites (production, staging, etc.)

**Current Status:** ~60% MVP complete. Core infrastructure is built, but Stage 2 (audio synthesis) needs OpenVoice V2 integration.

---

## 🤖 Agent-Based Development Workflow

This project uses specialized agents for different aspects of development. **Always delegate work to the appropriate agent** to maximize efficiency and maintain context.

### Available Agents

- **production-code-developer** - Implements features, writes production code, handles integrations
- **ux-product-designer** - Reviews user experience, designs interfaces, writes documentation
- **qa-testing-engineer** - Creates tests, finds bugs, validates fixes
- **code-cleaner** - Maintains repo cleanliness, removes dead code, refactors
- **security-auditor** - Reviews security, validates inputs, checks for vulnerabilities

### When to Use Which Agent

| Task | Agent | Example |
| --- | --- | --- |
| Implement Stage 2 audio synthesis | production-code-developer | "Integrate OpenVoice V2 for voice cloning" |
| Add new tech stack detector | production-code-developer | "Create Rust/Cargo.toml analyzer" |
| Review CLI output and error messages | ux-product-designer | "Make Stage 1 progress output more user-friendly" |
| Write tests for manifest generation | qa-testing-engineer | "Create test cases for Azure OpenAI manifest generation" |
| Clean up unused imports and dead code | code-cleaner | "Scan src/analyzers/ for unused code" |
| Review subprocess calls for injection | security-auditor | "Audit all FFmpeg commands for command injection" |
| Update README with new features | ux-product-designer | "Document voice cloning setup in README" |
| Debug video concatenation failure | production-code-developer | "Fix FFmpeg concat demuxer failing on mixed formats" |
| Find edge cases in tech detection | qa-testing-engineer | "Test with repos that have both Flask and FastAPI" |

### Parallel Development Pattern

**For independent tasks, call multiple developer agents simultaneously:**

```
When working on the MVP, call production-code-developer THREE TIMES in parallel:

Task 1 (production-code-developer): "Implement Stage 2 audio synthesis with OpenVoice V2. 
Read the specification in plan_to_dev.md Section 3. Create src/stages/stage2_audio.py 
that clones voice and generates narration."

Task 2 (production-code-developer): "Implement automatic dev server management in Stage 0.
Currently requires manual server start - automate this. Add process control, health checks,
and automatic port detection."

Task 3 (production-code-developer): "Add 3 new technology detectors: Rust (Cargo.toml),
Elixir (mix.exs), and Svelte (package.json + svelte dependency). Follow the pattern in
existing analyzers."

Then: qa-testing-engineer tests all three implementations
Then: ux-product-designer reviews user experience
Then: code-cleaner scans for any issues
```

**These tasks can run in parallel because they don't depend on each other.**

---

## Architecture: Four-Stage Pipeline

The system is organized as a sequential pipeline with distinct stages:

1. **Stage 0 (`src/stages/stage0_analyze.py`)**: Repository Analysis & Manifest Generation
  - Detects technology stack using analyzer modules
  - Generates `ActionManifest` via Azure OpenAI (GPT-5-nano)
  - Returns `ProjectMetadata` with setup/start commands
2. **Stage 1 (`src/stages/stage1_capture.py`)**: Video Capture
  - Uses Playwright to execute actions from manifest
  - Records one video segment per action (goto, click, fill, scroll, hover, wait)
  - Creates separate browser context for each segment to ensure clean video boundaries
3. **Stage 2 (`src/stages/stage2_audio.py`)**: Audio Synthesis ⚠️ **CRITICAL PRIORITY**
  - **NOT IMPLEMENTED** - needs OpenVoice V2 integration
  - Should clone voice from sample and generate narration for each action
  - **Assign to: production-code-developer**
4. **Stage 3 (`src/stages/stage3_standardize.py`)**: Asset Standardization
  - Converts WebM → MP4, WAV → AAC using FFmpeg
  - Normalizes resolution/framerate for concatenation
5. **Stage 4 (`src/stages/stage4_assemble.py`)**: Video Assembly
  - Concatenates video and audio segments
  - Merges video + audio tracks into final MP4

---

## Key Design Patterns

### Technology Detection System

Located in `src/analyzers/`, uses a priority-based detection system:

- Each analyzer subclasses `BaseAnalyzer` and implements `async analyze()`
- Returns `ProjectMetadata` with tech stack, commands, ports, entry points
- `detector.py` tries analyzers in order based on file indicators (package.json, requirements.txt, etc.)
- Supported: Node.js (React/Vue/Next.js/Angular), Python (FastAPI/Flask/Django), Ruby/Rails, PHP, Go, Static HTML

### Data Models (`src/models.py`)

- `ProjectMetadata`: Repository analysis results
- `ActionManifest`: Complete tutorial script with metadata and actions
- `Action`: Single step (action_type, selector, narration_text, delays)
- All models have `to_dict()` and `from_dict()` for JSON serialization

### Configuration (`src/config.py`)

- Loads from `.env` file (Azure OpenAI credentials)
- Global `config` instance with three sections:
  - `config.azure_openai`: API credentials
  - `config.paths`: All directory paths
  - `config.video`: Video/audio codec settings
- Call `config.paths.ensure_directories()` to create output dirs

### Async Execution

- All stage functions are async
- Use `asyncio.run()` in main orchestrator
- Playwright operations are naturally async
- Use `await asyncio.sleep()` for delays, not `time.sleep()`

---

## Progress Tracking with YAML

This project uses **YAML for progress tracking** to enable better tracking across sessions:

yaml

```yaml
# DEVELOPER_CHECKLIST.yaml structure:
- status: complete | partially_complete | in_progress | blocked | not_started
- priority: critical | high | medium | low
- depends_on: [list of dependencies]
- notes: "Session-specific notes and issues"
- blockers: [list of blocking issues]
```

### Using the Checklist Helper

bash

```bash
# Show next immediate steps
python checklist.py next

# Show current blockers
python checklist.py blockers

# Show known issues
python checklist.py issues

# Show overall progress
python checklist.py progress

# Show specific stage status
python checklist.py stage 2  # Shows Stage 2 status

# Show session notes
python checklist.py notes

# Add a session note
python checklist.py note "Completed Stage 1 testing, found issue with selectors"

# Or view raw YAML
cat DEVELOPER_CHECKLIST.yaml
```

### Updating Progress (Important!)

**After completing any task, update the checklist:**

1. Find the relevant section in DEVELOPER_CHECKLIST.yaml
2. Update `status` field:
  - `complete` - fully working, tested
  - `partially_complete` - works but needs polish
  - `in_progress` - actively being worked on
  - `blocked` - cannot proceed (note blocker)
  - `not_started` - not yet begun
3. Add `notes` about what worked/didn't work
4. Update `session_notes` section with findings
5. Add new items to `issues` section if discovered
6. Update `metadata.last_updated` with current date
7. Use `python checklist.py note "summary"` to quickly add session notes

**Example workflow:**

bash

```bash
# Before starting work
python checklist.py next  # See what to work on

# During work (production-code-developer implements Stage 2)
# ... coding happens ...

# After completing work
python checklist.py note "Implemented OpenVoice V2 integration in stage2_audio.py. Voice cloning works but narration timing needs adjustment."

# Manually update DEVELOPER_CHECKLIST.yaml:
# - Change stage2_audio.status to "partially_complete"
# - Add notes about timing issue
```

---

## Development Commands

### Setup

bash

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Convert voice sample (if needed)
ffmpeg -i your_voice.m4a -ar 44100 -ac 1 voice_sample.wav
```

### Running the Pipeline

bash

```bash
# Basic usage (no audio)
python generate_tutorial.py https://github.com/user/repo

# With voice cloning
python generate_tutorial.py https://github.com/user/repo --voice-sample voice_sample.wav

# Skip cloning (use existing repo in temp_repos/)
python generate_tutorial.py https://github.com/user/repo --skip-clone

# Custom output directory
python generate_tutorial.py https://github.com/user/repo --output ./my_videos/

# Auto-start dev server (non-interactive mode)
python generate_tutorial.py https://github.com/user/repo --auto-start

# Use external URL (skip local server startup)
python generate_tutorial.py https://github.com/user/repo --url https://example.com

# Combination: external URL + voice cloning
python generate_tutorial.py https://github.com/user/repo --url https://production.example.com --voice-sample voice_sample.wav
```

### Testing Individual Stages

bash

````bash
# Test technology detection
python -c "
import asyncio
from pathlib import Path
from src.analyzers import detect_tech_stack
metadata = asyncio.run(detect_tech_stack(Path('./temp_repos/test-repo')))
print(f'Detected: {metadata.tech_stack.value}')
"

# Test manifest generation
python -c "
import asyncio
from pathlib import Path
from src.stages import analyze_and_generate_manifest
metadata, manifest = asyncio.run(analyze_and_generate_manifest(Path('./temp_repos/test-repo')))
print(f'Actions: {len(manifest.actions)}')
"
```

---

## Agent Task Delegation Examples

### Example 1: Implementing a New Feature

**Scenario:** Add subtitle generation to Stage 4
```
Step 1: Call production-code-developer
"Implement subtitle generation in Stage 4. Generate SRT file from ActionManifest 
narration_text with proper timestamps. Save to output/tutorial.srt alongside video."

Step 2: Call qa-testing-engineer
"Test subtitle generation. Verify timestamps match video segments. Test with 
different narration lengths."

Step 3: Call ux-product-designer
"Review subtitle output. Ensure timing is readable. Update README with subtitle feature."

Step 4: Call code-cleaner
"Scan stage4_assemble.py for any cleanup after adding subtitle generation."
```

### Example 2: Debugging a Production Issue

**Scenario:** FFmpeg concatenation fails on some repos
```
Step 1: Call qa-testing-engineer
"Reproduce FFmpeg concatenation failure. Test with multiple repos. Identify which 
video formats/codecs cause failure. Create minimal reproduction case."

Step 2: Call production-code-developer
"Fix FFmpeg concatenation based on QA findings. Ensure Stage 3 standardization 
properly normalizes all formats before concat demuxer."

Step 3: Call qa-testing-engineer
"Verify fix works with previously failing repos. Run regression tests."

Step 4: Update DEVELOPER_CHECKLIST.yaml with fix details
```

### Example 3: Preparing for Release
```
Call ALL agents in sequence:

1. code-cleaner: "Scan entire codebase. Remove dead code, unused imports, TODOs."

2. security-auditor: "Full security audit. Check subprocess calls, input validation, 
   secrets handling."

3. qa-testing-engineer: "Run full test suite. Test with 10+ different repo types. 
   Document any failures."

4. production-code-developer: "Fix any issues found by QA. Implement any critical 
   missing features."

5. ux-product-designer: "Update all documentation. Ensure README, CLAUDE.md, and 
   inline docs are current. Write release notes."

6. Update DEVELOPER_CHECKLIST.yaml: Mark release checklist items complete
```

---

## Critical Implementation Notes

### Stage 2 Audio Synthesis (HIGH PRIORITY - production-code-developer)

Currently stubbed in `src/stages/stage2_audio.py`. To implement:

1. Clone OpenVoice V2 repository to `lib/OpenVoice/`
2. Download checkpoints (see OpenVoice docs)
3. Implement voice cloning in `synthesize_audio_segments()`
4. Convert narration text → WAV files in `raw_audio/`
5. Voice sample MUST be WAV format (44.1kHz or 48kHz, mono)

**Reference:** See `plan_to_dev.md` Section 3 for detailed OpenVoice V2 integration specs.

**Assign to:** production-code-developer

### Dev Server Management Options

The pipeline offers three modes for server management:

**Option 1: Manual Mode (Default)**
1. Pipeline clones repo and analyzes it
2. Displays setup commands and start command
3. User manually runs these commands in another terminal
4. User presses Enter when server is running
5. Pipeline proceeds with video capture

**Option 2: Auto-Start Mode (`--auto-start`)**
- Automatically spawns dev server process
- Performs health check polling (HTTP requests to detect when ready)
- Automatic port detection
- Process cleanup on completion/failure
- Perfect for CI/CD and non-interactive environments

**Option 3: External URL Mode (`--url`)**
- Skips local server startup entirely
- Captures video from an already-running website (production, staging, etc.)
- Still analyzes GitHub repo for intelligent tutorial generation
- Perfect for apps requiring complex setup (databases, API keys, etc.)
- Example: `--url https://production.example.com`

**Note:** `--auto-start` and `--url` cannot be used together (external URL doesn't need server startup)

### Playwright Video Recording

- Each action gets its own browser context for clean segmentation
- Videos saved as WebM in `raw_videos/`
- Recording stops when context closes (finalize video file)
- Non-headless mode (shows browser) for debugging
- For production: add `headless=True` to browser.launch()

### FFmpeg Integration

- Used for standardization (Stage 3) and assembly (Stage 4)
- Commands use `subprocess.run()` with `capture_output=True`
- Errors logged but pipeline continues when possible
- Concat demuxer requires **identical formats** (why standardization is critical)

**Security Note:** All FFmpeg commands should be reviewed by security-auditor for command injection risks.

### Azure OpenAI Integration

- Configured via `.env` file (see existing setup)
- Uses GPT-5-nano deployment
- Generates ActionManifest from project analysis
- Prompt engineering in `_create_manifest_prompt()` includes:
  - Tech stack, README summary, features
  - JSON schema for manifest
  - Guidelines for generic selectors
- Falls back to `_create_default_manifest()` on failure

---

## File Organization
```
src/
├── analyzers/         # Technology detection (one file per tech stack)
├── stages/           # Pipeline stages (stage0-4)
├── utils/            # Shared utilities (logger, file_utils, git_utils)
├── config.py         # Configuration management
└── models.py         # Data models with serialization

Output directories (gitignored):
├── output/           # Final videos and manifests
├── raw_videos/       # Playwright recordings (WebM)
├── raw_audio/        # TTS output (WAV)
├── standardized_*/   # FFmpeg normalized assets
└── temp_repos/       # Cloned repositories
````

---

## Common Tasks (With Agent Assignments)

### Adding a New Technology Analyzer

**Assign to:** production-code-developer

1. Create `src/analyzers/your_tech_analyzer.py`
2. Subclass `BaseAnalyzer`
3. Implement `async analyze() -> Optional[ProjectMetadata]`
4. Add to `detectors` list in `src/analyzers/detector.py`
5. Add detection file indicator (e.g., 'Cargo.toml' for Rust)

**Then:** qa-testing-engineer tests with real repos of that tech stack

### Modifying Action Types

**Assign to:** production-code-developer

1. Update `ActionType` enum in `src/models.py`
2. Implement execution logic in `_execute_action()` in `stage1_capture.py`
3. Update prompt in `stage0_analyze.py` to include new action type
4. Update manifest schema in prompt

**Then:** qa-testing-engineer tests new action type execution

### Changing Video Settings

**Assign to:** production-code-developer or ux-product-designer (for UX considerations)

Edit `VideoConfig` in `src/config.py`:

- `default_resolution`: "1920x1080", "1280x720", etc.
- `default_fps`: 30, 60, etc.
- `video_codec`: "libx264", "libx265", etc.
- `audio_codec`: "aac", "mp3", etc.

---

## Debugging

### Enable Debug Logging

python

```python
from src.utils.logger import setup_logger
logger = setup_logger('video_generator', level=logging.DEBUG)
```

### Check Generated Manifests

bash

```bash
# Manifests saved to output/action_manifest.json after Stage 0
cat output/action_manifest.json | jq .
```

### Validate Video Files

bash

```bash
# Check raw video segments
ls -lh raw_videos/
ffprobe raw_videos/*.webm

# Check standardized videos
ls -lh standardized_videos/
ffprobe standardized_videos/*.mp4
```

### Test Azure OpenAI Connection

python

```python
from src.config import config
is_valid, error = config.validate()
print(f"Valid: {is_valid}, Error: {error}")
```

---

## Important Constraints

- **Selectors in AI-generated manifests may not exist** - Stage 1 has error handling for missing elements
- **Video concatenation requires identical formats** - Stage 3 standardization is not optional
- **Async/await throughout** - Don't mix blocking I/O
- **Playwright contexts must close** to finalize video files
- **Voice sample must be WAV** - convert M4A/MP3 with FFmpeg first
- **Dev server must be running** before Stage 1 starts
- **FFmpeg required** - verify with `ffmpeg -version`

---

## Session Workflow

**At the start of each session:**

1. Run `python checklist.py next` to see immediate priorities
2. Check for blockers: `python checklist.py blockers`
3. Review known issues: `python checklist.py issues`

**During the session:**

1. Delegate tasks to appropriate agents (see agent table above)
2. For parallel work, call production-code-developer multiple times
3. Always follow with qa-testing-engineer for testing
4. Use ux-product-designer for user-facing changes
5. Use code-cleaner periodically to maintain quality

**At the end of each session:**

1. Add session notes: `python checklist.py note "What was accomplished"`
2. Update DEVELOPER_CHECKLIST.yaml with progress
3. Document any new issues discovered
4. Update blockers if any arose

---

## Reference Documentation

- **Full specification:** `plan_to_dev.md` - Complete technical architecture
- **Progress tracking:** `DEVELOPER_CHECKLIST.yaml` - Use this for session-to-session progress
- **Progress helper:** `checklist.py` - Commands for viewing/updating progress
- **Voice recording:** `VOICE_RECORDING_PROMPT.txt` - Guide for recording voice samples
- **Usage examples:** `README.md` - User-facing documentation
- **This file:** `CLAUDE.md` - Development guide and agent orchestration

---

## Quick Reference: Agent Delegation

| When you need to... | Call this agent |
| --- | --- |
| Write or fix code | production-code-developer |
| Improve UX or docs | ux-product-designer |
| Test or find bugs | qa-testing-engineer |
| Clean up codebase | code-cleaner |
| Check security | security-auditor |

**Remember:** Always update DEVELOPER_CHECKLIST.yaml after completing work!
