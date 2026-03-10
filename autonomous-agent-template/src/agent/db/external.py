"""Factory for connecting to external databases via any SQLAlchemy URL."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from agent.config import settings


def get_external_engine():
    """Return SQLAlchemy engine for the configured external DB URL."""
    url = settings.external_db_url
    if not url:
        raise RuntimeError(
            "EXTERNAL_DB_URL is not configured. Set it in .env or as an environment variable."
        )
    return create_engine(url, pool_pre_ping=True)


@contextmanager
def get_external_session() -> Generator[Session, None, None]:
    """Yield a session connected to the external database."""
    engine = get_external_engine()
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def test_external_connection() -> bool:
    """Return True if the external DB is reachable."""
    try:
        engine = get_external_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
