# GitHub Tutorial Video Generator - Complete Technical Specification

## Executive Summary

An autonomous system that generates professional video tutorials from **any GitHub repository** containing a web frontend, regardless of technology stack. The system analyzes the repository, generates an action plan, records segmented video demonstrations, synthesizes voice narration, and assembles a polished final video - all using free, local-first, open-source tools.

## Core Value Proposition

**Input:** GitHub repository URL (any web technology: React, Vue, Angular, Next.js, FastAPI, Flask, Django, Rails, PHP, static HTML, etc.)

**Output:** Professional tutorial video (MP4) with:

- Screen recordings of key features
- AI-generated narration in cloned voice
- Smooth transitions
- Text overlays
- Optional: ZIP bundle with source assets for editing

**Cost:** $0 (all processing runs locally)

---

## System Architecture

### Four-Stage Pipeline

```
Stage 0: Repository Analysis & Manifest Generation (NEW)
   ↓
Stage 1: Video Capture (from Gemini approach)
   ↓
Stage 2: Audio Synthesis (from Gemini approach - OpenVoice V2)
   ↓
Stage 3: Asset Standardization (from Gemini approach)
   ↓
Stage 4: Video Assembly (from Gemini approach + enhancements)
```

---

## Stage 0: Intelligent Repository Analysis (New Addition)

### Purpose

Automatically understand ANY repository structure and generate the Action Manifest that drives the entire pipeline.

### Technology Stack Detection

```python
async def detect_tech_stack(repo_path):
    """Detect technology stack by analyzing repo files"""

    detectors = {
        # Node.js ecosystems
        'package.json': analyze_nodejs_project,

        # Python ecosystems
        'requirements.txt': analyze_python_project,
        'pyproject.toml': analyze_python_pyproject,
        'Pipfile': analyze_python_pipenv,
        'setup.py': analyze_python_setup,

        # Ruby
        'Gemfile': analyze_ruby_project,

        # PHP
        'composer.json': analyze_php_project,
        'index.php': analyze_php_simple,

        # Go
        'go.mod': analyze_go_project,

        # Rust
        'Cargo.toml': analyze_rust_project,

        # Java
        'pom.xml': analyze_maven_project,
        'build.gradle': analyze_gradle_project,

        # Static sites
        'index.html': analyze_static_html,
    }

    for file_indicator, analyzer_func in detectors.items():
        if os.path.exists(os.path.join(repo_path, file_indicator)):
            return await analyzer_func(repo_path)

    raise Exception("Unable to detect technology stack")
```

### Project Analyzers

Each analyzer returns a standardized `ProjectMetadata` object:

```python
@dataclass
class ProjectMetadata:
    tech_stack: str  # "react", "fastapi", "rails", "static", etc.
    setup_commands: List[str]  # ["pip install -r requirements.txt"]
    start_command: str  # "uvicorn main:app --reload"
    default_port: int  # 8000
    entry_points: List[str]  # ["/", "/api/docs", "/admin"]
    readme_summary: str  # Extracted from README.md
    key_features: List[str]  # Parsed from README or inferred
```

### Example Analyzers

#### Python/FastAPI Analyzer

```python
async def analyze_python_project(repo_path):
    # Check for common Python web frameworks
    requirements = read_file(f"{repo_path}/requirements.txt")

    if "fastapi" in requirements:
        return ProjectMetadata(
            tech_stack="fastapi",
            setup_commands=[
                "python -m venv venv",
                "source venv/bin/activate",  # or venv\\Scripts\\activate on Windows
                "pip install -r requirements.txt"
            ],
            start_command=detect_uvicorn_command(repo_path),
            default_port=8000,
            entry_points=detect_fastapi_routes(repo_path),
            readme_summary=extract_readme(repo_path),
            key_features=extract_features_from_code(repo_path)
        )

    elif "flask" in requirements:
        return ProjectMetadata(
            tech_stack="flask",
            setup_commands=[
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt"
            ],
            start_command="flask run" or detect_flask_command(repo_path),
            default_port=5000,
            entry_points=detect_flask_routes(repo_path),
            readme_summary=extract_readme(repo_path),
            key_features=extract_features_from_code(repo_path)
        )

    elif "django" in requirements:
        return ProjectMetadata(
            tech_stack="django",
            setup_commands=[
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt",
                "python manage.py migrate"
            ],
            start_command="python manage.py runserver",
            default_port=8000,
            entry_points=detect_django_urls(repo_path),
            readme_summary=extract_readme(repo_path),
            key_features=extract_features_from_code(repo_path)
        )
```

