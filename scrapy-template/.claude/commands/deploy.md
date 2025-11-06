---
description: Docker deployment helper and Scrapyd upload for production deployment
argument-hint: [--docker|--scrapyd|--kubernetes] [options]
allowed-tools: Bash(*), Read(*), Write(*)
---

Deploy Scrapy spider to production using Docker, Scrapyd, or Kubernetes.

Arguments:
- $ARGUMENTS: Deployment target and options

Common usage patterns:
- `/deploy --docker` - Build and run Docker container
- `/deploy --scrapyd http://localhost:6800` - Deploy to Scrapyd server
- `/deploy --kubernetes` - Deploy to Kubernetes cluster
- `/deploy --docker --build-only` - Build Docker image only
- `/deploy --scrapyd --project myproject` - Deploy with custom project name

Deployment Options:

## 1. Docker Deployment

**Process**:

1. **Verify Dockerfile exists or create it**:
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables
ENV SCRAPY_SETTINGS_MODULE=settings

# Default command
CMD ["scrapy", "list"]
```

2. **Create .dockerignore**:
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.venv
venv/
*.egg-info/
.scrapy
*.log
.git
.gitignore
README.md
.env
data/
output/
```

3. **Build Docker image**:
```bash
docker build -t scrapy-project:latest .
```

4. **Run container**:
```bash
# Run specific spider
docker run scrapy-project:latest scrapy crawl myspider -o /app/data/output.json

# Run with volume mount for output
docker run -v $(pwd)/data:/app/data scrapy-project:latest scrapy crawl myspider -o /app/data/output.json

# Run with environment variables
docker run --env-file .env scrapy-project:latest scrapy crawl myspider
```

5. **Push to registry** (optional):
```bash
# Tag image
docker tag scrapy-project:latest registry.example.com/scrapy-project:latest

# Push to registry
docker push registry.example.com/scrapy-project:latest
```

**Docker Compose** (for complex deployments):

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  scrapy:
    build: .
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    environment:
      - SCRAPY_SETTINGS_MODULE=settings
      - DATABASE_URL=${DATABASE_URL}
    env_file:
      - .env
    command: scrapy crawl myspider -o /app/output/data.json

  # Optional: Scrapyd server
  scrapyd:
    image: vimagick/scrapyd
    ports:
      - "6800:6800"
    volumes:
      - ./scrapyd:/var/lib/scrapyd

  # Optional: Database for storing results
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: scrapy_db
      POSTGRES_USER: scrapy
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

Run with: `docker-compose up`

## 2. Scrapyd Deployment

**Process**:

1. **Install scrapyd-client**:
```bash
pip install scrapyd-client
```

2. **Configure scrapy.cfg**:
```ini
[settings]
default = settings

[deploy]
url = http://localhost:6800/
project = myproject
username = admin
password = secret
```

Or for multiple targets:
```ini
[deploy:production]
url = http://prod-server:6800/
project = myproject

[deploy:staging]
url = http://staging-server:6800/
project = myproject
```

3. **Package project**:
```bash
scrapyd-deploy --build-egg=myproject.egg
```

4. **Deploy to Scrapyd**:
```bash
# Deploy to default target
scrapyd-deploy

# Deploy to specific target
scrapyd-deploy production

# Deploy specific version
scrapyd-deploy --version 1.0.0
```

5. **Schedule spider on Scrapyd**:
```bash
curl http://localhost:6800/schedule.json \
    -d project=myproject \
    -d spider=myspider \
    -d setting=DOWNLOAD_DELAY=2
```

**Scrapyd Management**:

```python
# Using scrapyd-api
from scrapyd_api import ScrapydAPI

scrapyd = ScrapydAPI('http://localhost:6800')

# List projects
projects = scrapyd.list_projects()

# List spiders
spiders = scrapyd.list_spiders('myproject')

# Schedule job
job_id = scrapyd.schedule('myproject', 'myspider')

# List jobs
jobs = scrapyd.list_jobs('myproject')

# Cancel job
scrapyd.cancel('myproject', job_id)

# Delete project version
scrapyd.delete_version('myproject', '1.0.0')
```

## 3. Kubernetes Deployment

**Process**:

1. **Create Kubernetes manifests**:

`k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scrapy-spider
  labels:
    app: scrapy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: scrapy
  template:
    metadata:
      labels:
        app: scrapy
    spec:
      containers:
      - name: scrapy
        image: registry.example.com/scrapy-project:latest
        command: ["scrapy", "crawl", "myspider"]
        env:
        - name: SCRAPY_SETTINGS_MODULE
          value: "settings"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: scrapy-secrets
              key: database-url
        volumeMounts:
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: scrapy-data-pvc
```

