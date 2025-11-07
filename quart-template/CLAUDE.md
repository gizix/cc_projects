# Quart Async Web Application Template

This is a production-ready Quart application template with modern async patterns, JWT authentication, SQLAlchemy async ORM, and native WebSocket support.

## Project Overview

**Framework**: Quart 0.19+ (async Flask-compatible framework)
**Language**: Python 3.11+
**Database**: SQLAlchemy 2.0+ with async support
**Authentication**: JWT tokens with refresh token support
**Validation**: Pydantic + Quart-Schema with automatic OpenAPI generation
**Testing**: pytest with pytest-asyncio
**Code Quality**: Ruff (linter) + Black (formatter) + Mypy (type checker)

## Architecture & Design Principles

### Async-First Design

This application is built with async/await throughout:
- All route handlers are `async def` functions
- Database operations use async SQLAlchemy
- External API calls use async HTTP clients (httpx)
- WebSocket support is native and fully async
- Background tasks leverage asyncio patterns

**Critical Rule**: Never use blocking I/O in async code. Always use async libraries and await all I/O operations.

### Application Factory Pattern

The application uses the factory pattern (`create_app()`) to support multiple environments:
- **Development**: Debug mode, verbose logging, auto-reload
- **Testing**: In-memory database, fast execution
- **Production**: Optimized settings, minimal logging, security hardened

Configuration is class-based with environment variable overrides using `app.config.from_prefixed_env()`.

### Blueprint Organization

Routes are organized by resource domain using blueprints:
- `auth` - Authentication endpoints (register, login, token refresh, user info)
- `api` - RESTful resource management (CRUD operations)
- `ws` - WebSocket endpoints (echo, chat, notifications)

Each blueprint is self-contained with clear URL prefixes.

## Project Structure

```
quart-template/
├── src/
│   └── app/
│       ├── __init__.py           # Application factory, lifecycle hooks
│       ├── config.py              # Configuration classes (Dev, Test, Prod)
│       ├── auth.py                # JWT authentication utilities
│       ├── models/
│       │   └── __init__.py        # SQLAlchemy async models
│       ├── schemas/
│       │   └── __init__.py        # Pydantic validation schemas
│       └── routes/
│           ├── auth/              # Authentication blueprint
│           ├── api/               # API endpoints blueprint
│           └── ws/                # WebSocket blueprint
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   └── test_api.py                # API endpoint tests
├── .claude/
│   ├── commands/                  # Slash commands
│   ├── agents/                    # Specialized subagents
│   └── skills/                    # Agent skills
├── pyproject.toml                 # Dependencies & tool configs
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore patterns
├── README.md                      # User-facing documentation
└── CLAUDE.md                      # This file
```

## Core Technologies

### Quart

Quart is an async reimplementation of Flask with full compatibility for most Flask extensions. Key features:
- Native async/await support throughout
- Built-in WebSocket support (no extensions needed)
- Compatible with ASGI servers (Hypercorn, Uvicorn)
- Familiar Flask-like API

**Why Quart over Flask**: Better performance for I/O-bound operations, native WebSocket support, modern async patterns.

### Quart-Schema

Provides automatic request/response validation and OpenAPI documentation generation:
- Integrates with Pydantic for schema definitions
- Decorators: `@validate_request`, `@validate_response`, `@validate_querystring`
- Auto-generates OpenAPI 3.0 spec
- Multiple doc UIs: Swagger, ReDoc, Scalar

### SQLAlchemy 2.0 Async

Modern ORM with full async support:
- Use `Mapped[type]` for type hints
- Always use `async with get_session()` for session management
- All database operations must be awaited
- Supports PostgreSQL (asyncpg), MySQL (aiomysql), SQLite (aiosqlite)

**Example**:
```python
async with get_session() as session:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.email = new_email
        await session.commit()
        await session.refresh(user)
```

### JWT Authentication

Custom JWT implementation without heavy dependencies:
- Access tokens (short-lived, 1 hour default)
- Refresh tokens (long-lived, 30 days default)
- `@require_auth` decorator for protected routes
- `@optional_auth` for flexible endpoints
- Token validation in `Authorization: Bearer <token>` header

### Pydantic Schemas

All input/output validation uses Pydantic:
- `*CreateSchema` for POST requests
- `*UpdateSchema` for PUT/PATCH requests
- `*Schema` for responses
- Rich validation with Field() constraints
- Automatic OpenAPI documentation from schemas

## Coding Conventions

### Async Patterns

**Always use async/await**:
```python
# GOOD
@app.route("/users/<int:user_id>")
async def get_user(user_id: int):
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user.to_dict() if user else ({"error": "Not Found"}, 404)

# BAD - Missing async/await
@app.route("/users/<int:user_id>")
def get_user(user_id: int):  # Not async!
    session = get_session()  # Won't work
    user = session.query(User).get(user_id)  # Blocking!
```