#### Static HTML Analyzer

```python
async def analyze_static_html(repo_path):
    # For static HTML sites, just serve with a simple HTTP server
    return ProjectMetadata(
        tech_stack="static_html",
        setup_commands=[],  # No setup needed
        start_command="python -m http.server 8000",
        default_port=8000,
        entry_points=discover_html_files(repo_path),
        readme_summary=extract_readme(repo_path),
        key_features=extract_features_from_html(repo_path)
    )
```

#### Ruby/Rails Analyzer

```python
async def analyze_ruby_project(repo_path):
    gemfile = read_file(f"{repo_path}/Gemfile")

    if "rails" in gemfile:
        return ProjectMetadata(
            tech_stack="rails",
            setup_commands=[
                "bundle install",
                "rails db:migrate"
            ],
            start_command="rails server",
            default_port=3000,
            entry_points=detect_rails_routes(repo_path),
            readme_summary=extract_readme(repo_path),
            key_features=extract_features_from_code(repo_path)
        )
```

### AI-Powered Action Manifest Generation

Once the repository is analyzed, use a local LLM or Claude via API to generate the Action Manifest:

```python
async def generate_action_manifest(project_metadata, repo_path):
    """
    Use AI to generate the Action Manifest JSON based on repository analysis
    """

    prompt = f"""
You are generating a video tutorial script for a web application.

PROJECT DETAILS:
- Technology: {project_metadata.tech_stack}
- Description: {project_metadata.readme_summary}
- Key Features: {', '.join(project_metadata.key_features)}
- Entry Points: {', '.join(project_metadata.entry_points)}

TASK:
Generate a JSON "Action Manifest" that defines 5-10 key demonstration steps for this application.
Each step should show a meaningful user interaction or feature.

The manifest must follow this schema:
{{
  "tutorial_metadata": {{
    "title": "Tutorial title here",
    "target_url": "http://localhost:{project_metadata.default_port}",
    "video_resolution": "1920x1080"
  }},
  "actions": [
    {{
      "action_id": "step_1",
      "action_type": "goto",
      "selector": null,
      "narration_text": "Description of what's happening",
      "fill_text": null,
      "pre_action_delay_ms": 500,
      "post_action_delay_ms": 2000
    }},
    {{
      "action_id": "step_2",
      "action_type": "click",
      "selector": "button#submit",
      "narration_text": "Now we click the submit button",
      "fill_text": null,
      "pre_action_delay_ms": 500,
      "post_action_delay_ms": 1500
    }}
  ]
}}

Supported action_types: goto, click, fill, scroll, hover, wait
Ensure selectors are specific and likely to exist in a {project_metadata.tech_stack} application.
Make narration natural and informative.

Return ONLY valid JSON, no additional text.
"""

    # Option 1: Use Claude API (costs money but high quality)
    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    manifest_json = json.loads(response.content[0].text)

    # Option 2: Use local LLM (free but may need refinement)
    # response = await local_llm_client.generate(prompt)
    # manifest_json = json.loads(response)

    return manifest_json
```

---

## Stage 1: Video Capture (Adapted from Gemini)

### Playwright-Based Segmented Recording

```python
from playwright.async_api import async_playwright
import asyncio

async def capture_video_segments(manifest_data, project_url):
    """
    Execute Action Manifest and record one video per action
    Based on Gemini's approach but adapted for any URL
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        width, height = map(int, manifest_data['tutorial_metadata']['video_resolution'].split('x'))

        for i, action in enumerate(manifest_data['actions']):
            # Create NEW context for each action (ensures clean video segmentation)
            context = await browser.new_context(
                record_video={
                    'dir': 'raw_videos/',
                    'size': {'width': width, 'height': height}
                },
                viewport={'width': width, 'height': height}
            )

            page = await context.new_page()

            # Navigate if it's the first action
            if action['action_type'] == 'goto' or i == 0:
                await page.goto(project_url)

            # Pre-action delay
            await asyncio.sleep(action['pre_action_delay_ms'] / 1000)

            # Execute action
            if action['action_type'] == 'click':
                await page.click(action['selector'])

            elif action['action_type'] == 'fill':
                await page.fill(action['selector'], action['fill_text'])

            elif action['action_type'] == 'scroll':
                await page.evaluate(f"""
                    document.querySelector('{action['selector']}').scrollIntoView({{
                        behavior: 'smooth'
                    }})
                """)

            elif action['action_type'] == 'hover':
                await page.hover(action['selector'])

            elif action['action_type'] == 'wait':
                await page.wait_for_selector(action['selector'])

            # Post-action delay
            await asyncio.sleep(action['post_action_delay_ms'] / 1000)

            # Close context to finalize video
            await context.close()

            # Get video path
            video_path = await page.video().path()
            manifest_data['actions'][i]['video_segment_file'] = video_path

            print(f"✅ Recorded segment {i+1}/{len(manifest_data['actions'])}")

        await browser.close()

    return manifest_data
```

