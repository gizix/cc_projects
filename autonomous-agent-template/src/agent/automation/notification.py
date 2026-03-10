"""Cross-platform desktop notifications via plyer."""

from __future__ import annotations


def notify(title: str, message: str, timeout: int = 10, app_name: str = "Agent") -> None:
    """Send a cross-platform desktop notification.

    Silently no-ops in headless environments (Docker, CI).
    """
    import os
    import sys

    # Headless guard
    if os.environ.get("AGENT_HEADLESS", "").lower() in ("1", "true"):
        return
    if sys.platform == "linux" and not os.environ.get("DISPLAY"):
        return

    try:
        from plyer import notification as plyer_notify

        plyer_notify.notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=timeout,
        )
    except Exception:
        pass  # Never crash the agent due to notification failures
