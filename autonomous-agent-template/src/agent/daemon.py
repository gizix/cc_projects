"""Cross-platform daemon lifecycle: start, stop, status via PID file."""

from __future__ import annotations

import os
import signal
import sys
from pathlib import Path

import psutil
from rich.console import Console

console = Console()


def _read_pid(pid_file: Path) -> int | None:
    try:
        return int(pid_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def _write_pid(pid_file: Path) -> None:
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()))


def _remove_pid(pid_file: Path) -> None:
    try:
        pid_file.unlink()
    except FileNotFoundError:
        pass


def is_running(pid_file: Path) -> bool:
    pid = _read_pid(pid_file)
    if pid is None:
        return False
    return psutil.pid_exists(pid)


def get_pid(pid_file: Path) -> int | None:
    return _read_pid(pid_file)


def start(pid_file: Path) -> None:
    """Write PID file for the current process."""
    if is_running(pid_file):
        pid = _read_pid(pid_file)
        console.print(f"[yellow]Agent already running (PID {pid})[/yellow]")
        sys.exit(1)
    _write_pid(pid_file)


def stop(pid_file: Path, force: bool = False) -> bool:
    """Signal the daemon to stop. Returns True if a signal was sent."""
    pid = _read_pid(pid_file)
    if pid is None or not psutil.pid_exists(pid):
        _remove_pid(pid_file)
        return False

    sig = signal.SIGKILL if (force or sys.platform == "win32") else signal.SIGTERM
    try:
        os.kill(pid, sig)
        console.print(f"[green]Sent {'SIGKILL' if force else 'SIGTERM'} to PID {pid}[/green]")
        return True
    except PermissionError:
        console.print(f"[red]Permission denied — cannot signal PID {pid}[/red]")
        return False
    except ProcessLookupError:
        _remove_pid(pid_file)
        return False


def cleanup(pid_file: Path) -> None:
    """Remove PID file on clean shutdown."""
    _remove_pid(pid_file)
