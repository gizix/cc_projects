---
description: Run Scrapy performance benchmark and analyze crawl efficiency
argument-hint: [spider_name] [--pages 100] [--requests 1000]
allowed-tools: Bash(*), Read(*)
---

Execute a performance benchmark to measure spider speed, efficiency, and resource usage.

Arguments:
- $1: Spider name (optional, defaults to benchmark spider)
- $2: Number of pages to crawl (optional, default: 100)
- $3: Max concurrent requests (optional, default: from settings)

Common usage patterns:
- `/benchmark` - Run default benchmark
- `/benchmark myspider` - Benchmark specific spider
- `/benchmark myspider --pages 100` - Benchmark with page limit
- `/benchmark --requests 16` - Test with specific concurrency

Process:

1. **Run Scrapy Benchmark Spider**:

Create a simple benchmark spider if not exists:
```python
# Create benchmark_spider.py
import scrapy

class BenchmarkSpider(scrapy.Spider):
    name = 'benchmark'

    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100,
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': False,  # For benchmark only
    }

    start_urls = ['http://toscrape.com']

    def parse(self, response):
        # Extract some data to simulate real crawling
        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'links': len(response.css('a::attr(href)').getall()),
        }

        # Follow links
        for href in response.css('a::attr(href)').getall()[:10]:
            yield response.follow(href, self.parse)
```

2. **Execute Benchmark**:
```bash
# Run with stats collection
scrapy crawl benchmark \
    -s CLOSESPIDER_PAGECOUNT=100 \
    -s CONCURRENT_REQUESTS=$requests \
    -s LOG_LEVEL=INFO \
    2>&1 | tee benchmark_output.log
```

3. **Parse and Display Statistics**:

Extract and analyze Scrapy stats from output:

```python
import re
import json

# Parse stats from output
stats = {}

# Key metrics to extract:
# - downloader/request_count
# - downloader/response_count
# - item_scraped_count
# - elapsed_time_seconds
# - downloader/response_bytes
# - downloader/request_bytes
# - response_received_count

# Calculate derived metrics:
stats['pages_per_second'] = stats['response_count'] / stats['elapsed_time']
stats['items_per_second'] = stats['item_count'] / stats['elapsed_time']
stats['avg_response_time'] = stats['elapsed_time'] / stats['response_count']
stats['success_rate'] = stats['response_count'] / stats['request_count'] * 100
```

4. **Display Performance Report**:

```
Scrapy Performance Benchmark Report
=====================================

Spider: myspider
Duration: 45.2 seconds
Date: 2025-11-05 10:30:00

Request Statistics:
-------------------
  Total Requests:        1,247
  Successful Responses:  1,234
  Failed Requests:       13
  Success Rate:          98.96%

Performance Metrics:
--------------------
  Pages/Second:          27.3
  Items/Second:          24.1
  Avg Response Time:     0.037s
  Total Items Scraped:   1,089

Network Statistics:
-------------------
  Data Downloaded:       15.3 MB
  Data Uploaded:         245 KB
  Avg Page Size:         12.7 KB

Concurrency:
------------
  Concurrent Requests:   16
  Download Delay:        0.0s
  AutoThrottle:          Enabled

Response Status Codes:
----------------------
  200 OK:                1,234 (98.96%)
  404 Not Found:         8 (0.64%)
  500 Server Error:      3 (0.24%)
  Other:                 2 (0.16%)

Memory & Resources:
-------------------
  Peak Memory Usage:     187 MB
  Avg CPU Usage:         23%

Efficiency Metrics:
-------------------
  Items per Request:     0.87
  Cache Hit Rate:        N/A
  Retry Rate:            1.04%
```

5. **Performance Analysis and Recommendations**:

Based on results, provide recommendations:

```python
recommendations = []

# Check pages per second
if stats['pages_per_second'] < 5:
    recommendations.append({
        'issue': 'Low throughput (< 5 pages/sec)',
        'suggestions': [
            'Increase CONCURRENT_REQUESTS (currently 8, try 16-32)',
            'Reduce or disable DOWNLOAD_DELAY',
            'Enable HTTP caching for development',
            'Check network latency to target servers',
        ]
    })

# Check success rate
if stats['success_rate'] < 95:
    recommendations.append({
        'issue': f'Low success rate ({stats["success_rate"]:.1f}%)',
        'suggestions': [
            'Review failed requests logs',
            'Check for rate limiting (429 responses)',
            'Verify selectors are correct',
            'Add retry middleware',
            'Increase DOWNLOAD_TIMEOUT',
        ]
    })

# Check items per request
if stats['items_per_request'] < 0.5:
    recommendations.append({
        'issue': 'Low item extraction rate',
        'suggestions': [
            'Verify parse method is yielding items',
            'Check if selectors are finding elements',
            'Test selectors in shell: /shell',
            'Review item pipeline for drops',
        ]
    })

# Check retry rate
if stats.get('retry_rate', 0) > 5:
    recommendations.append({
        'issue': 'High retry rate (> 5%)',
        'suggestions': [
            'Reduce CONCURRENT_REQUESTS',
            'Increase DOWNLOAD_DELAY',
            'Enable AutoThrottle',
            'Check server rate limits',
        ]
    })

# Memory usage
if stats['peak_memory_mb'] > 500:
    recommendations.append({
        'issue': 'High memory usage (> 500 MB)',
        'suggestions': [
            'Use iterator for large result sets',
            'Clear item references in pipelines',
            'Limit CONCURRENT_REQUESTS',
            'Check for memory leaks in custom code',
        ]
    })
```

