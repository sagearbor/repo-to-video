# Auto-Start Feature Flow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  generate_tutorial.py                       │
│                                                             │
│  1. Parse arguments (--auto-start flag)                    │
│  2. Stage 0: Analyze repo & detect tech stack              │
│  3. Stage 1: Video capture (needs running server)          │
│     ├─ if --auto-start: Use DevServerManager               │
│     └─ else: Prompt user manually                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────┐
        │     Is --auto-start enabled?         │
        └──────────────────────────────────────┘
                   │                    │
              YES  │                    │  NO
                   ▼                    ▼
    ┌──────────────────────┐   ┌─────────────────────┐
    │  DevServerManager    │   │  Manual Mode        │
    │  (Automatic)         │   │  (Interactive)      │
    └──────────────────────┘   └─────────────────────┘
             │                          │
             │                          ▼
             │                  ┌─────────────────┐
             │                  │  Has TTY?       │
             │                  └─────────────────┘
             │                     │           │
             │                  YES│           │NO
             │                     ▼           ▼
             │              ┌──────────┐  ┌──────────┐
             │              │  Prompt  │  │ EOFError │
             │              │   User   │  │  with    │
             │              └──────────┘  │  Help    │
             │                            └──────────┘
             │
             ▼
    ┌─────────────────────────────────────────────┐
    │          DevServerManager Flow              │
    ├─────────────────────────────────────────────┤
    │  1. Run setup commands                      │
    │     ├─ npm install                          │
    │     ├─ pip install -r requirements.txt      │
    │     └─ etc.                                 │
    │                                             │
    │  2. Spawn server process                    │
    │     └─ subprocess.Popen(start_command)      │
    │                                             │
    │  3. Health check loop (every 1 second)      │
    │     ├─ Check if process crashed             │
    │     ├─ Check if port is open (socket)       │
    │     ├─ Try HTTP GET request                 │
    │     └─ Retry until timeout (120s)           │
    │                                             │
    │  4. Server ready ✓                          │
    │     └─ Return success                       │
    │                                             │
    │  5. Video capture proceeds                  │
    │                                             │
    │  6. Cleanup (finally block)                 │
    │     ├─ Send SIGTERM                         │
    │     ├─ Wait 5 seconds                       │
    │     └─ Send SIGKILL if needed               │
    └─────────────────────────────────────────────┘
```

## Detailed Health Check Flow

```
┌─────────────────────────────────────────────────────────────┐
│               Health Check Algorithm                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Wait 1 second   │
                    └──────────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │  Process still alive?  │
                  └────────────────────────┘
                       │              │
                   YES │              │ NO
                       ▼              ▼
              ┌──────────────┐   ┌─────────────┐
              │ Check Port   │   │   FAILED    │
              │ (socket)     │   │ (crashed)   │
              └──────────────┘   └─────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Port open?      │
              └──────────────────┘
                   │          │
              YES  │          │  NO
                   ▼          ▼
          ┌───────────┐   ┌─────────┐
          │ Try HTTP  │   │  Retry  │
          │  Request  │   └─────────┘
          └───────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ HTTP response?   │
          └──────────────────┘
                   │
              ┌────┴────┐
              │         │
        YES   ▼         ▼   NO (timeout/error)
      ┌─────────┐   ┌─────────┐
      │ SUCCESS │   │  Retry  │
      │ (ready) │   └─────────┘
      └─────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Scenarios                          │
└─────────────────────────────────────────────────────────────┘

1. Manual Mode + No TTY
   ┌──────────────┐
   │ input() call │
   └──────────────┘
          │
          ▼
   ┌──────────────┐
   │   EOFError   │
   └──────────────┘
          │
          ▼
   ┌─────────────────────────────────┐
   │ catch EOFError:                 │
   │   show clear error message      │
   │   suggest --auto-start          │
   │   exit with code 1              │
   └─────────────────────────────────┘


2. Auto-Start + Server Fails
   ┌──────────────────┐
   │ server.start()   │
   └──────────────────┘
          │
          ▼
   ┌──────────────────┐
   │ Returns False    │
   └──────────────────┘
          │
          ▼
   ┌─────────────────────────────────┐
   │ logger.error("Failed to start") │
   │ exit with code 1                │
   └─────────────────────────────────┘


3. Auto-Start + Server Crashes
   ┌──────────────────┐
   │ Health check     │
   └──────────────────┘
          │
          ▼
   ┌──────────────────┐
   │ process.poll()   │
   │ != None          │
   └──────────────────┘
          │
          ▼
   ┌─────────────────────────────────┐
   │ Get stdout/stderr               │
   │ logger.error("Process exited")  │
   │ Return False                    │
   └─────────────────────────────────┘


