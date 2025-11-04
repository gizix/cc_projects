# Flask REST API Template

A production-ready Flask 3.x template for building modern REST APIs with authentication, database management, and comprehensive testing.

## Features

- **Flask 3.x** - Latest stable version with modern features
- **JWT Authentication** - Secure token-based authentication with Flask-JWT-Extended
- **SQLAlchemy ORM** - Powerful database ORM with Flask-SQLAlchemy
- **Database Migrations** - Schema versioning with Flask-Migrate (Alembic)
- **Marshmallow Serialization** - Object serialization and validation
- **RESTful API Design** - Following REST best practices
- **Comprehensive Testing** - pytest with fixtures and coverage
- **Code Quality** - Black, flake8, isort, mypy
- **Docker Support** - Dockerfile and docker-compose for easy deployment
- **Claude Code Integration** - Optimized for AI-assisted development

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip and virtualenv
- PostgreSQL (for production) or SQLite (for development)

### Installation

1. **Clone or download this template**

   ```bash
   # If from repository
   git clone https://github.com/yourusername/flask-template.git
   cd flask-template
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv

   # On macOS/Linux
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Key variables to set:
   - `SECRET_KEY` - Your application secret key
   - `JWT_SECRET_KEY` - JWT token secret key
   - `DATABASE_URL` - Database connection string

5. **Initialize database**

   ```bash
   # Run migrations
   flask db upgrade

   # (Optional) Seed with sample data
   flask seed-db
   ```

6. **Run the development server**

   ```bash
   flask run
   ```

   The API will be available at `http://127.0.0.1:5000`

### Verify Installation

Test the health check endpoint:

```bash
curl http://127.0.0.1:5000/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get tokens | No |
| POST | `/api/auth/refresh` | Refresh access token | Yes (Refresh Token) |
| GET | `/api/auth/me` | Get current user info | Yes |
| POST | `/api/auth/logout` | Logout user | Yes |

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users` | List all users (paginated) | Yes |
| GET | `/api/users/:id` | Get specific user | Yes |
| PUT | `/api/users/:id` | Update user | Yes (Own profile) |
| DELETE | `/api/users/:id` | Delete user | Yes (Own account) |

### Example Requests

**Register a new user:**

```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Login:**

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

**Access protected endpoint:**

```bash
curl http://127.0.0.1:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
black app/ tests/

# Check code style
flake8 app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create a new migration after model changes
flask db migrate -m "description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade -1

# View migration history
flask db history

# View current migration
flask db current
```

### Flask Shell

Open an interactive Python shell with application context:

```bash
flask shell
```

Example usage:
```python
>>> from app.models.user import User
>>> users = User.query.all()
>>> user = User(username='test', email='test@example.com', password='pass123')
>>> db.session.add(user)
>>> db.session.commit()
```

## Docker Deployment

### Development with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web flask db upgrade

# Run tests
docker-compose exec web pytest

# Stop services
docker-compose down
```

