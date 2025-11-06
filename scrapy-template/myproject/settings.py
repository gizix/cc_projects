"""Scrapy settings for myproject project.

For simplicity, this file contains only settings considered important or
commonly used. You can find more settings consulting the documentation:

    https://docs.scrapy.org/en/latest/topics/settings.html
    https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
    https://docs.scrapy.org/en/latest/topics/spider-middleware.html
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_NAME = os.getenv("SCRAPY_PROJECT", "myproject")

SPIDER_MODULES = ["myproject.spiders"]
NEWSPIDER_MODULE = "myproject.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "myproject (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = os.getenv("ROBOTSTXT_OBEY", "true").lower() == "true"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", 16))

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = float(os.getenv("DOWNLOAD_DELAY", 1.0))

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "myproject.middlewares.MyprojectSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # Disable default User-Agent middleware
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    # Enable fake user agent middleware
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
    "scrapy_fake_useragent.middleware.RetryUserAgentMiddleware": 401,
    # Custom middlewares
    "myproject.middlewares.CustomHeadersMiddleware": 500,
}

# Fake User Agent settings
FAKEUSERAGENT_PROVIDERS = [
    "scrapy_fake_useragent.providers.FakeUserAgentProvider",
    "scrapy_fake_useragent.providers.FakerProvider",
    "scrapy_fake_useragent.providers.FixedUserAgentProvider",
]

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
    "scrapy.extensions.memusage.MemoryUsage": 1,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "myproject.pipelines.ValidationPipeline": 100,
    "myproject.pipelines.DuplicateFilterPipeline": 200,
    "myproject.pipelines.DatabasePipeline": 300,
    "myproject.pipelines.FileExportPipeline": 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = os.getenv("AUTOTHROTTLE_ENABLED", "true").lower() == "true"
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = os.getenv("HTTPCACHE_ENABLED", "false").lower() == "true"
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Feed exports
FEEDS = {
    "data/json/%(name)s_%(time)s.json": {
        "format": "json",
        "encoding": "utf8",
        "store_empty": False,
        "indent": 4,
        "overwrite": False,
    },
    "data/csv/%(name)s_%(time)s.csv": {
        "format": "csv",
        "encoding": "utf8",
        "store_empty": False,
        "overwrite": False,
    },
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/scrapy.log"
LOG_ENCODING = "utf-8"

# Memory usage settings
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = int(os.getenv("MEMUSAGE_LIMIT_MB", 512))
MEMUSAGE_WARNING_MB = 256

# Depth limit
DEPTH_LIMIT = 3

# Request timeouts
DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", 30))
DNS_TIMEOUT = int(os.getenv("DNS_TIMEOUT", 10))

# Playwright settings (for JavaScript rendering)
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = os.getenv("PLAYWRIGHT_BROWSER", "chromium")
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true",
}

# Twisted Reactor
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://scrapy:changeme@localhost:5432/scrapy")

# MongoDB settings
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "scrapy")

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
