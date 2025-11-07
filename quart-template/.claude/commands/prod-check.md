---
description: Pre-deployment validation checklist
---

Run pre-deployment checks to ensure production readiness.

I'll verify the following:

## Security Checks
- [ ] SECRET_KEY is set and not the default
- [ ] JWT_SECRET_KEY is set and strong
- [ ] Database URL uses secure connection
- [ ] CORS origins are explicitly set (not "*")
- [ ] Debug mode is disabled
- [ ] No sensitive data in logs

## Configuration
- [ ] All required environment variables are documented
- [ ] .env.example is up to date
- [ ] Production config class is properly configured
- [ ] Rate limiting is enabled

## Code Quality
- [ ] All tests pass: `pytest tests/`
- [ ] No linting errors: `ruff check src/`
- [ ] Code is formatted: `black src/`
- [ ] Type checking passes: `mypy src/`

## Database
- [ ] Migrations are up to date
- [ ] Database indexes are optimized
- [ ] Connection pooling is configured

## Dependencies
- [ ] All dependencies are pinned with versions
- [ ] No known security vulnerabilities: `pip-audit`
- [ ] Unused dependencies removed

## Performance
- [ ] Async patterns used correctly
- [ ] No blocking I/O in async functions
- [ ] Background tasks have timeouts
- [ ] Query N+1 problems resolved

## Deployment
- [ ] README has deployment instructions
- [ ] Hypercorn worker count configured
- [ ] Health check endpoint works
- [ ] Logging is production-ready
- [ ] Error handling covers edge cases

Run this command to perform automated checks:
```bash
cd quart-template && pytest tests/ && ruff check src/ && black --check src/ && mypy src/
```

Would you like me to review any specific area in detail?
