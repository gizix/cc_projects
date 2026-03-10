"""Tests for LLM client and PromptBuilder."""

from __future__ import annotations

import pytest

from agent.llm.prompt import PromptBuilder


class TestPromptBuilder:
    def test_system_user(self):
        messages = PromptBuilder().system("Be helpful.").user("Hello!").build()
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_multi_turn(self):
        messages = (
            PromptBuilder()
            .system("System prompt")
            .user("Q1")
            .assistant("A1")
            .user("Q2")
            .build()
        )
        assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]

    def test_render_sanitizes(self):
        pb = PromptBuilder()
        # Curly braces in values should not break format()
        rendered = pb.render("Hello {name}", name="Alice {hacker}")
        assert "Alice" in rendered

    def test_build_returns_copy(self):
        pb = PromptBuilder().system("s")
        m1 = pb.build()
        pb.user("u")
        m2 = pb.build()
        assert len(m1) == 1
        assert len(m2) == 2


class TestLLMClientDetection:
    def test_no_provider_raises(self, monkeypatch):
        from agent import config

        monkeypatch.setattr(config.settings, "azure_openai_api_key", None)
        monkeypatch.setattr(config.settings, "azure_openai_endpoint", None)
        monkeypatch.setattr(config.settings, "openai_api_key", None)
        monkeypatch.setattr(config.settings, "openai_base_url", None)

        from agent.llm.client import LLMClient

        with pytest.raises(RuntimeError, match="No LLM provider"):
            LLMClient()

    def test_azure_detection(self, monkeypatch):
        from agent import config

        monkeypatch.setattr(config.settings, "azure_openai_api_key", "fake-key")
        monkeypatch.setattr(config.settings, "azure_openai_endpoint", "https://fake.openai.azure.com")
        monkeypatch.setattr(config.settings, "azure_openai_deployment", "gpt-4o")

        from agent.llm.client import LLMClient

        client = LLMClient()
        assert client._provider == "azure"
