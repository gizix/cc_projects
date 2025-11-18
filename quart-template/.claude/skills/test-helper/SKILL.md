---
name: test-helper
description: Generate comprehensive async pytest tests for Quart endpoints, database operations, and WebSocket connections. Activates when writing tests or ensuring code coverage.
allowed-tools: Read, Write
---

Provide pytest-asyncio test templates and generate comprehensive test suites.

## Test Template for API Endpoints

```python
import pytest
from app.models.user import User

class Test{Resource}Endpoints:
    """Test {resource} CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_{resource}s_success(self, client, auth_headers):
        """Test listing {resource}s returns 200."""
        response = await client.get('/api/{resource}s', headers=auth_headers)

        assert response.status_code == 200
        data = await response.get_json()
        assert 'items' in data
        assert 'total' in data

    @pytest.mark.asyncio
    async def test_list_{resource}s_unauthorized(self, client):
        """Test listing without auth returns 401."""
        response = await client.get('/api/{resource}s')
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_{resource}_success(self, client, auth_headers, test_{resource}):
        """Test getting {resource} by ID."""
        response = await client.get(
            f'/api/{resource}s/{test_{resource}.id}',
            headers=auth_headers
        )

        assert response.status_code == 200
        data = await response.get_json()
        assert data['id'] == test_{resource}.id

    @pytest.mark.asyncio
    async def test_get_{resource}_not_found(self, client, auth_headers):
        """Test getting non-existent {resource} returns 404."""
        response = await client.get('/api/{resource}s/99999', headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_{resource}_success(self, client, auth_headers):
        """Test creating {resource}."""
        data = {'title': 'Test', 'description': 'Test description'}

        response = await client.post(
            '/api/{resource}s',
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 201
        result = await response.get_json()
        assert result['title'] == 'Test'
        assert 'id' in result

    @pytest.mark.asyncio
    async def test_create_{resource}_validation_error(self, client, auth_headers):
        """Test creating with invalid data."""
        data = {}  # Missing required fields

        response = await client.post(
            '/api/{resource}s',
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_{resource}_success(self, client, auth_headers, test_{resource}):
        """Test updating {resource}."""
        data = {'title': 'Updated Title'}

        response = await client.patch(
            f'/api/{resource}s/{test_{resource}.id}',
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 200
        result = await response.get_json()
        assert result['title'] == 'Updated Title'

    @pytest.mark.asyncio
    async def test_delete_{resource}_success(self, client, auth_headers, test_{resource}):
        """Test deleting {resource}."""
        response = await client.delete(
            f'/api/{resource}s/{test_{resource}.id}',
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(
            f'/api/{resource}s/{test_{resource}.id}',
            headers=auth_headers
        )
        assert get_response.status_code == 404
```

## Fixture Template

```python
@pytest_asyncio.fixture(name='test_{resource}')
async def _test_{resource}(db_session, test_user):
    """Create test {resource}."""
    from app.models.{resource} import {Resource}

    item = {Resource}(
        title='Test {Resource}',
        description='Test description',
        user_id=test_user.id
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item
```

## WebSocket Test Template

```python
@pytest.mark.asyncio
async def test_websocket_connection(app, auth_token):
    """Test WebSocket connection."""
    test_client = app.test_client()

    async with test_client.websocket(f'/ws/chat?token={auth_token}') as ws:
        # Send message
        await ws.send('Hello')

        # Receive response
        data = await ws.receive()
        assert isinstance(data, str)
```

Always test happy path, edge cases, validation, authentication, and authorization!
