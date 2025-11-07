"""Tests for API endpoints."""

import pytest


@pytest.mark.asyncio
class TestHealthCheck:
    """Tests for health check endpoint."""

    async def test_health_check(self, client):
        """Test health check returns 200."""
        response = await client.get("/api/health")
        assert response.status_code == 200

        data = await response.get_json()
        assert data["status"] == "healthy"
        assert "version" in data


@pytest.mark.asyncio
class TestAuthentication:
    """Tests for authentication endpoints."""

    async def test_register_success(self, client):
        """Test successful user registration."""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 201
        data = await response.get_json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "password" not in data

    async def test_register_duplicate_username(self, client, test_user):
        """Test registration fails with duplicate username."""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        data = await response.get_json()
        assert "already exists" in data["message"].lower()

    async def test_login_success(self, client, test_user):
        """Test successful login."""
        response = await client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = await response.get_json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client, test_user):
        """Test login fails with invalid credentials."""
        response = await client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = await response.get_json()
        assert "invalid" in data["message"].lower()

    async def test_get_current_user(self, client, test_user, auth_headers):
        """Test getting current user info."""
        response = await client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = await response.get_json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    async def test_get_current_user_unauthorized(self, client):
        """Test getting current user without token fails."""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestItems:
    """Tests for item endpoints."""

    async def test_list_items(self, client, test_items):
        """Test listing items."""
        response = await client.get("/api/items")

        assert response.status_code == 200
        data = await response.get_json()
        assert "items" in data
        assert data["total"] >= 2  # Only available items for unauthenticated
        assert data["page"] == 1

    async def test_list_items_pagination(self, client, test_items):
        """Test pagination."""
        response = await client.get("/api/items?page=1&page_size=1")

        assert response.status_code == 200
        data = await response.get_json()
        assert len(data["items"]) == 1
        assert data["page_size"] == 1

    async def test_get_item(self, client, test_items):
        """Test getting specific item."""
        item_id = test_items[0].id
        response = await client.get(f"/api/items/{item_id}")

        assert response.status_code == 200
        data = await response.get_json()
        assert data["id"] == item_id
        assert data["name"] == "Item 1"

    async def test_get_item_not_found(self, client):
        """Test getting non-existent item."""
        response = await client.get("/api/items/9999")

        assert response.status_code == 404

    async def test_create_item(self, client, auth_headers):
        """Test creating new item."""
        response = await client.post(
            "/api/items",
            headers=auth_headers,
            json={
                "name": "New Item",
                "description": "A new item",
                "price": 15.99,
                "is_available": True,
            },
        )

        assert response.status_code == 201
        data = await response.get_json()
        assert data["name"] == "New Item"
        assert data["price"] == 15.99

    async def test_create_item_unauthorized(self, client):
        """Test creating item without authentication fails."""
        response = await client.post(
            "/api/items",
            json={
                "name": "New Item",
                "description": "A new item",
                "price": 15.99,
            },
        )

        assert response.status_code == 401

    async def test_update_item(self, client, auth_headers, test_items):
        """Test updating item."""
        item_id = test_items[0].id
        response = await client.put(
            f"/api/items/{item_id}",
            headers=auth_headers,
            json={"name": "Updated Item", "price": 25.99},
        )

        assert response.status_code == 200
        data = await response.get_json()
        assert data["name"] == "Updated Item"
        assert data["price"] == 25.99

    async def test_delete_item(self, client, auth_headers, test_items):
        """Test deleting item."""
        item_id = test_items[0].id
        response = await client.delete(f"/api/items/{item_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify item is deleted
        response = await client.get(f"/api/items/{item_id}")
        assert response.status_code == 404

    async def test_delete_item_unauthorized(self, client, test_items):
        """Test deleting item without authentication fails."""
        item_id = test_items[0].id
        response = await client.delete(f"/api/items/{item_id}")

        assert response.status_code == 401
