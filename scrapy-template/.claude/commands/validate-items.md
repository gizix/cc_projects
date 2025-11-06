---
description: Check item schema compliance and validate scraped data quality
argument-hint: [output_file.json] [--schema items.py] [--strict]
allowed-tools: Bash(*), Read(*), Write(*)
---

Validate scraped items against defined schemas and check data quality.

Arguments:
- $1: Output file to validate (JSON/JSONL format)
- $2: Schema file (optional, defaults to items.py)
- $3: Validation mode (--strict for strict validation)

Common usage patterns:
- `/validate-items output.json` - Validate against items.py schema
- `/validate-items data.jsonl --strict` - Strict validation mode
- `/validate-items output.json --schema custom_schema.py` - Custom schema
- `/validate-items output.json --report validation_report.html` - Generate report

Process:

1. **Load Scraped Data**:
```python
import json

def load_items(file_path):
    """Load items from JSON or JSONL file."""
    items = []

    with open(file_path, 'r', encoding='utf-8') as f:
        if file_path.endswith('.jsonl') or file_path.endswith('.jl'):
            # JSON Lines format
            for line in f:
                if line.strip():
                    items.append(json.loads(line))
        else:
            # Regular JSON
            data = json.load(f)
            if isinstance(data, list):
                items = data
            else:
                items = [data]

    return items
```

2. **Load Item Schema**:
```python
import importlib.util
import scrapy

def load_schema(schema_file='items.py'):
    """Load and extract item classes from schema file."""

    # Import items module
    spec = importlib.util.spec_from_file_location("items", schema_file)
    items_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(items_module)

    # Find all Scrapy Item classes
    item_classes = {}
    for name in dir(items_module):
        obj = getattr(items_module, name)
        if (isinstance(obj, type) and
            issubclass(obj, scrapy.Item) and
            obj is not scrapy.Item):
            item_classes[name] = obj

    return item_classes
```

3. **Validate Schema Compliance**:
```python
def validate_schema(items, item_class):
    """Validate items against Scrapy Item schema."""

    errors = []
    warnings = []

    for idx, item_data in enumerate(items):
        item_errors = []

        # Check all required fields are present
        for field_name, field in item_class.fields.items():
            if field_name not in item_data:
                # Check if field is required
                required = field.get('required', False)
                if required:
                    item_errors.append({
                        'item_index': idx,
                        'field': field_name,
                        'error': 'Missing required field',
                        'severity': 'error'
                    })
                else:
                    warnings.append({
                        'item_index': idx,
                        'field': field_name,
                        'error': 'Optional field missing',
                        'severity': 'warning'
                    })

        # Check for unexpected fields
        defined_fields = set(item_class.fields.keys())
        actual_fields = set(item_data.keys())
        unexpected = actual_fields - defined_fields

        if unexpected:
            item_errors.append({
                'item_index': idx,
                'fields': list(unexpected),
                'error': 'Unexpected fields not in schema',
                'severity': 'warning'
            })

        errors.extend(item_errors)

    return errors, warnings
```

4. **Validate Data Quality**:
```python
def validate_data_quality(items, strict=False):
    """Check data quality: nulls, empty strings, formats, etc."""

    issues = []

    for idx, item in enumerate(items):
        for field, value in item.items():
            # Check for None/null values
            if value is None:
                issues.append({
                    'item_index': idx,
                    'field': field,
                    'issue': 'Null value',
                    'severity': 'error' if strict else 'warning'
                })

            # Check for empty strings
            elif isinstance(value, str) and not value.strip():
                issues.append({
                    'item_index': idx,
                    'field': field,
                    'issue': 'Empty string',
                    'severity': 'warning'
                })

            # Check URL format
            elif field in ['url', 'link', 'href', 'image_url']:
                if not is_valid_url(value):
                    issues.append({
                        'item_index': idx,
                        'field': field,
                        'value': value,
                        'issue': 'Invalid URL format',
                        'severity': 'error'
                    })

            # Check price format
            elif field in ['price', 'cost', 'amount']:
                if not is_valid_price(value):
                    issues.append({
                        'item_index': idx,
                        'field': field,
                        'value': value,
                        'issue': 'Invalid price format',
                        'severity': 'warning'
                    })

            # Check date format
            elif field in ['date', 'created_at', 'published_date']:
                if not is_valid_date(value):
                    issues.append({
                        'item_index': idx,
                        'field': field,
                        'value': value,
                        'issue': 'Invalid date format',
                        'severity': 'warning'
                    })

    return issues
```

5. **Check for Duplicates**:
```python
def check_duplicates(items, unique_fields=['url']):
    """Check for duplicate items based on unique fields."""

    duplicates = []
    seen = {}

    for idx, item in enumerate(items):
        # Create key from unique fields
        key = tuple(item.get(field) for field in unique_fields)

        if key in seen:
            duplicates.append({
                'item_index': idx,
                'duplicate_of': seen[key],
                'key_fields': unique_fields,
                'key_values': key,
            })
        else:
            seen[key] = idx

    return duplicates
```

6. **Generate Validation Report**:

