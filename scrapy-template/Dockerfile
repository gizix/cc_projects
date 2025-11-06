# Multi-stage Dockerfile for Scrapy project

# Builder stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --user --no-cache-dir \
    scrapy>=2.11.0 \
    scrapy-playwright>=0.0.34 \
    scrapy-fake-useragent>=1.4.4 \
    sqlalchemy>=2.0.0 \
    psycopg2-binary>=2.9.0 \
    pymongo>=4.5.0 \
    python-dotenv>=1.0.0 \
    itemloaders>=1.1.0 \
    w3lib>=2.1.2 \
    redis>=5.0.0

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p logs data/json data/csv data/raw

# Install Playwright browsers (optional, comment out if not needed)
RUN playwright install chromium && \
    playwright install-deps chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SCRAPY_SETTINGS_MODULE=myproject.settings

# Default command
CMD ["scrapy", "list"]
