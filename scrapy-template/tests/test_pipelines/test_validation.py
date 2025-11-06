"""Tests for validation pipeline."""

import pytest
from scrapy.exceptions import DropItem
from myproject.pipelines import ValidationPipeline, DuplicateFilterPipeline, DataCleaningPipeline
from myproject.items import Product
from datetime import datetime


class TestValidationPipeline:
    """Test cases for ValidationPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return ValidationPipeline()

    @pytest.fixture
    def valid_product(self):
        """Create valid product item."""
        return Product(
            name="Test Product",
            price=19.99,
            url="http://example.com/product",
            scraped_at=datetime.now()
        )

    @pytest.fixture
    def invalid_product(self):
        """Create invalid product item (missing required fields)."""
        return Product(
            name="Test Product",
            price=0.0,  # Has name and price
            url="",  # Missing URL
            scraped_at=datetime.now()
        )

    @pytest.fixture
    def mock_spider(self):
        """Create mock spider."""
        class MockSpider:
            name = "test_spider"
        return MockSpider()

    def test_valid_item_passes(self, pipeline, valid_product, mock_spider):
        """Test that valid items pass validation."""
        result = pipeline.process_item(valid_product, mock_spider)
        assert result == valid_product

    def test_invalid_item_raises_drop_item(self, pipeline, invalid_product, mock_spider):
        """Test that invalid items raise DropItem."""
        with pytest.raises(DropItem):
            pipeline.process_item(invalid_product, mock_spider)


class TestDuplicateFilterPipeline:
    """Test cases for DuplicateFilterPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return DuplicateFilterPipeline()

    @pytest.fixture
    def product(self):
        """Create product item."""
        return Product(
            name="Test Product",
            price=19.99,
            url="http://example.com/product",
            scraped_at=datetime.now()
        )

    @pytest.fixture
    def mock_spider(self):
        """Create mock spider."""
        class MockSpider:
            name = "test_spider"
        return MockSpider()

    def test_first_item_passes(self, pipeline, product, mock_spider):
        """Test that first item passes through."""
        result = pipeline.process_item(product, mock_spider)
        assert result == product

    def test_duplicate_item_raises_drop_item(self, pipeline, product, mock_spider):
        """Test that duplicate items are dropped."""
        # Process first time - should pass
        pipeline.process_item(product, mock_spider)

        # Process second time - should raise DropItem
        with pytest.raises(DropItem):
            pipeline.process_item(product, mock_spider)


class TestDataCleaningPipeline:
    """Test cases for DataCleaningPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return DataCleaningPipeline()

    @pytest.fixture
    def mock_spider(self):
        """Create mock spider."""
        class MockSpider:
            name = "test_spider"
        return MockSpider()

    def test_trims_whitespace(self, pipeline, mock_spider):
        """Test that whitespace is trimmed from strings."""
        product = Product(
            name="  Test Product  ",
            price=19.99,
            url="  http://example.com/product  ",
            description="  Description with spaces  ",
            scraped_at=datetime.now()
        )

        result = pipeline.process_item(product, mock_spider)

        assert result.name == "Test Product"
        assert result.url == "http://example.com/product"
        assert result.description == "Description with spaces"

    def test_converts_empty_strings_to_none(self, pipeline, mock_spider):
        """Test that empty strings are converted to None."""
        product = Product(
            name="Test Product",
            price=19.99,
            url="http://example.com/product",
            description="",
            brand="",
            scraped_at=datetime.now()
        )

        result = pipeline.process_item(product, mock_spider)

        assert result.description is None
        assert result.brand is None

    def test_converts_price_to_float(self, pipeline, mock_spider):
        """Test that price is converted to float."""
        product = Product(
            name="Test Product",
            price="19.99",  # String price
            url="http://example.com/product",
            scraped_at=datetime.now()
        )

        result = pipeline.process_item(product, mock_spider)

        assert isinstance(result.price, float)
        assert result.price == 19.99
