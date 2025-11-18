---
name: deployment-guide
description: Production deployment guidance for Quart applications including Docker, Hypercorn configuration, environment management, monitoring, and performance tuning. Activates when deploying or optimizing for production.
allowed-tools: Read, Write
---

Provide production deployment best practices and configurations for Quart applications.

## Docker Configuration

### Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system --no-cache .

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Run with Hypercorn
CMD ["hypercorn", "src.app:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "asyncio"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/quart_db
      - QUART_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=quart_db
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## Hypercorn Production Configuration

```bash
# Recommended production settings
hypercorn src.app:create_app() \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class asyncio \
    --access-log - \
    --error-log - \
    --access-logformat '%(h)s %(r)s %(s)s %(b)s %(D)s' \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --backlog 100
```

## Environment Variables

```bash
# Production .env (never commit!)
SECRET_KEY=generate-with-secrets.token-hex-32
JWT_SECRET_KEY=generate-with-secrets.token-hex-32
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
QUART_ENV=production
CORS_ORIGINS=https://example.com,https://app.example.com
LOG_LEVEL=INFO
```

## Nginx Reverse Proxy

```nginx
upstream quart_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # WebSocket support
    location /ws {
        proxy_pass http://quart_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # HTTP requests
    location / {
        proxy_pass http://quart_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring & Logging

```python
import logging
from quart.logging import default_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add request logging
@app.before_request
async def log_request():
    app.logger.info(f'{request.method} {request.path}')

@app.after_request
async def log_response(response):
    app.logger.info(f'{request.method} {request.path} - {response.status_code}')
    return response
```

## Health Check Endpoint

```python
@app.route('/health')
async def health_check():
    """Health check endpoint for load balancers."""
    # Check database
    try:
        async with get_session() as session:
            await session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'

    return {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'database': db_status,
        'version': app.config.get('API_VERSION')
    }
```

## Performance Tuning

- Workers: `(CPU cores * 2) + 1`
- Database pool: 5-10 per worker
- Connection timeout: 30s
- Keep-alive: 5s
- Backlog: 100-1000

## Pre-Deployment Checklist

- [ ] DEBUG=False
- [ ] Strong SECRET_KEY set
- [ ] Explicit CORS origins
- [ ] HTTPS enforced
- [ ] Database migrations applied
- [ ] Static files served by CDN/nginx
- [ ] Logging configured
- [ ] Health checks implemented
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Rate limiting enabled
- [ ] Security headers set
