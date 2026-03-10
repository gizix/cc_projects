---
name: scheduler-patterns
description: Provides cron/interval/one-time examples, timezone handling, and misfire config when scheduling complex tasks. Activates when user configures schedules or needs cron expression help.
allowed-tools: Read, Write
---

You provide comprehensive scheduling patterns and examples for the Autonomous Agent scheduler.

## When to Activate

- User needs help with cron syntax
- User asks "how do I schedule X every Y"
- User configures a complex recurring schedule
- User asks about timezone handling or misfire behavior

## Trigger Format Quick Reference

```
Format:   cron:<min> <hour> <dom> <month> <dow>
Example:  cron:*/5 * * * *   = every 5 minutes

Format:   interval:<seconds>
Example:  interval:300        = every 5 minutes exactly

Format:   once:<ISO datetime>
Example:  once:2025-06-01T09:00:00  = one-time on Jun 1 at 9 AM UTC
```

## Cron Expression Library

| Schedule | Expression |
|----------|-----------|
| Every minute | `cron:* * * * *` |
| Every 5 minutes | `cron:*/5 * * * *` |
| Every hour | `cron:0 * * * *` |
| Every day at midnight | `cron:0 0 * * *` |
| Every day at 9 AM UTC | `cron:0 9 * * *` |
| Every weekday at 9 AM | `cron:0 9 * * MON-FRI` |
| Every Monday at 8 AM | `cron:0 8 * * MON` |
| First of month midnight | `cron:0 0 1 * *` |
| Every quarter (Jan/Apr/Jul/Oct) | `cron:0 0 1 */3 *` |
| Every 15 min during biz hours | `cron:*/15 8-17 * * MON-FRI` |

## CLI Examples

```bash
# Desktop reminder every 30 minutes
uv run agent schedule add reminder "cron:*/30 * * * *" \
  '{"title": "Take a break", "message": "Stand up and stretch"}'

# HTTP health check every 5 minutes
uv run agent schedule add http_request "interval:300" \
  '{"url": "https://myapp.example.com/health", "expected_status": 200}'

# LLM morning briefing on weekdays at 8 AM UTC
uv run agent schedule add llm_inference "cron:0 8 * * MON-FRI" \
  '{"system_prompt": "You are a daily briefer.", "user_prompt": "Morning summary"}'

# One-time task on a specific date
uv run agent schedule add reminder "once:2025-07-04T12:00:00" \
  '{"title": "Holiday!", "message": "Happy 4th of July"}'

# Preview cron before scheduling
uv run agent schedule add reminder "cron:0 9 * * *" \
  '{"title": "Morning", "message": "Good morning"}' --preview
```

## Programmatic Scheduling

```python
from agent.scheduler.engine import add_job

# Add from within a task or script
job_id = add_job(
    task_type="http_request",
    trigger_str="cron:*/10 8-22 * * *",  # every 10 min, 8am-10pm
    config={
        "url": "https://api.example.com/sync",
        "method": "POST",
        "credential_name": "API_TOKEN",
    },
    job_id="sync-api-job",  # optional stable ID
)
```

## Misfire Configuration

Misfires occur when the scheduler was stopped during a scheduled fire time.

```python
# In scheduler/engine.py job_defaults:
job_defaults = {
    "coalesce": True,          # Merge all missed runs into ONE
    "max_instances": 1,        # No parallel executions of same job
    "misfire_grace_time": 60,  # Fire if up to 60s late
}
```

**Per-job override:**
```python
from apscheduler.triggers.cron import CronTrigger
sched.add_job(
    fn,
    trigger=CronTrigger(minute="*/5"),
    misfire_grace_time=300,    # This job: 5-minute grace
    coalesce=False,            # Run each missed instance
)
```

## Timezone Notes

All times are **UTC** by default. To schedule in local time:

```python
from apscheduler.triggers.cron import CronTrigger
import pytz

# 9 AM New York time
trigger = CronTrigger(hour=9, minute=0, timezone=pytz.timezone("America/New_York"))
```

For the CLI trigger strings, convert your local time to UTC first:
- New York (EST, UTC-5): 9 AM local = `cron:0 14 * * *`
- London (GMT): same as UTC
- Tokyo (JST, UTC+9): 9 AM local = `cron:0 0 * * *`

## Viewing Upcoming Fires

```bash
# Preview via CLI
uv run agent schedule add reminder "cron:0 9 * * MON-FRI" '{}' --preview

# Via Python
from agent.scheduler.triggers import preview_cron
for fire in preview_cron("0 9 * * MON-FRI", count=5):
    print(fire)
```

## Removing and Modifying Jobs

```bash
# Remove a job
uv run agent schedule remove <job-id>

# List all jobs to find IDs
uv run agent schedule list
```
