"""Click CLI entry point: agent run / stop / status / schedule / credential / task / llm."""

from __future__ import annotations

import json
import signal
import sys
import time
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from agent.config import settings
from agent.utils.logging import configure_logging, get_logger

console = Console()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------


@click.group()
@click.option("--log-level", default="INFO", help="Logging level")
def main(log_level: str) -> None:
    """Autonomous Agent — task scheduler, credential store, OS automation, LLM chat."""
    configure_logging(log_level)


# ---------------------------------------------------------------------------
# agent run
# ---------------------------------------------------------------------------


@main.command()
@click.option("--foreground", "-f", is_flag=True, default=False, help="Run in foreground (no daemonize)")
@click.option("--ui", is_flag=True, default=False, help="Open web dashboard in browser")
def run(foreground: bool, ui: bool) -> None:
    """Start the agent daemon (scheduler + web dashboard)."""
    from agent import daemon
    from agent.db.engine import init_db
    from agent.scheduler.engine import start_scheduler
    from agent.web.server import start_web_server

    # Ensure tasks are registered
    import agent.tasks.reminder  # noqa
    import agent.tasks.text_fill  # noqa
    import agent.tasks.program_launcher  # noqa
    import agent.tasks.http_task  # noqa
    import agent.tasks.llm_task  # noqa

    settings.ensure_data_dir()
    init_db()

    if not foreground:
        daemon.start(settings.pid_file)

    console.print("[green]Starting agent…[/green]")
    start_scheduler()

    if ui:
        settings.web_open_browser = True
    start_web_server()

    console.print(
        f"[bold green]Agent running[/bold green] — web UI: http://{settings.web_host}:{settings.web_port}"
    )

    def _shutdown(signum, frame):
        console.print("\n[yellow]Shutting down…[/yellow]")
        from agent.scheduler.engine import stop_scheduler

        stop_scheduler()
        daemon.cleanup(settings.pid_file)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        _shutdown(None, None)


# ---------------------------------------------------------------------------
# agent stop
# ---------------------------------------------------------------------------


@main.command()
@click.option("--force", is_flag=True, default=False, help="SIGKILL instead of SIGTERM")
def stop(force: bool) -> None:
    """Stop the running agent daemon."""
    from agent import daemon

    if daemon.stop(settings.pid_file, force=force):
        console.print("[green]Stop signal sent[/green]")
    else:
        console.print("[yellow]Agent does not appear to be running[/yellow]")


# ---------------------------------------------------------------------------
# agent status
# ---------------------------------------------------------------------------


@main.command()
def status() -> None:
    """Show daemon state, next 5 scheduled fires, last 5 task outcomes."""
    from agent import daemon
    from agent.db.session import get_session
    from agent.db.models import TaskRun
    from sqlalchemy import select

    running = daemon.is_running(settings.pid_file)
    pid = daemon.get_pid(settings.pid_file)

    console.print(
        f"[bold]Daemon:[/bold] {'[green]running[/green]' if running else '[red]stopped[/red]'}"
        + (f" (PID {pid})" if pid else "")
    )

    # Scheduler jobs
    try:
        from agent.scheduler.engine import list_jobs

        jobs = list_jobs()
        if jobs:
            console.print(f"\n[bold]Next {min(5,len(jobs))} scheduled fires:[/bold]")
            for j in jobs[:5]:
                console.print(f"  {j['id']:40s}  {j['next_run'] or '—'}")
    except Exception:
        pass

    # Recent runs
    try:
        with get_session() as session:
            stmt = select(TaskRun).order_by(TaskRun.started_at.desc()).limit(5)
            runs = session.execute(stmt).scalars().all()
        if runs:
            table = Table(title="Last 5 Task Runs", show_header=True)
            table.add_column("Job ID")
            table.add_column("Type")
            table.add_column("Status")
            table.add_column("Started")
            for r in runs:
                table.add_row(
                    r.job_id,
                    r.task_type,
                    f"[green]{r.status}[/green]" if r.status == "success" else f"[red]{r.status}[/red]",
                    r.started_at.strftime("%Y-%m-%d %H:%M:%S") if r.started_at else "",
                )
            console.print(table)
    except Exception as e:
        console.print(f"[yellow]Could not read task runs: {e}[/yellow]")


# ---------------------------------------------------------------------------
# schedule group
# ---------------------------------------------------------------------------


@main.group()
def schedule() -> None:
    """Manage scheduled tasks."""