6. **Comparison with Best Practices**:

```
Best Practice Checklist:
------------------------
  ✓ ROBOTSTXT_OBEY enabled
  ✓ Reasonable USER_AGENT set
  ✗ No DOWNLOAD_DELAY (consider adding 1-2 seconds)
  ✓ AutoThrottle enabled
  ~ CONCURRENT_REQUESTS=16 (acceptable, but monitor)
  ✓ Success rate > 95%
  ✗ No caching enabled (enable for development)
```

Alternative Benchmark Methods:

**1. Use Scrapy Bench Command** (if available):
```bash
scrapy bench
```

**2. Custom Benchmark Script**:
```python
# scripts/benchmark.py
import time
import statistics
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_benchmark(spider_name, iterations=3):
    results = []

    for i in range(iterations):
        print(f"\nRun {i+1}/{iterations}")

        settings = get_project_settings()
        settings['CLOSESPIDER_PAGECOUNT'] = 100

        process = CrawlerProcess(settings)

        start_time = time.time()
        process.crawl(spider_name)
        process.start()
        elapsed = time.time() - start_time

        results.append(elapsed)

    print("\nBenchmark Results:")
    print(f"Average time: {statistics.mean(results):.2f}s")
    print(f"Std deviation: {statistics.stdev(results):.2f}s")
    print(f"Min time: {min(results):.2f}s")
    print(f"Max time: {max(results):.2f}s")

if __name__ == '__main__':
    run_benchmark('myspider')
```

**3. Load Testing with Different Concurrency**:

Test with various CONCURRENT_REQUESTS values:

```bash
for concurrency in 1 4 8 16 32; do
    echo "Testing with CONCURRENT_REQUESTS=$concurrency"
    scrapy crawl myspider \
        -s CONCURRENT_REQUESTS=$concurrency \
        -s CLOSESPIDER_PAGECOUNT=100 \
        -o /dev/null \
        2>&1 | grep "elapsed"
done
```

Compare results to find optimal concurrency.

Settings for Optimal Performance:

```python
# settings.py

# Concurrency
CONCURRENT_REQUESTS = 16  # Adjust based on target server
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_ITEMS = 100

# Timeouts
DOWNLOAD_TIMEOUT = 180
DOWNLOAD_DELAY = 0  # Or 1-2 for respectful crawling

# AutoThrottle (recommended)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Caching (for development/testing)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Compression
COMPRESSION_ENABLED = True

# Cookies
COOKIES_ENABLED = True
```

Performance Monitoring Tools:

**1. Enable Stats Collection**:
```python
# settings.py
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# In spider or extension:
stats = spider.crawler.stats.get_stats()
```

**2. Use Scrapy Extensions**:
```python
# Custom stats extension
class PerformanceStats:
    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.stats)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_closed(self, spider):
        stats = self.stats.get_stats()
        # Log or save performance metrics
```

**3. External Monitoring**:
- Prometheus + Grafana for real-time monitoring
- Sentry for error tracking
- Custom logging to database/file

After Benchmark:

1. **Save Results**:
   - Log to file: `benchmark_results.log`
   - Save stats JSON: `benchmark_stats.json`
   - Compare with previous runs

2. **Identify Bottlenecks**:
   - Network latency
   - Parser inefficiency
   - Pipeline processing time
   - Database writes

3. **Optimize Based on Findings**:
   - Adjust concurrency settings
   - Add caching
   - Optimize selectors
   - Use faster parsers (lxml vs html.parser)

4. **Re-benchmark After Changes**:
   - Verify improvements
   - Ensure no regressions
   - Document optimal settings

Best Practices:
- Benchmark regularly as code changes
- Test with production-like data volumes
- Benchmark both speed and resource usage
- Compare different parser libraries
- Test with and without pipelines
- Monitor target server impact
- Document baseline performance
- Set performance budgets/targets

Common Performance Issues:
- Excessive DOM parsing - Use simple selectors
- No concurrency - Increase CONCURRENT_REQUESTS
- Download delays too high - Reduce or use AutoThrottle
- Synchronous database writes - Use async or batch
- Memory leaks - Profile and fix
- Inefficient selectors - Use CSS over complex XPath

Next Steps:
- Apply recommended optimizations
- Run production crawl: `/run-spider`
- Monitor real-world performance
- Set up continuous benchmarking in CI/CD
