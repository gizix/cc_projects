# Scrapy Template Setup Instructions

This guide will help you set up a new Scrapy project using this template.

## Prerequisites

- **Python 3.9 or higher** - Modern Python with type hints support
- **pip** - Python package installer (included with Python)
- **Git** - Version control
- **Docker** - For PostgreSQL, MongoDB, and Redis (optional but recommended)
- **VSCode with Claude Code extension** - For AI-assisted development

### Check Prerequisites

```bash
# Check Python version (should be 3.9+)
python --version

# Check pip
pip --version

# Check Docker (optional)
docker --version
docker-compose --version

# Check Git
git --version
```

## Quick Start

### 1. Set Up Python Virtual Environment

```bash
# Navigate to the template directory
cd scrapy-template

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify activation (should show venv path)
which python  # macOS/Linux
where python  # Windows
```

### 2. Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install project with development dependencies
pip install -e ".[dev]"

# This installs:
# - Scrapy 2.11+ (web scraping framework)
# - scrapy-playwright (JavaScript rendering)
# - SQLAlchemy + psycopg2 (PostgreSQL)
# - PyMongo (MongoDB)
# - redis-py (Redis cache)
# - pytest (testing framework)
# - Black, isort, flake8, mypy (code quality)
# - And more development tools
```

### 3. Install Playwright Browsers

Playwright is needed for scraping JavaScript-heavy websites:

```bash
# Install Chromium browser for Playwright
playwright install chromium

# Optional: Install all browsers (Firefox, WebKit)
playwright install

# Verify installation
playwright --version
```

**Note**: This downloads browser binaries (~300MB for Chromium). Skip this step if you don't need JavaScript rendering.

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# On Windows:
copy .env.example .env

# Edit .env file with your settings
# Use your favorite text editor or:
code .env  # VSCode
nano .env  # Terminal editor
```

**Key environment variables to configure**:

```bash
# Project name
SCRAPY_PROJECT=myproject

# Spider settings
CONCURRENT_REQUESTS=16
DOWNLOAD_DELAY=1.0
ROBOTSTXT_OBEY=true

# AutoThrottle (recommended)
AUTOTHROTTLE_ENABLED=true
AUTOTHROTTLE_START_DELAY=1
AUTOTHROTTLE_MAX_DELAY=10

# Playwright (for JavaScript rendering)
PLAYWRIGHT_BROWSER=chromium
PLAYWRIGHT_HEADLESS=true

# PostgreSQL database
DATABASE_URL=postgresql://scrapy:changeme@localhost:5432/scrapy

# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=scrapy

# Redis (for deduplication)
REDIS_HOST=localhost
REDIS_PORT=6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/scrapy.log
```

### 5. Start Development Services with Docker

**Option A: Using Docker Compose (Recommended)**

```bash
# Start PostgreSQL, MongoDB, and Redis
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# NAME                  STATUS
# scrapy-postgres       Up
# scrapy-mongodb        Up
# scrapy-redis          Up

# View logs if needed
docker-compose logs -f

# Stop services when done
docker-compose down
```

**Option B: Manual Installation**

If you prefer not to use Docker, install services manually:

**PostgreSQL**:
- Download: https://www.postgresql.org/download/
- Create database: `createdb scrapy`
- Update DATABASE_URL in .env

**MongoDB**:
- Download: https://www.mongodb.com/try/download/community
- Start service: `mongod`
- Update MONGO_URI in .env

**Redis**:
- Download: https://redis.io/download
- Start service: `redis-server`
- Update REDIS_HOST in .env

### 6. Initialize Database Schema (PostgreSQL)

```bash
# Run Python to create tables
python -c "from myproject.utils.database import init_db; init_db()"

# Or create a script: scripts/init_db.py
# Then run: python scripts/init_db.py
```

### 7. Verify Installation

