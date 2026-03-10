"""Tests for the Rust extension (skipped if not built)."""

from __future__ import annotations

import pytest

agent_core_ext = pytest.importorskip(
    "agent_core_ext",
    reason="Rust extension not built. Run: maturin develop --manifest-path rust_ext/Cargo.toml",
)


class TestHashTaskId:
    def test_returns_hex_string(self):
        result = agent_core_ext.hash_task_id('{"type":"reminder"}')
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 = 32 bytes = 64 hex chars

    def test_deterministic(self):
        s = '{"key":"value"}'
        assert agent_core_ext.hash_task_id(s) == agent_core_ext.hash_task_id(s)

    def test_different_inputs(self):
        h1 = agent_core_ext.hash_task_id("abc")
        h2 = agent_core_ext.hash_task_id("xyz")
        assert h1 != h2


class TestCronNextFire:
    def test_returns_list(self):
        import time

        fires = agent_core_ext.cron_next_fire("*/5 * * * *", time.time(), 3)
        assert len(fires) == 3
        assert all(isinstance(f, float) for f in fires)

    def test_ascending_order(self):
        import time

        fires = agent_core_ext.cron_next_fire("0 * * * *", time.time(), 3)
        assert fires[0] < fires[1] < fires[2]

    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError):
            agent_core_ext.cron_next_fire("invalid", 0.0, 3)


class TestVersion:
    def test_version_exists(self):
        assert hasattr(agent_core_ext, "__version__")
        assert agent_core_ext.__version__ == "0.1.0"
