# Scrapy Web Scraping Template

A comprehensive, production-ready Scrapy project template with Claude Code integration. This template includes pre-configured commands, specialized AI agents, and automated workflows to accelerate web scraping development.

## What's Included

### Claude Code Configuration

- **10 Custom Slash Commands**: Quick access to common Scrapy operations
- **6 Specialized Subagents**: AI assistants for spider development, security, testing, performance, pipelines, and deployment
- **4 Agent Skills**: Automated patterns for spider generation, data pipelines, Docker deployment, and test coverage
- **CLAUDE.md**: Comprehensive Scrapy context and best practices
- **Intelligent Workflows**: Auto-formatting, validation, and best practice enforcement

### Framework Setup

- Scrapy 2.11+ with modern async support
- Playwright integration for JavaScript rendering
- PostgreSQL + SQLAlchemy for relational data storage
- MongoDB + PyMongo for document storage
- Redis for distributed deduplication
- Development tools (pytest, Black, mypy, flake8)
- Code quality tools (pre-commit hooks, type checking)
- Docker Compose for development services
- Production-ready Dockerfile

### Project Structure

```
scrapy-template/
├── .claude/                       # Claude Code configuration
│   ├── commands/                  # 10 slash commands
│   │   ├── run-spider.md
│   │   ├── create-spider.md
│   │   ├── shell.md
│   │   ├── test-spider.md
│   │   ├── list-spiders.md
│   │   ├── export-data.md
│   │   ├── validate-items.md
│   │   ├── check-robots.md
│   │   ├── benchmark.md
│   │   └── deploy.md
│   ├── agents/                    # 6 specialized agents
│   │   ├── spider-dev.md
│   │   ├── security-advisor.md
│   │   ├── performance-tuner.md
│   │   ├── pipeline-expert.md
│   │   ├── testing-assistant.md
│   │   └── deployment-helper.md
│   ├── skills/                    # 4 automated skills
│   │   ├── spider-generator/
│   │   ├── data-pipeline/
│   │   ├── docker-deploy/
│   │   └── test-coverage/
│   └── settings.json              # Claude Code settings
├── myproject/                     # Scrapy project directory
│   ├── spiders/                   # Spider implementations
│   ├── items.py                   # Data models (dataclasses)
│   ├── pipelines.py              # Item processing pipelines
│   ├── middlewares.py            # Spider/downloader middlewares
│   ├── loaders.py                # Item loaders for data cleaning
│   ├── settings.py               # Scrapy configuration
│   └── utils/                    # Utility functions
├── tests/                         # Test suite
├── data/                          # Scraped data output
├── logs/                          # Log files
├── docker-compose.yml            # PostgreSQL, MongoDB, Redis
├── Dockerfile                    # Docker image for scrapers
├── pyproject.toml               # Python dependencies
├── pytest.ini                   # Test configuration
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore patterns
├── .pre-commit-config.yaml      # Code quality hooks
├── CLAUDE.md                    # Scrapy context and conventions
├── setup_instructions.md        # Detailed setup guide
└── README.md                    # This file
```

## Quick Start

### 1. Download Template

```bash
# Clone the repository
git clone <repo-url>

# Navigate to Scrapy template
cd scrapy-template

# Optional: Copy to your project directory
cp -r . /path/to/your/project
```

### 2. Set Up Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install Playwright browsers (for JavaScript rendering)
playwright install chromium

# Configure environment variables
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Development Services

```bash
# Start PostgreSQL, MongoDB, Redis with Docker
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Open in VSCode with Claude Code

```bash
# Open project in VSCode
code .

# Launch Claude Code and start developing!
```

## Using Claude Code Features

### Slash Commands

Quick access to common Scrapy operations:

| Command | Description | Example |
|---------|-------------|---------|
| `/run-spider` | Run a spider with output options | `/run-spider myspider -o data.json` |
| `/create-spider` | Generate new spider from template | `/create-spider products basic` |
| `/shell` | Open Scrapy shell for testing | `/shell https://example.com` |
| `/test-spider` | Test spider with contracts | `/test-spider myspider` |
| `/list-spiders` | List all available spiders | `/list-spiders` |
| `/export-data` | Export scraped data to database | `/export-data data.json --to postgres` |
| `/validate-items` | Validate scraped data quality | `/validate-items data.json` |
| `/check-robots` | Check robots.txt compliance | `/check-robots example.com` |
| `/benchmark` | Run spider performance benchmark | `/benchmark myspider` |
| `/deploy` | Deploy spider to production | `/deploy myspider --target production` |

