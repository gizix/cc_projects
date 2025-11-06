# Scrapy Template Skills

This directory contains 4 specialized agent skills for automating common Scrapy development workflows.

## Available Skills

### 1. spider-generator
**Purpose**: Automated spider scaffolding with best practices

**Files**:
- `SKILL.md` - Main skill definition with spider type templates
- `templates.md` - Quick reference templates for different spider types

**Activates when**:
- Creating new spiders
- Implementing scraping patterns
- Need for spider type recommendations

**Provides**:
- Basic Spider templates (simple scraping)
- CrawlSpider templates (rule-based navigation)
- Playwright Spider templates (JavaScript rendering)
- API Spider templates (REST/GraphQL endpoints)
- Best practices for error handling and rate limiting

---

### 2. data-pipeline
**Purpose**: Common pipeline patterns for data processing and storage

**Files**:
- `SKILL.md` - Main skill with comprehensive pipeline patterns
- `examples.md` - Real-world pipeline examples

**Activates when**:
- Processing scraped items
- Implementing validation or cleaning
- Setting up data export workflows
- Integrating with databases

**Provides**:
- Validation pipelines
- Data cleaning pipelines
- Duplicate filtering
- Database storage (PostgreSQL, SQLite)
- File export (CSV, JSON, JSONL)
- Image download pipelines
- Advanced patterns (conditional, retry logic)

---

### 3. docker-deploy
**Purpose**: Containerization and orchestration workflows

**Files**:
- `SKILL.md` - Main skill with Docker configurations
- `checklist.md` - Production deployment checklist

**Activates when**:
- Containerizing Scrapy projects
- Setting up production deployments
- Creating distributed scraping systems
- Implementing orchestration

**Provides**:
- Dockerfiles (basic, multi-stage, Playwright-enabled)
- docker-compose configurations (single spider, full stack, distributed)
- ScrapyD deployment setup
- Kubernetes configurations
- Deployment scripts
- Monitoring setup (Prometheus, Grafana)
- Production best practices

---

### 4. test-coverage
**Purpose**: Testing patterns and coverage improvement

**Files**:
- `SKILL.md` - Main skill with comprehensive test patterns
- `fixtures-guide.md` - Guide for creating and using test fixtures

**Activates when**:
- Writing tests for spiders
- Testing pipelines or middlewares
- Improving test coverage
- Setting up CI/CD

**Provides**:
- Unit tests for spiders
- Contract tests (@scrapes annotations)
- Integration tests (full spider runs)
- Pipeline tests (validation, cleaning, storage)
- Middleware tests
- pytest configuration
- Fixtures and mocking patterns
- Coverage analysis setup
- CI/CD integration (GitHub Actions)

---

## Skill Integration

These skills work together with the template's commands and agents:

### Commands Integration
- `/spider <name> <type>` → Uses `spider-generator`
- `/pipeline <type>` → Uses `data-pipeline`
- `/dockerize` → Uses `docker-deploy`
- `/test` → Uses `test-coverage`

### Agent Integration
- `@scrapy-expert` - Reviews generated code from all skills
- `@performance-optimizer` - Optimizes spider and pipeline configurations
- `@scraping-security` - Validates ethical scraping practices
- `@test-writer` - Uses test-coverage skill for test generation

## Usage Examples

### Generate a Playwright Spider
```
User: Create a spider for scraping a JavaScript-heavy e-commerce site
→ spider-generator skill activates
→ Generates Playwright spider with proper browser handling
```

### Setup Database Pipeline
```
User: I need to save scraped products to PostgreSQL
→ data-pipeline skill activates
→ Creates DatabasePipeline with proper connection handling
```

### Containerize Project
```
User: Dockerize this Scrapy project for production
→ docker-deploy skill activates
→ Generates Dockerfile, docker-compose.yml, deployment scripts
```

### Add Tests
```
User: Create tests for the product spider
→ test-coverage skill activates
→ Generates unit tests, fixtures, and contract tests
```

## Customization

Each skill can be customized by:
1. Editing the SKILL.md frontmatter (name, description, allowed-tools)
2. Modifying templates and examples
3. Adding new patterns or configurations
4. Updating activation triggers in descriptions

## Maintenance

When updating skills:
- Keep templates aligned with Scrapy best practices
- Update examples when Scrapy releases new versions
- Add new patterns as they emerge
- Test generated code with actual Scrapy projects
- Update documentation with new features

---

**Note**: These skills are designed to work automatically based on user intent. They analyze context and proactively generate appropriate code without requiring explicit skill invocation.
