# MCP Requirements for This Project

## Required MCPs: NONE ✅

This project does NOT require any MCPs to function. All functionality is implemented via Python libraries and command-line tools.

## Current MCPs You Have

Based on your `/context` output:

1. **puppeteer** (7 tools)
   - Purpose: Browser automation
   - Needed for this project? **NO** - We use Playwright Python library instead
   - Keep it? Yes, useful for other projects

2. **context7** (2 tools)
   - Purpose: Retrieve library documentation
   - Needed for this project? **NO** - But useful for development
   - Keep it? Yes, helps when implementing OpenVoice V2 integration

## How to Check Your MCPs

```bash
# List all configured MCPs
ls -la ~/.config/claude-code/mcp_servers/

# Check MCP configuration
cat ~/.config/claude-code/config.json | jq '.mcpServers'

# Or use the /mcp command in Claude Code
/mcp
```

## Optional MCPs That Could Help (Not Required)

These are **NOT required** but could improve development workflow:

### 1. Filesystem MCP (Recommended for Development)
- **Purpose:** Better file operations, searching, monitoring
- **Useful for:** Reading logs, monitoring output directories, file management
- **Install:** Available in Anthropic's MCP servers collection
- **URL:** https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem

```json
// Add to claude-code config
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/scb2/PROJECTS/gitRepos-wsl/repo-to-video"]
    }
  }
}
```

### 2. GitHub MCP (Optional)
- **Purpose:** Enhanced GitHub operations
- **Useful for:** If you want to automate repo cloning, issue tracking
- **Current status:** We use GitPython library (works fine)
- **URL:** https://github.com/modelcontextprotocol/servers/tree/main/src/github

### 3. Sequential Thinking MCP (Optional)
- **Purpose:** Better reasoning for complex problems
- **Useful for:** Debugging complex pipeline issues
- **URL:** https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking

## MCPs You DON'T Need

### ❌ Puppeteer MCP
We're using **Playwright** (Python library), not Puppeteer (Node.js library).
- Your existing Puppeteer MCP won't be used by this project
- Keep it if you use it elsewhere, but it's not needed here

### ❌ Any Video Processing MCP
Doesn't exist. We use FFmpeg via subprocess.

### ❌ Voice Processing MCP
Doesn't exist. We'll use OpenVoice V2 Python library.

## What Actually Needs to Be Installed

### Python Packages (via pip):
```bash
# Core dependencies
pip install -r requirements.txt

# This installs:
# - playwright (browser automation)
# - openai (Azure OpenAI API)
# - GitPython (git operations)
# - opencv-python (video processing)
# - aiofiles, pydantic, etc.

# Playwright browsers
playwright install chromium
```

### OpenVoice V2 (Manual Setup Required):
```bash
# Clone repository
git clone https://github.com/myshell-ai/OpenVoice.git

# Install
cd OpenVoice
pip install -e .

# Download checkpoints (see OpenVoice docs)
```

### FFmpeg (System Package):
```bash
# Already installed on your system ✅
ffmpeg -version  # 4.4.2
```

## Summary

**For this project to work:**
- ✅ Python packages: Install with `pip install -r requirements.txt`
- ✅ Playwright: Install with `playwright install chromium`
- ✅ FFmpeg: Already installed
- ⚠️ OpenVoice V2: Needs manual setup (see above)
- ❌ MCPs: None required

**For better development experience:**
- Consider adding Filesystem MCP
- Your existing Context7 MCP is useful for looking up library docs
- Your Puppeteer MCP is not used by this project

## How to Verify Everything Is Ready

```bash
# 1. Check Python version
python --version  # Should be 3.10+

# 2. Check if virtual environment is activated
which python  # Should point to venv/bin/python

# 3. Verify key packages are installed
python -c "import playwright; print('Playwright:', playwright.__version__)"
python -c "import openai; print('OpenAI:', openai.__version__)"
python -c "import git; print('GitPython OK')"

# 4. Check Playwright browsers
playwright --version

# 5. Check FFmpeg
ffmpeg -version

# 6. Test Azure OpenAI config
python -c "from src.config import config; print('Valid:', config.validate())"

# 7. Check OpenVoice V2 (after installation)
python -c "import openvoice; print('OpenVoice OK')"
```

## Troubleshooting

### "Module not found" errors
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Playwright errors
```bash
# Install browsers
playwright install chromium

# If permission issues
playwright install --with-deps chromium
```

### FFmpeg errors
```bash
# Verify it's in PATH
which ffmpeg

# Test a simple command
ffmpeg -version
```

### Azure OpenAI errors
```bash
# Check .env file exists and has values
cat .env

# Verify configuration loads
python -c "from src.config import config; print(config.azure_openai.endpoint)"
```
