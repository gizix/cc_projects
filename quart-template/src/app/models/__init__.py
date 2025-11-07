"""Database models and initialization.

This module sets up async SQLAlchemy and defines database models.
"""

from datetime import datetime
from typing import Optional

from quart import Quart
from sqlalchemy import String, DateTime, func
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Base class for all models
class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding password)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Item(Base):
    """Example Item model for API demonstration."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(nullable=False)
    is_available: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> dict:
        """Convert item to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Database session management
_async_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


async def init_db(app: Quart) -> None:
    """Initialize database connection and create tables.

    Args:
        app: Quart application instance
    """
    global _async_engine, _async_session_maker

    # Create async engine
    _async_engine = create_async_engine(
        app.config["DATABASE_URL"],
        echo=app.config["DEBUG"],
        pool_pre_ping=True,
    )

    # Create session maker
    _async_session_maker = async_sessionmaker(
        _async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Store engine in app for cleanup
    app.db_engine = _async_engine

    # Create all tables
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.logger.info("Database initialized")


def get_session() -> AsyncSession:
    """Get a new database session.

    Returns:
        AsyncSession instance

    Raises:
        RuntimeError: If database is not initialized
    """
    if _async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    return _async_session_maker()