```
Data Validation Report
======================

File: output.json
Items: 1,234
Validation Date: 2025-11-05 10:30:00

Schema Validation
-----------------
  Schema: ProductItem
  Required Fields: name, price, url, description

  ✓ Schema Compliance: 98.5% (1,215/1,234 items)

  Errors (19 items):
    • Item #45: Missing required field 'price'
    • Item #123: Missing required field 'url'
    • Item #456: Missing required field 'description'
    ... (16 more)

Data Quality Check
------------------
  ✓ Valid URLs: 100% (1,234/1,234)
  ⚠ Empty values: 2.3% (28 items have empty strings)
  ⚠ Null values: 1.5% (19 items have null fields)
  ✓ Valid prices: 99.2% (1,224/1,234)

  Issues Found:
    • Item #67: Empty string in 'description' field
    • Item #89: Null value in 'image_url' field
    • Item #234: Invalid price format: 'N/A'
    ... (25 more)

Duplicate Check
---------------
  Unique Fields: ['url']

  ✓ No duplicates found

Data Statistics
---------------
  Field Completeness:
    • name:        100.0% (1,234/1,234)
    • price:       98.5%  (1,215/1,234)
    • url:         99.8%  (1,232/1,234)
    • description: 96.2%  (1,187/1,234)
    • image_url:   85.3%  (1,053/1,234)

  Value Distributions:
    • price range: $0.99 - $9,999.99
    • avg price: $49.99
    • unique URLs: 1,232

Overall Score: 96.5/100

Recommendations
---------------
  1. Fix 19 items missing required fields
  2. Handle empty description fields (28 items)
  3. Validate price format for 10 items
  4. Consider making 'image_url' optional (low completion rate)
```

Validation Helpers:

```python
import re
from datetime import datetime
from urllib.parse import urlparse

def is_valid_url(url):
    """Check if string is a valid URL."""
    if not isinstance(url, str):
        return False

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_valid_price(price):
    """Check if price is in valid format."""
    if price is None:
        return False

    if isinstance(price, (int, float)):
        return price >= 0

    if isinstance(price, str):
        # Remove currency symbols and check if numeric
        clean = re.sub(r'[$€£¥,]', '', price.strip())
        try:
            return float(clean) >= 0
        except ValueError:
            return False

    return False

def is_valid_date(date_str):
    """Check if string is a valid date."""
    if not isinstance(date_str, str):
        return False

    # Try common date formats
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y-%m-%dT%H:%M:%S',
    ]

    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue

    return False

def calculate_completeness(items, field):
    """Calculate field completeness percentage."""
    total = len(items)
    complete = sum(1 for item in items if field in item and item[field])
    return (complete / total * 100) if total > 0 else 0
```

Advanced Validation:

**Custom Validators**:
```python
class ItemValidator:
    def __init__(self, item_class):
        self.item_class = item_class
        self.validators = {}

    def add_validator(self, field, validator_func):
        """Add custom validator for field."""
        self.validators[field] = validator_func

    def validate(self, item):
        """Run all validators on item."""
        errors = []

        for field, validator in self.validators.items():
            if field in item:
                try:
                    if not validator(item[field]):
                        errors.append(f"Validation failed for {field}")
                except Exception as e:
                    errors.append(f"Validation error for {field}: {e}")

        return errors

# Usage:
validator = ItemValidator(ProductItem)
validator.add_validator('price', lambda x: float(x) > 0)
validator.add_validator('url', is_valid_url)
```

**Statistical Analysis**:
```python
def analyze_data_distribution(items):
    """Analyze statistical distribution of data."""
    import statistics

    analysis = {}

    # Numeric fields
    numeric_fields = ['price', 'rating', 'reviews_count']

    for field in numeric_fields:
        values = [float(item[field]) for item in items
                  if field in item and item[field] is not None]

        if values:
            analysis[field] = {
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            }

    return analysis
```

HTML Report Generation:

```python
def generate_html_report(validation_results, output_file='validation_report.html'):
    """Generate interactive HTML validation report."""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Validation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .error {{ color: red; }}
            .warning {{ color: orange; }}
            .success {{ color: green; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
        </style>
    </head>
    <body>
        <h1>Data Validation Report</h1>

        <h2>Summary</h2>
        <ul>
            <li>Total Items: {validation_results['total_items']}</li>
            <li>Valid Items: <span class="success">{validation_results['valid_items']}</span></li>
            <li>Items with Errors: <span class="error">{validation_results['error_count']}</span></li>
            <li>Items with Warnings: <span class="warning">{validation_results['warning_count']}</span></li>
        </ul>

        <!-- Add detailed tables, charts, etc. -->
    </body>
    </html>
    """

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
```

After Validation:

1. **Show summary of issues**
2. **Provide actionable fixes**:
   - Re-run spider with updated selectors
   - Add item loaders for data cleaning
   - Implement item pipelines for validation
3. **Export issues** to CSV for review
4. **Suggest schema updates** if many items fail

Best Practices:
- Define item schemas in items.py
- Use Item Loaders for data cleaning
- Implement validation in pipelines
- Set up automated validation in CI/CD
- Track validation metrics over time
- Document expected data formats
- Handle missing data gracefully
- Validate during development, not just after

Next Steps:
- Fix identified issues in spider
- Update item schema if needed
- Add item pipeline validators
- Re-run spider: `/run-spider`
- Export clean data: `/export-data`
