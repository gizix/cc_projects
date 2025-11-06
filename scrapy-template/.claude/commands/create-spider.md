---
description: Generate new Scrapy spider with template options
argument-hint: <spider_name> <domain> [--template basic|crawl|playwright]
allowed-tools: Bash(*), Read(*), Write(*)
---

Create a new Scrapy spider with the specified template type.

Arguments:
- $1: Spider name (required)
- $2: Domain to crawl (required)
- $3: Template type (optional: basic, crawl, playwright)

Common usage patterns:
- `/create-spider myspider example.com` - Create basic spider
- `/create-spider myspider example.com --template crawl` - Create CrawlSpider
- `/create-spider myspider example.com --template playwright` - Create Playwright spider

Process:
1. Parse the arguments to extract spider name, domain, and template type
2. Determine template:
   - `basic`: Simple spider for scraping specific URLs
   - `crawl`: CrawlSpider with rules for following links automatically
   - `playwright`: Spider with Playwright for JavaScript-heavy sites
3. Generate spider file in `spiders/` directory with appropriate template
4. Create corresponding test file in `tests/test_spiders.py`
5. Add item classes to `items.py` if needed
6. Show the created files and provide usage instructions

Spider Templates:

**Basic Spider Template**:
```python
import scrapy

class {SpiderName}Spider(scrapy.Spider):
    name = '{spider_name}'
    allowed_domains = ['{domain}']
    start_urls = ['https://{domain}/']

    def parse(self, response):
        # Extract data from the page
        yield {
            'title': response.css('title::text').get(),
            'url': response.url,
        }
```

**CrawlSpider Template**:
```python
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class {SpiderName}Spider(CrawlSpider):
    name = '{spider_name}'
    allowed_domains = ['{domain}']
    start_urls = ['https://{domain}/']

    rules = (
        Rule(LinkExtractor(allow=r'/page/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        yield {
            'title': response.css('title::text').get(),
            'url': response.url,
        }
```

**Playwright Spider Template**:
```python
import scrapy

class {SpiderName}Spider(scrapy.Spider):
    name = '{spider_name}'
    allowed_domains = ['{domain}']

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://{domain}/',
            meta={'playwright': True},
        )

    def parse(self, response):
        yield {
            'title': response.css('title::text').get(),
            'url': response.url,
        }
```

After creation:
1. Show the spider file path and content
2. Explain how to run the spider: `/run-spider {spider_name}`
3. Suggest next steps:
   - Customize selectors for target data
   - Add item pipelines for data processing
   - Configure settings for respectful crawling
4. Remind about testing: `/test-spider {spider_name}`

Best practices:
- Use descriptive spider names (lowercase with underscores)
- Start with allowed_domains for safety
- Implement parse_item() or similar methods
- Use CSS or XPath selectors appropriately
- Add error handling for missing elements
- Respect robots.txt (check with `/check-robots`)
- Test selectors in Scrapy shell first (`/shell`)
