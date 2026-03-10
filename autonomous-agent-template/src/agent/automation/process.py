"""Cross-platform program open/close using subprocess + psutil."""

from __future__ import annotations

import subprocess
import sys
from typing import Optional

import psutil


def open_program(executable: str, *args: str, wait: bool = False) -> int:
    """Launch a program. Returns PID (or returncode if wait=True)."""
    cmd = [executable, *args]
    if wait:
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode
    proc = subprocess.Popen(cmd)
    return proc.pid


def close_program(name_or_path: str, signal: str = "terminate") -> int:
    """Terminate all processes matching name_or_path. Returns count killed."""
    killed = 0
    needle = name_or_path.lower()
    for proc in psutil.process_iter(["name", "exe", "cmdline"]):
        try:
            proc_name = (proc.info.get("name") or "").lower()
            proc_exe = (proc.info.get("exe") or "").lower()
            if needle in proc_name or needle in proc_exe:
                getattr(proc, signal)()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return killed


def find_process(name: str) -> Optional[psutil.Process]:
    """Return first running process matching name, or None."""
    needle = name.lower()
    for proc in psutil.process_iter(["name", "exe"]):
        try:
            if needle in (proc.info.get("name") or "").lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None
