# Quart Async Web Application Template

A production-ready template for building modern async web applications with Python using Quart framework.

## Features

✨ **Async-First**: Built with asyncio and async/await throughout
🔐 **JWT Authentication**: Secure token-based auth with access & refresh tokens
📊 **SQLAlchemy Async**: Modern ORM with full async support (PostgreSQL, MySQL, SQLite)
✅ **Validation**: Automatic request/response validation with Pydantic
📖 **OpenAPI Docs**: Auto-generated API documentation (Swagger, ReDoc, Scalar)
🔌 **WebSocket**: Native WebSocket support (echo, broadcast, chat patterns)
🧪 **Testing**: Comprehensive test suite with pytest-asyncio
🎨 **Code Quality**: Ruff linter, Black formatter, Mypy type checking
🚀 **Production Ready**: Hypercorn ASGI server, Docker support, deployment guides

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager

### Installation

1. **Clone or copy this template**

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Using pip
   pip install -e ".[dev]"

   # Or using uv (faster)
   uv pip install -e ".[dev]"
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run development server**
   ```bash
   # Using Quart CLI
   QUART_APP="src.app:create_app()" quart run

   # Or using Claude Code (if available)
   # /dev
   ```

6. **Access the application**
   - API: http://localhost:5000/api/health
   - OpenAPI Docs: http://localhost:5000/docs
   - ReDoc: http://localhost:5000/redocs
   - Scalar: http://localhost:5000/scalar

## Project Structure

```
quart-template/
├── src/app/              # Application code
│   ├── __init__.py       # App factory
│   ├── config.py         # Configuration
│   ├── auth.py           # JWT utilities
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   └── routes/           # API blueprints
│       ├── auth/         # Authentication
│       ├── api/          # REST API
│       └── ws/           # WebSockets
├── tests/                # Test suite
├── .claude/              # Claude Code config
├── pyproject.toml        # Dependencies
├── .env.example          # Env template
└── README.md             # This file
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

### Items (Example Resource)

- `GET /api/items` - List items (with pagination)
- `GET /api/items/{id}` - Get item by ID
- `POST /api/items` - Create item (auth required)
- `PUT /api/items/{id}` - Update item (auth required)
- `DELETE /api/items/{id}` - Delete item (auth required)

### WebSocket

- `WS /ws/echo` - Echo server (no auth)
- `WS /ws/chat` - Multi-user chat (auth required)
- `WS /ws/notifications?token=<jwt>` - Real-time notifications (auth required)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

### Code Quality

```bash
# Lint with Ruff
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix

# Format with Black
black src/ tests/

# Type check with Mypy
mypy src/

# Run all checks
ruff check src/ tests/ --fix && black src/ tests/ && mypy src/
```

### Database Migrations

This template uses auto table creation in development. For production, set up Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Application
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# CORS
CORS_ALLOWED_ORIGINS=*

# Logging
LOG_LEVEL=DEBUG
```

Generate secure keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database Options

**SQLite** (default, development):
```bash
DATABASE_URL=sqlite+aiosqlite:///./app.db
```

**PostgreSQL** (recommended for production):
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
pip install asyncpg
```

**MySQL**:
```bash
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/dbname
pip install aiomysql
```

## Deployment

### Using Hypercorn (Production)

```bash
# Basic
hypercorn "src.app:create_app('production')" --bind 0.0.0.0:8000

# With workers
hypercorn "src.app:create_app('production')" \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class asyncio
```

### Using Docker

```bash
# Build image
docker build -t quart-app .

# Run container
docker run -p 8000:8000 --env-file .env quart-app

# Using docker-compose
docker-compose up
```

### Using Systemd

See deployment documentation for systemd service configuration.

## Testing the API

### Using curl

```bash
# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123"}'

# Use token (replace TOKEN with actual token)
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### Using Python

```python
import asyncio
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        # Register
        response = await client.post(
            "http://localhost:5000/api/auth/register",
            json={
                "username": "test",
                "email": "test@example.com",
                "password": "password123"
            }
        )
        print(response.json())

        # Login
        response = await client.post(
            "http://localhost:5000/api/auth/login",
            json={"username": "test", "password": "password123"}
        )
        tokens = response.json()
        token = tokens["access_token"]

        # Authenticated request
        response = await client.get(
            "http://localhost:5000/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(response.json())

asyncio.run(test_api())
```

### Using WebSocket

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:5000/ws/echo"

    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send("Hello, WebSocket!")

        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(test_websocket())
```

## Claude Code Integration

This template includes full Claude Code configuration:

### Commands
- `/dev` - Start dev server
- `/test` - Run tests
- `/lint` - Code quality checks
- `/create-blueprint <name>` - New blueprint
- `/create-model <name>` - New model
- `/create-route <blueprint> <method> <path>` - New route
- `/create-websocket <path>` - New WebSocket

### Agents
- **quart-api-expert** - API guidance (proactive)
- **async-security-reviewer** - Security review (proactive)
- **database-assistant** - Database help
- **websocket-helper** - WebSocket patterns
- **deployment-advisor** - Deployment guidance

### Skills
- **async-error-handling** - Error patterns
- **api-schema-design** - API design
- **background-tasks** - Async tasks

## Documentation

- [Setup Instructions](setup_instructions.md) - Detailed setup guide
- [CLAUDE.md](CLAUDE.md) - Development context for Claude Code
- OpenAPI Docs - http://localhost:5000/docs (when running)

## Architecture

### Async-First

All code uses async/await:
- Route handlers are `async def`
- Database operations are awaited
- No blocking I/O in async context
- Background tasks use asyncio

### Application Factory

Multiple environments supported:
- **Development**: Debug, auto-reload, verbose logging
- **Testing**: In-memory DB, fast execution
- **Production**: Optimized, secure, minimal logging

### Blueprint Organization

Routes organized by domain:
- `auth` - Authentication
- `api` - REST resources
- `ws` - WebSockets

### Database

SQLAlchemy 2.0 with async:
- Type-safe with `Mapped[type]`
- Session management via context manager
- Auto table creation in dev
- Migrations via Alembic (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- [Quart Documentation](https://quart.palletsprojects.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic](https://docs.pydantic.dev/)
- [GitHub Issues](https://github.com/yourusername/quart-template/issues)

---

**Built with Quart** - Modern async Python web framework
