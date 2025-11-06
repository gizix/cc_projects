---
description: Run pytest with coverage for spider tests
argument-hint: [spider_name] [--cov] [-v] [-k test_pattern]
allowed-tools: Bash(*), Read(*)
---

Run the test suite for Scrapy spiders using pytest with optional coverage reporting.

Arguments:
- $ARGUMENTS: All arguments passed to pytest

Common usage patterns:
- `/test-spider` - Run all spider tests
- `/test-spider myspider` - Run tests for specific spider
- `/test-spider --cov` - Run with coverage report
- `/test-spider --cov --cov-report=html` - Generate HTML coverage report
- `/test-spider -v` - Verbose output
- `/test-spider -k test_parse` - Run tests matching pattern
- `/test-spider -x` - Stop at first failure
- `/test-spider --lf` - Run only last failed tests

Execute: `pytest tests/ $ARGUMENTS`

Process:
1. If specific spider mentioned, filter tests: `pytest tests/test_spiders.py::Test{SpiderName} $ARGUMENTS`
2. Otherwise run all tests: `pytest tests/ $ARGUMENTS`
3. Include coverage by default if `--cov` flag present:
   - `pytest --cov=spiders --cov=items --cov=pipelines --cov-report=term-missing tests/`

Test Structure:
Tests should be in `tests/` directory:
```
tests/
├── __init__.py
├── test_spiders.py       # Spider functionality tests
├── test_items.py         # Item validation tests
├── test_pipelines.py     # Pipeline tests
└── fixtures/             # Test data and mock responses
    └── sample_page.html
```

Example Spider Test:
```python
import pytest
from scrapy.http import HtmlResponse, Request
from spiders.myspider import MySpider

class TestMySpider:
    def test_parse(self):
        spider = MySpider()
        url = 'https://example.com'
        html = '''<html><body><h1>Test Title</h1></body></html>'''

        request = Request(url=url)
        response = HtmlResponse(url=url, request=request, body=html.encode('utf-8'))

        results = list(spider.parse(response))

        assert len(results) > 0
        assert results[0]['title'] == 'Test Title'

    def test_parse_handles_missing_elements(self):
        spider = MySpider()
        url = 'https://example.com'
        html = '''<html><body></body></html>'''

        request = Request(url=url)
        response = HtmlResponse(url=url, request=request, body=html.encode('utf-8'))

        results = list(spider.parse(response))

        # Should handle missing elements gracefully
        assert len(results) == 0 or results[0]['title'] is None
```

Coverage Thresholds:
- 80%+ coverage is good for spiders
- Focus on parse methods and item extraction logic
- Test edge cases: missing elements, malformed HTML, empty responses

After running tests:
1. Report test results:
   - Number of tests passed/failed
   - Test execution time
   - Coverage percentage (if --cov used)
2. If failures, show:
   - Failed test names
   - Assertion errors
   - Traceback information
3. If coverage < 80%, suggest areas needing tests:
   - Untested spider methods
   - Edge cases not covered
   - Pipeline logic without tests

Coverage Report Options:
- `--cov-report=term` - Terminal output (default)
- `--cov-report=term-missing` - Show line numbers not covered
- `--cov-report=html` - Generate HTML report in htmlcov/
- `--cov-report=xml` - Generate XML for CI/CD tools

Common Test Patterns:
1. **Parse Method Tests**: Verify item extraction from HTML
2. **Start Requests Tests**: Check initial URLs and parameters
3. **Link Following Tests**: Ensure CrawlSpider rules work correctly
4. **Error Handling Tests**: Test behavior with malformed responses
5. **Item Pipeline Tests**: Validate data transformation and storage

Pytest Markers:
Use markers to organize tests:
```python
@pytest.mark.slow
def test_full_crawl():
    # Long-running integration test
    pass

@pytest.mark.integration
def test_with_real_site():
    # Test against real website
    pass
```

Run marked tests: `pytest -m slow` or `pytest -m "not slow"`

Best Practices:
- Mock HTTP responses using HtmlResponse
- Use fixtures for common test data
- Test both success and failure cases
- Keep tests fast by avoiding real HTTP requests
- Use contracts for inline testing (Scrapy feature)
- Test with various response types (HTML, JSON, XML)
- Verify item schema compliance
- Test robots.txt handling
- Check request headers and cookies

Integration Testing:
For full crawl tests, use:
```python
from scrapy.crawler import CrawlerProcess

def test_full_spider_crawl():
    process = CrawlerProcess(settings={
        'ITEM_PIPELINES': {},
        'CLOSESPIDER_PAGECOUNT': 5,
    })
    process.crawl(MySpider)
    process.start()
```

CI/CD Integration:
Add to CI pipeline:
```bash
pytest tests/ --cov=. --cov-report=xml --cov-report=term
```

Next Steps After Testing:
- Fix any failing tests
- Improve coverage for critical paths
- Run spider in production: `/run-spider`
- Validate output data: `/validate-items`
