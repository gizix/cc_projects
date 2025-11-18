"""Test routes."""
import pytest

@pytest.mark.asyncio
async def test_health(client):
    """Test health endpoint."""
    response = await client.get('/health')
    assert response.status_code == 200
    data = await response.get_json()
    assert data['status'] == 'healthy'

@pytest.mark.asyncio
async def test_hello(client):
    """Test hello endpoint."""
    response = await client.get('/api/hello')
    assert response.status_code == 200
    data = await response.get_json()
    assert 'message' in data
