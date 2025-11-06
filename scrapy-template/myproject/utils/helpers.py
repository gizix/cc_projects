"""Helper functions and utilities for spiders."""

import hashlib
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def clean_text(text):
    """Clean and normalize text by removing extra whitespace."""
    if not text:
        return ""
    return " ".join(text.split())


def extract_numbers(text):
    """Extract all numbers from text."""
    if not text:
        return []
    return [int(num) for num in re.findall(r'\d+', text)]


def generate_item_id(item_data):
    """Generate unique ID for an item based on its data."""
    item_str = str(sorted(item_data.items()))
    return hashlib.md5(item_str.encode()).hexdigest()


def is_valid_url(url):
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def make_absolute_url(base_url, relative_url):
    """Convert relative URL to absolute URL."""
    return urljoin(base_url, relative_url)


def parse_relative_date(date_string):
    """Parse relative dates like '2 days ago', 'yesterday', etc."""
    date_string = date_string.lower().strip()
    now = datetime.now()

    # Today
    if 'today' in date_string or 'just now' in date_string:
        return now

    # Yesterday
    if 'yesterday' in date_string:
        return now - timedelta(days=1)

    # X days/hours/minutes ago
    patterns = {
        r'(\d+)\s*minutes?\s*ago': lambda m: now - timedelta(minutes=int(m.group(1))),
        r'(\d+)\s*hours?\s*ago': lambda m: now - timedelta(hours=int(m.group(1))),
        r'(\d+)\s*days?\s*ago': lambda m: now - timedelta(days=int(m.group(1))),
        r'(\d+)\s*weeks?\s*ago': lambda m: now - timedelta(weeks=int(m.group(1))),
        r'(\d+)\s*months?\s*ago': lambda m: now - timedelta(days=int(m.group(1)) * 30),
        r'(\d+)\s*years?\s*ago': lambda m: now - timedelta(days=int(m.group(1)) * 365),
    }

    for pattern, calculator in patterns.items():
        match = re.search(pattern, date_string)
        if match:
            return calculator(match)

    return None


def extract_json_from_script(html_text, variable_name=None):
    """Extract JSON data from <script> tags."""
    import json

    if variable_name:
        # Extract specific JavaScript variable
        pattern = rf'{variable_name}\s*=\s*(\{{.*?\}})'
        match = re.search(pattern, html_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON for variable: {variable_name}")
                return None
    else:
        # Extract all JSON objects from script tags
        pattern = r'<script[^>]*>(.*?)</script>'
        matches = re.findall(pattern, html_text, re.DOTALL | re.IGNORECASE)

        json_objects = []
        for script_content in matches:
            try:
                # Try to find JSON objects in script content
                json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                for json_match in re.finditer(json_pattern, script_content):
                    try:
                        obj = json.loads(json_match.group())
                        json_objects.append(obj)
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                logger.debug(f"Error extracting JSON from script: {e}")
                continue

        return json_objects if json_objects else None


def sanitize_filename(filename):
    """Sanitize filename by removing invalid characters."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:max_length - len(ext) - 1] + '.' + ext if ext else name[:max_length]
    return filename


def rate_limit_delay(response_status, base_delay=1.0):
    """Calculate delay based on response status for rate limiting."""
    if response_status == 429:  # Too Many Requests
        return base_delay * 10
    elif response_status >= 500:  # Server errors
        return base_delay * 5
    return base_delay


def extract_price_from_text(text):
    """Extract price from text with currency symbols."""
    if not text:
        return None

    # Remove common currency symbols and formatting
    cleaned = re.sub(r'[$€£¥,\s]', '', text)

    # Extract price pattern
    match = re.search(r'(\d+\.?\d*)', cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None

    return None


def chunk_list(lst, chunk_size):
    """Split a list into chunks of specified size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def get_domain(url):
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc


def is_same_domain(url1, url2):
    """Check if two URLs are from the same domain."""
    return get_domain(url1) == get_domain(url2)


class RateLimiter:
    """Simple rate limiter to track request timing."""

    def __init__(self, max_requests=10, time_window=60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def is_allowed(self):
        """Check if request is allowed based on rate limit."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]

        # Check if under limit
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True

        return False

    def wait_time(self):
        """Calculate wait time in seconds before next request is allowed."""
        if not self.requests:
            return 0

        now = datetime.now()
        oldest = self.requests[0]
        cutoff = oldest + timedelta(seconds=self.time_window)

        if cutoff > now:
            return (cutoff - now).total_seconds()

        return 0
