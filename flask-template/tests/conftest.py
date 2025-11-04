"""
Pytest configuration and fixtures.

Provides common fixtures for testing Flask application.
"""

import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope='session')
def app():
    """
    Create and configure a Flask application instance for testing.

    Returns:
        Flask: Configured test application
    """
    app = create_app('testing')

    # Establish application context
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def db(app):
    """
    Create database tables for testing.

    Args:
        app: Flask application fixture

    Returns:
        SQLAlchemy: Database instance
    """
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """
    Create a database session for a test with rollback.

    Args:
        db: Database fixture

    Returns:
        Session: Database session
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app, db):
    """
    Create a test client for the application.

    Args:
        app: Flask application fixture
        db: Database fixture

    Returns:
        FlaskClient: Test client
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Create a CLI test runner.

    Args:
        app: Flask application fixture

    Returns:
        FlaskCliRunner: CLI test runner
    """
    return app.test_cli_runner()


@pytest.fixture
def sample_user(db, session):
    """
    Create a sample user for testing.

    Args:
        db: Database fixture
        session: Database session fixture

    Returns:
        User: Sample user instance
    """
    user = User(
        username='testuser',
        email='test@example.com',
        password='TestPassword123!'
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def auth_headers(client, sample_user):
    """
    Get authentication headers with JWT token.

    Args:
        client: Test client fixture
        sample_user: Sample user fixture

    Returns:
        dict: Headers dictionary with Authorization header
    """
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'TestPassword123!'
    })

    assert response.status_code == 200
    data = response.get_json()
    token = data['access_token']

    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def another_user(db, session):
    """
    Create another sample user for testing.

    Args:
        db: Database fixture
        session: Database session fixture

    Returns:
        User: Another sample user instance
    """
    user = User(
        username='anotheruser',
        email='another@example.com',
        password='AnotherPassword123!'
    )
    session.add(user)
    session.commit()
    return user
