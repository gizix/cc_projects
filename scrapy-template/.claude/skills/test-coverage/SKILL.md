---
name: test-coverage
description: Generate comprehensive test suites for Scrapy spiders, pipelines, and middlewares when implementing tests or improving coverage. Creates unit tests, integration tests, and contract tests with proper fixtures and mocking.
allowed-tools: Read, Write, Grep
---

You are a Scrapy testing expert. You create comprehensive test suites with proper fixtures, mocking, and coverage strategies following Scrapy and pytest best practices.

## Testing Architecture

### Test Types
```
┌─────────────────────────────────────────┐
│         Scrapy Test Pyramid             │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Integration Tests                │ │
│  │  (Full spider runs)               │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Contract Tests                   │ │
│  │  (Parse methods with @scrapes)   │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Unit Tests                       │ │
│  │  (Individual methods)             │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Testing Setup

### pytest Configuration

**pytest.ini**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    contract: marks contract tests
    spider: marks spider tests
    pipeline: marks pipeline tests
    unit: marks unit tests

# Coverage
addopts =
    --verbose
    --strict-markers
    --cov=myproject
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

# Scrapy settings for tests
SCRAPY_SETTINGS_MODULE = myproject.test_settings
```

### conftest.py (Shared Fixtures)

```python
# tests/conftest.py
import pytest
from pathlib import Path
from scrapy.http import HtmlResponse, Request, TextResponse
from scrapy.settings import Settings


@pytest.fixture
def settings():
    """Provide test Scrapy settings."""
    s = Settings()
    s.update({
        'ITEM_PIPELINES': {},
        'DOWNLOADER_MIDDLEWARES': {},
        'SPIDER_MIDDLEWARES': {},
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'ERROR',
    })
    return s


@pytest.fixture
def response():
    """Create a basic HtmlResponse for testing."""
    def _response(url='http://example.com', body='', **kwargs):
        request = Request(url)
        return HtmlResponse(
            url=url,
            request=request,
            body=body.encode('utf-8') if isinstance(body, str) else body,
            **kwargs
        )
    return _response


@pytest.fixture
def fake_response_from_file():
    """Load response from HTML file."""
    def _response_from_file(filename: str, url: str = 'http://example.com'):
        """
        Load HTML from file and create response.

        Args:
            filename: Path to HTML file in tests/fixtures/
            url: URL for the response

        Returns:
            HtmlResponse object
        """
        file_path = Path(__file__).parent / 'fixtures' / filename
        with open(file_path, 'rb') as f:
            body = f.read()

        request = Request(url)
        return HtmlResponse(
            url=url,
            request=request,
            body=body,
            encoding='utf-8'
        )
    return _response_from_file


@pytest.fixture
def json_response():
    """Create JSON response for API testing."""
    import json

    def _json_response(data: dict, url: str = 'http://api.example.com', status: int = 200):
        request = Request(url)
        return TextResponse(
            url=url,
            request=request,
            body=json.dumps(data).encode('utf-8'),
            status=status,
            headers={'Content-Type': 'application/json'}
        )
    return _json_response


@pytest.fixture
def mock_crawler():
    """Mock Scrapy Crawler for testing."""
    from unittest.mock import Mock
    from scrapy.crawler import Crawler

    crawler = Mock(spec=Crawler)
    crawler.settings = Settings()
    return crawler
```

## Spider Testing

### 1. Basic Spider Unit Tests

