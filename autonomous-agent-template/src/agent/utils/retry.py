"""Exponential backoff retry decorator (synchronous)."""

from __future__ import annotations

import functools
import time
from typing import Callable, Any, Type

from agent.utils.logging import get_logger

logger = get_logger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
):
    """Decorator: retry ``max_attempts`` times with exponential backoff."""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_attempts:
                        raise
                    logger.warning(
                        "Attempt %d/%d failed (%s): %s — retrying in %.1fs",
                        attempt,
                        max_attempts,
                        fn.__name__,
                        exc,
                        wait,
                    )
                    time.sleep(wait)
                    wait *= backoff

        return wrapper

    return decorator
