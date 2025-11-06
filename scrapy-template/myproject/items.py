"""Define data models using Python dataclasses.

Modern approach to defining Scrapy items using dataclasses instead of traditional scrapy.Item.
This provides better IDE support, type hints, and cleaner syntax.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Product:
    """Product item for e-commerce scraping."""

    name: str
    price: float
    url: str
    description: Optional[str] = None
    currency: str = "USD"
    stock: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    category: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    images: List[str] = field(default_factory=list)
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class Article:
    """Article item for news/blog scraping."""

    title: str
    url: str
    content: str
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    word_count: int = 0
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class Review:
    """Review item for customer review scraping."""

    product_id: str
    product_name: str
    reviewer_name: Optional[str] = None
    rating: float = 0.0
    title: Optional[str] = None
    content: str = ""
    helpful_count: int = 0
    verified_purchase: bool = False
    review_date: Optional[datetime] = None
    images: List[str] = field(default_factory=list)
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobListing:
    """Job listing item for job board scraping."""

    title: str
    company: str
    url: str
    location: Optional[str] = None
    description: str = ""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    employment_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    experience_level: Optional[str] = None  # Entry, Mid, Senior, etc.
    skills: List[str] = field(default_factory=list)
    posted_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    remote: bool = False
    scraped_at: datetime = field(default_factory=datetime.now)


# Traditional Scrapy Item example (for backward compatibility)
# Uncomment if you prefer the classic approach:
"""
import scrapy


class ProductItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field(serializer=float)
    url = scrapy.Field()
    description = scrapy.Field()
    currency = scrapy.Field()
    stock = scrapy.Field(serializer=int)
    rating = scrapy.Field(serializer=float)
    reviews_count = scrapy.Field(serializer=int)
    category = scrapy.Field()
    brand = scrapy.Field()
    sku = scrapy.Field()
    images = scrapy.Field(serializer=list)
    scraped_at = scrapy.Field()
"""
