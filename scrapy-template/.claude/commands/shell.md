---
description: Open Scrapy shell for interactive debugging and selector testing
argument-hint: [url]
allowed-tools: Bash(*)
---

Launch the Scrapy interactive shell to test selectors and debug spider logic.

Arguments:
- $ARGUMENTS: URL to fetch and load into shell (optional)

Common usage patterns:
- `/shell https://example.com` - Open shell with URL loaded
- `/shell "https://example.com/page"` - Open shell with quoted URL
- `/shell` - Open shell without fetching a URL (can fetch later)

Execute: `scrapy shell $ARGUMENTS`

The Scrapy shell provides:
- `response` - The Response object from the fetched URL
- `request` - The Request object used
- `fetch(url)` - Fetch a new URL
- `view(response)` - Open response in browser
- `shelp()` - Show available variables and shortcuts

Common Shell Commands:

**Testing CSS Selectors**:
```python
# Extract text
response.css('h1::text').get()           # First h1 text
response.css('h1::text').getall()        # All h1 texts
response.css('a::attr(href)').getall()   # All link hrefs

# Extract with default
response.css('span.price::text').get(default='N/A')

# Nested selection
for article in response.css('article'):
    title = article.css('h2::text').get()
    link = article.css('a::attr(href)').get()
```

**Testing XPath Selectors**:
```python
# Extract text
response.xpath('//h1/text()').get()
response.xpath('//a/@href').getall()

# Complex queries
response.xpath('//div[@class="product"]/span/text()').get()
response.xpath('//table//tr[position()>1]/td/text()').getall()

# XPath functions
response.xpath('//text()[contains(., "search term")]').getall()
```

**Testing Selector Combinations**:
```python
# CSS to XPath
response.css('div.content').xpath('.//p/text()').getall()

# Re (regex) selector
response.css('div::text').re(r'Price: \$(\d+\.\d+)')
response.css('div::text').re_first(r'Price: \$(\d+\.\d+)')
```

**Fetching Different URLs**:
```python
# Fetch new URL
fetch('https://example.com/page2')

# Fetch with custom headers
fetch('https://example.com', headers={'User-Agent': 'MyBot'})

# Fetch with POST request
from scrapy import FormRequest
fetch(FormRequest('https://example.com/login',
                  formdata={'user': 'test', 'pass': 'test'}))
```

**Viewing Responses**:
```python
# Open response in browser
view(response)

# Check response status
response.status  # 200, 404, etc.

# Check response headers
response.headers
response.headers.get('Content-Type')

# Get response body
response.text    # Decoded text
response.body    # Raw bytes
```

**Testing Item Population**:
```python
# Import your items
from items import ProductItem

# Create and populate item
item = ProductItem()
item['name'] = response.css('h1::text').get()
item['price'] = response.css('span.price::text').get()
item['url'] = response.url

# Verify item
item
```

**Testing Link Extraction**:
```python
from scrapy.linkextractors import LinkExtractor

# Extract links matching pattern
le = LinkExtractor(allow=r'/product/\d+')
links = le.extract_links(response)

for link in links:
    print(link.url)
```

Debugging Tips:

1. **Inspect Response**:
   - `response.url` - Current URL
   - `response.status` - HTTP status code
   - `len(response.text)` - Content length
   - `response.headers` - All headers

2. **Test Selectors Incrementally**:
   ```python
   # Start broad
   response.css('div.product')

   # Narrow down
   response.css('div.product h2')

   # Extract final value
   response.css('div.product h2::text').get()
   ```

3. **Check for JavaScript-rendered Content**:
   ```python
   # If content is empty, page may be JS-rendered
   len(response.css('div.content').getall())

   # Consider using Playwright spider instead
   ```

4. **Test with Different Response Types**:
   ```python
   # JSON responses
   import json
   data = json.loads(response.text)

   # XML responses
   response.xpath('//item/title/text()').getall()
   ```

5. **Debug Unicode/Encoding Issues**:
   ```python
   response.encoding
   response.text  # Should be properly decoded
   ```

Common Shell Workflow:

1. Fetch URL: `fetch('https://target-site.com')`
2. Inspect page: `view(response)` (opens in browser)
3. Test selectors: Try CSS/XPath until correct data extracted
4. Copy working selectors to spider
5. Test with multiple URLs to ensure robustness
6. Exit: `exit()` or Ctrl+D

Shell Configuration:

The shell respects settings from `settings.py`:
- USER_AGENT
- ROBOTSTXT_OBEY
- DOWNLOAD_DELAY
- DEFAULT_REQUEST_HEADERS

Override in shell:
```python
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
settings['USER_AGENT'] = 'CustomBot'
```

Advanced Usage:

**Testing Callbacks**:
```python
# Import spider
from spiders.myspider import MySpider

# Create spider instance
spider = MySpider()

# Test parse method
results = list(spider.parse(response))
results[0]
```

**Testing Item Pipelines**:
```python
from pipelines import MyPipeline

pipeline = MyPipeline()
item = {'name': 'Test'}
processed = pipeline.process_item(item, spider)
```

**Testing with Fake Responses**:
```python
from scrapy.http import HtmlResponse

html = '''<html><body><h1>Test</h1></body></html>'''
fake_response = HtmlResponse(
    url='http://test.com',
    body=html.encode('utf-8')
)

fake_response.css('h1::text').get()
```

Exit the Shell:
- Type `exit()` or press Ctrl+D (Unix) or Ctrl+Z (Windows)

After Shell Session:
1. Copy working selectors to spider code
2. Update parse methods with tested logic
3. Add tests based on shell findings
4. Run spider to verify: `/run-spider`

Best Practices:
- Always test selectors in shell before adding to spider
- Test with multiple pages to ensure selector robustness
- Check for edge cases (missing elements, empty values)
- Verify data types and formats
- Use `getall()` to see all matches, not just first
- Compare CSS vs XPath performance for complex queries
- Test pagination and link following logic
- Verify robots.txt compliance before crawling

Common Issues:
- Empty results: Check response.text to see actual content
- JavaScript content: Use Playwright spider or splash
- Encoding issues: Check response.encoding
- Rate limiting: Add delays or change user agent
- 403/404 errors: Check URL and request headers

Next Steps:
- Create/update spider: `/create-spider`
- Run full crawl: `/run-spider`
- Write tests: `/test-spider`
