"""Inject credentials as environment variables for subprocess tasks."""

from __future__ import annotations

import os
from typing import Any

from agent.credentials.store import CredentialStore


def inject_credentials(
    store: CredentialStore,
    names: list[str],
    env: dict[str, str] | None = None,
) -> dict[str, str]:
    """Return an env dict with the requested credential names injected.

    Missing credentials are silently skipped (logged at WARNING level).
    """
    from agent.utils.logging import get_logger

    logger = get_logger(__name__)
    base = dict(os.environ) if env is None else dict(env)

    for name in names:
        value = store.get(name)
        if value is None:
            logger.warning("Credential '%s' not found in store — skipping injection", name)
            continue
        base[name] = value

    return base