### Database Operations

**Always use context managers**:
```python
# GOOD
async with get_session() as session:
    session.add(user)
    await session.commit()
    await session.refresh(user)

# BAD - Session leak
session = get_session()
session.add(user)
await session.commit()  # Session never closed!
```

### Error Handling

**Use custom exceptions or return error tuples**:
```python
# Option 1: Custom exceptions
from app.exceptions import NotFoundException

if not user:
    raise NotFoundException(f"User {user_id} not found")

# Option 2: Error tuple
if not user:
    return {"error": "Not Found", "message": "User not found"}, 404
```

### Validation

**Always validate input and output**:
```python
@api_bp.route("/items", methods=["POST"])
@validate_request(ItemCreateSchema)        # Validate input
@validate_response(ItemSchema, 201)        # Validate success response
@validate_response(ErrorSchema, 400)       # Validate error response
async def create_item(data: ItemCreateSchema):
    # data is validated Pydantic model
    pass
```

### Authentication

**Protect routes with decorators**:
```python
from app.auth import require_auth, optional_auth
from quart import g

@api_bp.route("/profile")
@require_auth  # Returns 401 if no valid token
async def get_profile():
    user_id = g.current_user["user_id"]  # Available after @require_auth
    # Implementation
```

## API Design Standards

### RESTful Conventions

- Use resource-based URLs: `/api/users`, `/api/items/{id}`
- Use proper HTTP methods: GET (read), POST (create), PUT (replace), PATCH (update), DELETE (delete)
- Return appropriate status codes:
  - 200 OK - Successful GET/PUT/PATCH
  - 201 Created - Successful POST
  - 204 No Content - Successful DELETE
  - 400 Bad Request - Invalid input
  - 401 Unauthorized - Missing/invalid auth
  - 403 Forbidden - Valid auth, insufficient permissions
  - 404 Not Found - Resource doesn't exist
  - 422 Validation Error - Failed schema validation
  - 500 Internal Server Error - Unexpected server error

### Response Format

**Success**:
```json
{
    "id": 123,
    "name": "Item Name",
    "created_at": "2024-01-01T12:00:00Z"
}
```

**Error**:
```json
{
    "error": "Not Found",
    "message": "Item not found",
    "details": null
}
```

### Pagination

Use query parameters:
- `page` - Page number (starts at 1)
- `page_size` - Items per page (max 100)
- `sort_by` - Field to sort by
- `order` - Sort order (asc/desc)

Response includes pagination metadata:
```json
{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
}
```

## WebSocket Patterns

### Native Quart WebSocket Support

Quart has built-in WebSocket support (no extensions needed):

```python
@ws_bp.websocket("/echo")
async def echo():
    try:
        while True:
            message = await websocket.receive()
            await websocket.send(f"Echo: {message}")
    except asyncio.CancelledError:
        pass  # Connection closed
```

### Authentication

Two approaches:

**1. Token in first message**:
```python
auth_message = await websocket.receive()
auth_data = json.loads(auth_message)
token = auth_data.get("token")
payload = decode_token(token)
```

**2. Token in query parameter** (recommended):
```python
token = request.args.get("token")
payload = decode_token(token)
```

### Message Format

Use JSON for structured communication:
```json
{
    "type": "message",
    "payload": {"content": "Hello"},
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## Testing

### Async Tests

All tests are async and use pytest-asyncio:

```python
import pytest

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/api/users", json={
        "username": "test",
        "email": "test@example.com",
        "password": "password123"
    })

    assert response.status_code == 201
    data = await response.get_json()
    assert data["username"] == "test"
```

### Fixtures

Common fixtures in `tests/conftest.py`:
- `app` - Test application instance
- `client` - Test client for requests
- `test_user` - Pre-created test user
- `auth_headers` - Authentication headers for test user
- `test_items` - Pre-created test items

## Development Workflow

### Setup

1. Copy `.env.example` to `.env` and configure
2. Install dependencies: `pip install -e ".[dev]"`
3. Run development server: `/dev` or `QUART_APP="src.app:create_app()" quart run`

### Code Quality

Run before committing:
- Lint: `ruff check src/ tests/ --fix`
- Format: `black src/ tests/`
- Type check: `mypy src/`
- Test: `pytest tests/ -v --cov=src/app`

### Available Commands

Claude Code slash commands:
- `/dev` - Start development server
- `/test` - Run test suite with coverage
- `/lint` - Run all code quality tools
- `/create-blueprint <name>` - Generate new blueprint
- `/create-model <name>` - Add new database model
- `/create-route <blueprint> <method> <path>` - Add new route
- `/create-websocket <path>` - Add WebSocket endpoint
- `/generate-docs` - View/export OpenAPI documentation
- `/prod-check` - Pre-deployment validation
- `/db-migrate [message]` - Database migrations (requires Alembic setup)

## Production Deployment

### Hypercorn ASGI Server

Quart runs on Hypercorn (default ASGI server):

```bash
hypercorn "src.app:create_app('production')" \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class asyncio \
    --access-log - \
    --error-log -
