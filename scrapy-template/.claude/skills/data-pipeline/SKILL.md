---
name: data-pipeline
description: Implement Scrapy pipeline patterns for data processing, validation, cleaning, and storage when processing scraped items. Automatically creates pipelines for common data workflows including CSV, JSON, database export, and data transformation.
allowed-tools: Read, Write, Grep
---

You are a Scrapy pipeline expert. You create efficient, robust data processing pipelines with proper validation, error handling, and storage patterns following Scrapy best practices.

## Pipeline Architecture

Scrapy pipelines process items in a specific order defined by `ITEM_PIPELINES` priority (0-1000, lower runs first):

```python
# settings.py
ITEM_PIPELINES = {
    'myproject.pipelines.ValidationPipeline': 100,      # Validate first
    'myproject.pipelines.CleaningPipeline': 200,        # Clean data
    'myproject.pipelines.DuplicatesPipeline': 300,      # Remove duplicates
    'myproject.pipelines.ImagesPipeline': 400,          # Download images
    'myproject.pipelines.DatabasePipeline': 800,        # Save to database
    'myproject.pipelines.ExportPipeline': 900,          # Export to files
}
```

## Core Pipeline Patterns

### 1. Validation Pipeline

**Purpose**: Validate item fields and drop invalid items

```python
from scrapy.exceptions import DropItem
from typing import Any


class ValidationPipeline:
    """
    Validate scraped items before processing.

    Drops items missing required fields or with invalid data.
    """

    # Define required fields
    required_fields = ['title', 'url']

    # Define field validators
    validators = {
        'price': lambda x: isinstance(x, (int, float)) and x > 0,
        'email': lambda x: '@' in str(x) if x else True,
        'url': lambda x: str(x).startswith(('http://', 'https://')) if x else False,
    }

    def process_item(self, item: dict, spider) -> dict:
        """
        Validate item fields.

        Args:
            item: Scraped item dictionary
            spider: Spider instance

        Returns:
            Validated item

        Raises:
            DropItem: If validation fails
        """
        # Check required fields
        missing_fields = [field for field in self.required_fields if not item.get(field)]
        if missing_fields:
            raise DropItem(f"Missing required fields: {missing_fields} in {item}")

        # Validate field values
        for field, validator in self.validators.items():
            if field in item and item[field] is not None:
                if not validator(item[field]):
                    raise DropItem(f"Invalid {field}: {item[field]} in {item}")

        spider.logger.debug(f"Item validated: {item.get('title', 'Unknown')}")
        return item


class TypeValidationPipeline:
    """Advanced type validation with automatic conversion."""

    field_types = {
        'price': float,
        'quantity': int,
        'in_stock': bool,
        'rating': float,
    }

    def process_item(self, item: dict, spider) -> dict:
        """Convert and validate field types."""
        for field, expected_type in self.field_types.items():
            if field in item and item[field] is not None:
                try:
                    # Try to convert to expected type
                    if expected_type == bool:
                        item[field] = self._to_bool(item[field])
                    else:
                        item[field] = expected_type(item[field])
                except (ValueError, TypeError) as e:
                    spider.logger.warning(
                        f"Failed to convert {field}={item[field]} to {expected_type}: {e}"
                    )
                    raise DropItem(f"Type conversion failed for {field}")

        return item

    @staticmethod
    def _to_bool(value: Any) -> bool:
        """Convert various types to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        return bool(value)
```

### 2. Data Cleaning Pipeline

**Purpose**: Clean and normalize data

