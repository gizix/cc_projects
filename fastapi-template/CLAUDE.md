# FastAPI Template - Claude Code Context

Production-ready FastAPI template with async SQLAlchemy 2.0, JWT authentication, and comprehensive testing.

## Architecture

**Framework**: FastAPI 0.115.x | **Package Manager**: uv | **Database**: PostgreSQL (async SQLAlchemy 2.0) | **Auth**: JWT OAuth2

### Project Structure

- `app/core/` - Configuration, database, security
- `app/models/` - SQLAlchemy ORM models
- `app/schemas/` - Pydantic validation schemas
- `app/api/v1/` - API routes and endpoints
- `app/services/` - Business logic layer
- `app/repositories/` - Data access layer (repository pattern)
- `tests/` - Pytest with async support
- `migrations/` - Alembic database migrations

### Key Patterns

**Clean Architecture**: API → Service → Repository → Database
**Dependency Injection**: FastAPI Depends for all layers
**Repository Pattern**: Abstract data access for testability
**Async/Await**: All I/O operations are async
**Type Safety**: Full type hints with MyPy strict mode

## FastAPI Conventions

### Routing & Responses

- API versioning: `/api/v1/...`
- Use Pydantic schemas: `*Create`, `*Update`, `*Public`, `*InDB`
- OAuth2 password bearer for authentication
- OpenAPI docs at `/docs` and `/redoc`

### Authentication Dependencies

```python
get_current_user        # Basic auth
get_current_active_user # Active users only
get_current_superuser   # Admin only
```

## Database (SQLAlchemy 2.0 Async)

### Always Use Async Patterns

```python
async with sessionmanager.get_session() as session:
    result = await session.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
```

### Model Definition

Use `Mapped[]` type annotations for all columns in SQLAlchemy 2.0.

### Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

Always import models in `migrations/env.py` for autogenerate.

## Security

- Passwords hashed with bcrypt via passlib
- JWT tokens (HS256) with configurable expiration
- Secrets in environment variables (`.env`)
- Input validation via Pydantic
- No passwords in API responses

## Testing

- Pytest with async support (`pytest-asyncio`)
- In-memory SQLite for fast tests
- Fresh database per test via fixtures
- Run: `uv run pytest --cov=app`

## Common Operations

### Adding New Endpoint

1. Model → `app/models/`
2. Schema → `app/schemas/`
3. Repository → `app/repositories/`
4. Service → `app/services/`
5. Router → `app/api/v1/endpoints/`
6. Register router in `app/api/v1/router.py`
7. Import model in `migrations/env.py`
8. Generate migration
9. Write tests

### Code Quality

```bash
uv run ruff format .        # Format
uv run ruff check . --fix   # Lint
uv run mypy app/            # Type check
uv run pytest               # Test
```

## Production

- Use environment-specific `.env` files
- Run with multiple uvicorn workers
- Enable CORS for frontend
- Implement rate limiting
- Add monitoring/logging
- Use HTTPS

This template follows FastAPI and SQLAlchemy 2.0 best practices for production-ready applications.
