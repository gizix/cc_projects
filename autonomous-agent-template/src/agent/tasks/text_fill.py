"""Type/paste text using pyautogui."""

from __future__ import annotations

import time

from agent.scheduler.registry import register_task
from agent.tasks.base import BaseTask, TaskResult
from agent.utils.logging import get_logger

logger = get_logger(__name__)


@register_task("text_fill")
class TextFillTask(BaseTask):
    """Simulate keyboard input to type text into the focused window.

    Config keys:
      - text (str): Text to type
      - delay_before (float, default 2.0): Seconds to wait before typing
      - interval (float, default 0.05): Seconds between keystrokes
      - use_clipboard (bool, default False): Paste via clipboard instead of typewrite
    """

    def run(self) -> TaskResult:
        text = self.config.get("text", "")
        delay_before = float(self.config.get("delay_before", 2.0))
        interval = float(self.config.get("interval", 0.05))
        use_clipboard = bool(self.config.get("use_clipboard", False))

        if not text:
            return TaskResult(status="skipped", message="No text configured")

        if not self.can_automate():
            return TaskResult(status="skipped", message="Headless environment")

        try:
            import pyautogui

            time.sleep(delay_before)
            if use_clipboard:
                import subprocess
                import sys

                if sys.platform == "win32":
                    subprocess.run("clip", input=text.encode("utf-16"), check=True)
                    pyautogui.hotkey("ctrl", "v")
                else:
                    pyautogui.hotkey("ctrl", "v")
            else:
                pyautogui.typewrite(text, interval=interval)

            return TaskResult(
                status="success",
                data={"chars": len(text)},
                message=f"Typed {len(text)} characters",
            )
        except Exception as exc:
            logger.error("TextFillTask failed: %s", exc)
            return TaskResult(status="error", message=str(exc))
