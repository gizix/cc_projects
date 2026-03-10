"""ThreadPoolExecutor wrapper with run-ID tracking."""

from __future__ import annotations

import threading
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Any

from agent.utils.logging import get_logger

logger = get_logger(__name__)

_executor: ThreadPoolExecutor | None = None
_lock = threading.Lock()

# Map run_id → Future
_active: dict[str, Future] = {}


def get_executor(max_workers: int = 4) -> ThreadPoolExecutor:
    global _executor
    with _lock:
        if _executor is None or _executor._shutdown:
            _executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="agent-worker")
    return _executor


def submit(fn: Callable, *args: Any, **kwargs: Any) -> tuple[str, Future]:
    """Submit a callable and return (run_id, future)."""
    run_id = str(uuid.uuid4())[:8]

    def _wrapper():
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            logger.exception("Worker %s raised: %s", run_id, exc)
            raise
        finally:
            _active.pop(run_id, None)

    from agent.config import settings

    future = get_executor(settings.worker_threads).submit(_wrapper)
    _active[run_id] = future
    return run_id, future


def active_count() -> int:
    return len(_active)


def shutdown(wait: bool = True) -> None:
    global _executor
    if _executor:
        _executor.shutdown(wait=wait)
        _executor = None
