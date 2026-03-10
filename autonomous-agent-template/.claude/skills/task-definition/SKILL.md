---
name: task-definition
description: Provides BaseTask template, TaskResult pattern, @register_task decorator usage, and pytest fixture when creating new task types. Activates when user creates a new task type or asks how to implement scheduled automation.
allowed-tools: Read, Write, Edit
---

You provide complete templates for creating new task types in the Autonomous Agent platform.

## When to Activate

- User asks "how do I create a new task type"
- User says "add a task that does X"
- User is creating a file in `src/agent/tasks/`

## Full Task Template

```python
# src/agent/tasks/my_new_task.py
"""Short description of what this task does."""

from __future__ import annotations

from agent.scheduler.registry import register_task
from agent.tasks.base import BaseTask, TaskResult
from agent.utils.logging import get_logger

logger = get_logger(__name__)


@register_task("my_new_task")       # ← must be unique snake_case
class MyNewTask(BaseTask):
    """One-line description.

    Config keys:
      - required_param (str): What it does
      - optional_param (int, default 30): Description of default
      - enabled_in_docker (bool, default False): Skip in headless env
    """

    def run(self) -> TaskResult:
        # 1. Extract config with safe defaults
        required = self.config.get("required_param")
        optional = int(self.config.get("optional_param", 30))

        # 2. Validate required fields
        if not required:
            return TaskResult(status="error", message="required_param not configured")

        # 3. Guard OS automation (omit if task doesn't touch display/input)
        if not self.can_automate():
            return TaskResult(status="skipped", message="Headless environment")

        # 4. Execute with error handling
        try:
            result = self._do_work(required, optional)
            return TaskResult(
                status="success",
                data={"key": result},
                message=f"Task completed: {result}",
            )
        except Exception as exc:
            logger.error("MyNewTask failed: %s", exc)
            return TaskResult(status="error", message=str(exc))

    def _do_work(self, param: str, timeout: int) -> str:
        # Implementation here
        return f"processed {param}"
```

## TaskResult Reference

```python
@dataclass
class TaskResult:
    status: str          # "success" | "error" | "skipped"
    data: dict = {}      # Arbitrary result data (stored as JSON)
    message: str = ""    # Human-readable summary (truncated in logs)
```

## Registration — REQUIRED

After creating the task file, add the import to `src/agent/cli.py`:

```python
# In the run() command and task run() command:
import agent.tasks.my_new_task  # noqa — registers MyNewTask
```

## Example Config JSON for CLI

```bash
uv run agent schedule add my_new_task "cron:*/5 * * * *" \
  '{"required_param": "value", "optional_param": 60}'
```

## Pytest Fixture

```python
# tests/test_tasks.py
import os
import pytest

class TestMyNewTask:
    def test_success(self):
        from agent.tasks.my_new_task import MyNewTask
        task = MyNewTask({"required_param": "test-value"})
        result = task.run()
        # In headless (AGENT_HEADLESS=1 set in conftest), check skipped
        assert result.status in ("success", "skipped")

    def test_missing_required_param(self):
        from agent.tasks.my_new_task import MyNewTask
        task = MyNewTask({})
        result = task.run()
        assert result.status == "error"
        assert "required_param" in result.message
```

Replace `my_new_task` / `MyNewTask` with your actual names throughout.