```bash
# Check Scrapy is installed
scrapy version

# List available spiders (should show example_spider)
scrapy list

# Run example spider (dry run)
scrapy check example_spider

# Test Scrapy shell
scrapy shell "https://quotes.toscrape.com"
# In shell, test selector:
>>> response.css('span.text::text').get()
>>> exit()
```

### 8. Run Your First Spider

```bash
# Run the example spider with JSON output
scrapy crawl example_spider -o data/example.json

# Check the output file
cat data/example.json  # macOS/Linux
type data\example.json  # Windows

# Run with detailed logging
scrapy crawl example_spider -o data/example.json -s LOG_LEVEL=DEBUG

# Run with limited pages (for testing)
scrapy crawl example_spider -o data/example.json -s CLOSESPIDER_PAGECOUNT=10
```

### 9. Open in VSCode with Claude Code

```bash
# Open project in VSCode
code .

# In VSCode:
# 1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
# 2. Type "Claude Code" and select "Launch Claude Code"
# 3. Start using slash commands and AI agents!
```

## Using Claude Code Features

This template includes pre-configured Claude Code features:

### Slash Commands

Available commands (use in Claude Code):

```bash
# List all available spiders
/list-spiders

# Create a new spider
/create-spider product_spider basic

# Test selectors in interactive shell
/shell https://example.com/products

# Run a spider with output
/run-spider example_spider -o data.json

# Test spider contracts
/test-spider example_spider

# Validate scraped data
/validate-items data/example.json

# Check robots.txt compliance
/check-robots example.com

# Benchmark spider performance
/benchmark example_spider

# Export data to database
/export-data data.json --to postgres

# Deploy spider to production
/deploy example_spider --target production
```

### Specialized Agents

Agents automatically activate based on context:

- **spider-dev**: Assists with spider creation and selector optimization
- **security-advisor**: Reviews scraping ethics and compliance
- **performance-tuner**: Optimizes spider settings and performance
- **pipeline-expert**: Designs data processing pipelines
- **testing-assistant**: Generates comprehensive tests
- **deployment-helper**: Sets up production deployments

**Explicit invocation**:
```
"Use the spider-dev agent to create a product spider"
"Use the security-advisor agent to review my scraping approach"
"Use the pipeline-expert agent to store data in PostgreSQL"
```

### Automated Skills

Skills automatically activate for common patterns:

- **spider-generator**: Creates spiders from templates
- **data-pipeline**: Implements data processing workflows
- **docker-deploy**: Sets up containerized deployments
- **test-coverage**: Generates comprehensive test suites

## Project Structure

After setup, your project should look like:

```
scrapy-template/
├── venv/                          # Virtual environment (not committed)
├── myproject/                     # Scrapy project directory
│   ├── spiders/                   # Your spiders go here
│   │   ├── __init__.py
│   │   └── example_spider.py     # Example spider
│   ├── items.py                   # Data models (dataclasses)
│   ├── pipelines.py              # Item processing pipelines
│   ├── middlewares.py            # Spider/downloader middlewares
│   ├── loaders.py                # Item loaders for cleaning
│   ├── settings.py               # Scrapy configuration
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── database.py           # Database helpers
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_spiders.py
│   ├── test_pipelines.py
│   └── fixtures/                 # Test data
├── data/                          # Scraped data output
│   ├── json/
│   └── csv/
├── logs/                          # Log files
│   └── scrapy.log
├── .claude/                       # Claude Code configuration
│   ├── commands/                  # 10 slash commands
│   ├── agents/                    # 6 specialized agents
│   ├── skills/                    # 4 automated skills
│   └── settings.json              # Claude Code settings
├── .env                          # Environment variables (not committed)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore patterns
├── .pre-commit-config.yaml       # Code quality hooks
├── docker-compose.yml            # Development services
├── Dockerfile                    # Docker image for scrapers
├── pyproject.toml               # Python dependencies
├── pytest.ini                   # Test configuration
├── scrapy.cfg                   # Scrapy deploy configuration
├── CLAUDE.md                    # Project context for Claude
├── README.md                    # Project documentation
└── setup_instructions.md        # This file
```

