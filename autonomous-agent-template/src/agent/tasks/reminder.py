"""Desktop notification task via plyer."""

from __future__ import annotations

from agent.scheduler.registry import register_task
from agent.tasks.base import BaseTask, TaskResult
from agent.utils.logging import get_logger

logger = get_logger(__name__)


@register_task("reminder")
class ReminderTask(BaseTask):
    """Send a desktop notification.

    Config keys:
      - title (str): Notification title
      - message (str): Notification body
      - timeout (int, default 10): Seconds before auto-dismiss
      - enabled_in_docker (bool, default False): Skip in headless/Docker
    """

    def run(self) -> TaskResult:
        title = self.config.get("title", "Agent Reminder")
        message = self.config.get("message", "")
        timeout = int(self.config.get("timeout", 10))

        if not self.can_automate():
            logger.warning("ReminderTask skipped — headless environment detected")
            return TaskResult(status="skipped", message="Headless environment")

        try:
            from plyer import notification

            notification.notify(
                title=title,
                message=message,
                timeout=timeout,
            )
            return TaskResult(status="success", data={"title": title}, message="Notification sent")
        except Exception as exc:
            logger.error("ReminderTask failed: %s", exc)
            return TaskResult(status="error", message=str(exc))