**Usage**: Type the command in Claude Code's input field and press Enter.

### Specialized Subagents

AI assistants that automatically activate based on context or can be explicitly invoked:

#### 1. Spider Development Agent
**Triggers**: Creating spiders, debugging selectors, parsing issues
**Capabilities**:
- Generate complete spider implementations
- Optimize XPath and CSS selectors
- Debug response parsing errors
- Handle pagination and link following
- Implement spider arguments and rules

**Explicit use**: "Use the spider-dev agent to create a product spider for example.com"

#### 2. Security Advisor Agent
**Triggers**: Security reviews, ethical scraping questions, ToS compliance
**Capabilities**:
- Review scraping legality and ethics
- Ensure robots.txt compliance
- Configure rate limiting and politeness
- Check data privacy considerations
- Validate user agent identification
- Review authentication handling

**Explicit use**: "Use the security-advisor agent to review my spider's compliance"

#### 3. Performance Tuner Agent
**Triggers**: Slow crawls, optimization requests, concurrency issues
**Capabilities**:
- Optimize spider settings for speed
- Configure AutoThrottle and concurrency
- Implement caching strategies
- Optimize selector performance
- Memory usage optimization
- Distributed crawling setup

**Explicit use**: "Use the performance-tuner agent to optimize my spider"

#### 4. Pipeline Expert Agent
**Triggers**: Data processing, storage, validation needs
**Capabilities**:
- Design item pipelines
- Implement database storage (PostgreSQL, MongoDB)
- Create data validation pipelines
- Build duplicate filtering logic
- Design data transformation workflows
- Implement export pipelines

**Explicit use**: "Use the pipeline-expert agent to create a database pipeline"

#### 5. Testing Assistant Agent
**Triggers**: Test creation, coverage checks, test failures
**Capabilities**:
- Generate spider tests with fixtures
- Implement pipeline tests
- Create spider contracts
- Set up test coverage reporting
- Mock HTTP responses
- Test edge cases and error handling

**Explicit use**: "Use the testing-assistant agent to create tests for my spider"

#### 6. Deployment Helper Agent
**Triggers**: Production deployment, Docker setup, scheduling
**Capabilities**:
- Configure Docker deployments
- Set up Scrapyd for distributed scraping
- Create cron jobs for scheduling
- Configure cloud deployments (AWS, GCP, Azure)
- Implement monitoring and alerting
- Production optimization

**Explicit use**: "Use the deployment-helper agent to create a Docker deployment"

### Automated Skills

Skills that automatically activate when appropriate:

#### Spider Generator Skill
**Auto-activates**: When creating new spiders or implementing scraping patterns
**Provides**: Basic spiders, CrawlSpiders, Playwright spiders, API spiders with best practices

#### Data Pipeline Skill
**Auto-activates**: When implementing data processing or storage
**Provides**: Database pipelines, validation pipelines, duplicate filtering, export pipelines

#### Docker Deploy Skill
**Auto-activates**: When setting up containerized deployments
**Provides**: Dockerfile optimization, docker-compose configuration, multi-stage builds

#### Test Coverage Skill
**Auto-activates**: When writing tests or checking coverage
**Provides**: Comprehensive test patterns, fixtures, mocking, coverage configuration

## Development Workflow

### Creating a New Spider

1. **Generate spider**:
   ```
   /create-spider product_spider basic
   ```
   Claude will generate a spider with proper structure

2. **Test selectors in shell**:
   ```
   /shell https://example.com/products
   ```
   Test CSS/XPath selectors interactively

3. **Implement parsing logic**:
   Ask: "Help me extract product name, price, and description"
   (spider-dev agent will activate)

4. **Run spider**:
   ```
   /run-spider product_spider -o data/products.json
   ```

5. **Validate data**:
   ```
   /validate-items data/products.json
   ```

6. **Create tests**:
   Ask: "Generate tests for product_spider"
   (testing-assistant agent will activate)

7. **Check performance**:
   ```
   /benchmark product_spider
   ```

### Handling JavaScript-Rendered Pages