---

## Stage 2: Audio Synthesis (Gemini's OpenVoice V2 Approach)

### Voice Cloning & TTS

```python
import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter

async def synthesize_audio_segments(manifest_data, voice_sample_path):
    """
    Use OpenVoice V2 to generate narration audio
    """

    # One-time voice cloning setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tone_color_converter = ToneColorConverter(f'checkpoints_v2/converter', device=device)

    # Extract tone color from voice sample
    target_se, audio_name = se_extractor.get_se(
        voice_sample_path, 
        tone_color_converter, 
        vad=True
    )

    # Generate audio for each action's narration
    for i, action in enumerate(manifest_data['actions']):
        narration_text = action['narration_text']
        output_path = f"raw_audio/segment_{i:03d}.wav"

        # Synthesize speech
        tone_color_converter.convert(
            audio_src_path=narration_text,  # Text input
            src_se=target_se,
            tgt_se=target_se,
            output_path=output_path,
            message="Generating narration"
        )

        manifest_data['actions'][i]['audio_segment_file'] = output_path
        print(f"🎤 Generated audio {i+1}/{len(manifest_data['actions'])}")

    return manifest_data
```

---

## Stage 3: Asset Standardization (Gemini's Approach)

```python
import subprocess
import os

def standardize_assets(raw_video_dir='raw_videos/', raw_audio_dir='raw_audio/'):
    """
    Normalize all assets to uniform format for fast concatenation
    Critical for performance - FFmpeg concat demuxer requires identical formats
    """

    os.makedirs('standardized_videos/', exist_ok=True)
    os.makedirs('standardized_audio/', exist_ok=True)

    # Standardize videos
    for video_file in os.listdir(raw_video_dir):
        if video_file.endswith('.webm'):
            input_path = os.path.join(raw_video_dir, video_file)
            output_path = os.path.join('standardized_videos/', video_file.replace('.webm', '.mp4'))

            subprocess.run([
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-s', '1920x1080',
                '-r', '30',
                output_path
            ], check=True)

    # Standardize audio
    for audio_file in os.listdir(raw_audio_dir):
        if audio_file.endswith('.wav'):
            input_path = os.path.join(raw_audio_dir, audio_file)
            output_path = os.path.join('standardized_audio/', audio_file.replace('.wav', '.aac'))

            subprocess.run([
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:a', 'aac',
                output_path
            ], check=True)

    print("✅ Asset standardization complete")
```

---

## Stage 4: Video Assembly (Gemini's Approach + Enhancements)

```python
def assemble_final_video(manifest_data, output_path='final_tutorial.mp4'):
    """
    Use FFmpeg to concatenate, add transitions, overlays, and sync audio
    """

    # Step 1: Create concat list for videos
    with open('video_list.txt', 'w') as f:
        for action in manifest_data['actions']:
            video_file = action['video_segment_file'].replace('.webm', '.mp4')
            video_file = video_file.replace('raw_videos/', 'standardized_videos/')
            f.write(f"file '{os.path.abspath(video_file)}'\n")

    # Step 2: Concatenate videos (fast, lossless)
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'video_list.txt',
        '-c', 'copy',
        'concatenated_video.mp4'
    ], check=True)

    # Step 3: Create concat list for audio
    with open('audio_list.txt', 'w') as f:
        for action in manifest_data['actions']:
            audio_file = action['audio_segment_file'].replace('.wav', '.aac')
            audio_file = audio_file.replace('raw_audio/', 'standardized_audio/')
            f.write(f"file '{os.path.abspath(audio_file)}'\n")

    # Step 4: Concatenate audio
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'audio_list.txt',
        '-c', 'copy',
        'concatenated_audio.aac'
    ], check=True)

    # Step 5: Merge video + audio
    subprocess.run([
        'ffmpeg', '-y',
        '-i', 'concatenated_video.mp4',
        '-i', 'concatenated_audio.aac',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-shortest',
        output_path
    ], check=True)

    print(f"✅ Final video created: {output_path}")
    return output_path
```

---

## Complete Orchestration Script

