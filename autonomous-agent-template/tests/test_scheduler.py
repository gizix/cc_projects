"""Tests for scheduler triggers and registry."""

from __future__ import annotations

import pytest

from agent.scheduler.registry import get_task_class, list_task_types, register_task
from agent.scheduler.triggers import parse_trigger, preview_cron
from agent.tasks.base import BaseTask, TaskResult


class TestTriggerParsing:
    def test_cron_trigger(self):
        t = parse_trigger("cron:*/5 * * * *")
        assert t is not None

    def test_interval_trigger(self):
        t = parse_trigger("interval:300")
        assert t is not None

    def test_once_trigger(self):
        t = parse_trigger("once:2030-01-01T09:00:00")
        assert t is not None

    def test_invalid_trigger_raises(self):
        with pytest.raises(ValueError):
            parse_trigger("unknown:something")

    def test_cron_wrong_fields_raises(self):
        with pytest.raises(ValueError):
            parse_trigger("cron:* * *")

    def test_preview_cron_returns_list(self):
        fires = preview_cron("*/10 * * * *", count=3)
        assert len(fires) == 3
        assert all(isinstance(f, str) for f in fires)


class TestRegistry:
    def test_register_and_retrieve(self):
        @register_task("_test_task_xyz")
        class _TestTask(BaseTask):
            def run(self) -> TaskResult:
                return TaskResult(status="success")

        cls = get_task_class("_test_task_xyz")
        assert cls is _TestTask

    def test_unknown_type_raises(self):
        with pytest.raises(KeyError):
            get_task_class("definitely_not_registered_xyz")

    def test_list_includes_registered(self):
        @register_task("_list_test_xyz")
        class _T(BaseTask):
            def run(self) -> TaskResult:
                return TaskResult(status="success")

        assert "_list_test_xyz" in list_task_types()
