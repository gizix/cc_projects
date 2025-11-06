# Test Fixtures Guide

Guide for creating and using test fixtures in Scrapy tests.

## HTML Fixtures

Store sample HTML responses for repeatable testing.

### Directory Structure

```
tests/
├── fixtures/
│   ├── product_list.html
│   ├── product_detail.html
│   ├── search_results.html
│   ├── empty_page.html
│   └── error_page.html
└── conftest.py
```

### Creating Fixtures

1. **Capture Real HTML**: Save actual page HTML
   ```bash
   curl https://example.com/products > tests/fixtures/product_list.html
   ```

2. **Simplify HTML**: Remove unnecessary elements
   ```html
   <!-- Keep only relevant structure -->
   <div class="product">
       <h2>Product Title</h2>
       <span class="price">$10.99</span>
   </div>
   ```

3. **Create Edge Cases**: Test boundary conditions
   ```html
   <!-- empty_page.html -->
   <html>
       <body>
           <p>No results found</p>
       </body>
   </html>
   ```

### Using Fixtures

```python
# In conftest.py
@pytest.fixture
def fake_response_from_file():
    def _response(filename, url='http://test.com'):
        file_path = Path(__file__).parent / 'fixtures' / filename
        with open(file_path, 'rb') as f:
            body = f.read()
        request = Request(url)
        return HtmlResponse(url=url, request=request, body=body)
    return _response

# In test file
def test_parse(spider, fake_response_from_file):
    response = fake_response_from_file('product_list.html')
    results = list(spider.parse(response))
    assert len(results) > 0
```

## JSON Fixtures

For API testing.

```python
# tests/fixtures/api_response.json
{
    "results": [
        {"id": 1, "name": "Product 1", "price": 10.99},
        {"id": 2, "name": "Product 2", "price": 20.99}
    ],
    "pagination": {
        "page": 1,
        "total_pages": 10
    }
}
```

```python
# Using JSON fixture
@pytest.fixture
def api_data():
    file_path = Path(__file__).parent / 'fixtures' / 'api_response.json'
    with open(file_path) as f:
        return json.load(f)

def test_api_parse(spider, json_response, api_data):
    resp = json_response(api_data)
    results = list(spider.parse(resp))
    assert len(results) == 2
```

## Database Fixtures

For pipeline testing.

```python
@pytest.fixture(scope='function')
def test_db():
    """Create temporary test database."""
    db_path = 'test.db'
    conn = sqlite3.connect(db_path)

    # Create tables
    conn.execute('''
        CREATE TABLE items (
            id INTEGER PRIMARY KEY,
            title TEXT,
            url TEXT UNIQUE,
            price REAL
        )
    ''')
    conn.commit()

    yield conn

    # Cleanup
    conn.close()
    Path(db_path).unlink()

def test_pipeline_saves(pipeline, test_db, spider):
    pipeline.connection = test_db
    pipeline.cursor = test_db.cursor()

    item = {'title': 'Test', 'url': 'http://test.com', 'price': 9.99}
    pipeline.process_item(item, spider)

    # Verify saved
    cursor = test_db.cursor()
    cursor.execute('SELECT * FROM items WHERE url = ?', ('http://test.com',))
    row = cursor.fetchone()
    assert row is not None
```

## Parametrized Fixtures

Test multiple scenarios.

```python
@pytest.mark.parametrize('html_file,expected_count', [
    ('product_list.html', 10),
    ('empty_page.html', 0),
    ('single_product.html', 1),
])
def test_various_pages(spider, fake_response_from_file, html_file, expected_count):
    response = fake_response_from_file(html_file)
    results = list(spider.parse(response))
    assert len(results) == expected_count
```

## Mock Fixtures

For external dependencies.

```python
@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis client."""
    from unittest.mock import Mock
    mock_client = Mock()
    mock_client.get.return_value = None
    mock_client.set.return_value = True

    def mock_redis_client(*args, **kwargs):
        return mock_client

    monkeypatch.setattr('redis.Redis', mock_redis_client)
    return mock_client

def test_with_redis(spider, mock_redis):
    # Redis calls are mocked
    spider.cache.set('key', 'value')
    mock_redis.set.assert_called_once()
```

## Best Practices

1. **Keep fixtures simple**: Only include necessary HTML/data
2. **Use realistic data**: Based on actual target sites
3. **Version fixtures**: Update when site structure changes
4. **Document fixtures**: Comment what each fixture tests
5. **Separate concerns**: Different fixtures for different scenarios
6. **Clean up**: Use yield fixtures for proper cleanup
7. **Parametrize**: Test multiple cases efficiently

## Example Test Suite

```python
# tests/test_spider_with_fixtures.py
import pytest
from pathlib import Path

class TestProductSpider:
    @pytest.fixture
    def spider(self):
        from myproject.spiders.product_spider import ProductSpider
        return ProductSpider()

    def test_normal_page(self, spider, fake_response_from_file):
        """Test parsing normal product page."""
        response = fake_response_from_file('product_list.html')
        items = list(spider.parse(response))
        assert len(items) == 10
        assert all('title' in item for item in items)

    def test_empty_page(self, spider, fake_response_from_file):
        """Test handling of empty results."""
        response = fake_response_from_file('empty_page.html')
        items = list(spider.parse(response))
        assert len(items) == 0

    def test_malformed_html(self, spider, fake_response_from_file):
        """Test handling of malformed HTML."""
        response = fake_response_from_file('malformed.html')
        items = list(spider.parse(response))
        # Should not crash, might have partial data
        assert isinstance(items, list)

    def test_pagination(self, spider, fake_response_from_file):
        """Test pagination link extraction."""
        response = fake_response_from_file('product_list.html')
        results = list(spider.parse(response))
        requests = [r for r in results if isinstance(r, Request)]
        assert len(requests) > 0
        assert 'page' in requests[0].url
```

This approach ensures comprehensive, maintainable test coverage.
