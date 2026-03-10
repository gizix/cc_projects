"""Shared pytest fixtures."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

# Use a temp directory for all data during tests
os.environ.setdefault("MASTER_PASSWORD", "test-master-password-123")
os.environ.setdefault("AGENT_HEADLESS", "1")  # Disable OS automation in tests


@pytest.fixture(scope="session")
def tmp_data(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("agent_data")


@pytest.fixture(autouse=True)
def patch_settings(tmp_data, monkeypatch):
    """Redirect all data paths to a temp directory for each test."""
    from agent import config as cfg

    monkeypatch.setattr(cfg.settings, "data_dir", tmp_data)
    monkeypatch.setattr(cfg.settings, "pid_file", tmp_data / "agent.pid")
    monkeypatch.setattr(cfg.settings, "credential_file", tmp_data / ".credentials.enc")
    monkeypatch.setattr(cfg.settings, "master_password", "test-master-password-123")
    yield


@pytest.fixture()
def credential_store(tmp_data):
    from agent.credentials.store import CredentialStore

    return CredentialStore(tmp_data / ".credentials.enc", "test-master-password-123")


@pytest.fixture()
def db_session(tmp_data):
    from agent.db.engine import init_db
    from agent.db.session import get_session

    init_db()
    with get_session() as session:
        yield session
