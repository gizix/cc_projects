---
description: Show daemon state, worker utilization, next 5 fires, last 5 outcomes
---

Display the current agent status.

```bash
uv run agent status
```

**Output includes:**
- Daemon running/stopped + PID
- Next 5 scheduled job fire times
- Rich table of the last 5 task run outcomes (status, type, timestamp)
- Worker thread utilization

**Tip:** For a live view, open the web dashboard: `/ui`
