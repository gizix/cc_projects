---
description: Export scraped data to various formats and databases
argument-hint: <input_file> --to <json|csv|excel|database|mongodb> [options]
allowed-tools: Bash(*), Read(*), Write(*)
---

Export and transform scraped data from one format to another or load into databases.

Arguments:
- $ARGUMENTS: Input file and export options

Common usage patterns:
- `/export-data data.json --to csv` - Convert JSON to CSV
- `/export-data data.jsonl --to excel` - Convert JSONL to Excel
- `/export-data data.json --to database` - Load into SQLite/PostgreSQL
- `/export-data data.json --to mongodb` - Load into MongoDB
- `/export-data data.csv --to json --pretty` - Convert CSV to formatted JSON
- `/export-data data.json --to database --table products` - Specify table name

Process:

**1. JSON to CSV Export**:
```python
import json
import csv

with open('data.json') as f:
    data = json.load(f)

# Flatten nested structures if needed
# Write to CSV
with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    if data:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
```

**2. JSON/JSONL to Excel**:
```python
import json
import pandas as pd

# Load JSON or JSONL
with open('data.jsonl') as f:
    data = [json.loads(line) for line in f]

# Create DataFrame
df = pd.DataFrame(data)

# Export to Excel
df.to_excel('output.xlsx', index=False, sheet_name='Scraped Data')
```

**3. Load into SQLite Database**:
```python
import json
import sqlite3
import pandas as pd

# Load data
with open('data.json') as f:
    data = json.load(f)

# Create DataFrame
df = pd.DataFrame(data)

# Connect to database
conn = sqlite3.connect('scraped_data.db')

# Write to table
table_name = 'products'  # or from arguments
df.to_sql(table_name, conn, if_exists='replace', index=False)

conn.close()
print(f"Loaded {len(df)} records into {table_name}")
```

**4. Load into PostgreSQL**:
```python
import json
import pandas as pd
from sqlalchemy import create_engine

# Load data
with open('data.json') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Connect to PostgreSQL (credentials from .env)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/dbname')
engine = create_engine(DATABASE_URL)

# Write to table
table_name = 'products'
df.to_sql(table_name, engine, if_exists='replace', index=False)

print(f"Loaded {len(df)} records into PostgreSQL table {table_name}")
```

**5. Load into MongoDB**:
```python
import json
from pymongo import MongoClient

# Load data
with open('data.json') as f:
    data = json.load(f)

# Connect to MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)

# Select database and collection
db = client['scrapy_db']
collection_name = 'products'  # or from arguments
collection = db[collection_name]

# Insert data
if isinstance(data, list):
    result = collection.insert_many(data)
    print(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
else:
    result = collection.insert_one(data)
    print(f"Inserted 1 document into {collection_name}")
```

**6. CSV to JSON**:
```python
import csv
import json

data = []
with open('data.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

# Write JSON
with open('output.json', 'w', encoding='utf-8') as f:
    if '--pretty' in arguments:
        json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        json.dump(data, f, ensure_ascii=False)
```

Export Options:

**CSV Options**:
- `--delimiter ,` - Set delimiter (default: comma)
- `--encoding utf-8` - Set encoding
- `--no-header` - Omit header row

**Excel Options**:
- `--sheet-name "My Data"` - Set sheet name
- `--freeze-panes` - Freeze top row

**Database Options**:
- `--table products` - Table name (default: from filename)
- `--if-exists replace|append|fail` - Handling existing table
- `--create-index` - Create indexes on key columns

**MongoDB Options**:
- `--collection products` - Collection name
- `--database scrapy_db` - Database name
- `--upsert` - Update or insert based on unique field

Data Transformation:

Before exporting, may need to:

1. **Flatten Nested JSON**:
```python
from pandas import json_normalize

data = json_normalize(data, max_level=1)
```

2. **Clean Data**:
```python
# Remove duplicates
df = df.drop_duplicates(subset=['url'])

# Handle missing values
df = df.fillna('')

# Convert types
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['date'] = pd.to_datetime(df['date'])
```

3. **Filter Data**:
```python
# Remove null rows
df = df.dropna(subset=['title'])

# Filter by condition
df = df[df['price'] > 0]
```

After Export:

1. Verify export:
   - Check file size and record count
   - Open file to verify formatting
   - Test database connection if applicable

2. Report statistics:
   - Number of records exported
   - File size or database table info
   - Any records skipped or errors

3. Provide next steps:
   - How to access the exported data
   - Sample query for database exports
   - Import instructions for other tools

Database Connection Setup:

**PostgreSQL** (.env):
```
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
```

**MongoDB** (.env):
```
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=scrapy_db
```

**MySQL** (.env):
```
DATABASE_URL=mysql://username:password@localhost:3306/dbname
```

Example Export Scripts:

Create a reusable export script in `scripts/export.py`:
```python
import sys
import json
import argparse
from exporters import (
    export_to_csv,
    export_to_excel,
    export_to_database,
    export_to_mongodb
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('--to', choices=['csv', 'excel', 'database', 'mongodb'])
    parser.add_argument('--table', default=None)
    parser.add_argument('--collection', default=None)

    args = parser.parse_args()

    # Load data
    with open(args.input_file) as f:
        if args.input_file.endswith('.jsonl'):
            data = [json.loads(line) for line in f]
        else:
            data = json.load(f)

    # Export based on target
    if args.to == 'csv':
        export_to_csv(data, args.input_file.replace('.json', '.csv'))
    elif args.to == 'excel':
        export_to_excel(data, args.input_file.replace('.json', '.xlsx'))
    elif args.to == 'database':
        export_to_database(data, args.table)
    elif args.to == 'mongodb':
        export_to_mongodb(data, args.collection)

if __name__ == '__main__':
    main()
```

Run: `python scripts/export.py data.json --to csv`

Best Practices:
- Validate data before export: `/validate-items`
- Clean and deduplicate data
- Use appropriate data types for database columns
- Create indexes on frequently queried columns
- Handle encoding properly (UTF-8 recommended)
- Backup existing database tables before replace
- Use transactions for database operations
- Log export operations and any errors
- Verify record counts match before/after
- Consider chunking for very large datasets

Common Issues:
- Unicode errors: Ensure UTF-8 encoding throughout
- Memory errors: Process data in chunks for large files
- Database connection errors: Check credentials and network
- Type conversion errors: Clean data before export
- Duplicate key errors: Use upsert or handle conflicts

Next Steps:
- Analyze exported data
- Create visualizations or reports
- Integrate with other applications
- Schedule regular exports with cron/scheduler
