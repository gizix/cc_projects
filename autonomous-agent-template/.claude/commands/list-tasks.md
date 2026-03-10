---
description: List all scheduled jobs
argument-hint: "[--filter STATUS]"
---

Display all scheduled tasks in a Rich table.

```bash
uv run agent schedule list $ARGUMENTS
```

Shows job ID, name, and next scheduled run time for every active job.

**Tip:** Use `uv run agent task run <job-id>` to execute a job immediately.
