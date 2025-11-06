"""CrawlSpider example for following links automatically.

CrawlSpider is useful for scraping sites by following link patterns.
It uses Rules to define which links to follow and which callbacks to use.
"""

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from myproject.items import Article
from myproject.loaders import ArticleLoader


class ExampleCrawlSpider(CrawlSpider):
    """CrawlSpider that automatically follows links based on rules."""

    name = "example_crawl"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com/blog"]

    # Define rules for following links
    rules = (
        # Follow category links but don't parse them
        Rule(
            LinkExtractor(restrict_css='nav.categories a'),
            follow=True
        ),

        # Follow pagination links
        Rule(
            LinkExtractor(restrict_css='div.pagination a'),
            follow=True
        ),

        # Follow article links and parse them
        Rule(
            LinkExtractor(restrict_css='article.post a.read-more'),
            callback='parse_article',
            follow=False
        ),

        # Using XPath link extractor
        # Rule(
        #     LinkExtractor(restrict_xpaths='//article[@class="post"]//a[@class="read-more"]'),
        #     callback='parse_article',
        #     follow=False
        # ),
    )

    def parse_article(self, response):
        """Parse individual article page."""
        self.logger.info(f"Parsing article: {response.url}")

        loader = ArticleLoader(item=Article, response=response)

        loader.add_css('title', 'h1.article-title::text')
        loader.add_value('url', response.url)
        loader.add_css('content', 'div.article-content p::text')
        loader.add_css('author', 'span.author-name::text')
        loader.add_css('published_date', 'time.published::attr(datetime)')
        loader.add_css('category', 'span.category::text')
        loader.add_css('tags', 'div.tags a.tag::text')
        loader.add_css('images', 'div.article-content img::attr(src)')
        loader.add_css('summary', 'meta[name="description"]::attr(content)')

        # Calculate word count
        content_text = ' '.join(response.css('div.article-content p::text').getall())
        word_count = len(content_text.split())
        loader.add_value('word_count', word_count)

        yield loader.load_item()


class NewsCrawlSpider(CrawlSpider):
    """Example spider for crawling news websites."""

    name = "news_crawl"
    allowed_domains = ["example-news.com"]
    start_urls = ["http://example-news.com/"]

    # Custom settings
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
    }

    rules = (
        # Follow category pages
        Rule(
            LinkExtractor(
                allow=(r'/category/\w+',),
                deny=(r'/tag/', r'/author/')
            ),
            follow=True
        ),

        # Follow article pages and parse them
        Rule(
            LinkExtractor(
                allow=(r'/\d{4}/\d{2}/\d{2}/[\w-]+',)  # Date-based URL pattern
            ),
            callback='parse_news_article',
            follow=False
        ),
    )

    def parse_news_article(self, response):
        """Parse news article."""
        yield {
            'title': response.css('h1.entry-title::text').get(),
            'url': response.url,
            'content': ' '.join(response.css('div.entry-content p::text').getall()),
            'author': response.css('span.author-name::text').get(),
            'published_date': response.css('time.entry-date::attr(datetime)').get(),
            'category': response.css('span.cat-links a::text').get(),
            'tags': response.css('span.tag-links a::text').getall(),
        }


class EcommerceCrawlSpider(CrawlSpider):
    """Example spider for crawling e-commerce product catalogs."""

    name = "ecommerce_crawl"
    allowed_domains = ["example-shop.com"]
    start_urls = ["http://example-shop.com/products"]

    rules = (
        # Follow category pages
        Rule(
            LinkExtractor(
                restrict_css='div.category-nav a',
                deny=(r'/checkout', r'/cart', r'/account')
            ),
            follow=True
        ),

        # Follow pagination
        Rule(
            LinkExtractor(
                restrict_css='nav.pagination a'
            ),
            follow=True
        ),

        # Parse product pages
        Rule(
            LinkExtractor(
                restrict_css='div.product-item a.product-link'
            ),
            callback='parse_product',
            follow=False
        ),
    )

    def parse_product(self, response):
        """Parse product page."""
        yield {
            'name': response.css('h1.product-name::text').get(),
            'price': response.css('span.price::text').get(),
            'sku': response.css('span.sku::text').get(),
            'description': response.css('div.description::text').get(),
            'brand': response.css('span.brand::text').get(),
            'category': response.css('nav.breadcrumb a:last-child::text').get(),
            'images': response.css('div.product-images img::attr(src)').getall(),
            'availability': response.css('span.stock::text').get(),
            'url': response.url,
        }


class DocsCrawlSpider(CrawlSpider):
    """Example spider for crawling documentation sites."""

    name = "docs_crawl"
    allowed_domains = ["docs.example.com"]
    start_urls = ["http://docs.example.com/"]

    # Stay within documentation section
    rules = (
        # Follow internal documentation links
        Rule(
            LinkExtractor(
                allow=(r'/docs/'),
                deny=(r'/api/', r'/download/', r'/blog/')
            ),
            callback='parse_doc_page',
            follow=True
        ),
    )

    def parse_doc_page(self, response):
        """Parse documentation page."""
        yield {
            'title': response.css('h1::text').get(),
            'url': response.url,
            'content': response.css('div.documentation-content').get(),
            'section': response.css('nav.breadcrumb a:last-child::text').get(),
            'headings': response.css('h2::text, h3::text').getall(),
            'code_examples': response.css('pre code::text').getall(),
        }

    def parse_start_url(self, response):
        """Parse the start URL (homepage)."""
        # CrawlSpider uses this method to parse start URLs
        return self.parse_doc_page(response)
