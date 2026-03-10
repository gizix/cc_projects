"""LLM provider registry."""

from __future__ import annotations

from typing import Callable, Any

_PROVIDERS: dict[str, Callable[..., Any]] = {}


def register_provider(name: str):
    """Register an LLM client factory under a provider name."""

    def decorator(fn: Callable) -> Callable:
        _PROVIDERS[name] = fn
        return fn

    return decorator


def get_provider_factory(name: str) -> Callable:
    if name not in _PROVIDERS:
        raise KeyError(
            f"Unknown LLM provider '{name}'. Available: {sorted(_PROVIDERS.keys())}"
        )
    return _PROVIDERS[name]


def list_providers() -> list[str]:
    return sorted(_PROVIDERS.keys())
