# Autonomous Agent Template

This is a production-ready autonomous task automation platform — a self-contained daemon with native scheduling, encrypted credential management, OS automation, multi-threaded execution, and an LLM chat interface (Azure OpenAI primary, any OpenAI-compatible API as fallback).

## Project Overview

**Language**: Python 3.11+
**Task Execution**: APScheduler 3.10+ with SQLAlchemyJobStore (SQLite)
**Concurrency**: `threading.ThreadPoolExecutor` (not asyncio — pyautogui/psutil are blocking)
**Database**: SQLAlchemy 2.0 sync ORM — two SQLite files: `agent_ops.db` (internal) + optional external DB
**Credentials**: Fernet + PBKDF2-HMAC-SHA256 encrypted JSON at `data/.credentials.enc`
**Web Dashboard**: FastAPI + Jinja2 + Tailwind CSS (CDN) + HTMX — runs in a daemon thread
**LLM**: Azure OpenAI (primary) → OpenAI → OpenAI-compatible (Ollama, LM Studio)
**Rust Extension**: PyO3 + Maturin — `agent_core_ext` module (graceful Python fallback)
**CLI**: Click with subcommand groups: `run` / `stop` / `status` / `schedule` / `task` / `credential` / `llm`
**Code Quality**: Ruff (linter + formatter), Mypy

## Project Structure

```
autonomous-agent-template/
├── src/agent/
│   ├── cli.py              # Click entry point (all commands)
│   ├── config.py           # Pydantic BaseSettings
│   ├── daemon.py           # PID-file daemon lifecycle
│   ├── scheduler/
│   │   ├── engine.py       # APScheduler + SQLAlchemyJobStore
│   │   ├── triggers.py     # Cron/interval/once builders
│   │   └── registry.py     # @register_task decorator
│   ├── tasks/
│   │   ├── base.py         # BaseTask ABC + TaskResult dataclass
│   │   ├── reminder.py     # Desktop notifications (plyer)
│   │   ├── text_fill.py    # Keyboard automation (pyautogui)
│   │   ├── program_launcher.py  # Open/close programs (psutil)
│   │   ├── http_task.py    # HTTP requests (httpx + tenacity)
│   │   └── llm_task.py     # LLM inference task
│   ├── db/
│   │   ├── engine.py       # SQLAlchemy engine (agent_ops.db)
│   │   ├── models.py       # TaskRun, CredentialRecord, AuditLog
│   │   ├── session.py      # Context-manager session
│   │   └── external.py     # External DB factory
│   ├── credentials/
│   │   ├── store.py        # CredentialStore: get/set/delete/rotate
│   │   ├── crypto.py       # Fernet + PBKDF2 (Rust ext if available)
│   │   └── env_bridge.py   # Inject creds as env vars for subprocesses
│   ├── llm/
│   │   ├── client.py       # LLMClient (Azure OpenAI + fallbacks)
│   │   ├── provider.py     # @register_provider registry
│   │   └── prompt.py       # PromptBuilder
│   ├── automation/
│   │   ├── keyboard.py     # pyautogui keyboard helpers
│   │   ├── process.py      # Cross-platform process management
│   │   └── notification.py # plyer desktop notifications
│   ├── utils/
│   │   ├── logging.py      # Rich logging handler
│   │   ├── threading.py    # ThreadPoolExecutor wrapper
│   │   └── retry.py        # Exponential backoff decorator
│   └── web/
│       ├── app.py          # FastAPI routes (all 6 views)
│       ├── server.py       # Start uvicorn in daemon thread
│       └── templates/      # Jinja2 + Tailwind + HTMX
├── rust_ext/
│   ├── Cargo.toml
│   └── src/lib.rs          # hash_task_id, cron_next_fire, derive_key
├── tests/
│   ├── conftest.py
│   ├── test_credentials.py
│   ├── test_scheduler.py
│   ├── test_tasks.py
│   ├── test_llm_client.py
│   └── test_rust_ext.py    # (skipped unless extension built)
├── pyproject.toml
├── Cargo.toml              # Workspace root
├── Dockerfile              # Multi-stage: rust-builder → python-builder → runtime
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Architecture Decisions

### Threading over Asyncio

This platform uses `threading.ThreadPoolExecutor`, not asyncio. Reasons:
- **pyautogui** is synchronous and blocks the calling thread
- **psutil** is synchronous
- **APScheduler** natively uses thread pools for job execution
- The web dashboard (FastAPI/uvicorn) runs in a separate daemon thread
- All I/O-bound tasks (HTTP, DB) are fast enough under threading for this use case

**Critical rule**: Do NOT introduce asyncio. Any `async def` in task code will break the scheduler's `ThreadPoolExecutor`.

### Two SQLite Files

- `data/agent_ops.db` — internal: TaskRun, CredentialRecord, AuditLog (managed by the agent)
- `data/scheduler_jobs.db` — APScheduler job persistence (managed by APScheduler)
- External DBs via `EXTERNAL_DB_URL` environment variable

### Credential Security Model

1. Values encrypted at rest (Fernet AES-128 + HMAC-SHA256)
2. PBKDF2-HMAC-SHA256 key derivation (600k iterations) — accelerated by Rust extension
3. Atomic write: `.credentials.enc.tmp` → verify → rename over original
4. `CredentialRecord` in SQLite stores **only name + metadata** — never values
5. Claude Code settings deny read/write of `.credentials.enc` (see `.claude/settings.json`)
6. Master password from `MASTER_PASSWORD` env var or interactive prompt — never stored

### Rust Extension (Optional)

Module `agent_core_ext` provides three Python-callable functions:
- `hash_task_id(s)` → SHA-256 hex (stable job IDs)
- `cron_next_fire(expr, ts, n)` → next N fire timestamps
- `derive_key(pwd, salt, iters)` → PBKDF2 key bytes (GIL released)

Every function has a pure-Python fallback. The extension is a performance enhancement, never a hard requirement.

## Coding Conventions

### Task Implementation

All tasks must:
1. Inherit from `BaseTask`
2. Be decorated with `@register_task("type-name")`
3. Implement `run() -> TaskResult`
4. Call `can_automate()` before any OS/GUI interaction
5. Catch all exceptions and return `TaskResult(status="error", ...)`
6. Be imported in `cli.py` for auto-registration

```python
from agent.scheduler.registry import register_task
from agent.tasks.base import BaseTask, TaskResult
from agent.utils.logging import get_logger