```python
# tests/test_spiders.py
import pytest
from scrapy.http import HtmlResponse, Request
from myproject.spiders.product_spider import ProductSpider


class TestProductSpider:
    """Test ProductSpider."""

    @pytest.fixture
    def spider(self):
        """Create spider instance."""
        return ProductSpider()

    def test_spider_initialization(self, spider):
        """Test spider is initialized correctly."""
        assert spider.name == 'product_spider'
        assert 'example.com' in spider.allowed_domains
        assert len(spider.start_urls) > 0

    def test_spider_with_arguments(self):
        """Test spider initialization with arguments."""
        spider = ProductSpider(category='electronics', max_pages=10)
        assert spider.category == 'electronics'
        assert spider.max_pages == 10

    def test_parse_method(self, spider, fake_response_from_file):
        """Test parse method extracts items correctly."""
        response = fake_response_from_file('product_list.html')
        results = list(spider.parse(response))

        # Check we got items
        assert len(results) > 0

        # Check item structure
        items = [r for r in results if not isinstance(r, Request)]
        assert len(items) > 0

        item = items[0]
        assert 'title' in item
        assert 'price' in item
        assert 'url' in item

        # Check item values
        assert item['title'] is not None
        assert item['price'] is not None
        assert item['url'].startswith('http')

    def test_parse_follows_pagination(self, spider, response):
        """Test parse follows pagination links."""
        html = '''
        <html>
            <div class="product">
                <h2 class="title">Product 1</h2>
                <span class="price">$10.99</span>
                <a href="/product/1">View</a>
            </div>
            <a class="next" href="/page/2">Next</a>
        </html>
        '''
        resp = response(body=html, url='http://example.com/page/1')
        results = list(spider.parse(resp))

        # Check for next page request
        requests = [r for r in results if isinstance(r, Request)]
        assert len(requests) > 0

        next_request = requests[0]
        assert '/page/2' in next_request.url

    def test_parse_handles_empty_page(self, spider, response):
        """Test parse handles page with no products."""
        html = '<html><body>No products found</body></html>'
        resp = response(body=html)
        results = list(spider.parse(resp))

        # Should return empty list, not error
        assert results == []

    def test_parse_product_detail(self, spider, fake_response_from_file):
        """Test parsing product detail page."""
        response = fake_response_from_file('product_detail.html')
        item = spider.parse_product(response)

        assert item['title'] is not None
        assert item['price'] > 0
        assert item['description'] is not None
        assert 'sku' in item
        assert len(item.get('images', [])) > 0


class TestAPISpider:
    """Test API spider."""

    @pytest.fixture
    def spider(self):
        from myproject.spiders.api_spider import APISpider
        return APISpider(api_key='test_key')

    def test_api_spider_requires_key(self):
        """Test API spider raises error without key."""
        from myproject.spiders.api_spider import APISpider
        with pytest.raises(ValueError, match="API key required"):
            APISpider()

    def test_parse_api_response(self, spider, json_response):
        """Test parsing API response."""
        data = {
            'results': [
                {'id': 1, 'name': 'Product 1', 'price': 10.99},
                {'id': 2, 'name': 'Product 2', 'price': 20.99},
            ],
            'pagination': {'next_page': 2}
        }
        resp = json_response(data)
        results = list(spider.parse_products(resp))

        # Check items
        items = [r for r in results if not isinstance(r, Request)]
        assert len(items) == 2

        # Check pagination
        requests = [r for r in results if isinstance(r, Request)]
        assert len(requests) == 1

    def test_parse_handles_invalid_json(self, spider, response):
        """Test handling of invalid JSON response."""
        resp = response(body='invalid json')
        results = list(spider.parse_products(resp))

        # Should handle gracefully, not crash
        assert results == []
```

### 2. Contract Tests

```python
# In spider file
class ProductSpider(scrapy.Spider):
    """Product spider with contracts."""

    name = 'product_spider'

    def parse(self, response):
        """
        Parse product listing page.

        @url http://example.com/products
        @returns items 10 100
        @returns requests 1 10
        @scrapes title price url
        """
        for product in response.css('div.product'):
            yield {
                'title': product.css('h2::text').get(),
                'price': product.css('span.price::text').get(),
                'url': response.urljoin(product.css('a::attr(href)').get()),
            }

    def parse_product(self, response):
        """
        Parse product detail page.

        @url http://example.com/product/123
        @returns items 1 1
        @scrapes title price description sku images
        """
        yield {
            'title': response.css('h1::text').get(),
            'price': response.css('span.price::text').get(),
            'description': response.css('div.desc::text').get(),
            'sku': response.css('span.sku::text').get(),
            'images': response.css('img::attr(src)').getall(),
        }
```

**Run contract tests**:
```bash
scrapy check product_spider
```

### 3. Integration Tests

