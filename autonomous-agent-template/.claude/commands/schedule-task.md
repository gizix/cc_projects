---
description: Add a scheduled task with optional cron preview
argument-hint: "<task_type> <trigger> '<config_json>' [--preview] [--job-id ID]"
---

Schedule a new task. Previews next fire times when using cron triggers.

```bash
uv run agent schedule add $ARGUMENTS
```

**Task types:** `reminder` | `text_fill` | `program_launcher` | `http_request` | `llm_inference`

**Trigger formats:**
| Format | Example |
|--------|---------|
| `cron:<5-field>` | `cron:*/5 * * * *` |
| `interval:<seconds>` | `interval:300` |
| `once:<ISO datetime>` | `once:2025-06-01T09:00:00` |

**Examples:**

```bash
# Reminder every 30 minutes
uv run agent schedule add reminder "cron:*/30 * * * *" '{"title":"Check In","message":"Time to check email"}' --preview

# HTTP health check every 5 minutes
uv run agent schedule add http_request "interval:300" '{"url":"https://example.com/health","expected_status":200}'

# LLM summary every morning at 8 AM
uv run agent schedule add llm_inference "cron:0 8 * * *" '{"system_prompt":"You are a daily briefer.","user_prompt":"Give me a morning briefing."}'
```

Add `--preview` to see the next 5 fire times before committing.