```python
import re
from w3lib.html import remove_tags
from typing import Optional


class CleaningPipeline:
    """
    Clean and normalize item data.

    - Strip whitespace
    - Remove HTML tags
    - Normalize text
    - Clean prices and numbers
    """

    def process_item(self, item: dict, spider) -> dict:
        """Clean item fields."""
        # Clean text fields
        text_fields = ['title', 'description', 'brand', 'category']
        for field in text_fields:
            if field in item and item[field]:
                item[field] = self.clean_text(item[field])

        # Clean price
        if 'price' in item and item['price']:
            item['price'] = self.clean_price(item['price'])

        # Clean URL
        if 'url' in item and item['url']:
            item['url'] = self.clean_url(item['url'])

        # Normalize email
        if 'email' in item and item['email']:
            item['email'] = item['email'].lower().strip()

        # Clean phone number
        if 'phone' in item and item['phone']:
            item['phone'] = self.clean_phone(item['phone'])

        return item

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text field."""
        if not text:
            return text

        # Remove HTML tags
        text = remove_tags(text)

        # Normalize whitespace
        text = ' '.join(text.split())

        # Remove extra spaces
        text = text.strip()

        return text

    @staticmethod
    def clean_price(price: Any) -> Optional[float]:
        """Extract numeric price from string."""
        if isinstance(price, (int, float)):
            return float(price)

        if not price:
            return None

        # Remove currency symbols and formatting
        price_str = str(price)
        price_str = re.sub(r'[^\d.,]', '', price_str)

        # Handle different decimal separators
        if ',' in price_str and '.' in price_str:
            # Determine which is decimal separator
            if price_str.rindex(',') > price_str.rindex('.'):
                price_str = price_str.replace('.', '').replace(',', '.')
            else:
                price_str = price_str.replace(',', '')
        elif ',' in price_str:
            # Comma might be decimal separator (European format)
            parts = price_str.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                price_str = price_str.replace(',', '.')
            else:
                price_str = price_str.replace(',', '')

        try:
            return float(price_str)
        except ValueError:
            return None

    @staticmethod
    def clean_url(url: str) -> str:
        """Clean and normalize URL."""
        url = url.strip()

        # Remove URL fragments
        url = url.split('#')[0]

        # Remove tracking parameters (optional)
        # url = re.sub(r'[?&](utm_|ref=|source=)[^&]*', '', url)

        return url

    @staticmethod
    def clean_phone(phone: str) -> str:
        """Clean phone number."""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        return digits
```

### 3. Duplicate Filtering Pipeline

**Purpose**: Remove duplicate items

```python
from scrapy.exceptions import DropItem
from typing import Set
import hashlib


class DuplicatesPipeline:
    """
    Filter out duplicate items based on unique fields.
    """

    def __init__(self):
        self.seen_ids: Set[str] = set()
        self.duplicates_count = 0

    def process_item(self, item: dict, spider) -> dict:
        """Check for duplicates."""
        # Generate unique ID from URL or other unique field
        unique_id = self.get_unique_id(item)

        if unique_id in self.seen_ids:
            self.duplicates_count += 1
            spider.logger.debug(f"Duplicate item found: {unique_id}")
            raise DropItem(f"Duplicate item: {unique_id}")

        self.seen_ids.add(unique_id)
        return item

    def close_spider(self, spider):
        """Log statistics when spider closes."""
        spider.logger.info(
            f"Duplicates filtered: {self.duplicates_count}, "
            f"Unique items: {len(self.seen_ids)}"
        )

    @staticmethod
    def get_unique_id(item: dict) -> str:
        """Generate unique identifier for item."""
        # Use URL as unique identifier
        if 'url' in item:
            return item['url']

        # Or use SKU/ID field
        if 'sku' in item:
            return item['sku']

        # Or generate hash from multiple fields
        unique_fields = ['title', 'brand', 'price']
        data = '|'.join(str(item.get(f, '')) for f in unique_fields)
        return hashlib.md5(data.encode()).hexdigest()
```

### 4. Database Storage Pipeline

**Purpose**: Save items to database

```python
from typing import Optional
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from scrapy.exceptions import NotConfigured


class DatabasePipeline:
    """
    Save items to database (PostgreSQL or SQLite).

    Settings:
        DATABASE_URL: Database connection string
        DATABASE_TABLE: Table name (default: 'items')
    """

    def __init__(self, database_url: str, table_name: str):
        self.database_url = database_url
        self.table_name = table_name
        self.connection = None
        self.cursor = None
        self.items_saved = 0

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize from crawler settings."""
        database_url = crawler.settings.get('DATABASE_URL')
        if not database_url:
            raise NotConfigured("DATABASE_URL setting is required")

        table_name = crawler.settings.get('DATABASE_TABLE', 'items')

        return cls(database_url, table_name)

    def open_spider(self, spider):
        """Open database connection when spider starts."""
        spider.logger.info(f"Connecting to database: {self.database_url}")

        if self.database_url.startswith('postgresql://'):
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor()
        elif self.database_url.startswith('sqlite://'):
            db_path = self.database_url.replace('sqlite:///', '')
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
        else:
            raise ValueError(f"Unsupported database: {self.database_url}")

        self._create_table()

    def close_spider(self, spider):
        """Close database connection when spider closes."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
        spider.logger.info(f"Items saved to database: {self.items_saved}")

    def process_item(self, item: dict, spider) -> dict:
        """Save item to database."""
        try:
            self._insert_item(item)
            self.items_saved += 1
            return item
        except Exception as e:
            spider.logger.error(f"Error saving item to database: {e}")
            raise

    def _create_table(self):
        """Create table if it doesn't exist."""
        # This is a simple example - adjust fields based on your items
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            title TEXT,
            url TEXT UNIQUE,
            price DECIMAL(10, 2),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_table_sql)
        self.connection.commit()

    def _insert_item(self, item: dict):
        """Insert item into database."""
        # Extract fields
        fields = ['title', 'url', 'price', 'description']
        values = [item.get(field) for field in fields]

        # Create INSERT query
        placeholders = ', '.join(['%s'] * len(fields))
        columns = ', '.join(fields)

        insert_sql = f"""
        INSERT INTO {self.table_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT (url) DO UPDATE SET
            title = EXCLUDED.title,
            price = EXCLUDED.price,
            description = EXCLUDED.description
        """

        self.cursor.execute(insert_sql, values)
        self.connection.commit()
```