@schedule.command("add")
@click.argument("task_type")
@click.argument("trigger")
@click.argument("config_json")
@click.option("--job-id", default=None, help="Optional custom job ID")
@click.option("--preview", is_flag=True, default=False, help="Preview next fires before adding")
def schedule_add(task_type: str, trigger: str, config_json: str, job_id: Optional[str], preview: bool) -> None:
    """Add a scheduled task.

    TASK_TYPE: reminder | text_fill | program_launcher | http_request | llm_inference\n
    TRIGGER: cron:*/5 * * * *  |  interval:300  |  once:2025-01-01T09:00:00\n
    CONFIG_JSON: JSON string with task configuration
    """
    import agent.tasks.reminder  # noqa
    import agent.tasks.text_fill  # noqa
    import agent.tasks.program_launcher  # noqa
    import agent.tasks.http_task  # noqa
    import agent.tasks.llm_task  # noqa
    from agent.db.engine import init_db
    from agent.scheduler.engine import add_job, start_scheduler, stop_scheduler

    try:
        config = json.loads(config_json)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON config: {e}[/red]")
        sys.exit(1)

    if preview and trigger.startswith("cron:"):
        from agent.scheduler.triggers import preview_cron

        expr = trigger[5:]
        console.print("[bold]Next 5 fire times:[/bold]")
        for fire in preview_cron(expr):
            console.print(f"  {fire}")

    settings.ensure_data_dir()
    init_db()
    start_scheduler()
    jid = add_job(task_type, trigger, config, job_id=job_id)
    stop_scheduler()
    console.print(f"[green]Scheduled job:[/green] {jid}")


@schedule.command("list")
@click.option("--filter", "status_filter", default=None)
def schedule_list(status_filter: Optional[str]) -> None:
    """List all scheduled jobs."""
    from agent.db.engine import init_db
    from agent.scheduler.engine import list_jobs, start_scheduler, stop_scheduler

    settings.ensure_data_dir()
    init_db()
    start_scheduler()
    jobs = list_jobs()
    stop_scheduler()

    if not jobs:
        console.print("[yellow]No scheduled jobs[/yellow]")
        return

    table = Table(title="Scheduled Jobs", show_header=True)
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Next Run")
    for j in jobs:
        table.add_row(j["id"], j["name"], j["next_run"] or "—")
    console.print(table)


@schedule.command("remove")
@click.argument("job_id")
def schedule_remove(job_id: str) -> None:
    """Remove a scheduled job by ID."""
    from agent.db.engine import init_db
    from agent.scheduler.engine import remove_job, start_scheduler, stop_scheduler

    settings.ensure_data_dir()
    init_db()
    start_scheduler()
    ok = remove_job(job_id)
    stop_scheduler()
    if ok:
        console.print(f"[green]Removed job:[/green] {job_id}")
    else:
        console.print(f"[red]Job not found:[/red] {job_id}")


# ---------------------------------------------------------------------------
# task group
# ---------------------------------------------------------------------------


@main.group()
def task() -> None:
    """Run tasks immediately."""


@task.command("run")
@click.argument("job_id")
def task_run(job_id: str) -> None:
    """Immediately execute a scheduled task by job ID."""
    from agent.db.engine import init_db
    from agent.scheduler.engine import run_job_now, start_scheduler
    from agent.utils.threading import shutdown

    import agent.tasks.reminder  # noqa
    import agent.tasks.text_fill  # noqa
    import agent.tasks.program_launcher  # noqa
    import agent.tasks.http_task  # noqa
    import agent.tasks.llm_task  # noqa

    settings.ensure_data_dir()
    init_db()
    start_scheduler()

    ok = run_job_now(job_id)
    if ok:
        console.print(f"[green]Task '{job_id}' queued for immediate execution[/green]")
        time.sleep(3)
    else:
        console.print(f"[red]Job '{job_id}' not found[/red]")
    shutdown(wait=True)


# ---------------------------------------------------------------------------
# credential group
# ---------------------------------------------------------------------------


@main.group()
def credential() -> None:
    """Manage encrypted credentials."""


@credential.command("set")
@click.argument("name")
@click.option("--password", default=None, envvar="MASTER_PASSWORD", help="Master password")
@click.option("--description", default=None)
def credential_set(name: str, password: Optional[str], description: Optional[str]) -> None:
    """Store an encrypted credential. Value is prompted (hidden input)."""
    from agent.credentials.store import get_store
    from agent.db.engine import init_db
    from agent.db.session import get_session
    from agent.db.models import CredentialRecord
    from sqlalchemy import select
    from datetime import datetime

    pwd = password or click.prompt("Master password", hide_input=True)
    value = click.prompt(f"Value for '{name}'", hide_input=True, confirmation_prompt=True)

    settings.ensure_data_dir()
    init_db()

    store = get_store(pwd)
    store.set(name, value)

    with get_session() as session:
        stmt = select(CredentialRecord).where(CredentialRecord.name == name)
        rec = session.execute(stmt).scalar_one_or_none()
        if rec:
            rec.updated_at = datetime.utcnow()
            if description:
                rec.description = description
        else:
            rec = CredentialRecord(name=name, description=description)
            session.add(rec)

    console.print(f"[green]Credential '{name}' stored[/green]")


