"""Pytest configuration and fixtures for async Quart testing."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import create_app
from app.models import Base, get_session, User, Item
from app.auth import hash_password


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def app():
    """Create application instance for testing."""
    test_app = await create_app("testing")
    yield test_app


@pytest.fixture
async def client(app):
    """Create test client for making requests."""
    return app.test_client()


@pytest.fixture
async def db_session(app):
    """Create a database session for testing."""
    async with get_session() as session:
        yield session


@pytest.fixture
async def test_user(app):
    """Create a test user."""
    async with get_session() as session:
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("testpassword123"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield user


@pytest.fixture
async def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = await client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpassword123"},
    )
    data = await response.get_json()
    token = data["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_items(app):
    """Create test items."""
    async with get_session() as session:
        items = [
            Item(
                name="Item 1",
                description="Description 1",
                price=10.99,
                is_available=True,
            ),
            Item(
                name="Item 2",
                description="Description 2",
                price=20.99,
                is_available=True,
            ),
            Item(
                name="Item 3",
                description="Description 3",
                price=30.99,
                is_available=False,
            ),
        ]

        for item in items:
            session.add(item)

        await session.commit()

        for item in items:
            await session.refresh(item)

        yield items
