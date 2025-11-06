"""Tests for user endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.user import User


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient) -> None:
    """Test successful user creation."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepassword123",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test user creation with duplicate email."""
    # Create existing user
    user = User(
        email="existing@example.com",
        username="existinguser",
        hashed_password=get_password_hash("password"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Attempt to create user with same email
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "existing@example.com",
            "username": "newuser",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_create_user_duplicate_username(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Test user creation with duplicate username."""
    # Create existing user
    user = User(
        email="existing@example.com",
        username="existinguser",
        hashed_password=get_password_hash("password"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Attempt to create user with same username
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "new@example.com",
            "username": "existinguser",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


@pytest.mark.asyncio
async def test_read_users_me(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test getting current user profile."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    # Get access token
    access_token = create_access_token(subject=user.username)

    # Get current user
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_read_users_me_unauthorized(client: AsyncClient) -> None:
    """Test getting current user without authentication."""
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