logger = get_logger(__name__)

@register_task("my_task")
class MyTask(BaseTask):
    def run(self) -> TaskResult:
        value = self.config.get("key", "default")
        if not self.can_automate():
            return TaskResult(status="skipped", message="Headless")
        try:
            # Do work
            return TaskResult(status="success", data={"result": value})
        except Exception as exc:
            logger.error("MyTask failed: %s", exc)
            return TaskResult(status="error", message=str(exc))
```

### Database Sessions

Always use the context manager:
```python
from agent.db.session import get_session

with get_session() as session:
    obj = MyModel(name="example")
    session.add(obj)
    # session.commit() called automatically on exit
```

### Credential Access

```python
from agent.credentials.store import get_store

store = get_store()  # uses MASTER_PASSWORD env var
value = store.get("MY_API_KEY")  # None if not found
```

**Never log credential values.** Use `logger.debug("Using credential '%s'", name)`.

### Logging

```python
from agent.utils.logging import get_logger
logger = get_logger(__name__)

# Use %s formatting — not f-strings in log calls
logger.info("Task %s completed in %.2fs", task_id, elapsed)
```

### Config Access

```python
from agent.config import settings

# Access any setting
print(settings.worker_threads)
print(settings.internal_db_url)
```

## Trigger Format Reference

```
cron:<min> <hour> <dom> <month> <dow>   e.g. cron:*/5 * * * *
interval:<seconds>                       e.g. interval:300
once:<ISO datetime>                      e.g. once:2025-06-01T09:00:00
```

## Available CLI Commands

```bash
agent run [--foreground] [--ui]         # Start daemon
agent stop [--force]                    # Stop daemon
agent status                            # Daemon state + recent runs

agent schedule add <type> <trigger> <json>  # Add scheduled task
agent schedule list                         # List all jobs
agent schedule remove <job-id>              # Remove a job

agent task run <job-id>                 # Run immediately

agent credential set <name>             # Store encrypted secret
agent credential get <name>             # Print value (scripting)
agent credential list                   # Names + metadata only
agent credential delete <name>          # Remove a credential