## Development Workflow

### Creating Your First Spider

**Step 1: Use Claude Code to generate spider**

```
Ask Claude: "Create a spider to scrape products from example.com"
```

Or use the command:
```
/create-spider product_spider basic
```

**Step 2: Test selectors in shell**

```bash
# Open shell with target URL
scrapy shell "https://example.com/products"

# Test CSS selectors
>>> response.css('div.product h2.title::text').get()
>>> response.css('span.price::text').getall()

# Test XPath selectors
>>> response.xpath('//div[@class="product"]//h2/text()').get()

# View response in browser
>>> view(response)

# Exit shell
>>> exit()
```

Or use Claude Code:
```
/shell https://example.com/products
```

**Step 3: Implement spider parsing logic**

Edit `myproject/spiders/product_spider.py`:

```python
import scrapy
from typing import Iterator


class ProductSpider(scrapy.Spider):
    """Spider for scraping products from example.com."""

    name = "product_spider"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/products"]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
    }

    def parse(self, response) -> Iterator[dict]:
        """Parse product listing page."""
        for product in response.css('div.product'):
            yield {
                'name': product.css('h2.title::text').get(),
                'price': product.css('span.price::text').get(),
                'url': response.urljoin(product.css('a::attr(href)').get()),
            }

        # Follow pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

**Step 4: Run the spider**

```bash
# Run with JSON output
scrapy crawl product_spider -o data/products.json

# Run with CSV output
scrapy crawl product_spider -o data/products.csv

# Run with debug logging
scrapy crawl product_spider -o data/products.json -s LOG_LEVEL=DEBUG
```

Or use Claude Code:
```
/run-spider product_spider -o data/products.json
```

**Step 5: Validate scraped data**

```bash
# Check the output
cat data/products.json

# Validate data quality
python -c "import json; data = json.load(open('data/products.json')); print(f'Scraped {len(data)} products')"
```

Or use Claude Code:
```
/validate-items data/products.json
```

### Creating Data Processing Pipelines

**Step 1: Ask Claude to create pipeline**

```
Ask Claude: "Create a pipeline to store products in PostgreSQL with duplicate detection"
```

**Step 2: Review generated pipeline**

Check `myproject/pipelines.py` for the new pipeline.

**Step 3: Enable pipeline in settings**

Edit `myproject/settings.py`:

```python
ITEM_PIPELINES = {
    'myproject.pipelines.ValidationPipeline': 100,
    'myproject.pipelines.DuplicateFilterPipeline': 200,
    'myproject.pipelines.PostgreSQLPipeline': 300,
}
```

**Step 4: Test pipeline**

```bash
# Run spider with pipeline enabled
scrapy crawl product_spider

# Check database
docker exec -it scrapy-postgres psql -U scrapy -d scrapy -c "SELECT COUNT(*) FROM products;"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_spiders.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=myproject --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov\index.html  # Windows
xdg-open htmlcov/index.html  # Linux

# Run spider contracts
scrapy check product_spider
```

Or use Claude Code:
```
/test-spider product_spider
```

### Code Quality and Formatting

```bash
# Format code with Black
black myproject/ tests/

# Sort imports
isort myproject/ tests/

# Run linter
flake8 myproject/ tests/

# Type checking
mypy myproject/

# Run all checks
black myproject/ && isort myproject/ && flake8 myproject/ && mypy myproject/

# Install pre-commit hooks (runs checks on git commit)
pre-commit install

# Run pre-commit manually
pre-commit run --all-files
```

### Handling JavaScript-Rendered Pages

**Step 1: Create Playwright spider**

```
Ask Claude: "Create a spider using Playwright to scrape JavaScript-rendered content from example.com"
```

Or use command:
```
/create-spider dynamic_spider playwright
```

**Step 2: Configure Playwright in spider**

```python
import scrapy


