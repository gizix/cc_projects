# Scrapy Project - Claude Code Configuration

## Project Type
Scrapy web scraping framework (Python-based)

## Scrapy Version
This template is configured for Scrapy 2.11+ (latest stable)

## Project Overview

Scrapy is a fast, high-level web crawling and web scraping framework. It's used to extract structured data from websites through spiders that crawl pages and parse content. This template includes:

- **Scrapy Core**: Full-featured web scraping with async/await support
- **Playwright Integration**: JavaScript rendering for dynamic websites
- **Database Support**: PostgreSQL (SQLAlchemy) and MongoDB (PyMongo)
- **Caching**: Redis for distributed deduplication
- **Data Export**: JSON, CSV, and database storage
- **Best Practices**: Rate limiting, robots.txt compliance, user agent rotation

## Project Structure and Architecture

### Standard Scrapy Project Structure
```
scrapy-template/
├── scrapy.cfg                    # Deploy configuration file
├── pyproject.toml               # Python dependencies and tool configuration
├── pytest.ini                   # Test configuration
├── docker-compose.yml           # PostgreSQL, MongoDB, Redis containers
├── Dockerfile                   # Docker image for scrapers
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore patterns
├── .pre-commit-config.yaml      # Code quality hooks
├── myproject/                   # Scrapy project directory
│   ├── __init__.py
│   ├── settings.py             # Scrapy settings and configuration
│   ├── items.py                # Data models (dataclasses)
│   ├── loaders.py              # Item loaders for data cleaning
│   ├── pipelines.py            # Item processing pipelines
│   ├── middlewares.py          # Spider and downloader middlewares
│   ├── spiders/                # Spider implementations
│   │   ├── __init__.py
│   │   └── example_spider.py  # Example spider
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── database.py         # Database helpers
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_spiders.py
│   ├── test_pipelines.py
│   └── fixtures/               # Test data
├── data/                        # Scraped data output
│   ├── json/
│   └── csv/
└── logs/                        # Log files
```

## Key Technologies

### Core Framework
- **Scrapy 2.11+**: Async web scraping framework with Twisted
- **Python 3.9+**: Modern Python with type hints
- **Playwright**: Headless browser for JavaScript-heavy sites
- **Twisted**: Async networking engine

### Data Processing
- **ItemLoaders**: Field processors and data cleaning
- **w3lib**: Web scraping utilities
- **python-dateutil**: Date parsing

### Databases
- **PostgreSQL + SQLAlchemy**: Relational data storage
- **MongoDB + PyMongo**: Document storage for unstructured data
- **Redis**: Distributed deduplication and caching

### Development Tools
- **pytest**: Testing framework
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting
- **pre-commit**: Git hooks

## Development Setup

### Prerequisites
```bash
# Python 3.9 or higher
python --version

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Install Playwright browsers (for JavaScript rendering)
playwright install chromium
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:

```bash
# Project
SCRAPY_PROJECT=myproject

# Spider settings
CONCURRENT_REQUESTS=16
DOWNLOAD_DELAY=1.0
ROBOTSTXT_OBEY=true

# AutoThrottle
AUTOTHROTTLE_ENABLED=true

# Playwright
PLAYWRIGHT_BROWSER=chromium
PLAYWRIGHT_HEADLESS=true

# Databases
DATABASE_URL=postgresql://scrapy:changeme@localhost:5432/scrapy
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=scrapy

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Logging
LOG_LEVEL=INFO
```

### Start Development Services
```bash
# Start PostgreSQL, MongoDB, Redis
docker-compose up -d

# Verify services
docker-compose ps
```

## Common Scrapy Commands

### Spider Management
- `scrapy list` - List all available spiders
- `scrapy crawl spider_name` - Run a spider
- `scrapy crawl spider_name -o output.json` - Run and save to file
- `scrapy crawl spider_name -a arg1=value1` - Pass arguments to spider
- `scrapy genspider spider_name example.com` - Generate new spider

### Development and Debugging
- `scrapy shell "http://example.com"` - Interactive shell for testing selectors
- `scrapy parse --spider=spider_name url` - Test spider on a URL
- `scrapy check spider_name` - Run spider contracts/tests
- `scrapy view url` - Download and open URL in browser (as Scrapy sees it)
- `scrapy fetch url` - Fetch a URL and print response

### Project Management
- `scrapy startproject project_name` - Create new project (already done)
- `scrapy version` - Show Scrapy version
- `scrapy bench` - Run benchmark test

### Data Export
```bash
# Export to JSON
scrapy crawl spider_name -o data.json

