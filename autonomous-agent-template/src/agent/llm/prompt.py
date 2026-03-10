"""PromptBuilder: fluent builder for system/user/assistant message chains."""

from __future__ import annotations

from typing import Any


class PromptBuilder:
    """Build an OpenAI-compatible messages list.

    Usage::

        messages = (
            PromptBuilder()
            .system("You are a helpful assistant.")
            .user("What is 2+2?")
            .build()
        )
    """

    def __init__(self) -> None:
        self._messages: list[dict[str, str]] = []

    def system(self, content: str) -> "PromptBuilder":
        self._messages.append({"role": "system", "content": content})
        return self

    def user(self, content: str) -> "PromptBuilder":
        self._messages.append({"role": "user", "content": content})
        return self

    def assistant(self, content: str) -> "PromptBuilder":
        self._messages.append({"role": "assistant", "content": content})
        return self

    def render(self, template: str, **variables: Any) -> str:
        """Render a template string with variables (sanitized)."""
        safe_vars = {k: str(v).replace("{", "{{").replace("}", "}}") for k, v in variables.items()}
        return template.format(**safe_vars)

    def build(self) -> list[dict[str, str]]:
        return list(self._messages)
