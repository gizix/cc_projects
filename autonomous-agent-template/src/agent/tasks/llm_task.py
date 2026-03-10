"""Scheduled LLM inference task."""

from __future__ import annotations

from agent.llm.client import LLMClient
from agent.llm.prompt import PromptBuilder
from agent.scheduler.registry import register_task
from agent.tasks.base import BaseTask, TaskResult
from agent.utils.logging import get_logger

logger = get_logger(__name__)


@register_task("llm_inference")
class LLMTask(BaseTask):
    """Run an LLM inference and store the result.

    Config keys:
      - system_prompt (str, optional): System message
      - user_prompt (str): User message (required)
      - temperature (float, default 0.7)
      - max_tokens (int, default 1024)
      - output_credential (str, optional): Store response in this credential name
    """

    def run(self) -> TaskResult:
        user_prompt = self.config.get("user_prompt", "")
        if not user_prompt:
            return TaskResult(status="error", message="No user_prompt configured")

        system_prompt = self.config.get("system_prompt", "You are a helpful assistant.")
        temperature = float(self.config.get("temperature", 0.7))
        max_tokens = int(self.config.get("max_tokens", 1024))
        output_cred = self.config.get("output_credential")

        try:
            client = LLMClient()
            messages = (
                PromptBuilder()
                .system(system_prompt)
                .user(user_prompt)
                .build()
            )
            response = client.chat(messages, temperature=temperature, max_tokens=max_tokens)

            if output_cred:
                try:
                    from agent.credentials.store import get_store

                    store = get_store()
                    store.set(output_cred, response)
                except Exception as e:
                    logger.warning("Could not store LLM response in credential '%s': %s", output_cred, e)

            return TaskResult(
                status="success",
                data={"response_length": len(response)},
                message=response[:200],
            )
        except Exception as exc:
            logger.error("LLMTask failed: %s", exc)
            return TaskResult(status="error", message=str(exc))
