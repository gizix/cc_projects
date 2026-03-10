# Autonomous Agent Template

A production-ready Python daemon for autonomous task automation. Schedule jobs, manage secrets, automate OS interactions, and chat with an LLM — all from a single self-contained process with a built-in web dashboard.

## What's Included

- **Task Scheduler** — APScheduler with SQLite job persistence. Cron, interval, and one-time triggers. Survives restarts.
- **5 Built-in Task Types** — desktop reminders, keyboard automation, program launch/close, HTTP requests, LLM inference
- **Encrypted Credential Store** — Fernet + PBKDF2-HMAC-SHA256. Values never in logs, never in SQLite.
- **Web Dashboard** — FastAPI + Tailwind + HTMX at `http://localhost:7890`. Live task management, LLM chat, log streaming.
- **LLM Chat** — Azure OpenAI (primary) with automatic fallback to OpenAI or any local model (Ollama, LM Studio).
- **Rust Extension** — Optional PyO3/Maturin module for fast key derivation and cron preview. Pure-Python fallback always available.
- **12 Slash Commands** — Full Claude Code integration with specialized agents and skills.

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (`pip install uv`)
- Rust toolchain (optional, for Rust extension): [rustup.rs](https://rustup.rs)

### Setup

```bash
# 1. Copy the template folder and open in VS Code
cd autonomous-agent-template

# 2. Configure environment
cp .env.example .env
# Edit .env: set MASTER_PASSWORD and at least one LLM provider

# 3. Install dependencies
uv sync

# 4. (Optional) Build Rust extension for best performance
maturin develop --manifest-path rust_ext/Cargo.toml

# 5. Start the agent with web UI
uv run agent run --foreground --ui
```

Open `http://localhost:7890` — the dashboard appears automatically.

## Configuration (`.env`)

```ini
# Required
MASTER_PASSWORD=your-strong-password-here

# LLM: Choose one
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# OR:
OPENAI_API_KEY=sk-...

# OR (local models):
OPENAI_BASE_URL=http://localhost:11434/v1   # Ollama
```

See `.env.example` for all options.

## CLI Reference

```bash
# Daemon
uv run agent run [--foreground] [--ui]
uv run agent stop [--force]
uv run agent status

# Schedule tasks
uv run agent schedule add <type> <trigger> '<config_json>'
uv run agent schedule list
uv run agent schedule remove <job-id>

# Run immediately
uv run agent task run <job-id>

# Credentials
uv run agent credential set <name>         # value prompted securely
uv run agent credential list               # names only, never values
uv run agent credential delete <name>

# LLM
uv run agent llm chat

# Dashboard
uv run agent ui
```

## Task Types

### Reminder (desktop notification)
```bash
uv run agent schedule add reminder "cron:0 9 * * MON-FRI" \
  '{"title": "Morning standup", "message": "Time for standup!", "timeout": 10}'
```

### HTTP Request (health check / webhook)
```bash
uv run agent schedule add http_request "interval:300" \
  '{"url": "https://myapp.com/health", "expected_status": 200}'
```

### LLM Inference (automated AI task)
```bash
uv run agent schedule add llm_inference "cron:0 8 * * *" \
  '{"system_prompt": "You are a daily briefer.", "user_prompt": "Morning briefing please."}'
```

### Text Fill (keyboard automation)
```bash
uv run agent schedule add text_fill "once:2025-06-01T09:00:00" \
  '{"text": "Hello World", "delay_before": 3.0}'
```

### Program Launcher
```bash
uv run agent schedule add program_launcher "cron:0 8 * * MON-FRI" \
  '{"action": "open", "program": "notepad"}'
```

## Credential Management

```bash
# Store a secret (value is prompted, hidden, never logged)
uv run agent credential set MY_API_KEY --description "Production API"

# Use in an HTTP task
uv run agent schedule add http_request "interval:60" \
  '{"url": "https://api.example.com/sync", "credential_name": "MY_API_KEY"}'

# List stored names (never values)
uv run agent credential list
```

## Web Dashboard

Start with `--ui` flag or run `/ui` in Claude Code:

| Page | Features |
|------|---------|
| **Dashboard** | Status pills, worker bar, next 5 fires, last 10 runs |
| **Tasks** | Sortable table, inline Run Now / Delete buttons |
| **Schedule** | Add-task wizard with live cron preview |
| **Credentials** | Metadata only, clearly marked as value-hidden |
| **LLM Chat** | Streaming SSE chat with model selector |
| **Logs** | Auto-refreshing task run history |

## Rust Extension (Optional)

```bash
# Build
maturin develop --manifest-path rust_ext/Cargo.toml

# Verify
python -c "import agent_core_ext; print(agent_core_ext.__version__)"
```

Provides:
- `hash_task_id(s)` — SHA-256 job ID hashing
- `cron_next_fire(expr, ts, n)` — cron schedule preview
- `derive_key(pwd, salt, iters)` — ~10× faster key derivation

All have pure-Python fallbacks — the agent works without the extension.

## Docker

```bash
# Build and start
docker compose up -d

# With external PostgreSQL
docker compose --profile external-db up -d

# Check status
docker compose exec agent agent status
```

## Adding Custom Tasks

1. Create `src/agent/tasks/my_task.py`:
```python
from agent.scheduler.registry import register_task
from agent.tasks.base import BaseTask, TaskResult

@register_task("my_task")
class MyTask(BaseTask):
    def run(self) -> TaskResult:
        value = self.config.get("key", "default")
        return TaskResult(status="success", data={"result": value})
```

2. Import in `src/agent/cli.py`:
```python
import agent.tasks.my_task  # noqa
```

3. Schedule it:
```bash
uv run agent schedule add my_task "cron:*/5 * * * *" '{"key": "hello"}'
```

For the complete guide, see the **task-definition** skill in Claude Code.

## Claude Code Integration

Open this folder in VS Code and launch Claude Code to access:

**Slash Commands:** `/run`, `/stop`, `/status`, `/schedule-task`, `/list-tasks`, `/run-task`, `/add-credential`, `/list-credentials`, `/llm-chat`, `/build-extension`, `/ui`, `/test`, `/prod-check`

**Agents (automatic):**
- `task-architect` — designs new task types
- `scheduler-expert` — cron expressions and APScheduler config
- `credential-guardian` — read-only secret security audit
- `automation-assistant` — platform-specific OS automation
- `llm-integration-expert` — Azure OpenAI and local model config
- `rust-extension-advisor` — PyO3/Maturin development

## Running Tests

```bash
uv run pytest tests/ -v --cov=src/agent --cov-report=term-missing
```

## License

MIT
