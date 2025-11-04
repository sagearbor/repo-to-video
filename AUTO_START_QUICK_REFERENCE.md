# Auto-Start Quick Reference

## The Problem We Solved

**Before:** Running the script without a TTY (e.g., in CI/CD) would fail with:
```
EOFError: EOF when reading a line
```

**After:** Use `--auto-start` flag to automatically start and manage the dev server.

## Quick Usage

### ✅ Recommended: Auto-Start Mode

```bash
# Simplest usage
python generate_tutorial.py https://github.com/user/repo --auto-start

# With all options
python generate_tutorial.py https://github.com/user/repo \
  --auto-start \
  --voice-sample voice.wav \
  --output ./videos/
```

**What happens:**
1. ✓ Dev server starts automatically
2. ✓ Script waits for server to be ready (polls HTTP endpoint)
3. ✓ Video capture begins when server responds
4. ✓ Server stops automatically when done

### Manual Mode (Default)

```bash
# Without --auto-start
python generate_tutorial.py https://github.com/user/repo
```

**What happens:**
1. ✓ Script shows setup commands
2. ✓ Prompts you to start server manually
3. ✓ You press Enter when ready
4. ✓ Video capture begins

⚠️ **Will fail if no TTY** (non-interactive environment)

## When to Use Each Mode

### Use `--auto-start` when:
- Running in CI/CD pipeline
- Running via cron job or scheduler
- Running in Docker without TTY
- Running via SSH without TTY
- You want fully automated workflow
- Testing locally without manual steps

### Use manual mode when:
- You want to see server logs
- You need to debug server startup
- You want control over when capture starts
- Running interactively and prefer manual control

## Error Messages and Solutions

### Error: "No TTY available for interactive input"

**Problem:** Running without `--auto-start` in non-interactive environment

**Solution:**
```bash
python generate_tutorial.py <url> --auto-start
```

### Error: "Failed to start dev server automatically"

**Possible causes:**
1. Server command is incorrect
2. Dependencies not installed
3. Port already in use
4. Server crashes on startup

**Solution:**
```bash
# Check the detected start command
cat output/action_manifest.json | grep start_command

# Try running manually first
cd temp_repos/<repo-name>
<run the start command shown>

# If it works manually, file a bug report
```

### Server takes too long to start

**Default timeout:** 120 seconds

**If your server needs more time:**
- The timeout is currently hardcoded
- Future enhancement: add `--timeout` flag
- Workaround: Start server manually before running script

## Technical Details

### Health Check Process

1. Checks if port is open (socket connection)
2. Tries HTTP GET to `http://localhost:<port>`
3. Accepts ANY HTTP response (200, 404, etc.)
4. Retries every 1 second
5. Times out after 120 seconds

### Server Management

**Startup:**
- Runs setup commands (npm install, pip install, etc.)
- Spawns server process in background
- Monitors for process crashes
- Waits for HTTP response

**Shutdown:**
- Sends SIGTERM (graceful)
- Waits 5 seconds
- Sends SIGKILL if still running
- Always runs (even on error)

## Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
- name: Generate tutorial video
  run: |
    python generate_tutorial.py \
      ${{ github.event.repository.clone_url }} \
      --auto-start \
      --output ./artifacts/
```

### Docker Container

```dockerfile
CMD ["python", "generate_tutorial.py", \
     "https://github.com/user/repo", \
     "--auto-start"]
```

### Shell Script

```bash
#!/bin/bash
set -e

repos=(
  "https://github.com/user/repo1"
  "https://github.com/user/repo2"
  "https://github.com/user/repo3"
)

for repo in "${repos[@]}"; do
  echo "Processing $repo..."
  python generate_tutorial.py "$repo" --auto-start
done
```

### Cron Job

```cron
# Generate video daily at 2 AM
0 2 * * * cd /path/to/repo-to-video && \
  /path/to/venv/bin/python generate_tutorial.py \
  https://github.com/user/repo --auto-start
```

## Debugging

### Enable verbose logging

```python
# In generate_tutorial.py, change logger level
logger = setup_logger('video_generator', level=logging.DEBUG)
```

### Check server process

```bash
# While script is running
ps aux | grep "python main.py"  # or npm, etc.

# Check port
netstat -tlnp | grep 8000  # replace with your port
```

### Test server manager directly

```bash
python test_server_manager.py
```

## FAQ

**Q: Can I use --auto-start with --skip-clone?**
A: Yes! Perfect for repeated runs:
```bash
python generate_tutorial.py <url> --skip-clone --auto-start
```

**Q: Does --auto-start work with all tech stacks?**
A: Yes, it uses the detected start command from Stage 0 analysis.

**Q: What if my server needs environment variables?**
A: They should be in your `.env` or set in your shell before running.

**Q: Can I see server logs?**
A: Currently captured but not displayed. Future enhancement planned.

**Q: What ports are supported?**
A: Any port detected by the analyzer (3000, 5000, 8000, 8080, etc.)

**Q: Does it work on Windows?**
A: Yes, uses cross-platform subprocess and socket APIs.

## Comparison

| Feature | Manual Mode | Auto-Start Mode |
|---------|-------------|-----------------|
| Interactive | ✓ | ✗ |
| CI/CD compatible | ✗ | ✓ |
| See server logs | ✓ | Future |
| Manual control | ✓ | ✗ |
| Fully automated | ✗ | ✓ |
| Error recovery | Manual | Automatic |
| Server cleanup | Manual | Automatic |
| Setup commands | Manual | Automatic |

## Migration Guide

### Old Way (Manual)

```bash
# Terminal 1: Start server manually
cd temp_repos/my-repo
npm install
npm start

# Terminal 2: Run generator
python generate_tutorial.py https://github.com/user/repo
# Press Enter when prompted
```

### New Way (Auto)

```bash
# Single command
python generate_tutorial.py https://github.com/user/repo --auto-start
```

**No more:**
- ✗ Multiple terminals
- ✗ Manual setup commands
- ✗ Waiting for server
- ✗ Remembering to stop server
- ✗ EOFError in CI/CD

**Benefits:**
- ✓ One command
- ✓ Automatic everything
- ✓ Works anywhere
- ✓ Clean shutdown
- ✓ Error handling
