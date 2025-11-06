# Spider Templates Reference

Quick reference for generating different spider types.

## Basic Spider Template

```python
import scrapy

class {{ spider_name }}Spider(scrapy.Spider):
    name = "{{ spider_name }}"
    allowed_domains = ["{{ domain }}"]
    start_urls = ["{{ start_url }}"]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'ROBOTSTXT_OBEY': True,
    }

    def parse(self, response):
        # Extract items
        for item in response.css('{{ selector }}'):
            yield {
                'field1': item.css('{{ field1_selector }}').get(),
                'field2': item.css('{{ field2_selector }}').get(),
            }

        # Follow pagination
        next_page = response.css('{{ next_selector }}').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

## CrawlSpider Template

```python
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class {{ spider_name }}CrawlSpider(CrawlSpider):
    name = "{{ spider_name }}_crawl"
    allowed_domains = ["{{ domain }}"]
    start_urls = ["{{ start_url }}"]

    rules = (
        Rule(LinkExtractor(restrict_css='{{ link_selector }}'), callback='parse_item'),
    )

    def parse_item(self, response):
        yield {
            'url': response.url,
            'title': response.css('{{ title_selector }}').get(),
        }
```

## API Spider Template

```python
import scrapy
import json

class {{ spider_name }}APISpider(scrapy.Spider):
    name = "{{ spider_name }}_api"

    def start_requests(self):
        yield scrapy.Request(
            url='{{ api_url }}',
            headers={'Authorization': 'Bearer {{ api_key }}'},
            callback=self.parse
        )

    def parse(self, response):
        data = json.loads(response.text)
        for item in data.get('results', []):
            yield {
                'id': item['id'],
                'name': item['name'],
            }
```

## Customization Guide

1. Replace `{{ spider_name }}` with your spider name
2. Replace `{{ domain }}` with target domain
3. Replace `{{ start_url }}` with starting URL
4. Update selectors (`{{ selector }}`) based on target HTML structure
5. Add custom fields as needed
