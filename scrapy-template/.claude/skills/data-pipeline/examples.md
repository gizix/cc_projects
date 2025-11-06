# Pipeline Examples

Real-world examples of pipeline implementations.

## Example 1: E-commerce Pipeline

Complete pipeline for product scraping:

```python
# myproject/pipelines.py
from scrapy.exceptions import DropItem
import re

class EcommercePipeline:
    """Process e-commerce product data."""

    def process_item(self, item, spider):
        # Validate required fields
        if not item.get('title') or not item.get('price'):
            raise DropItem("Missing title or price")

        # Clean title
        item['title'] = item['title'].strip()

        # Parse and validate price
        price_str = item['price']
        price_match = re.search(r'[\d,]+\.?\d*', price_str)
        if price_match:
            item['price'] = float(price_match.group().replace(',', ''))
        else:
            raise DropItem(f"Invalid price format: {price_str}")

        # Ensure price is positive
        if item['price'] <= 0:
            raise DropItem("Price must be positive")

        # Add metadata
        item['scraped_at'] = spider.crawler.stats.get_value('start_time')

        return item
```

## Example 2: Multi-format Export

Export to multiple formats simultaneously:

```python
import json
import csv
from pathlib import Path

class MultiFormatExportPipeline:
    """Export items to JSON, CSV, and database."""

    def open_spider(self, spider):
        # Setup JSON file
        self.json_file = open('output.jsonl', 'w', encoding='utf-8')

        # Setup CSV file
        self.csv_file = open('output.csv', 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.DictWriter(
            self.csv_file,
            fieldnames=['title', 'price', 'url']
        )
        self.csv_writer.writeheader()

    def close_spider(self, spider):
        self.json_file.close()
        self.csv_file.close()

    def process_item(self, item, spider):
        # Write to JSON
        self.json_file.write(json.dumps(dict(item)) + '\n')

        # Write to CSV
        self.csv_writer.writerow(item)

        return item
```

## Example 3: Image Processing Pipeline

Download and process product images:

```python
from scrapy.pipelines.images import ImagesPipeline
from PIL import Image
import io

class ProductImagePipeline(ImagesPipeline):
    """Download and optimize product images."""

    def get_media_requests(self, item, info):
        for image_url in item.get('image_urls', []):
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        item['images'] = image_paths
        return item

    def process_image(self, image, spider):
        """Resize images to max 800x800."""
        img = Image.open(io.BytesIO(image))

        # Resize if needed
        if img.width > 800 or img.height > 800:
            img.thumbnail((800, 800), Image.LANCZOS)

        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
```

## Pipeline Order Configuration

```python
# settings.py
ITEM_PIPELINES = {
    'myproject.pipelines.ValidationPipeline': 100,
    'myproject.pipelines.CleaningPipeline': 200,
    'myproject.pipelines.DuplicatesPipeline': 300,
    'myproject.pipelines.ProductImagePipeline': 400,
    'myproject.pipelines.DatabasePipeline': 800,
    'myproject.pipelines.MultiFormatExportPipeline': 900,
}
```