class DynamicSpider(scrapy.Spider):
    name = "dynamic_spider"

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
    }

    def start_requests(self):
        yield scrapy.Request(
            url="https://example.com/dynamic",
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    ('wait_for_selector', 'div.content'),
                    ('evaluate', 'window.scrollTo(0, document.body.scrollHeight)'),
                ],
            }
        )

    def parse(self, response):
        # Parse JavaScript-rendered content
        for item in response.css('div.item'):
            yield {
                'title': item.css('h2::text').get(),
                'content': item.css('p::text').get(),
            }
```

**Step 3: Run Playwright spider**

```bash
# Run with Playwright
scrapy crawl dynamic_spider -o data/dynamic.json

# Run with visible browser (for debugging)
scrapy crawl dynamic_spider -o data/dynamic.json -s PLAYWRIGHT_LAUNCH_OPTIONS='{"headless": false}'
```

## Production Deployment

### Docker Deployment

**Step 1: Build Docker image**

```bash
# Build image
docker build -t myproject-scraper:latest .

# Test image locally
docker run --env-file .env myproject-scraper:latest scrapy list
```

**Step 2: Run spider in container**

```bash
# Run spider
docker run --env-file .env myproject-scraper:latest scrapy crawl product_spider -o /data/products.json

# With volume mount for output
docker run -v $(pwd)/data:/data --env-file .env myproject-scraper:latest scrapy crawl product_spider -o /data/products.json
```

**Step 3: Deploy to Docker Hub (optional)**

```bash
# Tag image
docker tag myproject-scraper:latest username/myproject-scraper:latest

# Push to Docker Hub
docker push username/myproject-scraper:latest
```

Or use Claude Code:
```
/deploy product_spider --target docker
```

### Scrapyd Deployment

**Step 1: Install Scrapyd**

```bash
# On server
pip install scrapyd

# Start Scrapyd
scrapyd

# Access at http://localhost:6800
```

**Step 2: Configure deployment**

Edit `scrapy.cfg`:

```ini
[settings]
default = myproject.settings

[deploy:production]
url = http://your-server:6800/
project = myproject
```

**Step 3: Deploy project**

```bash
# Install scrapyd-client
pip install scrapyd-client

# Deploy to Scrapyd
scrapyd-deploy production -p myproject

# Verify deployment
curl http://your-server:6800/listprojects.json
```

**Step 4: Schedule spider**

```bash
# Schedule spider to run
curl http://your-server:6800/schedule.json \
    -d project=myproject \
    -d spider=product_spider

# Check job status
curl http://your-server:6800/listjobs.json?project=myproject
```

Or use Claude Code:
```
/deploy product_spider --target scrapyd --url http://your-server:6800
```

### Cron Job Scheduling

**Step 1: Create run script**

Create `scripts/run_spider.sh`:

```bash
#!/bin/bash

# Activate virtual environment
source /path/to/project/venv/bin/activate

# Change to project directory
cd /path/to/project

# Run spider
scrapy crawl product_spider -o data/products_$(date +%Y%m%d_%H%M%S).json

# Log completion
echo "Spider completed at $(date)" >> logs/cron.log
```

**Step 2: Make script executable**

```bash
chmod +x scripts/run_spider.sh
```

**Step 3: Add to crontab**

```bash
# Edit crontab
crontab -e

# Add cron jobs:

# Run daily at 2 AM
0 2 * * * /path/to/project/scripts/run_spider.sh

# Run every 6 hours
0 */6 * * * /path/to/project/scripts/run_spider.sh

# Run every Monday at 8 AM
0 8 * * 1 /path/to/project/scripts/run_spider.sh
```

## Common Issues and Solutions

### Issue: Import errors for installed packages

**Solution**: Ensure virtual environment is activated

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Verify
which python  # Should show venv path
```

### Issue: Playwright browser not installed

**Solution**: Install Playwright browsers

