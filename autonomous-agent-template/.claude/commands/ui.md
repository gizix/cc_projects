---
description: Open the web dashboard in the default browser
---

Open the agent web dashboard at `http://localhost:7890`.

```bash
uv run agent ui
```

**Dashboard pages:**
| Page | Description |
|------|-------------|
| Dashboard | Daemon status, worker bar, next 5 fires, last 10 runs |
| Tasks | All scheduled jobs with Run Now / Delete actions |
| Schedule | Wizard to add tasks with trigger preview |
| Credentials | Names + metadata only (values never shown) |
| LLM Chat | Streaming chat with model selector |
| Logs | Last 200 task run lines, auto-refreshes every 3s |

**Requires:** Agent daemon running (`/run` or `agent run`)
