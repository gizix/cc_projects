"""Playwright spider example for JavaScript-rendered pages.

This spider demonstrates:
- Using Playwright for browser automation
- Handling JavaScript-rendered content
- Taking screenshots
- Interacting with page elements
- Waiting for dynamic content
"""

import scrapy
from myproject.items import Product
from myproject.loaders import ProductLoader


class ExamplePlaywrightSpider(scrapy.Spider):
    """Spider using Playwright for JavaScript-rendered pages."""

    name = "example_playwright"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com/spa-products"]

    # Custom settings for Playwright
    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'timeout': 60000,
        },
    }

    def start_requests(self):
        """Generate start requests with Playwright enabled."""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        # Wait for specific element to load
                        {
                            'wait_for_selector': 'div.product-list',
                            'timeout': 10000,
                        }
                    ],
                },
                callback=self.parse,
                errback=self.errback_close_page,
            )

    async def parse(self, response):
        """Parse the page after JavaScript has rendered."""
        self.logger.info(f"Parsing page: {response.url}")

        # Access the Playwright page object
        page = response.meta.get('playwright_page')

        if page:
            # Take a screenshot
            await page.screenshot(path=f'screenshots/{self.name}_main.png', full_page=True)

            # Scroll to load lazy-loaded content
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)

            # Click a button if needed
            # await page.click('button.load-more')
            # await page.wait_for_selector('div.new-products')

        # Extract product data from rendered page
        product_cards = response.css('div.product-card')

        for card in product_cards:
            loader = ProductLoader(item=Product, selector=card)

            loader.add_css('name', 'h3.product-name::text')
            loader.add_css('price', 'span.price::text')
            loader.add_css('rating', 'div.rating::attr(data-rating)')

            # Get the product URL
            product_url = card.css('a.product-link::attr(href)').get()
            if product_url:
                loader.add_value('url', response.urljoin(product_url))

                # Follow product link with Playwright
                yield scrapy.Request(
                    response.urljoin(product_url),
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                    },
                    callback=self.parse_product,
                    errback=self.errback_close_page,
                )

        # Handle pagination
        if page:
            # Check if next button exists and click it
            next_button = await page.query_selector('button.next-page')
            if next_button:
                await page.click('button.next-page')
                await page.wait_for_load_state('networkidle')

                # Get the new URL after navigation
                new_url = page.url
                yield scrapy.Request(
                    new_url,
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                    },
                    callback=self.parse,
                    errback=self.errback_close_page,
                )

        # Always close the page when done
        if page:
            await page.close()

    async def parse_product(self, response):
        """Parse individual product page with Playwright."""
        page = response.meta.get('playwright_page')

        if page:
            # Wait for dynamic content to load
            await page.wait_for_selector('div.product-details', timeout=10000)

            # Interact with page if needed
            # await page.click('button.show-description')
            # await page.wait_for_selector('div.full-description')

            # Take product screenshot
            # await page.screenshot(path=f'screenshots/product_{hash(response.url)}.png')

        loader = ProductLoader(item=Product, response=response)

        loader.add_css('name', 'h1.product-title::text')
        loader.add_css('price', 'span.current-price::text')
        loader.add_value('url', response.url)
        loader.add_css('description', 'div.product-description::text')
        loader.add_css('stock', 'span.stock-status::text')
        loader.add_css('rating', 'div.rating::attr(data-rating)')
        loader.add_css('reviews_count', 'span.review-count::text')
        loader.add_css('brand', 'span.brand-name::text')
        loader.add_css('sku', 'span.product-sku::text')
        loader.add_css('images', 'div.product-images img::attr(src)')

        if page:
            await page.close()

        yield loader.load_item()

    async def errback_close_page(self, failure):
        """Close page on error."""
        self.logger.error(f"Request failed: {failure.request.url}")

        page = failure.request.meta.get('playwright_page')
        if page:
            await page.close()


class InfiniteScrollSpider(scrapy.Spider):
    """Example spider for handling infinite scroll pages."""

    name = "infinite_scroll"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com/infinite-scroll"]

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def start_requests(self):
        """Generate start request with Playwright."""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                },
                callback=self.parse,
            )

    async def parse(self, response):
        """Parse infinite scroll page."""
        page = response.meta['playwright_page']

        # Scroll multiple times to load more content
        scroll_count = 5  # Number of scrolls
        for i in range(scroll_count):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)  # Wait for content to load
            self.logger.info(f"Scroll #{i+1}")

        # Wait for final content to load
        await page.wait_for_load_state('networkidle')

        # Now extract all loaded items
        items = response.css('div.item')
        self.logger.info(f"Found {len(items)} items after scrolling")

        for item in items:
            yield {
                'title': item.css('h3::text').get(),
                'description': item.css('p.description::text').get(),
                'url': response.url,
            }

        await page.close()


class FormSubmissionSpider(scrapy.Spider):
    """Example spider for submitting forms with Playwright."""

    name = "form_submission"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com/search"]

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def start_requests(self):
        """Generate start request with form data."""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'search_query': 'laptop',  # Pass data to parse method
                },
                callback=self.parse,
            )

    async def parse(self, response):
        """Submit search form and parse results."""
        page = response.meta['playwright_page']
        search_query = response.meta.get('search_query', '')

        # Fill in search form
        await page.fill('input[name="q"]', search_query)

        # Submit form
        await page.click('button[type="submit"]')

        # Wait for results to load
        await page.wait_for_selector('div.search-results')
        await page.wait_for_load_state('networkidle')

        # Extract results
        results = response.css('div.result-item')

        for result in results:
            yield {
                'title': result.css('h3.title::text').get(),
                'description': result.css('p.description::text').get(),
                'url': result.css('a::attr(href)').get(),
                'search_query': search_query,
            }

        await page.close()


class DynamicContentSpider(scrapy.Spider):
    """Example spider for pages with dynamic content loading."""

    name = "dynamic_content"
    allowed_domains = ["example.com"]
    start_urls = ["http://example.com/dynamic"]

    def start_requests(self):
        """Generate start request with custom Playwright actions."""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        # Wait for specific content
                        {'wait_for_selector': 'div.content-loaded'},
                        # Execute custom JavaScript
                        {'evaluate': 'window.loadMoreContent()'},
                        # Wait for network to be idle
                        {'wait_for_load_state': 'networkidle'},
                    ],
                },
                callback=self.parse,
            )

    async def parse(self, response):
        """Parse dynamically loaded content."""
        page = response.meta.get('playwright_page')

        # Extract data from fully loaded page
        items = response.css('div.dynamic-item')

        for item in items:
            yield {
                'title': item.css('h2::text').get(),
                'content': item.css('p::text').get(),
                'timestamp': item.css('span.timestamp::text').get(),
            }

        if page:
            await page.close()