# Export to CSV
scrapy crawl spider_name -o data.csv

# Export to JSON Lines
scrapy crawl spider_name -o data.jsonl

# Export to XML
scrapy crawl spider_name -o data.xml

# Custom feed settings (use FEEDS in settings.py)
```

## Code Style and Conventions

### Python/Scrapy Style
- Follow **PEP 8** for Python code style
- Use **4 spaces** for indentation
- **Maximum line length: 100 characters** (configured in Black)
- Use **type hints** for function parameters and return values
- Write **docstrings** for all spiders, pipelines, and public functions
- Use descriptive variable names in **snake_case**
- Class names in **PascalCase**
- Constants in **UPPER_SNAKE_CASE**

### Item Definitions (Dataclasses)
Modern approach using Python dataclasses with type hints:

```python
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Product:
    """Product item for e-commerce scraping."""

    # Required fields
    name: str
    price: float
    url: str

    # Optional fields with defaults
    description: Optional[str] = None
    currency: str = "USD"
    stock: int = 0
    rating: float = 0.0
    images: List[str] = field(default_factory=list)

    # Metadata
    scraped_at: datetime = field(default_factory=datetime.now)
```

**Conventions**:
- Use descriptive, singular names: `Product`, `Article`, `Review`
- Required fields first, optional fields with defaults after
- Always include `scraped_at` timestamp
- Use `Optional[Type]` for nullable fields
- Use `field(default_factory=list)` for mutable defaults
- Include docstring describing the item's purpose

### Spider Conventions
Spiders are the core of Scrapy - they define how to crawl and extract data.

**Basic Spider Pattern**:
```python
import scrapy
from typing import Generator, Any
from myproject.items import Product


class ExampleSpider(scrapy.Spider):
    """Spider for scraping products from example.com."""

    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/products"]

    # Spider settings (override project settings)
    custom_settings = {
        "DOWNLOAD_DELAY": 2.0,
        "CONCURRENT_REQUESTS": 8,
    }

    def parse(self, response: scrapy.http.Response) -> Generator[Any, None, None]:
        """Parse main listing page and follow pagination."""
        # Extract product URLs
        for product_url in response.css("a.product-link::attr(href)").getall():
            yield response.follow(product_url, callback=self.parse_product)

        # Follow pagination
        next_page = response.css("a.next-page::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response: scrapy.http.Response) -> Product:
        """Parse individual product page."""
        return Product(
            name=response.css("h1.product-name::text").get(),
            price=float(response.css("span.price::text").re_first(r"[\d.]+") or 0),
            url=response.url,
            description=response.css("div.description::text").get(),
            images=response.css("img.product-image::attr(src)").getall(),
        )
```

**Spider Best Practices**:
- Always include docstring explaining what the spider scrapes
- Use descriptive spider name (lowercase, hyphens for multi-word)
- Set `allowed_domains` to prevent accidental crawling
- Use `custom_settings` for spider-specific configuration
- Type hint `response` and return values
- Use CSS selectors (`.css()`) or XPath (`.xpath()`)
- Use `response.follow()` for relative URLs
- Implement `parse_*` methods for different page types
- Handle missing data gracefully with `.get()` and defaults
- Log important events with `self.logger.info()`, `.warning()`, `.error()`

### Item Loaders
ItemLoaders provide a convenient way to populate items with input/output processors:

```python
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags


class ProductLoader(ItemLoader):
    """Loader for Product items with field processors."""

    default_output_processor = TakeFirst()

    # Clean name: remove tags, strip whitespace
    name_in = MapCompose(remove_tags, str.strip)

    # Parse price: extract digits, convert to float
    price_in = MapCompose(lambda x: x.replace(",", ""), float)
    price_out = TakeFirst()

    # Join description paragraphs
    description_in = MapCompose(remove_tags, str.strip)
    description_out = Join("\n")

    # Collect all images (no TakeFirst)
    images_out = lambda x: x  # Return all values
```

**Usage in Spider**:
```python
from myproject.loaders import ProductLoader

def parse_product(self, response):
    loader = ProductLoader(item=Product(), response=response)
    loader.add_css("name", "h1.product-name")
    loader.add_css("price", "span.price")
    loader.add_css("description", "div.description p")
    loader.add_css("images", "img.product-image::attr(src)")
    loader.add_value("url", response.url)
    return loader.load_item()
```

### Pipeline Conventions
Pipelines process items after spiders yield them. Common pipeline order:

1. **Validation Pipeline** (100): Validate required fields
2. **Data Cleaning Pipeline** (200): Clean and normalize data
3. **Duplicate Filter Pipeline** (300): Remove duplicates
4. **Database Pipeline** (400): Store in database
5. **Export Pipeline** (500): Export to files

**Pipeline Pattern**:
```python
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ValidationPipeline:
    """Validate items have required fields."""

    required_fields = ["name", "url"]

    def process_item(self, item, spider):
        """Validate item or drop it."""
        adapter = ItemAdapter(item)

        for field in self.required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field}")

        return item