```bash
playwright install chromium
```

### Issue: Database connection errors

**Solution**:
1. Check Docker services are running: `docker-compose ps`
2. Verify credentials in `.env` file
3. Test connection manually:
   ```bash
   # PostgreSQL
   docker exec -it scrapy-postgres psql -U scrapy -d scrapy

   # MongoDB
   docker exec -it scrapy-mongodb mongo scrapy

   # Redis
   docker exec -it scrapy-redis redis-cli ping
   ```

### Issue: Selectors not extracting data

**Solution**: Test in Scrapy shell

```bash
scrapy shell "https://example.com"
>>> response.css('div.product::text').get()  # Test your selector
>>> view(response)  # View page as Scrapy sees it
```

### Issue: 403 Forbidden errors

**Solution**: Configure proper User-Agent and delays

```python
# In spider custom_settings
custom_settings = {
    'USER_AGENT': 'MyBot/1.0 (+http://www.mysite.com/bot)',
    'DOWNLOAD_DELAY': 2,
    'RANDOMIZE_DOWNLOAD_DELAY': True,
}
```

### Issue: Spider running too slowly

**Solution**: Optimize settings

```python
custom_settings = {
    'CONCURRENT_REQUESTS': 16,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 0.5,
}
```

Or ask Claude:
```
"Use the performance-tuner agent to optimize my spider settings"
```

### Issue: Memory errors on large crawls

**Solution**: Enable job persistence

```bash
# Run with JOBDIR for resumable crawls
scrapy crawl product_spider -s JOBDIR=crawls/product_spider_001

# Resume if interrupted
scrapy crawl product_spider -s JOBDIR=crawls/product_spider_001
```

### Issue: Pre-commit hooks failing

**Solution**: Run formatters manually

```bash
# Format code
black myproject/ tests/
isort myproject/ tests/

# Try commit again
git commit -m "Your message"
```

## Additional Resources

### Documentation
- Scrapy Documentation: https://docs.scrapy.org/
- Scrapy Tutorial: https://docs.scrapy.org/en/latest/intro/tutorial.html
- scrapy-playwright: https://github.com/scrapy-plugins/scrapy-playwright
- Scrapyd Documentation: https://scrapyd.readthedocs.io/

### Community
- Scrapy Google Group: https://groups.google.com/forum/#!forum/scrapy-users
- Stack Overflow: https://stackoverflow.com/questions/tagged/scrapy
- GitHub Issues: https://github.com/scrapy/scrapy/issues

### Learning Resources
- Scrapy at a Glance: https://docs.scrapy.org/en/latest/intro/overview.html
- Common Practices: https://docs.scrapy.org/en/latest/topics/practices.html
- Web Scraping with Python (Book): https://www.oreilly.com/library/view/web-scraping-with/9781491985564/

## Getting Help

1. **Check logs**: Review `logs/scrapy.log` for error messages
2. **Test selectors**: Use `/shell URL` to test selectors interactively
3. **Ask Claude Code**: Use specialized agents for guidance:
   - Spider issues: `"Use spider-dev agent to debug my selector"`
   - Performance: `"Use performance-tuner agent to optimize"`
   - Security: `"Use security-advisor agent to review compliance"`
4. **Review CLAUDE.md**: Check project-specific conventions
5. **Scrapy documentation**: Official docs are comprehensive
6. **Community forums**: Ask in Scrapy Google Group or Stack Overflow

## Next Steps

After completing setup:

1. **Create your first spider**: `/create-spider myspider basic`
2. **Test with Scrapy shell**: `/shell https://your-target-site.com`
3. **Run and iterate**: `/run-spider myspider -o data.json`
4. **Add data pipelines**: Ask Claude to create PostgreSQL pipeline
5. **Write tests**: `/test-spider myspider`
6. **Deploy to production**: `/deploy myspider --target docker`

Happy scraping! Remember to always scrape ethically and legally.
