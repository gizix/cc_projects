"""Internal SQLite engine (agent_ops.db)."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from agent.config import settings


class Base(DeclarativeBase):
    pass


def get_engine():
    settings.ensure_data_dir()
    return create_engine(
        settings.internal_db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )


def init_db() -> None:
    from agent.db import models  # noqa: F401 — ensure models are registered

    engine = get_engine()
    Base.metadata.create_all(engine)
