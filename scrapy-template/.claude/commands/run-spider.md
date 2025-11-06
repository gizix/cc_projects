---
description: Run Scrapy spider with output format and settings
argument-hint: <spider_name> [-o output.json|csv|xml] [-s SETTING=VALUE]
allowed-tools: Bash(*), Read(*)
---

Execute a Scrapy spider with specified output format and custom settings.

Arguments:
- $ARGUMENTS: All arguments including spider name, output options, and settings

Common usage patterns:
- `/run-spider myspider` - Run spider with default settings
- `/run-spider myspider -o data.json` - Output to JSON file
- `/run-spider myspider -o data.csv` - Output to CSV file
- `/run-spider myspider -o data.xml` - Output to XML file
- `/run-spider myspider -s LOG_LEVEL=DEBUG` - Run with debug logging
- `/run-spider myspider -s CONCURRENT_REQUESTS=1` - Limit concurrency
- `/run-spider myspider -o data.json -s CLOSESPIDER_PAGECOUNT=100` - Limit pages

Execute: `scrapy crawl $ARGUMENTS`

Process:
1. Verify the spider exists by running `scrapy list`
2. If spider not found, suggest available spiders with `/list-spiders`
3. Execute the crawl command with provided arguments
4. Monitor the output for:
   - Items scraped count
   - Pages crawled count
   - Any errors or warnings
   - Response status codes
   - Crawl duration and speed

Output Format Options:
- `-o output.json` - JSON format (default, good for APIs)
- `-o output.jsonl` - JSON Lines (one item per line, better for large datasets)
- `-o output.csv` - CSV format (good for spreadsheets)
- `-o output.xml` - XML format
- `-o output.jl` - Same as jsonl
- Multiple outputs: `-o data.json -o data.csv`

Common Settings Override:
- `-s LOG_LEVEL=DEBUG` - Enable debug logging
- `-s LOG_LEVEL=INFO` - Default logging level
- `-s CONCURRENT_REQUESTS=1` - Disable concurrency for debugging
- `-s CONCURRENT_REQUESTS=16` - Increase concurrency (default: 16)
- `-s DOWNLOAD_DELAY=2` - Add 2 second delay between requests
- `-s CLOSESPIDER_PAGECOUNT=100` - Stop after 100 pages
- `-s CLOSESPIDER_ITEMCOUNT=1000` - Stop after 1000 items
- `-s ROBOTSTXT_OBEY=False` - Disable robots.txt (use carefully!)
- `-s USER_AGENT="Custom Agent"` - Override user agent

After execution:
1. Report crawl statistics:
   - Total items scraped
   - Total requests made
   - Success/failure rate
   - Average response time
   - Crawl duration
2. If output file specified, show file location and size
3. Display any errors or warnings encountered
4. Suggest optimizations if crawl was slow or had issues

Performance Monitoring:
- Watch for 400/500 status codes (may need to adjust selectors or handle errors)
- Check item_scraped_count vs request_count ratio
- Monitor memory usage for large crawls
- Look for redirect chains or retry attempts

Common Issues:
- "Spider not found" - Use `/list-spiders` to see available spiders
- "403 Forbidden" - May need custom headers or user agent
- "Offsite request filtered" - Check allowed_domains setting
- No items scraped - Use `/shell` to test selectors
- Memory issues - Use `-s JOBDIR=crawls/job1` to enable persistence

Next Steps:
- Validate scraped data: `/validate-items output.json`
- Export to database: `/export-data output.json --to database`
- Run tests: `/test-spider myspider`
- Check performance: `/benchmark myspider`

Best Practices:
- Always respect robots.txt in production
- Add download delays for respectful crawling
- Use AutoThrottle for automatic rate limiting
- Monitor server responses and adjust if needed
- Save output to files for later processing
- Use JOBDIR for resumable crawls on large sites
