"""Session context manager for the internal database."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from agent.db.engine import get_engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Yield a transactional session; commit on exit, rollback on error."""
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