1. **Create Playwright spider**:
   ```
   /create-spider dynamic_spider playwright
   ```

2. **Configure page interactions**:
   Ask: "Add scrolling and wait for dynamic content"
   (spider-dev agent will help)

3. **Test with headless browser**:
   ```
   /run-spider dynamic_spider -o data/dynamic.json
   ```

### Setting Up Data Pipelines

1. **Design pipeline**:
   Ask: "Create a pipeline to store products in PostgreSQL"
   (pipeline-expert agent will activate)

2. **Configure database**:
   Update `.env` with database credentials

3. **Enable pipeline**:
   Add to `settings.py` ITEM_PIPELINES

4. **Test pipeline**:
   ```
   /test-spider product_spider
   ```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_spiders.py

# With coverage
pytest --cov=myproject --cov-report=html

# Run spider contracts
/test-spider myspider
```

### Code Quality

The template includes automatic code quality tools:

- **Black**: Auto-formats Python files (configured in pyproject.toml)
- **isort**: Sorts imports automatically
- **flake8**: Linting for code quality
- **mypy**: Type checking
- **pre-commit**: Git hooks run checks before commit

```bash
# Format code
black myproject/

# Sort imports
isort myproject/

# Run linter
flake8 myproject/

# Type check
mypy myproject/

# Install pre-commit hooks
pre-commit install
```

## Web Scraping Best Practices

This template enforces ethical and legal scraping practices:

### Respect and Compliance

- ✅ robots.txt compliance (ROBOTSTXT_OBEY = True)
- ✅ Rate limiting and download delays
- ✅ Proper User-Agent identification
- ✅ AutoThrottle for dynamic adjustment
- ✅ Respect website ToS
- ✅ No bypass of authentication/paywalls
- ✅ Privacy law compliance (GDPR, CCPA)

### Technical Best Practices

- ✅ Efficient selector optimization
- ✅ Comprehensive error handling
- ✅ Data validation and cleaning
- ✅ Duplicate detection (Redis)
- ✅ Resumable crawls (JOBDIR)
- ✅ Request/response logging
- ✅ Memory-efficient processing

## JavaScript Rendering with Playwright

For dynamic websites that require JavaScript:

```python
# Configure in spider
custom_settings = {
    'DOWNLOAD_HANDLERS': {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    },
}

# Use in requests
yield scrapy.Request(
    url,
    meta={
        'playwright': True,
        'playwright_page_methods': [
            ('wait_for_selector', 'div.content'),
            ('evaluate', 'window.scrollTo(0, document.body.scrollHeight)'),
        ],
    }
)
```

## Database Integration

### PostgreSQL Storage

```python
# Pipeline automatically created via pipeline-expert agent
class PostgreSQLPipeline:
    def process_item(self, item, spider):
        # Store in PostgreSQL with SQLAlchemy
        session.add(ProductModel(**item))
        session.commit()
        return item
```

### MongoDB Storage

```python
# Pipeline for document storage
class MongoDBPipeline:
    def process_item(self, item, spider):
        # Store in MongoDB
        collection.insert_one(dict(item))
        return item
```

### Redis Deduplication

```python
# Duplicate filtering with Redis
class RedisDuplicatesPipeline:
    def process_item(self, item, spider):
        # Check if item exists
        if self.redis.exists(item['url']):
            raise DropItem(f"Duplicate: {item['url']}")
        self.redis.set(item['url'], 1)
        return item
```

## Production Deployment

### Docker Deployment

```bash
# Build image
docker build -t myproject-scraper .

# Run spider in container
docker run --env-file .env myproject-scraper scrapy crawl spider_name

# Docker Compose (with services)
docker-compose up -d
docker-compose run scraper scrapy crawl spider_name
```

### Scrapyd (Distributed Scraping)

```bash
# Install Scrapyd
pip install scrapyd scrapyd-client

# Deploy project
scrapyd-deploy production -p myproject

# Schedule spider
curl http://localhost:6800/schedule.json \
    -d project=myproject \
    -d spider=spider_name
```

### Cron Scheduling

```bash
# Edit crontab
crontab -e

# Run spider daily at 2 AM
0 2 * * * cd /path/to/project && /path/to/venv/bin/scrapy crawl spider_name

