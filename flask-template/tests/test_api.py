"""
Tests for API endpoints.
"""

import pytest


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert 'user' in data
        assert data['user']['username'] == 'newuser'

    def test_register_duplicate_username(self, client, sample_user):
        """Test registration with duplicate username."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'SecurePass123!'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'Validation failed' in data['error']

    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email."""
        response = client.post('/api/auth/register', json={
            'username': 'differentuser',
            'email': 'test@example.com',  # Already exists
            'password': 'SecurePass123!'
        })

        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'not-an-email',
            'password': 'SecurePass123!'
        })

        assert response.status_code == 400

    def test_login_success(self, client, sample_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'bearer'
        assert 'user' in data

    def test_login_wrong_password(self, client, sample_user):
        """Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid email or password' in data['error']

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        })

        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get('/api/auth/me', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get('/api/auth/me')

        assert response.status_code == 401

    def test_refresh_token(self, client, sample_user):
        """Test refreshing access token."""
        # First login to get refresh token
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        refresh_token = login_response.get_json()['refresh_token']

        # Use refresh token to get new access token
        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

    def test_logout(self, client, auth_headers):
        """Test logout endpoint."""
        response = client.post('/api/auth/logout', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'Successfully logged out' in data['message']


class TestUserEndpoints:
    """Tests for user management endpoints."""

    def test_get_users(self, client, auth_headers, sample_user):
        """Test getting list of users."""
        response = client.get('/api/users', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert 'total' in data
        assert isinstance(data['users'], list)

    def test_get_users_pagination(self, client, auth_headers, sample_user):
        """Test user list pagination."""
        response = client.get('/api/users?page=1&per_page=10', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['page'] == 1
        assert data['per_page'] == 10

    def test_get_user_by_id(self, client, auth_headers, sample_user):
        """Test getting specific user."""
        response = client.get(f'/api/users/{sample_user.id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_user.id
        assert data['username'] == 'testuser'

    def test_get_nonexistent_user(self, client, auth_headers):
        """Test getting non-existent user."""
        response = client.get('/api/users/9999', headers=auth_headers)

        assert response.status_code == 404

    def test_update_own_user(self, client, auth_headers, sample_user):
        """Test updating own user profile."""
        response = client.put(f'/api/users/{sample_user.id}',
                             headers=auth_headers,
                             json={'username': 'updateduser'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['username'] == 'updateduser'

    def test_update_other_user_forbidden(self, client, auth_headers, another_user):
        """Test that users cannot update other users."""
        response = client.put(f'/api/users/{another_user.id}',
                             headers=auth_headers,
                             json={'username': 'hacked'})

        assert response.status_code == 403

    def test_delete_own_user(self, client, sample_user):
        """Test deleting own user account."""
        # Login first
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        response = client.delete(f'/api/users/{sample_user.id}', headers=headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'successfully' in data['message'].lower()

    def test_delete_other_user_forbidden(self, client, auth_headers, another_user):
        """Test that users cannot delete other users."""
        response = client.delete(f'/api/users/{another_user.id}', headers=auth_headers)

        assert response.status_code == 403


class TestResourceEndpoints:
    """Tests for resource endpoints."""

    def test_get_resources(self, client, auth_headers):
        """Test getting list of resources."""
        response = client.get('/api/resources', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data

    def test_create_resource(self, client, auth_headers):
        """Test creating a resource."""
        response = client.post('/api/resources',
                              headers=auth_headers,
                              json={'name': 'Test Resource', 'description': 'Test'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['resource']['name'] == 'Test Resource'

    def test_get_resource_by_id(self, client, auth_headers):
        """Test getting specific resource."""
        response = client.get('/api/resources/1', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'id' in data


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
