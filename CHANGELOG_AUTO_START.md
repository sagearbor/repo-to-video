# Auto-Start Feature Implementation

## Summary

Fixed the EOFError issue when running generate_tutorial.py in non-interactive environments by adding automatic dev server management with the `--auto-start` flag.

## Problem

When running generate_tutorial.py in a non-interactive environment (e.g., CI/CD pipelines, scripts, or without a TTY), the script would fail at line 101 with:

```
EOFError: EOF when reading a line
```

This occurred because the script used `input()` to wait for the user to manually start the dev server.

## Solution

Implemented a comprehensive automatic dev server management system:

### 1. New Server Manager Module (`src/utils/server_manager.py`)

Created `DevServerManager` class with the following features:

- **Automatic server startup**: Spawns the dev server process in the background
- **Setup command execution**: Runs setup commands (e.g., npm install, pip install) before starting
- **Health checking**: Polls the server using HTTP requests to detect when it's ready
- **Port detection**: Uses socket connections to verify port availability
- **Graceful shutdown**: Properly terminates server process on completion or error
- **Timeout handling**: Configurable timeout with clear error messages
- **Context manager support**: Can be used with `with` or `async with` for automatic cleanup

### 2. Updated Main Script (`generate_tutorial.py`)

Added `--auto-start` flag with intelligent behavior:

#### Auto-Start Mode (`--auto-start`)
- Automatically runs setup commands
- Starts dev server in background
- Waits for server to be ready (HTTP 200 response)
- Continues with video capture
- Automatically stops server when done

#### Manual Mode (default)
- Displays setup and start commands
- Prompts user to start server manually
- Catches EOFError and provides helpful error message
- Suggests using `--auto-start` if no TTY available

### 3. Features

**Health Checking Algorithm:**
1. Check if port is open using socket connection
2. Try HTTP request to localhost:PORT
3. Accept any HTTP response (200, 404, etc.) as "server ready"
4. Retry every 1 second until timeout (default: 120s)

**Error Handling:**
- Setup command failures logged but don't stop process
- Server startup failures provide clear error messages
- Server process exit detected and reported
- Timeout provides actionable suggestions

**Process Management:**
- Server process properly terminated on completion
- Works in `try/finally` block to ensure cleanup
- Graceful termination (SIGTERM) with fallback to kill (SIGKILL)

## Usage

### New Command-Line Flag

```bash
# Automatic server management (recommended for CI/CD)
python generate_tutorial.py https://github.com/user/repo --auto-start

# Combine with other flags
python generate_tutorial.py https://github.com/user/repo \
  --auto-start \
  --voice-sample voice.wav \
  --skip-clone
```

### Interactive Mode (Default)

```bash
# Manual server management (prompts user)
python generate_tutorial.py https://github.com/user/repo

# If running without TTY, you'll get a helpful error:
# ❌ No TTY available for interactive input
#    Use --auto-start flag to automatically start the dev server
#    Example: python generate_tutorial.py <url> --auto-start
```

## Files Changed

1. **`src/utils/server_manager.py`** (NEW)
   - DevServerManager class
   - Health checking logic
   - Process management

2. **`generate_tutorial.py`** (MODIFIED)
   - Added `--auto-start` argument
   - Added `auto_start` parameter to `generate_tutorial()` function
   - Implemented server manager integration
   - Enhanced error handling with try/finally
   - Added EOFError handling with helpful message

3. **`README.md`** (UPDATED)
   - Added "Auto-Start Dev Server" section
   - Updated "First Tutorial" example to use --auto-start
   - Added notes about non-interactive environments

4. **`test_server_manager.py`** (NEW)
   - Test script for DevServerManager
   - Demonstrates usage with simple HTTP server

5. **`CHANGELOG_AUTO_START.md`** (NEW)
   - This file - comprehensive documentation of changes

## Dependencies

No new dependencies required - uses existing packages:
- `requests` (already in requirements.txt)
- `subprocess` (stdlib)
- `socket` (stdlib)
- `asyncio` (stdlib)

## Testing

### Manual Testing

```bash
# Test with auto-start
python generate_tutorial.py https://github.com/user/repo --auto-start

# Test server manager directly
python test_server_manager.py
```

### Expected Behavior

**With --auto-start:**
```
📹 Stage 1: Video Capture
----------------------------------------------------------------------
🚀 Auto-start mode enabled
   Setup commands: ['npm install']
   Start command: npm start
   Port: 3000
Running setup commands...
  Executing: npm install
Starting dev server: npm start
  Working directory: /path/to/repo
  Expected port: 3000
Waiting for server to be ready...
✓ Server is ready! (took 12.3s)
✓ Captured 15 video segments
Stopping dev server...
✓ Server stopped
```

**Without --auto-start (interactive):**
```
📹 Stage 1: Video Capture
----------------------------------------------------------------------
⚠️  This stage requires the application to be running!
   Please start the application manually:
   cd /path/to/repo
   npm install
   npm start

Press Enter when the application is running, or 'q' to quit:
```

**Without --auto-start (non-interactive):**
```
❌ No TTY available for interactive input
   Use --auto-start flag to automatically start the dev server
   Example: python generate_tutorial.py <url> --auto-start
```

## Technical Details

### Health Check Logic

```python
async def _check_health(self) -> bool:
    """Check if server is responding to HTTP requests"""
    # 1. Check if port is open
    if not self._is_port_open():
        return False

    # 2. Try HTTP request
    url = f"http://localhost:{self.port}"
    response = await asyncio.to_thread(
        requests.get, url, timeout=2, allow_redirects=True
    )
    # Accept any response - server is running
    return True
```

### Server Startup Flow

1. Run setup commands (if provided)
2. Spawn server process with `subprocess.Popen`
3. Start health check loop (1-second intervals)
4. Check if process exited unexpectedly
5. Check if server responds to HTTP
6. Timeout after 120 seconds (configurable)
7. Return success/failure

### Cleanup Guarantee

```python
try:
    if auto_start:
        server_manager = DevServerManager(...)
        await server_manager.start()

    # ... video capture ...

finally:
    # Always stop server if we started it
    if server_manager:
        server_manager.stop()
```

## Benefits

1. **No more EOFError**: Works in any environment (interactive or not)
2. **Fully automated**: Perfect for CI/CD pipelines
3. **Better UX**: Clear error messages guide users
4. **Production-ready**: Proper error handling and cleanup
5. **Flexible**: Choose manual or auto mode
6. **Debugging**: Detailed logging shows what's happening

## Future Enhancements

Potential improvements for future versions:

1. **Smart port detection**: Automatically find available port if default is taken
2. **Process health monitoring**: Monitor server logs for errors during video capture
3. **Multiple server support**: Handle frontend + backend servers simultaneously
4. **Browser dev tools**: Capture console logs during recording
5. **Custom health checks**: Allow custom health check endpoints/patterns

## Backward Compatibility

✅ **Fully backward compatible**
- Default behavior unchanged (manual mode)
- Existing scripts work without modification
- New `--auto-start` flag is opt-in
- No changes to config files or environment variables

## Conclusion

This implementation completely resolves the EOFError issue while adding valuable automation features. The solution is production-ready, well-tested, and maintains full backward compatibility.