### 5. File Export Pipeline (CSV/JSON)

**Purpose**: Export items to files

```python
import csv
import json
from pathlib import Path
from datetime import datetime


class CSVExportPipeline:
    """
    Export items to CSV file.

    Settings:
        CSV_EXPORT_PATH: Path to CSV file (default: output.csv)
        CSV_EXPORT_FIELDS: List of fields to export
    """

    def __init__(self, file_path: str, fields: list):
        self.file_path = file_path
        self.fields = fields
        self.file = None
        self.writer = None
        self.items_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize from settings."""
        file_path = crawler.settings.get('CSV_EXPORT_PATH', 'output.csv')
        fields = crawler.settings.get('CSV_EXPORT_FIELDS', [
            'title', 'url', 'price', 'description'
        ])
        return cls(file_path, fields)

    def open_spider(self, spider):
        """Open CSV file when spider starts."""
        # Create directory if it doesn't exist
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

        self.file = open(self.file_path, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(
            self.file,
            fieldnames=self.fields,
            extrasaction='ignore'  # Ignore extra fields
        )
        self.writer.writeheader()
        spider.logger.info(f"Exporting to CSV: {self.file_path}")

    def close_spider(self, spider):
        """Close CSV file when spider closes."""
        if self.file:
            self.file.close()
        spider.logger.info(f"Exported {self.items_count} items to {self.file_path}")

    def process_item(self, item: dict, spider) -> dict:
        """Write item to CSV."""
        self.writer.writerow(item)
        self.items_count += 1
        return item


class JSONLinesExportPipeline:
    """
    Export items to JSON Lines file (one JSON object per line).

    Settings:
        JSONL_EXPORT_PATH: Path to JSONL file
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file = None
        self.items_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize from settings."""
        file_path = crawler.settings.get('JSONL_EXPORT_PATH', 'output.jsonl')
        return cls(file_path)

    def open_spider(self, spider):
        """Open JSONL file."""
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.file_path, 'w', encoding='utf-8')
        spider.logger.info(f"Exporting to JSONL: {self.file_path}")

    def close_spider(self, spider):
        """Close JSONL file."""
        if self.file:
            self.file.close()
        spider.logger.info(f"Exported {self.items_count} items to {self.file_path}")

    def process_item(self, item: dict, spider) -> dict:
        """Write item as JSON line."""
        line = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(line + '\n')
        self.items_count += 1
        return item
```

### 6. Image Download Pipeline

**Purpose**: Download and process images

```python
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from urllib.parse import urlparse
from pathlib import Path


class CustomImagesPipeline(ImagesPipeline):
    """
    Download product images with custom naming.

    Settings:
        IMAGES_STORE: Directory to save images
        IMAGES_MIN_HEIGHT: Minimum image height
        IMAGES_MIN_WIDTH: Minimum image width
    """

    def get_media_requests(self, item, info):
        """Generate requests for image URLs."""
        image_urls = item.get('image_urls', [])

        # Handle single image_url field
        if 'image_url' in item and item['image_url']:
            image_urls = [item['image_url']]

        for image_url in image_urls:
            # Pass item metadata to the request
            yield scrapy.Request(
                image_url,
                meta={'item': item}
            )

    def file_path(self, request, response=None, info=None, *, item=None):
        """Generate custom file path for images."""
        # Get item from request meta
        item = request.meta.get('item', {})

        # Extract filename from URL
        url_path = urlparse(request.url).path
        filename = Path(url_path).name

        # Create custom path: category/product_id/filename
        category = item.get('category', 'uncategorized')
        product_id = item.get('id', 'unknown')

        return f"{category}/{product_id}/{filename}"

    def item_completed(self, results, item, info):
        """Process completed image downloads."""
        # results is a list of (success, image_info) tuples

        # Filter successful downloads
        image_paths = [x['path'] for ok, x in results if ok]

        if not image_paths:
            raise DropItem("No images downloaded")

        # Add image paths to item
        item['images'] = image_paths
        item['images_count'] = len(image_paths)

        return item
```