```

**Pipeline Best Practices**:
- Use low numbers (100-900) for priority
- Return `item` to pass to next pipeline
- Raise `DropItem` to stop processing and discard item
- Use `open_spider()` and `close_spider()` for setup/teardown
- Use `ItemAdapter` for item access (works with dicts and dataclasses)
- Log dropped items with reason
- Handle database connections in lifecycle methods

### Middleware Conventions
Middlewares intercept requests and responses:

**Downloader Middleware**:
```python
class CustomHeadersMiddleware:
    """Add custom headers to all requests."""

    def process_request(self, request, spider):
        """Add headers before request is sent."""
        request.headers["X-Custom-Header"] = "value"
        return None  # Continue processing

    def process_response(self, request, response, spider):
        """Process response before returning to spider."""
        return response  # Return response to continue
```

**Spider Middleware**:
```python
class ErrorHandlingMiddleware:
    """Handle spider errors gracefully."""

    def process_spider_exception(self, response, exception, spider):
        """Handle exceptions raised by spider."""
        spider.logger.error(f"Spider error: {exception}")
        return []  # Return empty list to continue
```

## Scrapy Best Practices

### 1. Respect robots.txt and Rate Limiting

**Always check robots.txt**:
```python
# settings.py
ROBOTSTXT_OBEY = True  # Respect site rules
```

**Configure rate limiting**:
```python
# Polite crawling
DOWNLOAD_DELAY = 2.0  # Seconds between requests
CONCURRENT_REQUESTS_PER_DOMAIN = 8  # Max concurrent per domain
RANDOMIZE_DOWNLOAD_DELAY = True  # Add randomness

# AutoThrottle (dynamic adjustment)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
```

### 2. Use Item Loaders for Data Cleaning

Instead of manual cleaning in spiders, use ItemLoaders:

```python
# Bad: Manual cleaning in spider
def parse(self, response):
    name = response.css("h1::text").get()
    name = name.strip() if name else ""
    price = response.css("span.price::text").get()
    price = float(price.replace("$", "").replace(",", "")) if price else 0

# Good: ItemLoader handles cleaning
def parse(self, response):
    loader = ProductLoader(item=Product(), response=response)
    loader.add_css("name", "h1")
    loader.add_css("price", "span.price")
    return loader.load_item()
```

### 3. Pipeline Ordering and Responsibilities

**Correct pipeline order**:
```python
ITEM_PIPELINES = {
    "myproject.pipelines.ValidationPipeline": 100,      # Validate first
    "myproject.pipelines.CleaningPipeline": 200,        # Clean data
    "myproject.pipelines.DuplicateFilterPipeline": 300, # Filter duplicates
    "myproject.pipelines.DatabasePipeline": 400,        # Store in DB
    "myproject.pipelines.FileExportPipeline": 500,      # Export to files
}
```

**Pipeline responsibilities**:
- **Validation**: Check required fields, data types, ranges
- **Cleaning**: Normalize, format, convert data
- **Duplicate Filtering**: Check if item already exists (Redis/DB)
- **Storage**: Save to database, file, API
- **Notification**: Send alerts, update dashboards

### 4. Error Handling and Retry Logic

**Handle errors gracefully**:
```python
class RobustSpider(scrapy.Spider):
    name = "robust"

    def parse(self, response):
        try:
            # Parse with specific error handling
            product = self.parse_product(response)
            yield product
        except Exception as e:
            self.logger.error(f"Parse error for {response.url}: {e}")
            # Optionally yield an error item or skip