agent llm chat [--model] [--system-prompt]  # Interactive chat
agent ui                                # Open web dashboard
```

## Available Slash Commands

- `/run [--foreground] [--ui]` — Start agent daemon
- `/stop [--force]` — Gracefully stop daemon
- `/status` — Daemon state, next 5 fires, last 5 outcomes
- `/schedule-task <type> <trigger> <config>` — Add scheduled task with cron preview
- `/list-tasks` — All scheduled jobs in a Rich table
- `/run-task <job-id>` — Execute a task immediately
- `/add-credential <name>` — Store encrypted secret (value prompted)
- `/list-credentials` — Names and metadata only
- `/llm-chat [--model] [--system-prompt]` — Interactive streaming chat
- `/build-extension [--release]` — Compile Rust extension + verify import
- `/ui` — Open web dashboard at http://localhost:7890
- `/test [path] [-k filter]` — pytest with coverage
- `/prod-check` — Pre-deployment checklist

## Available Agents

- **task-architect** — PROACTIVELY designs new task types and config schemas
- **scheduler-expert** — PROACTIVELY assists with APScheduler cron expressions and persistence
- **credential-guardian** — PROACTIVELY read-only audits code touching secrets (never writes)
- **automation-assistant** — PROACTIVELY handles pyautogui/psutil/plyer platform quirks
- **llm-integration-expert** — PROACTIVELY assists with Azure OpenAI, streaming, 429 retry
- **rust-extension-advisor** — PROACTIVELY helps with PyO3, GIL release, maturin failures

## Available Skills

- **task-definition** — BaseTask template, TaskResult pattern, @register_task decorator
- **credential-management** — CredentialStore.get(), env_bridge injection, rotation workflow
- **scheduler-patterns** — Cron/interval/once examples, timezone handling, misfire config
- **llm-prompt-design** — PromptBuilder usage, JSON-mode structured output, template sanitization

## Development Workflow

### First-time Setup

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# 2. Install dependencies
uv sync

# 3. (Optional) Build Rust extension
maturin develop --manifest-path rust_ext/Cargo.toml

# 4. Start the agent
uv run agent run --foreground --ui
```

### Running Tests

```bash
uv run pytest tests/ -v --cov=src/agent
```

### Adding a New Task Type

1. Create `src/agent/tasks/my_task.py` — use the **task-definition** skill
2. Import in `cli.py` (`import agent.tasks.my_task  # noqa`)
3. Add tests in `tests/test_tasks.py`
4. Schedule: `uv run agent schedule add my_task "cron:*/5 * * * *" '{...}'`

## Web Dashboard

The dashboard runs at `http://127.0.0.1:7890` when the daemon is running.

| Page | Description |
|------|-------------|
| Dashboard | Daemon status, workers, next 5 fires, last 10 runs |
| Tasks | All jobs with Run Now / Delete (HTMX actions) |
| Schedule | Wizard form with cron preview |
| Credentials | Metadata only — values never shown |
| LLM Chat | Streaming chat via Server-Sent Events |
| Logs | Last 200 entries, auto-refreshes every 3s |

Launch with browser: `uv run agent run --ui`

## Security Best Practices

1. **Never commit `.env`** — it's in `.gitignore`
2. **Never commit `data/`** — contains SQLite + credential store
3. **Strong master password** — use `python -c "import secrets; print(secrets.token_urlsafe(32))"`
4. **`.credentials.enc` is unreadable to Claude Code** — enforced in `settings.json`
5. **Rotate credentials regularly** — use `store.rotate(new_password)`
6. **Audit logs** — all credential access is recorded in `AuditLog` table
7. **Headless Docker** — `AGENT_HEADLESS=1` disables OS automation safely

## Troubleshooting

### "Master password not set"
Set `MASTER_PASSWORD=your-password` in `.env` or pass `--password` to credential commands.

### "No LLM provider configured"
Set at least one of: `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT`, or `OPENAI_API_KEY`, or `OPENAI_BASE_URL`.

### "agent_core_ext not found"
The Rust extension is optional. Build it with: `maturin develop --manifest-path rust_ext/Cargo.toml`

### Tasks show status="skipped"
On Linux/Docker: `DISPLAY` is not set. Set `AGENT_HEADLESS=0` to force-run (only for tasks that actually need a display).

### Scheduler jobs lost after restart
Ensure `data/scheduler_jobs.db` persists. In Docker, mount the `/app/data` volume.

### APScheduler "job store not found"
Call `init_db()` and `start_scheduler()` before any `add_job()` calls.

## Docker Deployment

```bash
# Build and run
docker compose up -d

# With external PostgreSQL
docker compose --profile external-db up -d

# View logs
docker compose logs -f agent

# Execute CLI commands in running container
docker compose exec agent agent status
docker compose exec agent agent credential list
```

## Production Checklist

Run `/prod-check` or manually verify:
- [ ] `MASTER_PASSWORD` set (strong, random)
- [ ] LLM provider credentials configured
- [ ] `data/` directory persistent (volume mount in Docker)
- [ ] Rust extension built: `python -c "import agent_core_ext"`
- [ ] Tests passing: `uv run pytest tests/ -v`
- [ ] No hardcoded secrets in source
- [ ] `DEBUG` / verbose logging disabled
- [ ] Docker: `AGENT_HEADLESS=1` set

## Resources

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Click Documentation](https://click.palletsprojects.com/)
- [PyO3 Documentation](https://pyo3.rs/)
- [Maturin Documentation](https://www.maturin.rs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

---

This template is designed for production use. All patterns are battle-tested and optimised for a single-process, self-contained automation daemon. Follow the threading-first architecture — do not introduce asyncio into task code.
