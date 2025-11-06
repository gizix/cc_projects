"""Item loaders for processing and validating scraped data.

Item loaders provide a convenient mechanism for populating items with data.
They offer input and output processors for cleaning and transforming data.
"""

from itemloaders.processors import TakeFirst, MapCompose, Join, Identity
from itemloaders import ItemLoader
import w3lib.html
from datetime import datetime
import re


def strip_whitespace(value):
    """Remove leading/trailing whitespace."""
    if value:
        return value.strip()
    return value


def remove_html_tags(value):
    """Remove HTML tags from text."""
    if value:
        return w3lib.html.remove_tags(value).strip()
    return value


def extract_price(value):
    """Extract numeric price from string with currency symbols."""
    if value:
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', value)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


def extract_number(value):
    """Extract integer from string."""
    if value:
        cleaned = re.sub(r'\D', '', value)
        try:
            return int(cleaned)
        except ValueError:
            return 0
    return 0


def normalize_text(value):
    """Normalize text by removing extra whitespace."""
    if value:
        return ' '.join(value.split())
    return value


def parse_date(value):
    """Parse various date formats."""
    if not value:
        return None

    # Add your date parsing logic here
    # Example formats to handle:
    # - "2023-01-15"
    # - "January 15, 2023"
    # - "15/01/2023"

    try:
        # Simple ISO format parsing
        return datetime.fromisoformat(value)
    except (ValueError, AttributeError):
        return None


class ProductLoader(ItemLoader):
    """Item loader for Product items."""

    default_output_processor = TakeFirst()

    # Name processing
    name_in = MapCompose(str.strip, str.title, normalize_text)

    # Price processing
    price_in = MapCompose(strip_whitespace, extract_price)
    price_out = TakeFirst()

    # URL processing
    url_in = MapCompose(str.strip)

    # Description processing
    description_in = MapCompose(remove_html_tags, normalize_text)
    description_out = Join(' ')

    # Currency processing
    currency_in = MapCompose(str.strip, str.upper)

    # Numeric fields
    stock_in = MapCompose(extract_number)
    rating_in = MapCompose(extract_price)  # Reuse price extraction for floats
    reviews_count_in = MapCompose(extract_number)

    # Category and brand
    category_in = MapCompose(strip_whitespace, normalize_text)
    brand_in = MapCompose(strip_whitespace)

    # SKU
    sku_in = MapCompose(strip_whitespace)

    # Images (keep all URLs)
    images_in = MapCompose(str.strip)
    images_out = Identity()  # Return list of all images


class ArticleLoader(ItemLoader):
    """Item loader for Article items."""

    default_output_processor = TakeFirst()

    # Title processing
    title_in = MapCompose(remove_html_tags, normalize_text)

    # URL processing
    url_in = MapCompose(str.strip)

    # Content processing
    content_in = MapCompose(remove_html_tags, normalize_text)
    content_out = Join('\n\n')

    # Author processing
    author_in = MapCompose(strip_whitespace, normalize_text)

    # Date processing
    published_date_in = MapCompose(strip_whitespace, parse_date)

    # Category processing
    category_in = MapCompose(strip_whitespace, normalize_text)

    # Tags (keep all)
    tags_in = MapCompose(strip_whitespace, str.lower)
    tags_out = Identity()

    # Images (keep all)
    images_in = MapCompose(str.strip)
    images_out = Identity()

    # Summary
    summary_in = MapCompose(remove_html_tags, normalize_text)

    # Word count
    word_count_in = MapCompose(extract_number)


class ReviewLoader(ItemLoader):
    """Item loader for Review items."""

    default_output_processor = TakeFirst()

    # Product information
    product_id_in = MapCompose(str.strip)
    product_name_in = MapCompose(strip_whitespace, normalize_text)

    # Reviewer information
    reviewer_name_in = MapCompose(strip_whitespace, normalize_text)

    # Rating
    rating_in = MapCompose(extract_price)

    # Review content
    title_in = MapCompose(remove_html_tags, normalize_text)
    content_in = MapCompose(remove_html_tags, normalize_text)
    content_out = Join(' ')

    # Helpful count
    helpful_count_in = MapCompose(extract_number)

    # Verified purchase (boolean)
    verified_purchase_in = MapCompose(
        str.strip,
        lambda x: x.lower() in ['true', 'yes', '1', 'verified']
    )

    # Review date
    review_date_in = MapCompose(strip_whitespace, parse_date)

    # Images (keep all)
    images_in = MapCompose(str.strip)
    images_out = Identity()


class JobListingLoader(ItemLoader):
    """Item loader for Job Listing items."""

    default_output_processor = TakeFirst()

    # Basic information
    title_in = MapCompose(remove_html_tags, normalize_text)
    company_in = MapCompose(strip_whitespace, normalize_text)
    url_in = MapCompose(str.strip)
    location_in = MapCompose(strip_whitespace, normalize_text)

    # Description
    description_in = MapCompose(remove_html_tags, normalize_text)
    description_out = Join('\n\n')

    # Salary information
    salary_min_in = MapCompose(extract_price)
    salary_max_in = MapCompose(extract_price)
    salary_currency_in = MapCompose(str.strip, str.upper)

    # Employment details
    employment_type_in = MapCompose(strip_whitespace, normalize_text)
    experience_level_in = MapCompose(strip_whitespace, normalize_text)

    # Skills (keep all)
    skills_in = MapCompose(strip_whitespace, normalize_text)
    skills_out = Identity()

    # Dates
    posted_date_in = MapCompose(strip_whitespace, parse_date)
    application_deadline_in = MapCompose(strip_whitespace, parse_date)

    # Remote flag
    remote_in = MapCompose(
        str.strip,
        lambda x: x.lower() in ['true', 'yes', '1', 'remote']
    )
