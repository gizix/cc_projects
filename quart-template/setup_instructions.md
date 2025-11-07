# Quart Template - Detailed Setup Instructions

This guide will walk you through setting up the Quart application template from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Verification](#verification)
7. [Development Tools](#development-tools)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

**Python 3.11 or higher**
```bash
# Check Python version
python --version

# Should output: Python 3.11.x or higher
```

**Package Manager**

Option 1: pip (included with Python)
```bash
pip --version
```

Option 2: uv (faster, recommended)
```bash
pip install uv
```

### Optional Tools

- **Git** - For version control
- **Docker** - For containerized deployment
- **PostgreSQL** - For production database (SQLite works for development)

## Initial Setup

### Step 1: Get the Template

**Option A: Clone from repository**
```bash
git clone https://github.com/yourusername/quart-template.git
cd quart-template
```

**Option B: Copy template directory**
```bash
# If this is part of a template collection
cp -r path/to/quart-template my-project
cd my-project
```

### Step 2: Create Virtual Environment

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

**Install core dependencies:**
```bash
# Using pip
pip install -e ".[dev]"

# Or using uv (faster)
uv pip install -e ".[dev]"
```

This installs:
- Quart framework
- SQLAlchemy with async support
- Pydantic for validation
- Quart-Schema for OpenAPI
- JWT for authentication
- pytest for testing
- Ruff, Black, Mypy for code quality

**For PostgreSQL support:**
```bash
pip install ".[postgres]"
```

**For MySQL support:**
```bash
pip install ".[mysql]"
```

**Verify installation:**
```bash
python -c "import quart; print(quart.__version__)"
```

## Environment Configuration

### Step 1: Create .env file

```bash
cp .env.example .env
```

### Step 2: Generate Secure Keys

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"
```

**Generate JWT_SECRET_KEY:**
```bash
python -c "import secrets; print(f'JWT_SECRET_KEY={secrets.token_hex(32)}')"
```

Copy these values into your `.env` file.

### Step 3: Configure Environment Variables

Edit `.env` and configure:

**Development Configuration:**
```bash
# Application
QUART_ENV=development
SECRET_KEY=<generated-secret-key>
JWT_SECRET_KEY=<generated-jwt-secret-key>

# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./app.db

# CORS (allow all in development)
CORS_ALLOWED_ORIGINS=*

# Logging
LOG_LEVEL=DEBUG

# Rate limiting (disabled in dev)
RATE_LIMIT_ENABLED=false
```

**Production Configuration:**
```bash
# Application
QUART_ENV=production
SECRET_KEY=<strong-secret-key>
JWT_SECRET_KEY=<strong-jwt-secret-key>

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# CORS (explicit origins)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Logging
LOG_LEVEL=INFO

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100 per hour
```

## Database Setup

### SQLite (Development - Default)

No additional setup needed. Database file `app.db` will be created automatically on first run.

### PostgreSQL (Production - Recommended)

**1. Install PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Mac (using Homebrew)
brew install postgresql

# Or use Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=quart_db \
  -p 5432:5432 \
  postgres:15-alpine
```

**2. Create Database:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE quart_db;
CREATE USER quart_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE quart_db TO quart_user;
\q
```

**3. Install async driver:**
```bash
pip install asyncpg
```

**4. Update .env:**
```bash
DATABASE_URL=postgresql+asyncpg://quart_user:secure_password@localhost:5432/quart_db
```

### MySQL (Alternative)

**1. Install MySQL:**
```bash
# Ubuntu/Debian
sudo apt-get install mysql-server

# Mac (using Homebrew)
brew install mysql

# Or use Docker
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=yourpassword \
  -e MYSQL_DATABASE=quart_db \
  -p 3306:3306 \
  mysql:8
```

**2. Create Database:**
```bash
mysql -u root -p

CREATE DATABASE quart_db;
CREATE USER 'quart_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON quart_db.* TO 'quart_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**3. Install async driver:**
```bash
pip install aiomysql
```

**4. Update .env:**
```bash
DATABASE_URL=mysql+aiomysql://quart_user:secure_password@localhost:3306/quart_db
```

### Database Migrations (Optional, for Production)

**1. Install Alembic:**
```bash
pip install alembic
```

**2. Initialize Alembic:**
```bash
alembic init alembic
```

**3. Configure Alembic:**

Edit `alembic/env.py` to use async engine and your models.

**4. Create Initial Migration:**
```bash
alembic revision --autogenerate -m "Initial migration"
```

**5. Apply Migrations:**
```bash
alembic upgrade head
```

## Running the Application

### Development Server

**Method 1: Using Quart CLI**
```bash
QUART_APP="src.app:create_app()" quart run
```

With hot reload:
```bash
QUART_APP="src.app:create_app()" quart run --reload
```

**Method 2: Using Hypercorn directly**
```bash
hypercorn "src.app:create_app('development')" \
    --bind 0.0.0.0:5000 \
    --reload
```

**Method 3: Using Claude Code** (if available)
```bash
/dev
```

The server will start at: http://localhost:5000

### Production Server

**Using Hypercorn:**
```bash
hypercorn "src.app:create_app('production')" \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class asyncio \
    --access-log - \
    --error-log -
```

**Using Docker:**
```bash
docker build -t quart-app .
docker run -p 8000:8000 --env-file .env quart-app
```

**Using Docker Compose:**
```bash
docker-compose up -d
```

**Using Systemd:**

Create `/etc/systemd/system/quart-app.service` and use systemctl commands.

## Verification

### Step 1: Check Health Endpoint

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "message": "Quart API is running"
}
```

### Step 2: Access API Documentation

Open in browser:
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redocs
- **Scalar**: http://localhost:5000/scalar

### Step 3: Test Authentication Flow

**Register a user:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

**Test authenticated endpoint:**
```bash
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 4: Test WebSocket

**Using Python:**
```python
import asyncio
import websockets

async def test():
    uri = "ws://localhost:5000/ws/echo"
    async with websockets.connect(uri) as ws:
        await ws.send("Hello!")
        response = await ws.recv()
        print(response)  # Should print: "Echo: Hello!"

asyncio.run(test())
```

### Step 5: Run Test Suite

```bash
pytest tests/ -v
```

All tests should pass.

## Development Tools

### Code Formatting

**Format code with Black:**
```bash
black src/ tests/
```

### Linting

**Lint with Ruff:**
```bash
# Check for issues
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix
```

### Type Checking

**Check types with Mypy:**
```bash
mypy src/
```

### Testing

**Run tests:**
```bash
pytest
```

**With coverage:**
```bash
pytest --cov=src/app --cov-report=html
```

View coverage report: `htmlcov/index.html`

**Run specific test:**
```bash
pytest tests/test_api.py::TestAuthentication::test_login_success -v
```

### Combined Quality Check

```bash
# Run all checks
ruff check src/ tests/ --fix && \
black src/ tests/ && \
mypy src/ && \
pytest
```

Or use Claude Code:
```bash
/lint
```

## Troubleshooting

### Issue: Module not found

**Solution:**
```bash
# Reinstall in editable mode
pip install -e ".[dev]"

# Or add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Issue: Database connection error

**Solution:**
- Check DATABASE_URL in .env
- Verify database server is running
- Test connection:
  ```bash
  # PostgreSQL
  psql -U quart_user -d quart_db

  # MySQL
  mysql -u quart_user -p quart_db
  ```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
QUART_APP="src.app:create_app()" quart run --port 5001
```

### Issue: JWT token invalid

**Solution:**
- Verify JWT_SECRET_KEY matches between token creation and validation
- Check token expiration (default: 1 hour)
- Ensure token is in correct format: `Authorization: Bearer <token>`

### Issue: WebSocket connection fails

**Solution:**
- Check if server supports WebSocket (Hypercorn does by default)
- Verify firewall allows WebSocket connections
- If using reverse proxy (Nginx), ensure WebSocket headers are set:
  ```nginx
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  ```

### Issue: Import errors in tests

**Solution:**
```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or install pytest-asyncio explicitly
pip install pytest-asyncio
```

### Issue: CORS errors

**Solution:**
- In development, set `CORS_ALLOWED_ORIGINS=*` in .env
- In production, set explicit origins:
  ```bash
  CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
  ```

### Getting Help

- Check [CLAUDE.md](CLAUDE.md) for development patterns
- Review [README.md](README.md) for quick reference
- Open an issue on GitHub
- Consult [Quart documentation](https://quart.palletsprojects.com/)

## Next Steps

1. **Customize the application:**
   - Modify models in `src/app/models/`
   - Add routes in `src/app/routes/`
   - Update schemas in `src/app/schemas/`

2. **Add features:**
   - Use `/create-blueprint` to add new blueprints
   - Use `/create-model` to add new models
   - Use `/create-route` to add new endpoints

3. **Configure production:**
   - Set up PostgreSQL database
   - Configure reverse proxy (Nginx/Caddy)
   - Set up SSL certificates
   - Configure monitoring

4. **Deploy:**
   - Build Docker image
   - Deploy to cloud provider
   - Set up CI/CD pipeline
   - Configure logging and monitoring

---

**You're all set!** Your Quart application is ready for development.

For more details, see [README.md](README.md) and [CLAUDE.md](CLAUDE.md).