```

**Configure retries**:
```python
# settings.py
RETRY_ENABLED = True
RETRY_TIMES = 3  # Retry failed requests 3 times
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]
```

### 5. Logging Best Practices

**Use appropriate log levels**:
```python
class MySpider(scrapy.Spider):
    name = "myspider"

    def parse(self, response):
        # Debug: Detailed information
        self.logger.debug(f"Processing {response.url}")

        # Info: General progress
        self.logger.info(f"Found {len(products)} products")

        # Warning: Unexpected but recoverable
        self.logger.warning(f"Missing price for {product_name}")

        # Error: Significant problems
        self.logger.error(f"Failed to parse {response.url}: {error}")
```

**Configure logging**:
```python
# settings.py
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "logs/scrapy.log"
LOG_ENCODING = "utf-8"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
```

### 6. Use Spider Arguments

Make spiders flexible with command-line arguments:

```python
class FlexibleSpider(scrapy.Spider):
    name = "flexible"

    def __init__(self, category=None, max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category
        self.max_pages = int(max_pages)
        self.start_urls = [f"https://example.com/{category}"]
```

**Run with arguments**:
```bash
scrapy crawl flexible -a category=electronics -a max_pages=5
```

### 7. Use Scrapy Shell for Development

Test selectors interactively:

```bash
# Open shell with URL
scrapy shell "https://example.com/product/123"

# Test CSS selectors
>>> response.css("h1.title::text").get()
'Product Name'

# Test XPath
>>> response.xpath("//h1[@class='title']/text()").get()
'Product Name'

# View response
>>> view(response)  # Opens in browser
```

## Testing Strategy

### Test Structure
- **Unit tests**: Test individual functions and methods
- **Spider tests**: Test spider parsing logic
- **Pipeline tests**: Test item processing
- **Integration tests**: Test full scraping flow
- **Contract tests**: Use Scrapy contracts for inline tests

### Spider Contracts
Inline tests for spiders using contracts:

```python
class MySpider(scrapy.Spider):
    name = "myspider"

    def parse(self, response):
        """Parse listing page.

        @url http://example.com/products
        @returns items 10 20
        @returns requests 1 10
        @scrapes name price url
        """
        # Spider implementation
```

**Run contracts**:
```bash
scrapy check myspider
```

### Unit Tests with pytest

**Test spider parsing**:
```python
import pytest
from scrapy.http import HtmlResponse
from myproject.spiders.example import ExampleSpider


def test_parse_product():
    """Test product parsing."""
    spider = ExampleSpider()

    # Create fake response
    html = """
    <html>
        <h1 class="product-name">Test Product</h1>
        <span class="price">$99.99</span>
    </html>
    """
    response = HtmlResponse(
        url="http://example.com/product/1",
        body=html.encode("utf-8")
    )

    # Test parsing
    result = spider.parse_product(response)
    assert result.name == "Test Product"
    assert result.price == 99.99
```

**Test pipeline**:
```python
from myproject.pipelines import ValidationPipeline
from myproject.items import Product
from scrapy.exceptions import DropItem


def test_validation_pipeline():
    """Test validation pipeline."""
    pipeline = ValidationPipeline()

    # Valid item
    valid_item = Product(name="Test", price=99.99, url="http://example.com")
    result = pipeline.process_item(valid_item, None)
    assert result == valid_item

    # Invalid item (missing name)
    invalid_item = Product(name="", price=99.99, url="http://example.com")
    with pytest.raises(DropItem):
        pipeline.process_item(invalid_item, None)
```

### Test Coverage

```bash
# Run tests with coverage
pytest --cov=myproject --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

## Database Integration

### PostgreSQL with SQLAlchemy

**Define models** (`utils/database.py`):
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    url = Column(String, unique=True, nullable=False)
    description = Column(String)
    scraped_at = Column(DateTime, default=datetime.now)
```

**Pipeline for PostgreSQL**:
```python
from sqlalchemy.orm import sessionmaker
from myproject.utils.database import ProductModel, engine


class PostgreSQLPipeline:
    """Store items in PostgreSQL."""

    def open_spider(self, spider):
        """Create database session."""
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def close_spider(self, spider):
        """Close database session."""
        self.session.close()

    def process_item(self, item, spider):
        """Save item to database."""
        product = ProductModel(
            name=item.name,
            price=item.price,
            url=item.url,
            description=item.description,
            scraped_at=item.scraped_at,
        )
        self.session.add(product)
        self.session.commit()
        return item
```

### MongoDB with PyMongo

**Pipeline for MongoDB**:
```python
from pymongo import MongoClient
from itemadapter import ItemAdapter
from dataclasses import asdict


class MongoDBPipeline:
    """Store items in MongoDB."""

    def open_spider(self, spider):
        """Connect to MongoDB."""
        self.client = MongoClient(spider.settings.get("MONGO_URI"))
        self.db = self.client[spider.settings.get("MONGO_DATABASE")]

    def close_spider(self, spider):
        """Close MongoDB connection."""
        self.client.close()

    def process_item(self, item, spider):
        """Save item to MongoDB."""
        collection = self.db[spider.name]
        item_dict = asdict(item) if hasattr(item, "__dataclass_fields__") else dict(item)
        collection.insert_one(item_dict)
        return item
```

## Playwright Integration

For JavaScript-heavy websites that require browser rendering:

**Enable Playwright in spider**:
```python
import scrapy


class JavaScriptSpider(scrapy.Spider):
    """Spider for JavaScript-rendered pages."""

    name = "javascript_spider"

    def start_requests(self):
        """Send requests with Playwright."""
        yield scrapy.Request(
            url="https://example.com/js-page",
            meta={
                "playwright": True,
                "playwright_page_goto_kwargs": {
                    "wait_until": "networkidle",
                },
            }
        )

    def parse(self, response):
        """Parse JavaScript-rendered page."""
        # Page is fully rendered, extract data normally
        title = response.css("h1::text").get()
        yield {"title": title}
```

**Advanced Playwright usage**:
```python
def start_requests(self):
    yield scrapy.Request(
        url="https://example.com",
        meta={
            "playwright": True,
            "playwright_page_goto_kwargs": {
                "wait_until": "networkidle",
                "timeout": 30000,
            },
            "playwright_page_methods": [
                # Click button
                ("click", "button.load-more"),
                # Wait for selector
                ("wait_for_selector", "div.content"),
                # Take screenshot
                ("screenshot", {"path": "page.png"}),
            ],
        }
    )
```

## Security and Ethics

### Legal Considerations

**Before scraping, consider**:
1. **Terms of Service**: Review website's ToS for scraping policies
2. **robots.txt**: Always respect robots.txt (use `ROBOTSTXT_OBEY = True`)
3. **Copyright**: Respect intellectual property rights
4. **Personal Data**: Comply with GDPR, CCPA, and other privacy laws
5. **Rate Limits**: Don't overload servers or cause disruption

**Best practices**:
- Scrape publicly available data only
- Don't scrape personal information without consent
- Don't bypass authentication or paywalls
- Don't redistribute scraped content commercially without permission
- Identify your bot with accurate User-Agent

### User Agent Identification

**Use descriptive User-Agent**:
```python
# settings.py
USER_AGENT = "MyCompanyBot/1.0 (+https://mycompany.com/bot)"
```

**Rotate user agents** (for legitimate use cases):
```python
# Already configured in template
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
}
```

### Proxy Usage Guidelines

**When to use proxies**:
- Geographic restrictions (with permission)
- Avoid IP bans from legitimate use
- Distribute load across IPs

**When NOT to use proxies**:
- To bypass rate limits maliciously
- To hide identity for unauthorized scraping
- To scrape private/protected content

**Configure proxies**:
```python
# Install: pip install scrapy-rotating-proxies
DOWNLOADER_MIDDLEWARES = {
    "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
    "rotating_proxies.middlewares.BanDetectionMiddleware": 620,
}

