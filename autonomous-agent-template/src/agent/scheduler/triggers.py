"""Trigger builders for APScheduler + optional cron-preview via Rust ext."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Optional Rust extension for schedule preview
try:
    from agent_core_ext import cron_next_fire as _rust_cron_next_fire  # type: ignore[import]

    _HAS_RUST = True
except ImportError:
    _HAS_RUST = False


def parse_trigger(trigger_str: str, **kwargs: Any):
    """Parse a trigger string into an APScheduler trigger object.

    Formats:
      - ``cron:<expr>``  e.g. ``cron:*/5 * * * *``
      - ``interval:<seconds>``  e.g. ``interval:300``
      - ``once:<ISO datetime>``  e.g. ``once:2025-01-01T09:00:00``
    """
    if trigger_str.startswith("cron:"):
        expr = trigger_str[5:]
        parts = expr.split()
        if len(parts) != 5:
            raise ValueError(f"Cron expression must have 5 fields; got: {expr!r}")
        min_, hour, dom, month, dow = parts
        return CronTrigger(
            minute=min_,
            hour=hour,
            day=dom,
            month=month,
            day_of_week=dow,
            timezone="UTC",
            **kwargs,
        )

    if trigger_str.startswith("interval:"):
        seconds = int(trigger_str[9:])
        return IntervalTrigger(seconds=seconds, **kwargs)

    if trigger_str.startswith("once:"):
        run_date = datetime.fromisoformat(trigger_str[5:])
        return DateTrigger(run_date=run_date, **kwargs)

    raise ValueError(
        f"Unknown trigger format: {trigger_str!r}. "
        "Use cron:<expr>, interval:<seconds>, or once:<ISO datetime>."
    )


def preview_cron(expression: str, count: int = 5) -> list[str]:
    """Return the next ``count`` fire times for a cron expression as ISO strings.

    Uses the Rust extension when available; falls back to APScheduler iteration.
    """
    if _HAS_RUST:
        timestamps = _rust_cron_next_fire(expression, time.time(), count)
        return [
            datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
            for ts in timestamps
        ]

    # Pure-Python fallback via APScheduler
    trigger = parse_trigger(f"cron:{expression}")
    now = datetime.utcnow()
    results: list[str] = []
    current = now
    for _ in range(count):
        nxt = trigger.get_next_fire_time(current, current)
        if nxt is None:
            break
        results.append(nxt.strftime("%Y-%m-%d %H:%M:%S UTC"))
        current = nxt
    return results
