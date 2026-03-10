---
description: Gracefully stop the agent daemon
argument-hint: "[--force]"
---

Stop the running agent daemon.

```bash
uv run agent stop $ARGUMENTS
```

**Options:**
- `--force`: Send SIGKILL instead of SIGTERM (use if graceful stop hangs)

The daemon will complete any in-progress task runs before shutting down (unless `--force` is used).