```python
# tests/test_integration.py
import pytest
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer, reactor
from myproject.spiders.product_spider import ProductSpider


@pytest.mark.integration
@pytest.mark.slow
class TestSpiderIntegration:
    """Integration tests that run full spider."""

    @pytest.fixture
    def runner(self, settings):
        """Create crawler runner."""
        return CrawlerRunner(settings)

    @defer.inlineCallbacks
    def test_full_spider_run(self, runner):
        """Test complete spider execution."""
        # This test actually runs the spider
        stats = {}

        def collect_stats(spider):
            stats.update(spider.crawler.stats.get_stats())

        # Run spider
        yield runner.crawl(
            ProductSpider,
            category='electronics',
            **{'closed': collect_stats}
        )

        # Check stats
        assert stats['item_scraped_count'] > 0
        assert stats['response_received_count'] > 0
        assert stats.get('spider_exceptions', 0) == 0

    @defer.inlineCallbacks
    def test_spider_respects_robotstxt(self, runner, settings):
        """Test spider respects robots.txt."""
        settings.set('ROBOTSTXT_OBEY', True)

        yield runner.crawl(ProductSpider)

        # Spider should have checked robots.txt
        # Check logs or stats for robots.txt requests
```

## Pipeline Testing

### 1. Validation Pipeline Tests

```python
# tests/test_pipelines.py
import pytest
from scrapy.exceptions import DropItem
from myproject.pipelines import ValidationPipeline


class TestValidationPipeline:
    """Test validation pipeline."""

    @pytest.fixture
    def pipeline(self):
        return ValidationPipeline()

    @pytest.fixture
    def spider(self):
        from unittest.mock import Mock
        spider = Mock()
        spider.logger = Mock()
        return spider

    def test_valid_item_passes(self, pipeline, spider):
        """Test valid item passes validation."""
        item = {
            'title': 'Product Title',
            'url': 'http://example.com/product',
            'price': 10.99,
        }

        result = pipeline.process_item(item, spider)
        assert result == item

    def test_missing_required_field_drops_item(self, pipeline, spider):
        """Test item with missing required field is dropped."""
        item = {
            'title': 'Product Title',
            # Missing 'url' field
        }

        with pytest.raises(DropItem, match='Missing required fields'):
            pipeline.process_item(item, spider)

    def test_invalid_field_value_drops_item(self, pipeline, spider):
        """Test item with invalid field value is dropped."""
        item = {
            'title': 'Product',
            'url': 'http://example.com',
            'price': -10,  # Invalid negative price
        }

        with pytest.raises(DropItem, match='Invalid price'):
            pipeline.process_item(item, spider)

    @pytest.mark.parametrize('price,expected', [
        (10.99, True),
        (0, False),
        (-5, False),
        ('10.99', True),
    ])
    def test_price_validation(self, pipeline, spider, price, expected):
        """Test price validation with various inputs."""
        item = {
            'title': 'Product',
            'url': 'http://example.com',
            'price': price,
        }

        if expected:
            result = pipeline.process_item(item, spider)
            assert result == item
        else:
            with pytest.raises(DropItem):
                pipeline.process_item(item, spider)
```

### 2. Cleaning Pipeline Tests

```python
class TestCleaningPipeline:
    """Test data cleaning pipeline."""

    @pytest.fixture
    def pipeline(self):
        from myproject.pipelines import CleaningPipeline
        return CleaningPipeline()

    @pytest.fixture
    def spider(self):
        from unittest.mock import Mock
        return Mock()

    def test_text_cleaning(self, pipeline, spider):
        """Test text fields are cleaned properly."""
        item = {
            'title': '  Product  Title  ',
            'description': '<p>Great product!</p>',
        }

        result = pipeline.process_item(item, spider)

        assert result['title'] == 'Product Title'
        assert result['description'] == 'Great product!'

    @pytest.mark.parametrize('input_price,expected', [
        ('$10.99', 10.99),
        ('€20,50', 20.50),
        ('1,234.56', 1234.56),
        ('100', 100.0),
        (None, None),
    ])
    def test_price_cleaning(self, pipeline, spider, input_price, expected):
        """Test price cleaning with various formats."""
        item = {'price': input_price}
        result = pipeline.process_item(item, spider)

        assert result['price'] == expected
```

### 3. Database Pipeline Tests

