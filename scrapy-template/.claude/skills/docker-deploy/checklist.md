# Production Deployment Checklist

Use this checklist when deploying Scrapy to production.

## Pre-Deployment

- [ ] All tests passing (`pytest`)
- [ ] Code coverage above 80%
- [ ] Security scan completed (`bandit -r myproject/`)
- [ ] Dependencies updated and locked
- [ ] Environment variables documented in `.env.example`
- [ ] Secrets not committed to repository
- [ ] Docker images build successfully
- [ ] Resource limits configured

## Docker Configuration

- [ ] Dockerfile uses multi-stage build
- [ ] Non-root user configured
- [ ] Health checks implemented
- [ ] Logging configured properly
- [ ] Volume mounts for data persistence
- [ ] Network configuration secure
- [ ] Image size optimized (<500MB for Python)

## Performance

- [ ] DOWNLOAD_DELAY configured appropriately
- [ ] CONCURRENT_REQUESTS tuned for target
- [ ] AUTOTHROTTLE enabled
- [ ] Connection pooling configured
- [ ] Memory limits set (`deploy.resources.limits.memory`)
- [ ] CPU limits set (`deploy.resources.limits.cpus`)

## Monitoring

- [ ] Logging level set to INFO or WARNING
- [ ] Log aggregation configured (ELK, CloudWatch, etc.)
- [ ] Metrics collection enabled
- [ ] Alerts configured for failures
- [ ] Dashboard setup (Grafana, etc.)
- [ ] Health check endpoints working

## Security

- [ ] robots.txt respected
- [ ] Rate limiting configured
- [ ] User agent identifies bot
- [ ] HTTPS enforced
- [ ] Secrets in environment variables or secrets manager
- [ ] No sensitive data in logs
- [ ] Dependencies scanned for vulnerabilities
- [ ] Container runs as non-root user

## Data Management

- [ ] Database backups configured
- [ ] Data retention policy defined
- [ ] Export formats validated
- [ ] Storage quotas monitored
- [ ] Duplicate detection working
- [ ] Data validation in place

## Scaling

- [ ] Horizontal scaling tested
- [ ] Redis/queue configured for distributed scraping
- [ ] Database handles concurrent connections
- [ ] Load balancing configured if needed
- [ ] Auto-scaling rules defined

## Post-Deployment

- [ ] Monitoring active
- [ ] First run successful
- [ ] Data quality validated
- [ ] Performance metrics baseline established
- [ ] Documentation updated
- [ ] Team trained on operations

## Common Issues Checklist

- [ ] DNS resolution working in container
- [ ] Firewall rules allow outbound connections
- [ ] SSL certificates valid
- [ ] Timezone configured correctly
- [ ] File permissions correct for volumes
- [ ] Database connection pooling not exhausted

## Rollback Plan

- [ ] Previous version image tagged
- [ ] Rollback procedure documented
- [ ] Database migrations reversible
- [ ] Backup verified and restorable
- [ ] Team knows rollback procedure

## Commands Quick Reference

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Check logs
docker-compose logs -f scrapy

# Check status
docker-compose ps

# Stop
docker-compose down

# Restart
docker-compose restart scrapy

# Scale
docker-compose up -d --scale scrapy=3

# Execute commands
docker-compose exec scrapy scrapy list
```