ROTATING_PROXY_LIST = [
    "http://proxy1.com:8000",
    "http://proxy2.com:8000",
]
```

### Data Privacy and Storage

**Secure storage**:
- Encrypt sensitive data at rest
- Use secure connections (HTTPS, SSL/TLS) for databases
- Implement access controls and authentication
- Regularly delete or anonymize old data
- Follow data retention policies

**Environment variables for secrets**:
```bash
# .env (never commit!)
DATABASE_URL=postgresql://user:password@host:5432/db
MONGO_URI=mongodb://user:password@host:27017/
API_KEY=your-secret-api-key
```

## Deployment

### Docker Deployment

**Build image**:
```bash
docker build -t myproject-scraper .
```

**Run spider in container**:
```bash
docker run --env-file .env myproject-scraper scrapy crawl spider_name
```

**Docker Compose (with services)**:
```bash
# Start all services
docker-compose up -d

# Run spider
docker-compose run scraper scrapy crawl spider_name

# View logs
docker-compose logs -f scraper
```

### Scrapyd (Distributed Scraping)

**Install Scrapyd**:
```bash
pip install scrapyd scrapyd-client
```

**Deploy project**:
```bash
scrapyd-deploy production -p myproject
```

**Schedule spider**:
```bash
curl http://localhost:6800/schedule.json \
    -d project=myproject \
    -d spider=spider_name
