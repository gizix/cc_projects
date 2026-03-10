"""BaseTask ABC and TaskResult dataclass."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskResult:
    status: str  # "success" | "error" | "skipped"
    data: dict[str, Any] = field(default_factory=dict)
    message: str = ""


class BaseTask(ABC):
    """All task types inherit from this class.

    Subclasses must:
    1. Decorate with ``@register_task("<type-name>")``
    2. Implement :meth:`run` → :class:`TaskResult`
    3. Define ``CONFIG_SCHEMA`` as a Pydantic model (optional but recommended)
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @abstractmethod
    def run(self) -> TaskResult:
        """Execute the task and return a :class:`TaskResult`."""

    def can_automate(self) -> bool:
        """Return False if automation is impossible in the current environment."""
        import os

        # Docker/headless guard
        if os.environ.get("AGENT_HEADLESS", "").lower() in ("1", "true", "yes"):
            return False
        if os.name == "posix" and not os.environ.get("DISPLAY"):
            return False
        return True
