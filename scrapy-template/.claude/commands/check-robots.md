---
description: Verify robots.txt compliance and crawl permissions for URL
argument-hint: <url> [--user-agent USER_AGENT]
allowed-tools: Bash(*), Read(*)
---

Check robots.txt file and verify if your spider is allowed to crawl specific URLs.

Arguments:
- $1: URL to check (required)
- $2: Custom user agent (optional, defaults to project settings)

Common usage patterns:
- `/check-robots https://example.com` - Check robots.txt for domain
- `/check-robots https://example.com/page` - Check if specific URL is allowed
- `/check-robots https://example.com --user-agent MyBot/1.0` - Check with custom UA

Process:

1. **Fetch and Parse robots.txt**:
```python
import urllib.robotparser
from urllib.parse import urlparse

url = '$1'
parsed_url = urlparse(url)
robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

# Create parser
rp = urllib.robotparser.RobotFileParser()
rp.set_url(robots_url)

try:
    rp.read()
    print(f"Successfully fetched: {robots_url}\n")
except Exception as e:
    print(f"Error fetching robots.txt: {e}")
    exit(1)
```

2. **Check URL Permissions**:
```python
# Get user agent from settings or argument
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
user_agent = '$2' if '$2' else settings.get('USER_AGENT', 'Scrapy')

# Check if allowed
can_fetch = rp.can_fetch(user_agent, url)

if can_fetch:
    print(f"✓ ALLOWED: '{user_agent}' can crawl {url}")
else:
    print(f"✗ DISALLOWED: '{user_agent}' cannot crawl {url}")
```

3. **Display robots.txt Content**:
```python
import requests

response = requests.get(robots_url)
if response.status_code == 200:
    print("\n--- robots.txt content ---")
    print(response.text)
    print("--- end of robots.txt ---\n")
else:
    print(f"robots.txt not found (HTTP {response.status_code})")
```

4. **Parse and Display Rules**:
```python
# Show applicable rules for user agent
print(f"\nRules for user agent: {user_agent}")
print("-" * 50)

lines = response.text.split('\n')
current_ua = None
relevant_rules = []

for line in lines:
    line = line.strip()

    if line.lower().startswith('user-agent:'):
        ua = line.split(':', 1)[1].strip()
        current_ua = ua

    elif current_ua and (current_ua == '*' or user_agent.lower() in current_ua.lower()):
        if line.lower().startswith(('disallow:', 'allow:')):
            relevant_rules.append(line)

if relevant_rules:
    for rule in relevant_rules:
        print(f"  {rule}")
else:
    print("  No specific rules (all allowed)")
```

5. **Check Crawl Delay**:
```python
# Get crawl delay recommendation
crawl_delay = rp.crawl_delay(user_agent)

if crawl_delay:
    print(f"\n⏱ Crawl-delay: {crawl_delay} seconds")
    print(f"  Recommendation: Set DOWNLOAD_DELAY={crawl_delay} in settings.py")
else:
    print("\n⏱ No crawl-delay specified")
    print("  Recommendation: Use default delay or AutoThrottle")
```

6. **Check Sitemap**:
```python
# Look for sitemap URLs in robots.txt
sitemaps = []
for line in lines:
    if line.lower().startswith('sitemap:'):
        sitemap_url = line.split(':', 1)[1].strip()
        sitemaps.append(sitemap_url)

if sitemaps:
    print("\n📋 Sitemaps found:")
    for sitemap in sitemaps:
        print(f"  {sitemap}")
    print("\n  You can use sitemaps to discover URLs:")
    print("  Add to spider: start_urls = [sitemap_url]")
```

Output Report:

Provide a comprehensive report:

```
Robots.txt Check for: https://example.com
================================================

Status: ALLOWED ✓
User-Agent: MyBot/1.0

Applicable Rules:
  Disallow: /admin/
  Disallow: /private/
  Allow: /public/

Crawl Delay: 1 second
  » Set DOWNLOAD_DELAY=1 in settings.py

Sitemaps:
  https://example.com/sitemap.xml
  https://example.com/sitemap_index.xml

Recommendations:
  ✓ Respecting robots.txt is enabled (ROBOTSTXT_OBEY=True)
  • Add crawl delay to avoid overloading server
  • Check sitemap for efficient crawling
  • Consider using AutoThrottle extension

Testing Specific Paths:
  https://example.com/             → ALLOWED ✓
  https://example.com/admin/       → DISALLOWED ✗
  https://example.com/public/page  → ALLOWED ✓
```

Advanced Checks:

**Test Multiple URLs**:
```python
test_urls = [
    'https://example.com/',
    'https://example.com/products/',
    'https://example.com/admin/',
    'https://example.com/api/',
]

print("\nTesting multiple paths:")
print("-" * 50)
for test_url in test_urls:
    allowed = rp.can_fetch(user_agent, test_url)
    status = "✓ ALLOWED" if allowed else "✗ DISALLOWED"
    print(f"{status:15} {test_url}")
```

**Compare User Agents**:
```python
user_agents = [
    'Googlebot',
    'Scrapy',
    '*',
    settings.get('USER_AGENT', 'Custom'),
]

print("\nPermissions by user agent:")
print("-" * 50)
for ua in user_agents:
    allowed = rp.can_fetch(ua, url)
    status = "✓" if allowed else "✗"
    print(f"{status} {ua:20} → {url}")
```

Best Practices Reminder:

1. **Always Respect robots.txt**:
   - Keep `ROBOTSTXT_OBEY=True` in settings.py
   - Honor crawl-delay directives
   - Don't crawl disallowed paths

2. **Be a Good Bot**:
   - Identify yourself with descriptive USER_AGENT
   - Add download delays between requests
   - Use AutoThrottle for dynamic rate limiting
   - Don't overwhelm servers with concurrent requests

3. **Use Sitemaps**:
   - Sitemaps provide efficient URL discovery
   - Often more complete than link crawling
   - Respect sitemap priorities and change frequencies

4. **Monitor and Adapt**:
   - Check robots.txt periodically (it may change)
   - Respect rate limits and 429 responses
   - Stop crawling if you receive blocking signals

Settings Recommendations:

Based on robots.txt, update `settings.py`:

```python
# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Set download delay (from Crawl-delay directive)
DOWNLOAD_DELAY = 1  # seconds

# Or use AutoThrottle for dynamic adjustment
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Identify your bot
USER_AGENT = 'MyBot/1.0 (+https://mysite.com/bot)'
```

Common Robots.txt Patterns:

**Disallow All**:
```
User-agent: *
Disallow: /
```
This means: Don't crawl this site with automated tools.

**Allow All**:
```
User-agent: *
Disallow:
```
This means: Crawl freely (but still be respectful).

**Specific Paths**:
```
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/
```

**Wildcard Patterns**:
```
User-agent: *
Disallow: /*?  # Disallow URLs with query parameters
Disallow: /*.pdf$  # Disallow PDFs
```

Next Steps:
- Update spider settings based on recommendations
- Add crawl delays to respect server resources
- Use discovered sitemaps for URL discovery
- Test spider: `/run-spider`
- Monitor crawl behavior for compliance

Common Issues:
- 404 on robots.txt: Website doesn't have one (all allowed)
- Overly restrictive rules: Contact site owner if needed
- Crawl-delay too high: May slow down crawling significantly
- Changing rules: Check regularly or cache robots.txt checks
