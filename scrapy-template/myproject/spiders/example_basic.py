"""Basic spider example for simple web scraping.

This spider demonstrates:
- Basic spider structure
- CSS and XPath selectors
- Using Item Loaders
- Following pagination links
"""

import scrapy
from myproject.items import Product
from myproject.loaders import ProductLoader


class ExampleBasicSpider(scrapy.Spider):
    """Basic spider for scraping product information."""

    name = "example_basic"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com/products"]

    # Custom settings for this spider
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        'ROBOTSTXT_OBEY': True,
    }

    def parse(self, response):
        """
        Parse the main product listing page.

        @url http://example.com/products
        @returns items 1 20
        @returns requests 1 10
        @scrapes name price url
        """
        self.logger.info(f"Parsing product list: {response.url}")

        # Extract product links using CSS selector
        product_links = response.css('div.product a.product-link::attr(href)').getall()

        for link in product_links:
            # Follow each product link
            yield response.follow(link, callback=self.parse_product)

        # Handle pagination - follow next page link
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            self.logger.info(f"Following next page: {next_page}")
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        """Parse individual product page."""
        self.logger.debug(f"Parsing product: {response.url}")

        # Use ItemLoader for cleaner data extraction
        loader = ProductLoader(item=Product, response=response)

        # Extract data using CSS selectors
        loader.add_css('name', 'h1.product-title::text')
        loader.add_css('price', 'span.price::text')
        loader.add_value('url', response.url)
        loader.add_css('description', 'div.product-description::text')
        loader.add_css('currency', 'span.currency::text')
        loader.add_css('stock', 'span.stock-count::text')
        loader.add_css('rating', 'div.rating span.value::text')
        loader.add_css('reviews_count', 'span.reviews-count::text')
        loader.add_css('category', 'nav.breadcrumb a:last-child::text')
        loader.add_css('brand', 'span.brand::text')
        loader.add_css('sku', 'span.sku::text')

        # Extract multiple images
        loader.add_css('images', 'div.product-images img::attr(src)')

        # Using XPath as alternative
        # loader.add_xpath('name', '//h1[@class="product-title"]/text()')
        # loader.add_xpath('price', '//span[@class="price"]/text()')

        yield loader.load_item()

    def closed(self, reason):
        """Called when spider closes."""
        self.logger.info(f"Spider closed: {reason}")


class QuotesSpider(scrapy.Spider):
    """Example spider for scraping quotes (using quotes.toscrape.com as demo)."""

    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/"]

    def parse(self, response):
        """Parse quotes from the page."""
        self.logger.info(f"Scraping page: {response.url}")

        # Extract all quotes on the page
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
                'url': response.url,
            }

        # Follow pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


class BooksSpider(scrapy.Spider):
    """Example spider for scraping book information."""

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        """Parse book catalog page."""
        # Extract book details from each article
        for book in response.css('article.product_pod'):
            yield {
                'title': book.css('h3 a::attr(title)').get(),
                'price': book.css('p.price_color::text').get(),
                'availability': book.css('p.instock.availability::text').re_first(r'\w+'),
                'rating': book.css('p.star-rating::attr(class)').re_first(r'star-rating (\w+)'),
                'url': response.urljoin(book.css('h3 a::attr(href)').get()),
            }

        # Handle pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_detail(self, response):
        """Parse detailed book information page."""
        yield {
            'title': response.css('div.product_main h1::text').get(),
            'price': response.css('p.price_color::text').get(),
            'description': response.css('#product_description + p::text').get(),
            'upc': response.css('table.table tr:nth-child(1) td::text').get(),
            'availability': response.css('table.table tr:nth-child(6) td::text').get(),
            'number_of_reviews': response.css('table.table tr:nth-child(7) td::text').get(),
            'url': response.url,
        }