```python
#!/usr/bin/env python3
"""
GitHub Tutorial Video Generator - Master Orchestrator
Generates professional video tutorials from any GitHub repository
"""

import asyncio
import json
import sys
from pathlib import Path

async def generate_tutorial(github_url, voice_sample_path, output_dir='output'):
    """
    Main pipeline orchestration
    """

    print("🚀 GitHub Tutorial Video Generator")
    print("="*50)

    try:
        # Stage 0: Analyze Repository
        print("\n📦 Stage 0: Repository Analysis")
        repo_path = await clone_repository(github_url)
        project_metadata = await detect_tech_stack(repo_path)
        print(f"   Detected: {project_metadata.tech_stack}")

        # Setup project
        await run_setup_commands(project_metadata.setup_commands, repo_path)

        # Start dev server
        dev_server_process = await start_dev_server(
            project_metadata.start_command,
            repo_path
        )
        project_url = f"http://localhost:{project_metadata.default_port}"
        print(f"   Server running at {project_url}")

        # Generate Action Manifest
        print("\n🤖 Generating Action Manifest with AI...")
        manifest_data = await generate_action_manifest(project_metadata, repo_path)

        # Save manifest
        Path(output_dir).mkdir(exist_ok=True)
        with open(f'{output_dir}/action_manifest.json', 'w') as f:
            json.dump(manifest_data, f, indent=2)

        # Stage 1: Capture Video Segments
        print("\n📹 Stage 1: Video Capture")
        manifest_data = await capture_video_segments(manifest_data, project_url)

        # Stage 2: Synthesize Audio
        print("\n🎤 Stage 2: Audio Synthesis")
        manifest_data = await synthesize_audio_segments(manifest_data, voice_sample_path)

        # Stage 3: Standardize Assets
        print("\n⚙️  Stage 3: Asset Standardization")
        standardize_assets()

        # Stage 4: Assemble Final Video
        print("\n🎬 Stage 4: Video Assembly")
        final_video = assemble_final_video(manifest_data, f'{output_dir}/tutorial.mp4')

        # Optional: Create ZIP bundle
        print("\n📦 Creating asset bundle...")
        create_output_bundle(output_dir, manifest_data)

        print("\n✅ SUCCESS!")
        print(f"   Video: {final_video}")
        print(f"   Bundle: {output_dir}/tutorial_bundle.zip")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

    finally:
        # Cleanup
        if dev_server_process:
            dev_server_process.terminate()
        cleanup_temp_files()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_tutorial.py <github_url> <voice_sample.wav>")
        sys.exit(1)

    github_url = sys.argv[1]
    voice_sample = sys.argv[2]

    asyncio.run(generate_tutorial(github_url, voice_sample))
```

---

## Technology Support Matrix

| Technology | Supported | Setup Command | Start Command | Detection File |
| --- | --- | --- | --- | --- |
| **React** | ✅   | `npm install` | `npm start` | package.json + react dependency |
| **Vue** | ✅   | `npm install` | `npm run dev` | package.json + vue dependency |
| **Angular** | ✅   | `npm install` | `ng serve` | package.json + @angular/core |
| **Next.js** | ✅   | `npm install` | `npm run dev` | package.json + next dependency |
| **FastAPI** | ✅   | `pip install -r requirements.txt` | `uvicorn main:app` | requirements.txt + fastapi |
| **Flask** | ✅   | `pip install -r requirements.txt` | `flask run` | requirements.txt + flask |
| **Django** | ✅   | `pip install -r requirements.txt` + migrate | `python manage.py runserver` | requirements.txt + django |
| **Rails** | ✅   | `bundle install` | `rails server` | Gemfile + rails |
| **PHP** | ✅   | `composer install` | `php -S localhost:8000` | composer.json or index.php |
| **Static HTML** | ✅   | None | `python -m http.server` | index.html |
| **Go** | ✅   | `go mod download` | `go run main.go` | go.mod |

---

## MVP Implementation Order

### Phase 1: Core Pipeline (1-2 days)

1. ✅ Stage 0: Basic tech detection (Node.js, Python, static HTML only)
2. ✅ Stage 1: Playwright video capture
3. ✅ Stage 2: Simple TTS (system voice as fallback)
4. ✅ Stage 3: FFmpeg standardization
5. ✅ Stage 4: FFmpeg assembly

**Test with:** Simple static HTML site, then basic React app

### Phase 2: AI & Voice (1 day)

6. ✅ OpenVoice V2 integration
7. ✅ AI-powered Action Manifest generation
8. ✅ Voice cloning

