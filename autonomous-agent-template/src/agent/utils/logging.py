"""Rich-enhanced logging setup for the agent."""

from __future__ import annotations

import logging
from functools import lru_cache

from rich.logging import RichHandler

_configured = False


def configure_logging(level: str = "INFO") -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )
    _configured = True


@lru_cache(maxsize=None)
def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
