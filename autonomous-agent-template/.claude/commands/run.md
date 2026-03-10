---
description: Start the agent daemon (scheduler + web UI)
argument-hint: "[--foreground] [--ui]"
---

Start the autonomous agent daemon. The scheduler and web dashboard launch together.

```bash
uv run agent run $ARGUMENTS
```

**Options:**
- `--foreground` / `-f`: Stay in foreground (no PID file, useful for debugging)
- `--ui`: Open web dashboard at http://localhost:7890 in the default browser

**What starts:**
1. Internal SQLite database initialised (`data/agent_ops.db`)
2. APScheduler loaded from `data/scheduler_jobs.db`
3. FastAPI web dashboard at http://127.0.0.1:7890
4. PID file written to `data/agent.pid`

**Stop with:** `/stop` or `Ctrl+C` (foreground mode)
