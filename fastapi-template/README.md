# FastAPI Template

Production-ready FastAPI template with async SQLAlchemy 2.0, JWT authentication, testing, and Docker support.

## Features

- **FastAPI 0.115.x** - Latest stable FastAPI with modern patterns
- **Async SQLAlchemy 2.0** - Fully async database operations with PostgreSQL
- **JWT Authentication** - OAuth2 password flow with secure token handling
- **Repository Pattern** - Clean architecture with separation of concerns
- **Testing** - Pytest with async support and coverage reporting
- **Docker** - Multi-stage Dockerfile and docker-compose setup
- **Alembic** - Database migrations with autogenerate
- **Code Quality** - Ruff formatting, MyPy type checking, pre-commit hooks
- **uv Package Manager** - Ultra-fast dependency management

## Quick Start

### Prerequisites

- Python 3.12+
- uv package manager
- PostgreSQL (or use Docker)

### Installation

1. Clone and navigate to the template:
```bash
cd fastapi-template
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and set your configuration (especially `SECRET_KEY`):
```bash
# Generate a secure secret key
openssl rand -hex 32
```

4. Install dependencies:
```bash
uv sync
```

5. Start PostgreSQL (or use Docker):
```bash
docker-compose up -d db
```

6. Run database migrations:
```bash
uv run alembic upgrade head
```

7. Start the development server:
```bash
uv run fastapi dev
```

The API will be available at http://localhost:8000

-Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Project Structure

```
fastapi-template/
├── app/
│   ├── core/               # Core functionality (config, database, security)
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── api/v1/             # API routes
│   ├── services/           # Business logic
│   ├── repositories/       # Data access layer
│   └── main.py             # FastAPI application
├── tests/                  # Pytest tests
├── migrations/             # Alembic migrations
├── scripts/                # Utility scripts
├── .claude/                # Claude Code configuration
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_api/test_auth.py
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint and fix
uv run ruff check . --fix

# Type checking
uv run mypy app/
```

### Database Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login with username/password, get JWT token

### Users

- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/me` - Get current user profile (requires auth)

### Health

- `GET /` - Root endpoint
- `GET /api/v1/health` - Health check

## Authentication

This template uses JWT tokens with OAuth2 password flow:

1. **Register a user**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"testuser","password":"securepass123"}'
```

2. **Login to get token**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=securepass123"
```

3. **Use token in requests**:
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <your-token>"
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (generate with `openssl rand -hex 32`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins

### Settings

Application settings are managed via Pydantic Settings in `app/core/config.py`. All settings can be overridden via environment variables.

## Testing

Tests use pytest with async support and an in-memory SQLite database:

- `tests/conftest.py` - Shared fixtures
- `tests/test_api/` - API endpoint tests
- Coverage reports generated in `htmlcov/`

## Adding New Features

### Creating a New Endpoint

1. Create model in `app/models/your_model.py`
2. Create schemas in `app/schemas/your_schema.py`
3. Create repository in `app/repositories/your_repository.py`
4. Create service in `app/services/your_service.py`
5. Create router in `app/api/v1/endpoints/your_endpoint.py`
6. Register router in `app/api/v1/router.py`
7. Import model in `migrations/env.py`
8. Create migration: `uv run alembic revision --autogenerate -m "add your_model"`
9. Apply migration: `uv run alembic upgrade head`
10. Write tests in `tests/test_api/test_your_endpoint.py`

## Production Deployment

### Security Checklist

- [ ] Generate strong `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure proper `BACKEND_CORS_ORIGINS`
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Review authentication flows
- [ ] Scan dependencies for vulnerabilities

### Running in Production

```bash
# Using uvicorn with multiple workers
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using gunicorn with uvicorn workers
uv run gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## License

This template is provided as-is for use in your projects.

## Support

For issues or questions:
1. Check the FastAPI documentation: https://fastapi.tiangolo.com
2. Review the code comments and docstrings
3. Examine the test files for usage examples