Services:
- **web**: Flask application (port 5000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

### Production Deployment

1. **Build production image:**

   ```bash
   docker build -t flask-api:latest .
   ```

2. **Run with environment variables:**

   ```bash
   docker run -d \
     -p 5000:5000 \
     -e SECRET_KEY=your-secret-key \
     -e JWT_SECRET_KEY=your-jwt-key \
     -e DATABASE_URL=postgresql://user:pass@host:5432/db \
     flask-api:latest
   ```

3. **Or use docker-compose:**

   ```bash
   # Set environment variables in .env
   docker-compose -f docker-compose.yml up -d
   ```

## Project Structure

```
flask-template/
├── app/                      # Main application package
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Extension initialization
│   ├── models/              # Database models
│   ├── api/                 # API blueprints
│   ├── schemas/             # Marshmallow schemas
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── tests/                    # Test suite
├── migrations/               # Database migrations
├── instance/                 # Instance-specific files
├── .claude/                  # Claude Code configuration
├── requirements.txt          # Python dependencies
├── wsgi.py                   # WSGI entry point
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This file
```

## Claude Code Integration

This template is optimized for use with Claude Code and includes:

### Slash Commands

- `/run` - Start Flask development server
- `/shell` - Open Flask interactive shell
- `/db-upgrade` - Run database migrations
- `/db-migrate` - Create new migration
- `/db-downgrade` - Rollback migration
- `/test` - Run pytest test suite
- `/create-blueprint` - Generate new API blueprint
- `/create-model` - Generate SQLAlchemy model
- `/create-schema` - Generate Marshmallow schema
- `/routes` - Display all registered routes

### Specialized Agents

Claude Code will automatically use specialized agents for:

- **flask-security**: Security vulnerability review
- **api-optimizer**: Performance optimization
- **test-generator**: Test generation
- **schema-expert**: Marshmallow schema design
- **migration-assistant**: Database migration help
- **blueprint-architect**: Blueprint organization

### Automated Skills

Skills that activate automatically when:

- **flask-patterns**: Implementing Flask design patterns
- **rest-api-generator**: Creating REST API endpoints
- **auth-system**: Building authentication systems
- **database-validator**: Adding model validation

## Configuration

### Environment Variables

Key configuration variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Application entry point | `wsgi.py` |
| `FLASK_ENV` | Environment (development/production) | `development` |
| `SECRET_KEY` | Application secret key | *(required)* |
| `JWT_SECRET_KEY` | JWT token secret key | *(required)* |
| `DATABASE_URL` | Database connection string | `sqlite:///instance/dev.db` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

### Configuration Classes

The application supports multiple configuration environments:

- **DevelopmentConfig**: SQLite database, debug mode enabled
- **TestingConfig**: In-memory database, testing mode
- **ProductionConfig**: PostgreSQL, strict security settings

Set the environment with `FLASK_ENV`:

```bash
# Development
FLASK_ENV=development flask run

# Production
FLASK_ENV=production gunicorn wsgi:app
```

## Security Considerations

### Best Practices Implemented

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ SQL injection prevention (parameterized queries)
- ✅ Input validation with Marshmallow
- ✅ CORS configuration
- ✅ Security headers
- ✅ Secrets management via environment variables
- ✅ No hardcoded credentials

### Production Security Checklist

Before deploying to production:

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure restrictive CORS origins
- [ ] Enable HTTPS with SSL certificates
- [ ] Set secure cookie flags
- [ ] Configure rate limiting
- [ ] Set up logging and monitoring
- [ ] Regular security updates
- [ ] Database backups
- [ ] Review and restrict file permissions

## Extending the Template

### Adding a New Model

1. Create model in `app/models/your_model.py`
2. Import in `app/models/__init__.py`
3. Create migration: `flask db migrate -m "add your_model"`
4. Apply migration: `flask db upgrade`

### Adding a New API Endpoint

1. Create blueprint in `app/api/your_blueprint.py`
2. Register in `app/__init__.py`
3. Create schema in `app/schemas/`
4. Write tests in `tests/test_your_blueprint.py`

### Adding Third-Party Packages

1. Add package to `requirements.txt`
2. Run `pip install -r requirements.txt`
3. If it's a Flask extension, initialize in `app/extensions.py`
4. Configure in `app/config.py` if needed

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError`
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: Database errors
- **Solution**: Run `flask db upgrade` to apply migrations

**Issue**: JWT token errors
- **Solution**: Check JWT_SECRET_KEY matches, tokens haven't expired

**Issue**: CORS errors in browser
- **Solution**: Add your frontend origin to CORS_ORIGINS

**Issue**: Permission denied on port 5000
- **Solution**: Use a different port with `flask run --port 8000`

### Getting Help

- Check the [Flask documentation](https://flask.palletsprojects.com/)
- Review `CLAUDE.md` for detailed technical context
- Open an issue on GitHub
- Ask Claude Code for assistance

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This template is available under the MIT License. See LICENSE file for details.

## Acknowledgments

- Flask and the Pallets team
- SQLAlchemy contributors
- Marshmallow contributors
- All open-source contributors

---

**Happy coding!** 🚀

For questions or issues, please open a GitHub issue or contact the maintainers.
