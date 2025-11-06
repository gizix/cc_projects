"""Pytest configuration and shared fixtures."""

import pytest
from scrapy.http import HtmlResponse, Request, TextResponse
from scrapy.utils.project import get_project_settings


@pytest.fixture
def settings():
    """Get Scrapy project settings."""
    return get_project_settings()


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <div class="product">
                <h1 class="product-title">Test Product</h1>
                <span class="price">$19.99</span>
                <span class="currency">USD</span>
                <p class="description">This is a test product description.</p>
                <div class="images">
                    <img src="/image1.jpg" />
                    <img src="/image2.jpg" />
                </div>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_response(sample_html):
    """Create a sample Scrapy response."""
    request = Request(url='http://example.com/product/123')
    return HtmlResponse(
        url='http://example.com/product/123',
        request=request,
        body=sample_html.encode('utf-8'),
        encoding='utf-8'
    )


@pytest.fixture
def sample_product_list_html():
    """Sample HTML for product listing page."""
    return """
    <html>
        <body>
            <div class="product-list">
                <article class="product">
                    <h3><a href="/product/1">Product 1</a></h3>
                    <span class="price">$10.00</span>
                </article>
                <article class="product">
                    <h3><a href="/product/2">Product 2</a></h3>
                    <span class="price">$20.00</span>
                </article>
            </div>
            <a class="next-page" href="/products?page=2">Next</a>
        </body>
    </html>
    """


@pytest.fixture
def product_list_response(sample_product_list_html):
    """Create a sample response for product listing."""
    request = Request(url='http://example.com/products')
    return HtmlResponse(
        url='http://example.com/products',
        request=request,
        body=sample_product_list_html.encode('utf-8'),
        encoding='utf-8'
    )


@pytest.fixture
def sample_product_item():
    """Sample product item for testing."""
    from myproject.items import Product
    from datetime import datetime

    return Product(
        name="Test Product",
        price=19.99,
        url="http://example.com/product/123",
        description="Test description",
        currency="USD",
        stock=10,
        rating=4.5,
        reviews_count=100,
        category="Electronics",
        brand="TestBrand",
        sku="TEST123",
        images=["http://example.com/image1.jpg"],
        scraped_at=datetime.now()
    )


@pytest.fixture
def sample_article_item():
    """Sample article item for testing."""
    from myproject.items import Article
    from datetime import datetime

    return Article(
        title="Test Article",
        url="http://example.com/article/123",
        content="This is test article content.",
        author="Test Author",
        published_date=datetime.now(),
        category="Technology",
        tags=["test", "article"],
        images=["http://example.com/article-image.jpg"],
        summary="Test article summary",
        word_count=100,
        scraped_at=datetime.now()
    )


@pytest.fixture
def mock_spider_stats():
    """Mock spider stats object."""
    class MockStats:
        def __init__(self):
            self.stats = {}

        def set_value(self, key, value):
            self.stats[key] = value

        def get_value(self, key, default=None):
            return self.stats.get(key, default)

        def inc_value(self, key, count=1):
            self.stats[key] = self.stats.get(key, 0) + count

    return MockStats()
