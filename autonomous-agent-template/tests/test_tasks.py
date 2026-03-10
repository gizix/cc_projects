"""Tests for built-in task types."""

from __future__ import annotations

import pytest

import agent.tasks.http_task  # noqa — register tasks
import agent.tasks.llm_task  # noqa
import agent.tasks.program_launcher  # noqa
import agent.tasks.reminder  # noqa
import agent.tasks.text_fill  # noqa


class TestReminderTask:
    def test_skipped_in_headless(self):
        from agent.tasks.reminder import ReminderTask

        task = ReminderTask({"title": "Test", "message": "Hello"})
        result = task.run()
        # AGENT_HEADLESS=1 set in conftest
        assert result.status == "skipped"


class TestTextFillTask:
    def test_skipped_in_headless(self):
        from agent.tasks.text_fill import TextFillTask

        task = TextFillTask({"text": "hello world"})
        result = task.run()
        assert result.status == "skipped"

    def test_no_text_skipped(self):
        from agent.tasks.text_fill import TextFillTask

        task = TextFillTask({})
        result = task.run()
        assert result.status == "skipped"


class TestProgramLauncherTask:
    def test_skipped_in_headless(self):
        from agent.tasks.program_launcher import ProgramLauncherTask

        task = ProgramLauncherTask({"action": "open", "program": "notepad"})
        result = task.run()
        assert result.status == "skipped"


class TestHttpTask:
    def test_missing_url(self):
        from agent.tasks.http_task import HttpTask

        task = HttpTask({})
        result = task.run()
        assert result.status == "error"

    def test_successful_request(self, httpserver):
        """Requires pytest-localserver or similar — skip if unavailable."""
        pytest.importorskip("pytest_localserver")
        from agent.tasks.http_task import HttpTask

        httpserver.expect_request("/ping").respond_with_data("OK")
        task = HttpTask({"url": httpserver.url_for("/ping"), "expected_status": 200})
        result = task.run()
        assert result.status == "success"
