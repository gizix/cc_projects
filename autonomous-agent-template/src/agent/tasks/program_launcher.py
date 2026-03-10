"""Open or close programs using psutil + subprocess."""

from __future__ import annotations

import subprocess
import sys

import psutil

from agent.scheduler.registry import register_task
from agent.tasks.base import BaseTask, TaskResult
from agent.utils.logging import get_logger

logger = get_logger(__name__)


@register_task("program_launcher")
class ProgramLauncherTask(BaseTask):
    """Launch or terminate a program.

    Config keys:
      - action (str): "open" or "close"
      - program (str): Executable name or full path
      - args (list[str], optional): CLI arguments for "open"
      - wait (bool, default False): Wait for process exit on "open"
      - signal (str, default "terminate"): "terminate" or "kill" for "close"
    """

    def run(self) -> TaskResult:
        action = self.config.get("action", "open").lower()
        program = self.config.get("program", "")

        if not program:
            return TaskResult(status="error", message="No program specified")

        if not self.can_automate():
            return TaskResult(status="skipped", message="Headless environment")

        if action == "open":
            return self._open(program)
        elif action == "close":
            return self._close(program)
        else:
            return TaskResult(status="error", message=f"Unknown action: {action}")

    def _open(self, program: str) -> TaskResult:
        args = self.config.get("args", [])
        wait = bool(self.config.get("wait", False))
        cmd = [program] + list(args)
        try:
            if wait:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return TaskResult(
                    status="success" if result.returncode == 0 else "error",
                    data={"returncode": result.returncode},
                )
            else:
                proc = subprocess.Popen(cmd)
                return TaskResult(status="success", data={"pid": proc.pid})
        except FileNotFoundError:
            return TaskResult(status="error", message=f"Program not found: {program}")
        except Exception as exc:
            return TaskResult(status="error", message=str(exc))

    def _close(self, program: str) -> TaskResult:
        sig = self.config.get("signal", "terminate")
        killed = 0
        for proc in psutil.process_iter(["name", "exe"]):
            name = (proc.info.get("name") or "").lower()
            exe = (proc.info.get("exe") or "").lower()
            if program.lower() in name or program.lower() in exe:
                try:
                    getattr(proc, sig)()
                    killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return TaskResult(
            status="success" if killed > 0 else "skipped",
            data={"killed": killed},
            message=f"Terminated {killed} process(es)",
        )
