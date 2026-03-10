"""LLMClient: Azure OpenAI primary, OpenAI-compatible fallback."""

from __future__ import annotations

from typing import Any, Generator, Iterator

from agent.config import settings
from agent.llm.provider import register_provider
from agent.utils.logging import get_logger
from agent.utils.retry import retry

logger = get_logger(__name__)


class LLMClient:
    """Unified LLM client supporting Azure OpenAI and OpenAI-compatible APIs.

    Provider selection (in order):
    1. Azure OpenAI (if AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT configured)
    2. OpenAI-compatible (OPENAI_API_KEY, optional OPENAI_BASE_URL for local models)
    """

    def __init__(self, provider: str | None = None) -> None:
        self._provider = provider or self._detect_provider()
        self._client = self._build_client()

    # ------------------------------------------------------------------
    # Provider detection
    # ------------------------------------------------------------------

    def _detect_provider(self) -> str:
        if settings.azure_openai_api_key and settings.azure_openai_endpoint:
            return "azure"
        if settings.openai_api_key:
            return "openai"
        if settings.openai_base_url:
            return "openai_compatible"
        raise RuntimeError(
            "No LLM provider configured. Set AZURE_OPENAI_API_KEY or OPENAI_API_KEY in .env"
        )

    def _build_client(self):
        if self._provider == "azure":
            from openai import AzureOpenAI

            return AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
            )
        else:
            from openai import OpenAI

            kwargs: dict[str, Any] = {"api_key": settings.openai_api_key or "sk-local"}
            if settings.openai_base_url:
                kwargs["base_url"] = settings.openai_base_url
            return OpenAI(**kwargs)

    def _model(self) -> str:
        if self._provider == "azure":
            return settings.azure_openai_deployment or "gpt-4o"
        return settings.openai_model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @retry(max_attempts=3, delay=2.0, backoff=2.0)
    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        """Single-turn completion. Returns assistant message content."""
        response = self._client.chat.completions.create(
            model=self._model(),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    def stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Streaming completion — yields text chunks."""
        stream = self._client.chat.completions.create(
            model=self._model(),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def structured(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """JSON-mode structured output. Returns parsed dict."""
        import json

        fmt = response_format or {"type": "json_object"}
        content = self.chat(messages, response_format=fmt, **kwargs)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw": content}


# Register built-in providers for the registry
@register_provider("azure")
def _azure_factory(**kwargs):
    return LLMClient(provider="azure")


@register_provider("openai")
def _openai_factory(**kwargs):
    return LLMClient(provider="openai")


@register_provider("openai_compatible")
def _compat_factory(**kwargs):
    return LLMClient(provider="openai_compatible")
