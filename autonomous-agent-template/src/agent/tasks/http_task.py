"""HTTP request task with tenacity retry logic."""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from agent.scheduler.registry import register_task
from agent.tasks.base import BaseTask, TaskResult
from agent.utils.logging import get_logger

logger = get_logger(__name__)


@register_task("http_request")
class HttpTask(BaseTask):
    """Perform an HTTP request and (optionally) assert on the response.

    Config keys:
      - url (str): Target URL
      - method (str, default "GET"): HTTP method
      - headers (dict, optional): Request headers
      - body (dict | str, optional): Request body (JSON dict → application/json)
      - timeout (float, default 30.0): Request timeout seconds
      - expected_status (int, optional): Assert this status code
      - credential_name (str, optional): Inject a credential as Bearer token
    """

    def run(self) -> TaskResult:
        url = self.config.get("url", "")
        if not url:
            return TaskResult(status="error", message="No URL specified")

        method = self.config.get("method", "GET").upper()
        headers: dict[str, str] = self.config.get("headers", {})
        body = self.config.get("body")
        timeout = float(self.config.get("timeout", 30.0))
        expected_status = self.config.get("expected_status")
        cred_name = self.config.get("credential_name")

        if cred_name:
            try:
                from agent.credentials.store import get_store

                store = get_store()
                token = store.get(cred_name)
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            except Exception:
                pass

        try:
            response = self._do_request(method, url, headers, body, timeout)
            status_ok = expected_status is None or response.status_code == expected_status
            return TaskResult(
                status="success" if status_ok else "error",
                data={
                    "status_code": response.status_code,
                    "url": url,
                    "response_bytes": len(response.content),
                },
                message=f"HTTP {method} {url} → {response.status_code}",
            )
        except Exception as exc:
            logger.error("HttpTask failed for %s: %s", url, exc)
            return TaskResult(status="error", message=str(exc))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _do_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: Any,
        timeout: float,
    ) -> httpx.Response:
        with httpx.Client(timeout=timeout) as client:
            if isinstance(body, dict):
                return client.request(method, url, headers=headers, json=body)
            elif body:
                return client.request(method, url, headers=headers, content=str(body).encode())
            else:
                return client.request(method, url, headers=headers)
