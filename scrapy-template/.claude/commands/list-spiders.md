---
description: Display all available spiders with descriptions and stats
argument-hint: [--verbose]
allowed-tools: Bash(*), Read(*), Grep(*)
---

List all available Scrapy spiders in the project with their descriptions and key information.

Arguments:
- $ARGUMENTS: Optional flags (--verbose, --stats)

Common usage patterns:
- `/list-spiders` - List all spiders with basic info
- `/list-spiders --verbose` - Show detailed information
- `/list-spiders --stats` - Include crawl statistics if available

Execute: `scrapy list`

Process:

1. **Get Spider List from Scrapy**:
```bash
scrapy list
```

2. **Gather Spider Information**:

For each spider, extract:
- Spider name
- Spider class
- Allowed domains
- Start URLs
- Spider type (Spider, CrawlSpider, etc.)
- Custom settings
- Docstring/description

```python
import importlib
import inspect
from scrapy.utils.project import get_project_settings
from scrapy.spiderloader import SpiderLoader

# Load spiders
settings = get_project_settings()
spider_loader = SpiderLoader.from_settings(settings)
spider_names = spider_loader.list()

spiders_info = []

for name in spider_names:
    spider_class = spider_loader.load(name)

    # Extract information
    info = {
        'name': name,
        'class': spider_class.__name__,
        'module': spider_class.__module__,
        'type': get_spider_type(spider_class),
        'domains': getattr(spider_class, 'allowed_domains', []),
        'start_urls': getattr(spider_class, 'start_urls', []),
        'description': inspect.getdoc(spider_class) or 'No description',
        'custom_settings': getattr(spider_class, 'custom_settings', {}),
    }

    spiders_info.append(info)
```

3. **Display Basic List**:

```
Available Scrapy Spiders
========================

1. example_spider
   Type: Basic Spider
   Domains: example.com
   Description: Scrapes products from Example.com

2. news_crawler
   Type: CrawlSpider
   Domains: news-site.com
   Description: Crawls news articles with automatic link following

3. js_heavy_spider
   Type: Playwright Spider
   Domains: javascript-site.com
   Description: Scrapes JavaScript-rendered content using Playwright

Total: 3 spiders
```

4. **Display Verbose Information**:

If `--verbose` flag is present:

```
Spider Details
==============

1. example_spider
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Name:           example_spider
   Class:          ExampleSpider
   Module:         spiders.example_spider
   Type:           scrapy.Spider
   File:           E:\Projects\scrapy-template\spiders\example_spider.py

   Allowed Domains:
     • example.com

   Start URLs:
     • https://example.com/products
     • https://example.com/categories

   Description:
     Scrapes product information from Example.com including:
     - Product names and prices
     - Product descriptions
     - Images and ratings

   Custom Settings:
     DOWNLOAD_DELAY: 2
     CONCURRENT_REQUESTS: 8

   Usage:
     scrapy crawl example_spider -o products.json

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. news_crawler
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Name:           news_crawler
   Class:          NewsCrawler
   Type:           scrapy.spiders.CrawlSpider

   Allowed Domains:
     • news-site.com

   Start URLs:
     • https://news-site.com/

   Rules:
     • LinkExtractor(allow=r'/article/\d+')
     • LinkExtractor(allow=r'/category/\w+', follow=True)

   Description:
     Automatically crawls and extracts news articles.
     Follows category links to discover more articles.

   Usage:
     scrapy crawl news_crawler -o articles.json

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

5. **Display with Statistics** (if --stats):

```
Spider Performance Statistics
==============================

Spider: example_spider
  Last Run: 2025-11-04 14:30:00
  Duration: 45.2 seconds
  Items Scraped: 1,234
  Pages Crawled: 1,456
  Success Rate: 98.5%

Spider: news_crawler
  Last Run: 2025-11-05 09:15:00
  Duration: 120.5 seconds
  Items Scraped: 3,456
  Pages Crawled: 4,123
  Success Rate: 97.2%

Spider: js_heavy_spider
  Status: Never run

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 3 spiders
```

Helper Functions:

```python
def get_spider_type(spider_class):
    """Determine spider type based on base classes."""
    from scrapy.spiders import CrawlSpider
    from scrapy import Spider

    if issubclass(spider_class, CrawlSpider):
        return 'CrawlSpider'
    elif issubclass(spider_class, Spider):
        # Check for Playwright
        if 'playwright' in str(spider_class.custom_settings.get('DOWNLOAD_HANDLERS', {})):
            return 'Playwright Spider'
        return 'Basic Spider'
    else:
        return 'Custom Spider'