# Run spider every 6 hours
0 */6 * * * cd /path/to/project && /path/to/venv/bin/scrapy crawl spider_name
```

## Data Export Formats

Scrapy supports multiple export formats:

```bash
# JSON (default, good for APIs)
/run-spider myspider -o data.json

# JSON Lines (one item per line, better for large datasets)
/run-spider myspider -o data.jsonl

# CSV (good for spreadsheets)
/run-spider myspider -o data.csv

# XML
/run-spider myspider -o data.xml

# Multiple outputs
/run-spider myspider -o data.json -o data.csv

# Export to database (via pipeline)
/export-data data.json --to postgres
```

## Customization

### Adding More Commands

Create `.claude/commands/mycommand.md`:

```markdown
---
description: Description of what this command does
argument-hint: <required> [optional]
allowed-tools: Bash(*), Read(*)
---

Command instructions here
```

### Creating Custom Agents

Create `.claude/agents/my-agent.md`:

```markdown
---
name: my-agent
description: PROACTIVELY assists when [conditions]
tools: Read, Write, Bash, Grep
model: sonnet
---

Agent system prompt and instructions
```

### Adding Skills

Create `.claude/skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: What this skill does and when to trigger it
allowed-tools: Read, Write
---

Detailed skill instructions with examples
```

## Resources

### Documentation
- Scrapy: https://docs.scrapy.org/
- Scrapy-Playwright: https://github.com/scrapy-plugins/scrapy-playwright
- ItemLoaders: https://itemloaders.readthedocs.io/
- Scrapyd: https://scrapyd.readthedocs.io/
- Claude Code: https://docs.claude.com/en/docs/claude-code

### Community
- Scrapy Forum: https://groups.google.com/forum/#!forum/scrapy-users
- Stack Overflow: Tag `scrapy`
- Reddit: r/scrapy

### Legal and Ethical
- robots.txt: https://www.robotstxt.org/
- Web Scraping Best Practices: https://www.scraperapi.com/blog/web-scraping-best-practices/
- GDPR Guidelines: https://gdpr.eu/

### Learning
- Scrapy Tutorial: https://docs.scrapy.org/en/latest/intro/tutorial.html
- Scrapy Course: https://www.udemy.com/topic/scrapy/
- Web Scraping with Python: https://www.oreilly.com/library/view/web-scraping-with/9781491985564/

## Troubleshooting

### Common Issues

**Q: Spider not found**
A: Use `/list-spiders` to see available spiders, ensure spider is in myproject/spiders/

**Q: Selectors not extracting data**
A: Use `/shell URL` to test selectors interactively, check page structure

**Q: 403 Forbidden errors**
A: Configure proper User-Agent, add download delays, check robots.txt

**Q: JavaScript content not loading**
A: Use Playwright integration for JavaScript rendering, see setup_instructions.md

**Q: Database connection errors**
A: Check `.env` file has correct credentials, ensure Docker services are running

**Q: Memory issues on large crawls**
A: Use JOBDIR for persistence, reduce CONCURRENT_REQUESTS, implement batch processing

### Getting Help

1. Check `setup_instructions.md` for detailed guidance
2. Review `CLAUDE.md` for Scrapy-specific conventions
3. Ask Claude Code directly - agents will help!
4. Use `/shell` to debug selector issues
5. Check Scrapy logs in `logs/` directory
6. Refer to Scrapy documentation

## Contributing

To improve this template:

1. Test changes thoroughly with real websites
2. Update documentation
3. Maintain consistency with Scrapy best practices
4. Ensure all agents and commands work correctly
5. Respect ethical scraping principles

## License

[Your chosen license]

---

**Ready to build powerful web scrapers with AI assistance? Start scraping responsibly!**

For detailed setup instructions, see [setup_instructions.md](setup_instructions.md).

For Scrapy conventions and patterns, see [CLAUDE.md](CLAUDE.md).

---

## Important Legal Notice

**Web scraping must be done ethically and legally:**

- Always review and respect website Terms of Service
- Respect robots.txt directives
- Use appropriate rate limiting
- Identify your bot with accurate User-Agent
- Comply with data privacy laws (GDPR, CCPA, etc.)
- Only scrape publicly available data
- Don't bypass authentication or paywalls
- Don't cause server disruption

This template provides tools for web scraping. Users are solely responsible for ensuring their use complies with applicable laws and website policies.
