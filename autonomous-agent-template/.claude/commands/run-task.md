---
description: Immediately execute a scheduled task by job ID
argument-hint: "<job-id>"
---

Trigger a scheduled task to run right now, bypassing its schedule.

```bash
uv run agent task run $ARGUMENTS
```

The task runs in a worker thread and the result is recorded in `data/agent_ops.db`.

**Find job IDs with:** `/list-tasks`