```

### Cron Scheduling

**Add to crontab**:
```bash
# Edit crontab
crontab -e

# Run spider daily at 2 AM
0 2 * * * cd /path/to/project && /path/to/venv/bin/scrapy crawl spider_name

# Run spider every 6 hours
0 */6 * * * cd /path/to/project && /path/to/venv/bin/scrapy crawl spider_name
```

## Available Commands

This template includes custom slash commands for common operations. See `.claude/commands/` for:

- `/spider-create` - Create a new spider
- `/spider-run` - Run a spider with options
- `/spider-test` - Test spider in Scrapy shell
- `/item-create` - Create new item model
- `/pipeline-create` - Create new pipeline
- `/middleware-create` - Create new middleware
- `/deploy` - Deploy to production
- `/test` - Run test suite
- `/lint` - Run code quality checks

Use `/help` to see all available commands.

## Development Workflow

### 1. Create Spider

```bash
# Generate spider template
scrapy genspider product_spider example.com

# Or use custom command
/spider-create product_spider example.com
```

### 2. Test Locally

```bash
# Test in Scrapy shell
scrapy shell "https://example.com/products"

# Test selector extraction
>>> response.css("h1.product-name::text").get()

# Run spider with output
scrapy crawl product_spider -o test_output.json
```

### 3. Implement Spider Logic

- Define start URLs
- Implement parse methods
- Extract data with CSS/XPath selectors
- Follow pagination and links
- Handle errors and edge cases

### 4. Add Item Loaders (Optional)

Create item loader for data cleaning:

```python
# myproject/loaders.py
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose

class ProductLoader(ItemLoader):
    default_output_processor = TakeFirst()

    price_in = MapCompose(lambda x: float(x.replace("$", "")))
```

### 5. Configure Pipelines

Enable pipelines in settings.py:

```python
ITEM_PIPELINES = {
    "myproject.pipelines.ValidationPipeline": 100,
    "myproject.pipelines.DatabasePipeline": 300,
}
```

### 6. Run with Data Export

```bash
# Export to JSON
scrapy crawl product_spider -o data/products.json

# Export to CSV
scrapy crawl product_spider -o data/products.csv

# Export to database (configured in pipeline)
scrapy crawl product_spider
```

### 7. Monitor and Debug

```bash
# Check logs
tail -f logs/scrapy.log

# Run with debug logging
scrapy crawl product_spider -L DEBUG

# Check spider contracts
scrapy check product_spider
```

### 8. Test and Validate

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=myproject

# Lint code
flake8 myproject/
black myproject/
isort myproject/
```

### 9. Deploy

```bash
# Docker deployment
docker-compose up -d
docker-compose run scraper scrapy crawl product_spider

# Scrapyd deployment
scrapyd-deploy production
curl http://localhost:6800/schedule.json -d project=myproject -d spider=product_spider

# Cron scheduling
crontab -e
```

## Documentation Links

### Official Scrapy Documentation
- Scrapy Documentation: https://docs.scrapy.org/
- Scrapy Tutorial: https://docs.scrapy.org/en/latest/intro/tutorial.html
- Selectors: https://docs.scrapy.org/en/latest/topics/selectors.html
- Item Pipeline: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
- Spider Middlewares: https://docs.scrapy.org/en/latest/topics/spider-middleware.html
- Settings: https://docs.scrapy.org/en/latest/topics/settings.html

### Extensions and Tools
- Scrapy-Playwright: https://github.com/scrapy-plugins/scrapy-playwright
- ItemLoaders: https://itemloaders.readthedocs.io/
- Scrapyd: https://scrapyd.readthedocs.io/

### Python Resources
- PEP 8 Style Guide: https://pep8.org/
- Python Type Hints: https://docs.python.org/3/library/typing.html
- dataclasses: https://docs.python.org/3/library/dataclasses.html

### Legal and Ethical Scraping
- robots.txt Specification: https://www.robotstxt.org/
- Web Scraping Best Practices: https://www.scraperapi.com/blog/web-scraping-best-practices/
- GDPR Guidelines: https://gdpr.eu/

---

**Remember**: Web scraping should be done ethically and legally. Always respect website terms of service, robots.txt, rate limits, and privacy laws. Scrapy provides powerful tools - use them responsibly.
