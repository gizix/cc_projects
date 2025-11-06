"""
Database connection and session management.

This module provides async SQLAlchemy 2.0 setup with proper session lifecycle management.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class DatabaseSessionManager:
    """
    Manages database engine and session lifecycle.

    This class ensures proper connection pooling and session management
    following SQLAlchemy 2.0 async patterns.
    """

    def __init__(self, database_url: str) -> None:
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
            pool_pre_ping=True,  # Test connections before using
            pool_size=5,
            max_overflow=10,
        )

        self._async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Dependency for getting async database sessions.

        Yields:
            AsyncSession: Database session with automatic rollback on errors
        """
        async with self._async_session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global session manager instance
sessionmanager = DatabaseSessionManager(str(settings.DATABASE_URL))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Usage:
        @app.get("/users")
        async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
            ...
    """
    async for session in sessionmanager.get_session():
        yield session
