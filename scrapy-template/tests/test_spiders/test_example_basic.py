"""Tests for example_basic spider."""

import pytest
from myproject.spiders.example_basic import ExampleBasicSpider, QuotesSpider, BooksSpider


class TestExampleBasicSpider:
    """Test cases for ExampleBasicSpider."""

    @pytest.fixture
    def spider(self):
        """Create spider instance."""
        return ExampleBasicSpider()

    def test_spider_attributes(self, spider):
        """Test spider has correct attributes."""
        assert spider.name == 'example_basic'
        assert 'example.com' in spider.allowed_domains
        assert len(spider.start_urls) > 0

    def test_parse_product(self, spider, sample_response):
        """Test parsing of product page."""
        results = list(spider.parse_product(sample_response))

        assert len(results) == 1
        item = results[0]

        # Check that item has required fields
        assert 'name' in item
        assert 'price' in item
        assert 'url' in item

    def test_parse_extracts_product_links(self, spider, product_list_response):
        """Test that parse method extracts product links."""
        results = list(spider.parse(product_list_response))

        # Should have requests for product links
        from scrapy import Request
        requests = [r for r in results if isinstance(r, Request)]

        assert len(requests) > 0

    def test_parse_follows_pagination(self, spider, product_list_response):
        """Test that pagination links are followed."""
        results = list(spider.parse(product_list_response))

        from scrapy import Request
        pagination_requests = [
            r for r in results
            if isinstance(r, Request) and 'page=' in r.url
        ]

        assert len(pagination_requests) > 0


class TestQuotesSpider:
    """Test cases for QuotesSpider."""

    @pytest.fixture
    def spider(self):
        """Create spider instance."""
        return QuotesSpider()

    @pytest.fixture
    def quotes_html(self):
        """Sample quotes HTML."""
        return """
        <html>
            <body>
                <div class="quote">
                    <span class="text">"Test quote"</span>
                    <small class="author">Test Author</small>
                    <div class="tags">
                        <a class="tag" href="/tag/test">test</a>
                        <a class="tag" href="/tag/quote">quote</a>
                    </div>
                </div>
                <li class="next">
                    <a href="/page/2/">Next</a>
                </li>
            </body>
        </html>
        """

    @pytest.fixture
    def quotes_response(self, quotes_html):
        """Create quotes response."""
        from scrapy.http import HtmlResponse, Request

        request = Request(url='http://quotes.toscrape.com/')
        return HtmlResponse(
            url='http://quotes.toscrape.com/',
            request=request,
            body=quotes_html.encode('utf-8')
        )

    def test_spider_attributes(self, spider):
        """Test spider attributes."""
        assert spider.name == 'quotes'
        assert 'quotes.toscrape.com' in spider.allowed_domains

    def test_parse_extracts_quotes(self, spider, quotes_response):
        """Test that quotes are extracted."""
        results = list(spider.parse(quotes_response))

        # Should have at least one quote item
        items = [r for r in results if isinstance(r, dict)]
        assert len(items) >= 1

        quote = items[0]
        assert 'text' in quote
        assert 'author' in quote
        assert 'tags' in quote


class TestBooksSpider:
    """Test cases for BooksSpider."""

    @pytest.fixture
    def spider(self):
        """Create spider instance."""
        return BooksSpider()

    def test_spider_attributes(self, spider):
        """Test spider attributes."""
        assert spider.name == 'books'
        assert 'books.toscrape.com' in spider.allowed_domains