@credential.command("get")
@click.argument("name")
@click.option("--password", default=None, envvar="MASTER_PASSWORD")
def credential_get(name: str, password: Optional[str]) -> None:
    """Print a credential value (for scripting)."""
    from agent.credentials.store import get_store

    pwd = password or click.prompt("Master password", hide_input=True)
    settings.ensure_data_dir()
    store = get_store(pwd)
    value = store.get(name)
    if value is None:
        console.print(f"[red]Credential '{name}' not found[/red]")
        sys.exit(1)
    click.echo(value)


@credential.command("list")
@click.option("--password", default=None, envvar="MASTER_PASSWORD")
def credential_list(password: Optional[str]) -> None:
    """List stored credential names and metadata (never values)."""
    from agent.db.engine import init_db
    from agent.db.session import get_session
    from agent.db.models import CredentialRecord
    from sqlalchemy import select

    settings.ensure_data_dir()
    init_db()

    with get_session() as session:
        stmt = select(CredentialRecord).order_by(CredentialRecord.name)
        records = session.execute(stmt).scalars().all()

    if not records:
        console.print("[yellow]No credentials stored[/yellow]")
        return

    table = Table(title="Stored Credentials", show_header=True)
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Updated")
    for r in records:
        table.add_row(
            r.name,
            r.description or "",
            r.updated_at.strftime("%Y-%m-%d") if r.updated_at else "",
        )
    console.print(table)


@credential.command("delete")
@click.argument("name")
@click.option("--password", default=None, envvar="MASTER_PASSWORD")
def credential_delete(name: str, password: Optional[str]) -> None:
    """Delete a stored credential."""
    from agent.credentials.store import get_store
    from agent.db.engine import init_db
    from agent.db.session import get_session
    from agent.db.models import CredentialRecord
    from sqlalchemy import select

    pwd = password or click.prompt("Master password", hide_input=True)
    settings.ensure_data_dir()
    init_db()

    store = get_store(pwd)
    deleted = store.delete(name)

    with get_session() as session:
        stmt = select(CredentialRecord).where(CredentialRecord.name == name)
        rec = session.execute(stmt).scalar_one_or_none()
        if rec:
            session.delete(rec)

    if deleted:
        console.print(f"[green]Deleted credential '{name}'[/green]")
    else:
        console.print(f"[yellow]Credential '{name}' not found[/yellow]")


# ---------------------------------------------------------------------------
# llm group
# ---------------------------------------------------------------------------


@main.group()
def llm() -> None:
    """LLM chat interface."""


@llm.command("chat")
@click.option("--model", default=None, help="Model name override")
@click.option("--system-prompt", default="You are a helpful assistant.", show_default=True)
@click.option("--stream", "use_stream", is_flag=True, default=True)
def llm_chat(model: Optional[str], system_prompt: str, use_stream: bool) -> None:
    """Interactive streaming LLM chat (Ctrl+C to exit)."""
    from agent.llm.client import LLMClient
    from agent.llm.prompt import PromptBuilder

    if model:
        settings.openai_model = model

    client = LLMClient()
    history: list[dict] = []

    console.print(f"[bold cyan]LLM Chat[/bold cyan] — system: {system_prompt[:80]}")
    console.print("[dim]Ctrl+C or type 'exit' to quit[/dim]\n")

    while True:
        try:
            user_input = click.prompt("You", prompt_suffix="> ")
        except (click.Abort, EOFError):
            console.print("\n[yellow]Goodbye[/yellow]")
            break

        if user_input.strip().lower() in ("exit", "quit", "q"):
            console.print("[yellow]Goodbye[/yellow]")
            break

        history.append({"role": "user", "content": user_input})
        messages = PromptBuilder().system(system_prompt).build() + history

        try:
            if use_stream:
                console.print("[bold blue]Assistant:[/bold blue] ", end="")
                full_response = ""
                for chunk in client.stream(messages):
                    print(chunk, end="", flush=True)
                    full_response += chunk
                print()
                history.append({"role": "assistant", "content": full_response})
            else:
                response = client.chat(messages)
                console.print(f"[bold blue]Assistant:[/bold blue] {response}")
                history.append({"role": "assistant", "content": response})
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


# ---------------------------------------------------------------------------
# ui command
# ---------------------------------------------------------------------------


@main.command()
def ui() -> None:
    """Open the web dashboard in the default browser."""
    import webbrowser

    url = f"http://{settings.web_host}:{settings.web_port}"
    console.print(f"Opening {url}")
    webbrowser.open(url)