`k8s/cronjob.yaml` (for scheduled crawls):
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scrapy-daily-crawl
spec:
  schedule: "0 2 * * *"  # Run at 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scrapy
            image: registry.example.com/scrapy-project:latest
            command: ["scrapy", "crawl", "myspider", "-o", "/app/data/output.json"]
            env:
            - name: SCRAPY_SETTINGS_MODULE
              value: "settings"
          restartPolicy: OnFailure
```

`k8s/secrets.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: scrapy-secrets
type: Opaque
stringData:
  database-url: "postgresql://user:pass@host/db"
```

2. **Apply manifests**:
```bash
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/cronjob.yaml
```

3. **Monitor deployment**:
```bash
# Check pods
kubectl get pods -l app=scrapy

# View logs
kubectl logs -f deployment/scrapy-spider

# Check cronjob
kubectl get cronjobs
kubectl get jobs
```

## Deployment Checklist

Before deploying:

```
Pre-Deployment Checklist
========================

Configuration:
  ☐ Environment variables set (.env file)
  ☐ Database connection configured
  ☐ API keys and credentials secured
  ☐ ROBOTSTXT_OBEY=True for production
  ☐ Appropriate DOWNLOAD_DELAY set
  ☐ LOG_LEVEL set to INFO or WARNING

Testing:
  ☐ All tests passing (/test-spider)
  ☐ Spider tested with production data
  ☐ Item validation passing (/validate-items)
  ☐ Performance benchmarked (/benchmark)
  ☐ robots.txt checked (/check-robots)

Security:
  ☐ No hardcoded secrets in code
  ☐ .env file not committed to git
  ☐ Secure API endpoints protected
  ☐ Rate limiting configured
  ☐ Error handling implemented

Infrastructure:
  ☐ Docker image builds successfully
  ☐ Resource limits configured
  ☐ Storage volumes configured
  ☐ Monitoring/logging set up
  ☐ Backup strategy defined

Documentation:
  ☐ README.md updated
  ☐ Deployment instructions documented
  ☐ Runbook for troubleshooting
  ☐ Contact information for alerts
```

## Production Settings

Create `production_settings.py`:
```python
from settings import *

# Production overrides
DEBUG = False
LOG_LEVEL = 'INFO'

# Respect robots.txt in production
ROBOTSTXT_OBEY = True

# Polite crawling
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# AutoThrottle for dynamic rate limiting
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Identify your bot
USER_AGENT = 'MyBot/1.0 (+https://mywebsite.com/bot-info)'

# Database storage (instead of files)
ITEM_PIPELINES = {
    'pipelines.DatabasePipeline': 300,
}

# Monitoring
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,  # Disable telnet
    'scrapy.extensions.logstats.LogStats': 500,
}

# Security
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Memory management
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 512
MEMUSAGE_WARNING_MB = 384
```

Use in deployment: `SCRAPY_SETTINGS_MODULE=production_settings`

## Monitoring & Logging

**Structured Logging**:
```python
# settings.py
LOG_FORMATTER = 'scrapy.logformatter.LogFormatter'
LOG_FILE = 'scrapy.log'
LOG_FILE_APPEND = False
LOG_ENCODING = 'utf-8'

# JSON logging for log aggregation
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'spider': getattr(record, 'spider', None),
            'message': record.getMessage(),
        }
        return json.dumps(log_data)
```

**Prometheus Metrics** (optional):
```python
# Custom extension for metrics
from prometheus_client import Counter, Gauge

items_scraped = Counter('scrapy_items_scraped', 'Items scraped')
requests_total = Counter('scrapy_requests_total', 'Total requests')
```

After Deployment:

1. **Verify deployment**:
   - Check logs for errors
   - Verify items are being scraped
   - Monitor resource usage
   - Test spider endpoint/API

2. **Set up monitoring**:
   - Log aggregation (ELK, Splunk, etc.)
   - Metrics (Prometheus, Grafana)
   - Alerts (PagerDuty, email, Slack)
   - Uptime monitoring

3. **Schedule regular crawls**:
   - Cron jobs
   - Kubernetes CronJobs
   - Scrapyd periodic scheduling
   - Airflow/Prefect workflows

Best Practices:
- Use environment variables for configuration
- Never commit secrets to version control
- Implement proper error handling and retries
- Set resource limits to prevent runaway processes
- Monitor spider performance and adjust settings
- Implement health checks and readiness probes
- Use persistent storage for output data
- Back up crawled data regularly
- Version your deployments
- Have rollback strategy ready

Common Issues:
- Memory leaks: Monitor with MEMUSAGE settings
- Rate limiting: Adjust DOWNLOAD_DELAY and concurrency
- Network timeouts: Increase DOWNLOAD_TIMEOUT
- Storage full: Implement data retention policy
- Permission errors: Check file/directory permissions

Next Steps:
- Monitor initial crawl runs
- Set up automated testing in CI/CD
- Configure alerting for failures
- Document operational procedures
- Plan for scaling if needed