def get_spider_stats(spider_name):
    """Load last crawl statistics for spider."""
    import json
    import os

    stats_file = f'stats/{spider_name}_last.json'
    if os.path.exists(stats_file):
        with open(stats_file) as f:
            return json.load(f)
    return None
```

Read Spider Files:

For verbose mode, read spider file to extract additional info:

```python
def analyze_spider_file(spider_module):
    """Analyze spider source file for additional details."""
    import ast

    # Get source file path
    file_path = inspect.getfile(spider_module)

    # Read and parse
    with open(file_path) as f:
        source = f.read()

    tree = ast.parse(source)

    # Extract:
    # - Imports (to identify dependencies like selenium, playwright)
    # - Methods (parse, parse_item, etc.)
    # - Custom attributes

    info = {
        'file_path': file_path,
        'imports': extract_imports(tree),
        'methods': extract_methods(tree),
        'line_count': len(source.split('\n')),
    }

    return info
```

Display by Category:

Group spiders by type or domain:

```
Spiders by Type
===============

Basic Spiders (2):
  • example_spider - Scrapes example.com products
  • simple_scraper - Basic page scraper

CrawlSpiders (1):
  • news_crawler - Crawls news with automatic following

Playwright Spiders (1):
  • js_heavy_spider - JavaScript-rendered content

Total: 4 spiders
```

Quick Reference Table:

```
┌──────────────────┬──────────────┬────────────────────┬───────────────┐
│ Spider Name      │ Type         │ Domain             │ Last Run      │
├──────────────────┼──────────────┼────────────────────┼───────────────┤
│ example_spider   │ Basic        │ example.com        │ 2025-11-04    │
│ news_crawler     │ CrawlSpider  │ news-site.com      │ 2025-11-05    │
│ js_heavy_spider  │ Playwright   │ javascript-site.com│ Never         │
│ product_scraper  │ Basic        │ shop.example.com   │ 2025-11-03    │
└──────────────────┴──────────────┴────────────────────┴───────────────┘
```

Additional Information:

**Spider Templates Available**:
```
To create new spiders:

  Basic Spider:
    /create-spider myspider example.com

  CrawlSpider:
    /create-spider myspider example.com --template crawl

  Playwright Spider:
    /create-spider myspider example.com --template playwright
```

**Quick Actions**:
```
Run a spider:
  /run-spider example_spider -o output.json

Test selectors:
  /shell https://example.com

Run tests:
  /test-spider example_spider

Check robots.txt:
  /check-robots https://example.com
```

Search Spiders:

If searching for specific spider (not standard feature but useful):

```python
def search_spiders(query):
    """Search spiders by name, domain, or description."""
    results = []

    for spider_info in spiders_info:
        if (query.lower() in spider_info['name'].lower() or
            query.lower() in str(spider_info['domains']).lower() or
            query.lower() in spider_info['description'].lower()):
            results.append(spider_info)

    return results
```

Spider Health Check:

For each spider, check:
- Spider file exists and is valid Python
- Required attributes present (name, parse method)
- Start URLs are valid (if defined)
- Allowed domains match start URLs
- No syntax errors

```
Spider Health Check
===================

✓ example_spider
  • Valid Python syntax
  • Has parse() method
  • Start URLs defined
  • Domains configured

✗ broken_spider
  • ERROR: Missing parse() method
  • WARNING: No start_urls defined

⚠ old_spider
  • WARNING: Using deprecated API
  • Suggestion: Update to Scrapy 2.x patterns
```

After Listing:

1. Show next steps:
   - How to run a specific spider
   - How to create a new spider
   - How to test a spider

2. Suggest improvements:
   - Spiders without descriptions
   - Spiders missing tests
   - Spiders with no recent runs

3. Provide documentation links:
   - Link to each spider's documentation
   - Link to CLAUDE.md for conventions

Export Spider List:

Optionally export to formats:

```bash
# JSON export
/list-spiders --export json > spiders.json

# Markdown export
/list-spiders --export markdown > SPIDERS.md

# CSV export
/list-spiders --export csv > spiders.csv
```

Best Practices:
- Add docstrings to all spiders
- Keep spider list manageable (organize in subdirectories if many)
- Document expected output format in description
- Include example usage in spider docstring
- Tag spiders by status (production, development, deprecated)
- Version control spider configurations

Common Issues:
- ImportError: Check spider file syntax
- Spider not listed: Ensure it's in spiders/ directory
- Duplicate names: Each spider must have unique name
- Missing attributes: All spiders need 'name' attribute

Next Steps:
- Run a spider: `/run-spider <name>`
- Create new spider: `/create-spider`
- Test spider: `/test-spider <name>`
- View spider code: Read spiders/spider_name.py