```

### Worker Count

Recommended: `(CPU cores * 2) + 1`

For I/O-bound async apps, more workers = better concurrency.

### Environment Variables

Required in production:
- `SECRET_KEY` - Strong secret for sessions
- `JWT_SECRET_KEY` - Strong secret for JWT
- `DATABASE_URL` - Production database connection
- `CORS_ALLOWED_ORIGINS` - Explicit allowed origins (not "*")

### Reverse Proxy

Use Nginx or Caddy in front of Hypercorn for:
- SSL termination
- Load balancing
- Static file serving
- WebSocket proxy support

## Security Best Practices

1. **Never commit `.env` file** - Contains secrets
2. **Use strong SECRET_KEY** - Generate with `secrets.token_hex(32)`
3. **Validate all input** - Use Pydantic schemas
4. **Parameterize database queries** - SQLAlchemy handles this
5. **Set explicit CORS origins** - Don't use "*" in production
6. **Enable rate limiting** - Prevent abuse
7. **Use HTTPS** - TLS 1.2+ required
8. **Hash passwords** - Never store plain text (using werkzeug)
9. **Set DEBUG=False** - In production
10. **Keep dependencies updated** - Run `pip-audit` regularly

## Common Patterns

### Pagination Helper

```python
async def paginate_query(query, page: int, page_size: int):
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.limit(page_size).offset(offset)

    return query, total
```

### Background Task

```python
@app.route("/send-email", methods=["POST"])
async def send_email():
    email_data = await request.get_json()

    # Add background task (doesn't block response)
    app.add_background_task(send_email_async, email_data)

    return {"message": "Email queued"}, 202
```

### Retry with Backoff

```python
async def retry_async(func, max_attempts=3, delay=1.0, backoff=2.0):
    for attempt in range(max_attempts):
        try:
            return await func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            await asyncio.sleep(delay * (backoff ** attempt))
```

## Available Agents

Claude Code specialized agents:
- **quart-api-expert** - API design, async patterns (PROACTIVE)
- **async-security-reviewer** - Security vulnerabilities (PROACTIVE)
- **database-assistant** - SQLAlchemy async operations
- **websocket-helper** - WebSocket implementation
- **deployment-advisor** - Production deployment guidance

## Available Skills

- **async-error-handling** - Exception patterns and error boundaries
- **api-schema-design** - RESTful design and Pydantic schemas
- **background-tasks** - Long-running async tasks and lifecycle

## Performance Tips

1. **Use connection pooling** - Configure in `create_async_engine()`
2. **Eager load relationships** - Use `selectinload()` to avoid N+1 queries
3. **Add database indexes** - On frequently queried columns
4. **Implement caching** - For expensive operations
5. **Use pagination** - Don't return entire collections
6. **Batch operations** - Group database operations
7. **Profile async code** - Use `asyncio` debugging tools
8. **Set timeouts** - On long-running async operations
9. **Monitor memory** - Background tasks can leak memory
10. **Use async libraries** - Never mix blocking and async code

## Troubleshooting

### Common Issues

**RuntimeError: no running event loop**
- Forgot to use `async def` or `await`
- Trying to run async code from sync context

**Session not closed / connection pool exhausted**
- Not using `async with get_session()` context manager
- Session leaking in error paths

**SQLAlchemy error: greenlet_spawn has not been called**
- Missing `await` on database operation
- Using sync SQLAlchemy patterns with async engine

**WebSocket disconnects immediately**
- Not handling `asyncio.CancelledError`
- Nginx timeout too short for long-lived connections

**401 Unauthorized on valid token**
- Token expired
- Wrong JWT_SECRET_KEY
- Token not in `Authorization: Bearer <token>` format

## Resources

- [Quart Documentation](https://quart.palletsprojects.com/)
- [Quart-Schema Documentation](https://quart-schema.readthedocs.io/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Hypercorn Documentation](https://hypercorn.readthedocs.io/)

## Contributing

When adding new features:
1. Follow async patterns consistently
2. Add Pydantic schemas for validation
3. Write tests (async with pytest-asyncio)
4. Update OpenAPI docs (automatic via Quart-Schema)
5. Add error handling
6. Update this CLAUDE.md if adding patterns

---

This template is designed for production use with modern async Python best practices. All patterns follow Quart's async-first approach.