4. Cleanup Always Runs
   ┌──────────────────┐
   │ try:             │
   │   start server   │
   │   capture video  │
   └──────────────────┘
          │
          ▼
   ┌──────────────────┐
   │ finally:         │
   │   stop server    │
   └──────────────────┘
    (Always executes)
```

## State Diagram

```
                        ┌──────────┐
                        │  START   │
                        └──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Parse --auto-start  │
                   └─────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
               enabled               disabled
                    │                   │
                    ▼                   ▼
        ┌────────────────────┐   ┌─────────────┐
        │  Create Server     │   │   Manual    │
        │  Manager           │   │   Prompt    │
        └────────────────────┘   └─────────────┘
                    │                   │
                    ▼                   │
        ┌────────────────────┐          │
        │  Run Setup Cmds    │          │
        └────────────────────┘          │
                    │                   │
                    ▼                   │
        ┌────────────────────┐          │
        │  Spawn Process     │          │
        └────────────────────┘          │
                    │                   │
                    ▼                   │
        ┌────────────────────┐          │
        │  Health Check Loop │          │
        │  (max 120s)        │          │
        └────────────────────┘          │
                    │                   │
              ┌─────┴─────┐             │
              │           │             │
          ready      timeout           │
              │           │             │
              ▼           ▼             │
        ┌─────────┐  ┌────────┐        │
        │ SUCCESS │  │  FAIL  │        │
        └─────────┘  └────────┘        │
              │           │             │
              └───────┬───┴─────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │  Capture Video   │
            └──────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │  Stop Server     │
            │  (if started)    │
            └──────────────────┘
                      │
                      ▼
                  ┌──────┐
                  │ DONE │
                  └──────┘
```

## Component Interaction

```
┌────────────────────────────────────────────────────────────────┐
│                     Component Diagram                          │
└────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  generate_tutorial.py                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  async def generate_tutorial(auto_start=False)      │   │
│  │                                                     │   │
│  │  if auto_start:                                     │   │
│  │      server_manager = DevServerManager(...)         │   │
│  │      await server_manager.start()                   │   │
│  │                                                     │   │
│  │  try:                                               │   │
│  │      await capture_video_segments(...)              │   │
│  │  finally:                                           │   │
│  │      if server_manager:                             │   │
│  │          server_manager.stop()                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              src/utils/server_manager.py                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  class DevServerManager:                            │   │
│  │                                                     │   │
│  │      async def start(timeout=120):                  │   │
│  │          1. Run setup commands                      │   │
│  │          2. Spawn process                           │   │
│  │          3. Health check loop                       │   │
│  │          4. Return success/failure                  │   │
│  │                                                     │   │
│  │      def stop():                                    │   │
│  │          1. SIGTERM                                 │   │
│  │          2. Wait 5s                                 │   │
│  │          3. SIGKILL if needed                       │   │
│  │                                                     │   │
│  │      async def _check_health():                     │   │
│  │          1. Check port (socket)                     │   │
│  │          2. Try HTTP request                        │   │
│  │          3. Return True/False                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   System Libraries                          │
│                                                             │
│  ┌──────────────┐  ┌───────────┐  ┌─────────────────┐      │
│  │ subprocess   │  │  socket   │  │    requests     │      │
│  │  .Popen()    │  │ .connect()│  │     .get()      │      │
│  └──────────────┘  └───────────┘  └─────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Timeline Comparison

### Without --auto-start (Manual)
```
Time  │ User Action                     │ System State
──────┼─────────────────────────────────┼──────────────────
0:00  │ Run: python generate_tutorial.py│ Stage 0 starts
0:30  │ (wait for analysis)             │ Analyzing repo
1:00  │ See prompt: "Start server..."   │ Waiting
1:05  │ Open new terminal               │ Waiting
1:10  │ cd temp_repos/repo              │ Waiting
1:15  │ npm install                     │ Waiting
2:00  │ npm start                       │ Waiting
2:15  │ Wait for server...              │ Waiting
2:30  │ Press Enter                     │ Stage 1 starts
7:30  │                                 │ Done
```

### With --auto-start (Automatic)
```
Time  │ User Action                     │ System State
──────┼─────────────────────────────────┼──────────────────
0:00  │ Run: python ... --auto-start    │ Stage 0 starts
0:30  │ (walk away, get coffee)         │ Analyzing repo
1:00  │                                 │ Running npm install
1:30  │                                 │ Starting server
1:45  │                                 │ Health checking
2:00  │                                 │ Server ready!
2:01  │                                 │ Stage 1 starts
7:01  │                                 │ Done
```

**Time saved: ~30 seconds**
**User effort saved: 6 manual steps**

## Success Criteria

✅ Works in CI/CD (no TTY)
✅ Works interactively (with TTY)
✅ Backward compatible (default unchanged)
✅ Clear error messages
✅ Automatic cleanup
✅ Health checking
✅ Timeout handling
✅ Process monitoring
✅ Cross-platform
✅ Well documented
