"""Spider and downloader middlewares.

Middlewares can be used to process requests before they are sent and
responses before they are passed to spiders.
"""

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import logging
import random

logger = logging.getLogger(__name__)


class MyprojectSpiderMiddleware:
    """Spider middleware example.

    Spider middleware processes spider input (responses) and output (items and requests).
    """

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler."""
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def process_spider_input(self, response, spider):
        """Process response before passing to spider callback."""
        return None

    def process_spider_output(self, response, result, spider):
        """Process spider output (items and requests)."""
        for item in result:
            yield item

    def process_spider_exception(self, response, exception, spider):
        """Handle exceptions raised during spider processing."""
        logger.error(f"Spider exception: {exception}")

    def process_start_requests(self, start_requests, spider):
        """Process spider start requests."""
        for request in start_requests:
            yield request

    def spider_opened(self, spider):
        """Called when spider opens."""
        logger.info(f"Spider opened: {spider.name}")


class CustomHeadersMiddleware:
    """Add custom headers to requests."""

    def __init__(self, headers=None):
        self.headers = headers or {}

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler settings."""
        headers = crawler.settings.get('CUSTOM_HEADERS', {})
        return cls(headers=headers)

    def process_request(self, request, spider):
        """Add custom headers to request."""
        for header, value in self.headers.items():
            request.headers[header] = value


class RandomUserAgentMiddleware:
    """Rotate user agents from a list (alternative to scrapy-fake-useragent)."""

    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler settings."""
        user_agents = crawler.settings.get('USER_AGENT_LIST', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        ])

        if not user_agents:
            raise NotConfigured('USER_AGENT_LIST is empty')

        return cls(user_agents=user_agents)

    def process_request(self, request, spider):
        """Set random user agent for request."""
        request.headers['User-Agent'] = random.choice(self.user_agents)


class ProxyMiddleware:
    """Proxy middleware for rotating proxies."""

    def __init__(self, proxy_list):
        self.proxy_list = proxy_list

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler settings."""
        proxy_list = crawler.settings.get('PROXY_LIST', [])

        if not proxy_list:
            raise NotConfigured('PROXY_LIST is empty')

        return cls(proxy_list=proxy_list)

    def process_request(self, request, spider):
        """Set random proxy for request."""
        proxy = random.choice(self.proxy_list)
        request.meta['proxy'] = proxy
        logger.debug(f"Using proxy: {proxy}")


class CustomRetryMiddleware(RetryMiddleware):
    """Custom retry middleware with exponential backoff."""

    def __init__(self, settings):
        super().__init__(settings)
        self.max_retry_times = settings.getint('RETRY_TIMES', 3)
        self.retry_http_codes = set(settings.getlist('RETRY_HTTP_CODES', [500, 502, 503, 504, 408, 429]))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST', -1)

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler."""
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        """Process response and retry if needed."""
        if request.meta.get('dont_retry', False):
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            retry_times = request.meta.get('retry_times', 0) + 1

            # Exponential backoff
            delay = 2 ** retry_times

            logger.warning(
                f"Retrying {request.url} (status={response.status}), "
                f"retry_times={retry_times}, delay={delay}s"
            )

            if retry_times <= self.max_retry_times:
                request.meta['retry_times'] = retry_times
                request.meta['download_delay'] = delay
                return self._retry(request, reason, spider) or response

        return response


class RequestStatsMiddleware:
    """Track request statistics."""

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler."""
        middleware = cls(crawler.stats)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        """Track request."""
        self.stats.inc_value('custom/requests_sent')

    def process_response(self, request, response, spider):
        """Track response."""
        self.stats.inc_value(f'custom/response_status/{response.status}')
        return response

    def process_exception(self, request, exception, spider):
        """Track exceptions."""
        self.stats.inc_value('custom/exceptions')
        self.stats.inc_value(f'custom/exception_type/{type(exception).__name__}')

    def spider_opened(self, spider):
        """Initialize stats when spider opens."""
        logger.info("Request stats middleware initialized")

    def spider_closed(self, spider):
        """Log stats when spider closes."""
        logger.info("Request stats:")
        logger.info(f"  Requests sent: {self.stats.get_value('custom/requests_sent', 0)}")
        logger.info(f"  Exceptions: {self.stats.get_value('custom/exceptions', 0)}")


class CookieDebugMiddleware:
    """Debug middleware to log cookies."""

    def process_request(self, request, spider):
        """Log cookies in request."""
        cookies = request.headers.get('Cookie')
        if cookies:
            logger.debug(f"Request cookies for {request.url}: {cookies}")

    def process_response(self, request, response, spider):
        """Log cookies in response."""
        set_cookie = response.headers.get('Set-Cookie')
        if set_cookie:
            logger.debug(f"Response set cookie from {response.url}: {set_cookie}")
        return response