```python
class TestDatabasePipeline:
    """Test database storage pipeline."""

    @pytest.fixture
    def pipeline(self, mock_crawler):
        """Create pipeline with mocked database."""
        from myproject.pipelines import DatabasePipeline
        from unittest.mock import Mock

        mock_crawler.settings.set('DATABASE_URL', 'sqlite:///:memory:')
        mock_crawler.settings.set('DATABASE_TABLE', 'test_items')

        pipeline = DatabasePipeline.from_crawler(mock_crawler)
        pipeline.connection = Mock()
        pipeline.cursor = Mock()

        return pipeline

    @pytest.fixture
    def spider(self):
        from unittest.mock import Mock
        spider = Mock()
        spider.logger = Mock()
        return spider

    def test_pipeline_saves_item(self, pipeline, spider):
        """Test pipeline saves item to database."""
        item = {
            'title': 'Test Product',
            'url': 'http://example.com/test',
            'price': 19.99,
        }

        result = pipeline.process_item(item, spider)

        # Check cursor.execute was called
        assert pipeline.cursor.execute.called
        assert result == item

    def test_pipeline_handles_duplicate_url(self, pipeline, spider):
        """Test pipeline handles duplicate URL with upsert."""
        item = {
            'title': 'Updated Product',
            'url': 'http://example.com/test',
            'price': 24.99,
        }

        # Should not raise error, uses ON CONFLICT
        result = pipeline.process_item(item, spider)
        assert result == item

    def test_pipeline_closes_connection(self, pipeline, spider):
        """Test pipeline closes database connection."""
        pipeline.close_spider(spider)

        assert pipeline.connection.commit.called
        assert pipeline.connection.close.called
```

## Middleware Testing

```python
# tests/test_middlewares.py
import pytest
from scrapy.http import Request, Response
from myproject.middlewares import CustomMiddleware


class TestCustomMiddleware:
    """Test custom middleware."""

    @pytest.fixture
    def middleware(self, mock_crawler):
        return CustomMiddleware.from_crawler(mock_crawler)

    @pytest.fixture
    def spider(self):
        from unittest.mock import Mock
        return Mock()

    def test_process_request(self, middleware, spider):
        """Test request processing."""
        request = Request('http://example.com')
        result = middleware.process_request(request, spider)

        # Check middleware modifies request
        assert result is None or isinstance(result, Request)

    def test_process_response(self, middleware, spider):
        """Test response processing."""
        request = Request('http://example.com')
        response = Response('http://example.com', request=request)

        result = middleware.process_response(request, response, spider)

        assert isinstance(result, Response)

    def test_process_exception(self, middleware, spider):
        """Test exception handling."""
        request = Request('http://example.com')
        exception = Exception('Test error')

        result = middleware.process_exception(request, exception, spider)

        # Middleware should handle exception
        assert result is None or isinstance(result, (Request, Response))
```

## Coverage Analysis

### Running Tests with Coverage

```bash
# Run all tests with coverage
pytest --cov=myproject --cov-report=html --cov-report=term-missing

# Run specific test types
pytest -m unit                    # Unit tests only
pytest -m "not slow"             # Skip slow tests
pytest -m integration            # Integration tests only

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_spiders.py

# Run specific test
pytest tests/test_spiders.py::TestProductSpider::test_parse_method

# Run with debugging
pytest --pdb  # Drop into debugger on failure
```

### Coverage Report Example

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
myproject/__init__.py             0      0   100%
myproject/spiders.py            120      5    96%   45-47, 89, 102
myproject/pipelines.py           95      8    92%   67-70, 120-123
myproject/middlewares.py         45      3    93%   23-25
myproject/items.py               15      0   100%
-----------------------------------------------------------
TOTAL                           275     16    94%
```

## Test Fixtures

### HTML Fixtures

```python
# tests/fixtures/product_list.html
<!DOCTYPE html>
<html>
<head><title>Products</title></head>
<body>
    <div class="product">
        <h2 class="title">Laptop</h2>
        <span class="price">$999.99</span>
        <a href="/product/1">View Details</a>
    </div>
    <div class="product">
        <h2 class="title">Mouse</h2>
        <span class="price">$29.99</span>
        <a href="/product/2">View Details</a>
    </div>
    <a class="next" href="/page/2">Next</a>
</body>
</html>
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest --cov=myproject --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## When to Use This Skill

Use this skill when:
- Creating test suites for new spiders
- Improving test coverage
- Debugging spider behavior
- Implementing CI/CD pipelines
- Validating parsing logic
- Testing pipeline functionality

## Integration with Commands

**Commands**:
- `/test` - Run test suite
- `/coverage` - Generate coverage report
- `/test-spider <spider>` - Test specific spider

This skill ensures comprehensive testing with proper fixtures, mocking, and coverage analysis.
