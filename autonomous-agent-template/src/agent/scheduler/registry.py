"""Task type registry: @register_task decorator + lookup."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from agent.tasks.base import BaseTask

_REGISTRY: dict[str, Type["BaseTask"]] = {}


def register_task(task_type: str):
    """Class decorator to register a BaseTask subclass under a string key."""

    def decorator(cls: Type["BaseTask"]) -> Type["BaseTask"]:
        _REGISTRY[task_type] = cls
        return cls

    return decorator


def get_task_class(task_type: str) -> Type["BaseTask"]:
    if task_type not in _REGISTRY:
        raise KeyError(
            f"Unknown task type '{task_type}'. "
            f"Available: {sorted(_REGISTRY.keys())}"
        )
    return _REGISTRY[task_type]


def list_task_types() -> list[str]:
    return sorted(_REGISTRY.keys())