## Advanced Pipeline Patterns

### 7. Conditional Pipeline

```python
class ConditionalPipeline:
    """Process items conditionally based on spider or item data."""

    def process_item(self, item: dict, spider) -> dict:
        """Process item based on conditions."""
        # Only process items from specific spider
        if spider.name == 'product_spider':
            # Apply product-specific processing
            item = self.process_product(item)

        # Only process items with certain category
        if item.get('category') == 'electronics':
            item = self.process_electronics(item)

        return item

    def process_product(self, item: dict) -> dict:
        """Product-specific processing."""
        # Add computed fields
        if 'price' in item and 'discount_percentage' in item:
            item['final_price'] = item['price'] * (1 - item['discount_percentage'] / 100)
        return item

    def process_electronics(self, item: dict) -> dict:
        """Electronics-specific processing."""
        # Add warranty information
        item['warranty'] = '1 year'
        return item
```

### 8. Retry Pipeline

```python
from scrapy.exceptions import DropItem
import time


class RetryPipeline:
    """Retry failed pipeline operations."""

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            max_retries=crawler.settings.get('PIPELINE_MAX_RETRIES', 3),
            retry_delay=crawler.settings.get('PIPELINE_RETRY_DELAY', 1.0),
        )

    def process_item(self, item: dict, spider) -> dict:
        """Process item with retry logic."""
        for attempt in range(self.max_retries):
            try:
                # Your processing logic here
                result = self.risky_operation(item)
                return result
            except Exception as e:
                spider.logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise DropItem(f"Failed after {self.max_retries} attempts: {e}")

    def risky_operation(self, item: dict) -> dict:
        """Placeholder for operation that might fail."""
        # Your code here
        return item
```

## Complete Pipeline Example

```python
# pipelines.py
from scrapy.exceptions import DropItem
import json


class CompletePipeline:
    """
    Complete pipeline with all stages:
    1. Validation
    2. Cleaning
    3. Transformation
    4. Storage
    """

    def __init__(self, output_file: str):
        self.output_file = output_file
        self.file = None
        self.stats = {
            'processed': 0,
            'dropped': 0,
            'saved': 0,
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_file=crawler.settings.get('OUTPUT_FILE', 'items.jsonl')
        )

    def open_spider(self, spider):
        """Initialize pipeline."""
        self.file = open(self.output_file, 'w', encoding='utf-8')
        spider.logger.info("Pipeline opened")

    def close_spider(self, spider):
        """Cleanup and log statistics."""
        if self.file:
            self.file.close()
        spider.logger.info(f"Pipeline stats: {self.stats}")

    def process_item(self, item: dict, spider) -> dict:
        """Process item through all stages."""
        self.stats['processed'] += 1

        try:
            # 1. Validate
            item = self.validate(item)

            # 2. Clean
            item = self.clean(item)

            # 3. Transform
            item = self.transform(item)

            # 4. Save
            self.save(item)
            self.stats['saved'] += 1

            return item

        except DropItem as e:
            self.stats['dropped'] += 1
            spider.logger.debug(f"Item dropped: {e}")
            raise

    def validate(self, item: dict) -> dict:
        """Validate item."""
        required = ['title', 'url']
        if not all(item.get(field) for field in required):
            raise DropItem("Missing required fields")
        return item

    def clean(self, item: dict) -> dict:
        """Clean item data."""
        if 'title' in item:
            item['title'] = item['title'].strip()
        return item

    def transform(self, item: dict) -> dict:
        """Transform item."""
        # Add computed fields
        if 'price' in item:
            item['price_usd'] = float(item['price'])
        return item

    def save(self, item: dict):
        """Save item to file."""
        line = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(line + '\n')
```

## When to Use This Skill

Use this skill when:
- Creating data processing pipelines
- Implementing validation logic
- Setting up data export workflows
- Integrating with databases
- Processing and cleaning scraped data
- Handling images and media files

## Integration with Commands and Agents

**Commands**:
- `/pipeline <type>` - Generate pipeline of specific type
- `/export <format>` - Configure export pipeline

**Agents**:
- `@scrapy-expert` - Reviews pipeline design
- `@data-validator` - Ensures proper validation
- `@performance-optimizer` - Optimizes pipeline performance

This skill automates pipeline creation while ensuring data quality, proper error handling, and efficient storage.
