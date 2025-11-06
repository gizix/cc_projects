"""Item pipelines for processing scraped data.

Pipelines process items after they are scraped by spiders. Common uses:
- Validating scraped data
- Checking for duplicates and dropping duplicate items
- Storing items in databases
- Exporting to files
"""

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import pymongo
import json
import csv
import os
import hashlib
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class ValidationPipeline:
    """Validate required fields in scraped items."""

    def process_item(self, item, spider):
        """Validate item has required fields."""
        adapter = ItemAdapter(item)

        # Define required fields by item type
        required_fields = {
            'Product': ['name', 'price', 'url'],
            'Article': ['title', 'url', 'content'],
            'Review': ['product_id', 'content'],
            'JobListing': ['title', 'company', 'url'],
        }

        item_type = type(item).__name__
        if item_type in required_fields:
            for field in required_fields[item_type]:
                if not adapter.get(field):
                    raise DropItem(f"Missing required field '{field}' in {item_type}: {item}")

        return item


class DuplicateFilterPipeline:
    """Filter out duplicate items based on URL or unique identifier."""

    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item, spider):
        """Check if item is duplicate based on URL or ID."""
        adapter = ItemAdapter(item)

        # Try to get unique identifier
        unique_id = adapter.get('url') or adapter.get('product_id') or adapter.get('sku')

        if not unique_id:
            # If no unique ID, generate hash from item content
            item_str = json.dumps(dict(adapter), sort_keys=True, default=str)
            unique_id = hashlib.md5(item_str.encode()).hexdigest()

        if unique_id in self.seen_ids:
            raise DropItem(f"Duplicate item found: {unique_id}")
        else:
            self.seen_ids.add(unique_id)
            return item


class DatabasePipeline:
    """Store items in PostgreSQL database using SQLAlchemy."""

    def __init__(self, database_url):
        self.database_url = database_url
        self.engine = None
        self.Session = None

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler settings."""
        return cls(
            database_url=crawler.settings.get('DATABASE_URL')
        )

    def open_spider(self, spider):
        """Initialize database connection when spider opens."""
        try:
            self.engine = create_engine(self.database_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.engine = None

    def close_spider(self, spider):
        """Close database connection when spider closes."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

    def process_item(self, item, spider):
        """Store item in database."""
        if not self.engine:
            logger.warning("Database not available, skipping item storage")
            return item

        session = self.Session()
        try:
            # Convert item to database model
            # This is a simplified example - adapt to your data models
            adapter = ItemAdapter(item)
            item_dict = dict(adapter)

            # Store based on item type
            # Add your database models and storage logic here

            session.commit()
            logger.debug(f"Stored item in database: {item_dict.get('url', 'unknown')}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing item in database: {e}")
        finally:
            session.close()

        return item


class MongoPipeline:
    """Store items in MongoDB."""

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler settings."""
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        """Initialize MongoDB connection when spider opens."""
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            logger.info(f"Connected to MongoDB database: {self.mongo_db}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None

    def close_spider(self, spider):
        """Close MongoDB connection when spider closes."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def process_item(self, item, spider):
        """Store item in MongoDB."""
        if not self.client:
            logger.warning("MongoDB not available, skipping item storage")
            return item

        try:
            adapter = ItemAdapter(item)
            item_dict = dict(adapter)

            # Convert datetime objects to ISO format strings
            for key, value in item_dict.items():
                if isinstance(value, datetime):
                    item_dict[key] = value.isoformat()

            # Store in collection named after item type
            collection_name = type(item).__name__.lower() + 's'
            collection = self.db[collection_name]

            # Insert or update based on unique field
            unique_field = 'url' if 'url' in item_dict else '_id'
            if unique_field == 'url':
                collection.update_one(
                    {unique_field: item_dict[unique_field]},
                    {'$set': item_dict},
                    upsert=True
                )
            else:
                collection.insert_one(item_dict)

            logger.debug(f"Stored item in MongoDB: {item_dict.get('url', 'unknown')}")
        except Exception as e:
            logger.error(f"Error storing item in MongoDB: {e}")

        return item


class FileExportPipeline:
    """Export items to JSON or CSV files."""

    def __init__(self, export_dir, export_format):
        self.export_dir = export_dir
        self.export_format = export_format
        self.files = {}
        self.csv_writers = {}

    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler settings."""
        return cls(
            export_dir=crawler.settings.get('EXPORT_DIR', 'data'),
            export_format=crawler.settings.get('EXPORT_FORMAT', 'json')
        )

    def open_spider(self, spider):
        """Create export directory when spider opens."""
        os.makedirs(self.export_dir, exist_ok=True)
        logger.info(f"Export directory: {self.export_dir}")

    def close_spider(self, spider):
        """Close all file handles when spider closes."""
        for file_handle in self.files.values():
            file_handle.close()
        logger.info("Export files closed")

    def process_item(self, item, spider):
        """Export item to file."""
        item_type = type(item).__name__

        if self.export_format == 'json':
            self._export_json(item, item_type, spider)
        elif self.export_format == 'csv':
            self._export_csv(item, item_type, spider)

        return item

    def _export_json(self, item, item_type, spider):
        """Export item to JSON file."""
        filename = f"{self.export_dir}/{spider.name}_{item_type.lower()}s.jsonl"

        if filename not in self.files:
            self.files[filename] = open(filename, 'a', encoding='utf-8')

        adapter = ItemAdapter(item)
        item_dict = dict(adapter)

        # Convert datetime objects to ISO format
        for key, value in item_dict.items():
            if isinstance(value, datetime):
                item_dict[key] = value.isoformat()

        line = json.dumps(item_dict, ensure_ascii=False) + '\n'
        self.files[filename].write(line)

    def _export_csv(self, item, item_type, spider):
        """Export item to CSV file."""
        filename = f"{self.export_dir}/{spider.name}_{item_type.lower()}s.csv"
        adapter = ItemAdapter(item)
        item_dict = dict(adapter)

        # Convert datetime objects to ISO format
        for key, value in item_dict.items():
            if isinstance(value, datetime):
                item_dict[key] = value.isoformat()
            elif isinstance(value, list):
                item_dict[key] = ', '.join(str(v) for v in value)

        if filename not in self.files:
            self.files[filename] = open(filename, 'w', newline='', encoding='utf-8')
            self.csv_writers[filename] = csv.DictWriter(
                self.files[filename],
                fieldnames=item_dict.keys()
            )
            self.csv_writers[filename].writeheader()

        self.csv_writers[filename].writerow(item_dict)


class DataCleaningPipeline:
    """Clean and normalize data."""

    def process_item(self, item, spider):
        """Clean and normalize item data."""
        adapter = ItemAdapter(item)

        # Trim whitespace from string fields
        for field, value in adapter.items():
            if isinstance(value, str):
                adapter[field] = value.strip()

        # Convert empty strings to None
        for field, value in adapter.items():
            if value == '':
                adapter[field] = None

        # Ensure numeric fields are proper numbers
        if 'price' in adapter and adapter['price']:
            try:
                adapter['price'] = float(adapter['price'])
            except (ValueError, TypeError):
                adapter['price'] = 0.0

        return item