**Test with:** FastAPI example, Django tutorial project

### Phase 3: Wide Tech Support (1 day)

9. ✅ Add analyzers for all major frameworks
10. ✅ Improve route/feature detection
11. ✅ Better error handling

**Test with:** Rails app, PHP project, Go service

### Phase 4: Polish & Productization (1-2 days)

12. ✅ MCP server wrapper
13. ✅ ZIP bundle output
14. ✅ Azure deployment
15. ✅ Batch processing for multiple URLs

---

## MCP Server Implementation

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("github-tutorial-generator")

@app.tool()
async def generate_tutorial(
    github_url: str,
    voice_sample_url: str = None,
    quality: str = "standard"
) -> list[TextContent]:
    """
    Generate a video tutorial from a GitHub repository

    Args:
        github_url: URL to GitHub repository (any web technology)
        voice_sample_url: Optional URL to voice sample (10+ seconds WAV)
        quality: draft|standard|high (affects resolution and processing time)

    Returns:
        Job ID for tracking progress
    """

    job_id = str(uuid.uuid4())

    # Add to job queue
    await queue.add_job(job_id, {
        'github_url': github_url,
        'voice_sample_url': voice_sample_url,
        'quality': quality
    })

    return [TextContent(
        type="text",
        text=f"Tutorial generation started. Job ID: {job_id}\n"
             f"Use get_job_status('{job_id}') to check progress."
    )]

@app.tool()
async def get_job_status(job_id: str) -> list[TextContent]:
    """Check status of video generation job"""

    status = await queue.get_status(job_id)

    return [TextContent(
        type="text",
        text=json.dumps(status, indent=2)
    )]
```

---

## Azure Deployment (Simplest Approach)

### Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright
RUN pip install playwright && playwright install --with-deps chromium

# Install OpenVoice V2
WORKDIR /app
RUN git clone https://github.com/myshell-ai/OpenVoice.git
WORKDIR /app/OpenVoice
RUN pip install -r requirements.txt

# Copy application
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 3000
CMD ["python", "mcp_server.py"]
```

### Deploy to Azure Container Instances

```bash
az container create \
  --resource-group tutorial-gen-rg \
  --name tutorial-generator \
  --image myregistry.azurecr.io/tutorial-gen:latest \
  --cpu 4 \
  --memory 8 \
  --ports 3000 \
  --environment-variables \
    NODE_OPTIONS="--max-old-space-size=4096"
```

---

## Cost Analysis for SaaS Product

### Per-Video Costs (Azure)

- **Compute (Container Instances):** ~$0.05/video (4 vCPU for 5 mins)
- **Storage:** ~$0.01/video (20GB temp during processing)
- **Egress:** ~$0.10/video (assuming 100MB final video)
- **Total:** ~$0.16/video

### Pricing Strategy

- **Freemium:** 2 free videos/month
- **Starter:** $19/month - 20 videos
- **Professional:** $49/month - 100 videos
- **Enterprise:** $199/month - Unlimited + priority + custom branding

### Break-even Analysis

- At 100 videos/month: $16 cost → $49 revenue = $33 profit (67% margin)
- Market: Thousands of open-source projects, SaaS companies, educators

---

## Key Advantages Over Original Plans

| Feature | Original Plan | This Hybrid Plan |
| --- | --- | --- |
| **Tech Support** | Node.js only | ANY web technology |
| **AI Integration** | Manual script | Auto-generated manifest |
| **GitHub Support** | Clone + guess | Intelligent analysis |
| **Voice Quality** | System TTS | OpenVoice V2 cloning |
| **Performance** | Unknown | Optimized (Gemini's approach) |
| **Productizable** | Maybe | Definitely (supports SaaS model) |

---

## Success Metrics

### MVP Success

- ✅ Generates video from 5+ different tech stacks
- ✅ Under 10 minutes processing time
- ✅ 90%+ success rate (no crashes)
- ✅ Acceptable voice quality

### Product Success

- ✅ $1000/month revenue within 3 months
- ✅ 100+ repositories processed
- ✅ <5% refund rate
- ✅ Positive user testimonials

---

## Next Steps for Implementation

**Immediate actions:**

1. Set up development environment (Python 3.10, FFmpeg, Playwright)
2. Implement Stage 0 analyzer for 3 tech stacks (Node.js, Python, static)
3. Test Gemini's video capture approach with a simple manifest
4. Integrate OpenVoice V2 for TTS
5. Build basic orchestrator
6. Test end-to-end with one repository

**This specification is ready for Claude Code to implement.**
