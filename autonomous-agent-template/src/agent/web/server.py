"""Start uvicorn in a daemon thread alongside the scheduler."""

from __future__ import annotations

import threading
from typing import Optional

from agent.config import settings
from agent.utils.logging import get_logger

logger = get_logger(__name__)

_server_thread: Optional[threading.Thread] = None


def start_web_server() -> None:
    """Start the FastAPI web dashboard in a daemon thread."""
    global _server_thread

    import uvicorn
    from agent.web.app import app

    config = uvicorn.Config(
        app,
        host=settings.web_host,
        port=settings.web_port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)

    def _run():
        logger.info("Web dashboard at http://%s:%d", settings.web_host, settings.web_port)
        server.run()

    _server_thread = threading.Thread(target=_run, daemon=True, name="web-dashboard")
    _server_thread.start()

    if settings.web_open_browser:
        _open_browser()


def _open_browser() -> None:
    import time
    import webbrowser

    time.sleep(1.5)
    url = f"http://{settings.web_host}:{settings.web_port}"
    webbrowser.open(url)
