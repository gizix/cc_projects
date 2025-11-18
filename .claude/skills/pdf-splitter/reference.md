# pypdf Library API Reference

## Installation

```bash
# Modern pypdf library (recommended)
pip install pypdf

# Legacy PyPDF2 (fallback)
pip install PyPDF2
```

## Core Classes

### PdfReader

**Purpose**: Read and parse PDF files

**Constructor**:
```python
from pypdf import PdfReader

reader = PdfReader("path/to/file.pdf")
```

**Key Properties**:
- `reader.pages` - List-like object containing all pages (0-indexed)
- `reader.metadata` - Dictionary with PDF metadata (title, author, etc.)
- `len(reader.pages)` - Total page count

**Key Methods**:
```python
# Get specific page (0-indexed)
page = reader.pages[0]  # First page

# Iterate through all pages
for page in reader.pages:
    # Process page

# Get page count
total_pages = len(reader.pages)
```

**Error Handling**:
```python
from pypdf import PdfReader
from pypdf.errors import PdfReadError

try:
    reader = PdfReader("file.pdf")
except FileNotFoundError:
    print("PDF file not found")
except PdfReadError:
    print("Corrupted or invalid PDF")
except Exception as e:
    print(f"Error: {e}")
```

---

### PdfWriter

**Purpose**: Create and write PDF files

**Constructor**:
```python
from pypdf import PdfWriter

writer = PdfWriter()
```

**Key Methods**:

#### add_page(page)
Add a page to the PDF being created
```python
writer.add_page(page_object)
```

#### write(file_handle)
Write the PDF to a file
```python
with open("output.pdf", "wb") as f:
    writer.write(f)
```

#### add_metadata(metadata_dict)
Add metadata to the output PDF
```python
writer.add_metadata({
    "/Title": "Split Pages",
    "/Author": "PDF Splitter",
    "/Subject": "Extracted Pages"
})
```

---

### PageObject

**Purpose**: Represents a single PDF page

**Obtained from**: `PdfReader.pages[index]`

**Key Methods**:
- `page.extract_text()` - Extract text content (useful for verification)
- `page.mediabox` - Get page dimensions
- `page.rotate(degrees)` - Rotate page

**Example**:
```python
reader = PdfReader("input.pdf")
page = reader.pages[0]

# Get page info
text = page.extract_text()
width = page.mediabox.width
height = page.mediabox.height
```

---

## Common Operations

### 1. Reading a PDF

```python
from pypdf import PdfReader

# Open and read
reader = PdfReader("document.pdf")

# Get basic info
print(f"Total pages: {len(reader.pages)}")
print(f"Metadata: {reader.metadata}")

# Access specific page
first_page = reader.pages[0]
last_page = reader.pages[-1]
```

### 2. Creating a New PDF from Existing Pages

```python
from pypdf import PdfReader, PdfWriter

# Read source PDF
reader = PdfReader("source.pdf")

# Create new PDF
writer = PdfWriter()

# Add pages
writer.add_page(reader.pages[0])  # Add first page
writer.add_page(reader.pages[2])  # Add third page

# Write to file
with open("output.pdf", "wb") as f:
    writer.write(f)
```

### 3. Splitting All Pages

```python
from pypdf import PdfReader, PdfWriter
import os

reader = PdfReader("input.pdf")
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

for i, page in enumerate(reader.pages, start=1):
    writer = PdfWriter()
    writer.add_page(page)

    output_path = os.path.join(output_dir, f"page_{i:03d}.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)
```

### 4. Extracting Page Range

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# Extract pages 5-10 (0-indexed, so 4-9)
for i in range(4, 10):
    if i < len(reader.pages):
        writer.add_page(reader.pages[i])

with open("pages_5-10.pdf", "wb") as f:
    writer.write(f)
```

### 5. Splitting into Chunks

```python
from pypdf import PdfReader, PdfWriter
import os

reader = PdfReader("input.pdf")
chunk_size = 5
output_dir = "chunks"
os.makedirs(output_dir, exist_ok=True)

total_pages = len(reader.pages)
chunk_num = 1

for start in range(0, total_pages, chunk_size):
    writer = PdfWriter()
    end = min(start + chunk_size, total_pages)

    for i in range(start, end):
        writer.add_page(reader.pages[i])

    output_path = os.path.join(output_dir, f"chunk_{chunk_num:03d}.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    chunk_num += 1
```

---

## File Path Operations

### Getting Filename Without Extension

```python
import os

# Method 1: os.path
full_path = "/path/to/document.pdf"
base_name = os.path.splitext(os.path.basename(full_path))[0]
# Result: "document"

# Method 2: pathlib
from pathlib import Path
base_name = Path(full_path).stem
# Result: "document"
```

### Creating Output Directory Beside Original File

```python
import os

input_path = "/path/to/document.pdf"

# Get directory and filename
input_dir = os.path.dirname(input_path)
base_name = os.path.splitext(os.path.basename(input_path))[0]

# Create output directory beside original file
output_dir = os.path.join(input_dir, f"{base_name}_split")
os.makedirs(output_dir, exist_ok=True)
```

### Handling Relative and Absolute Paths

```python
import os

# Convert to absolute path
input_path = "document.pdf"
abs_path = os.path.abspath(input_path)

# Check if file exists
if os.path.exists(input_path):
    # Process file
    pass
else:
    print(f"File not found: {input_path}")
```

---

## Advanced Features

### Preserving Metadata

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# Copy pages
for page in reader.pages:
    writer.add_page(page)

# Copy metadata
if reader.metadata:
    writer.add_metadata(reader.metadata)

# Write output
with open("output.pdf", "wb") as f:
    writer.write(f)
```

### Password-Protected PDFs

```python
from pypdf import PdfReader

reader = PdfReader("protected.pdf")

if reader.is_encrypted:
    # Try to decrypt
    success = reader.decrypt("password")
    if success:
        # Process pages
        for page in reader.pages:
            # ...
    else:
        print("Incorrect password")
```

### Progress Reporting for Large Files

```python
from pypdf import PdfReader, PdfWriter
import os

reader = PdfReader("large_file.pdf")
total_pages = len(reader.pages)
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

for i, page in enumerate(reader.pages, start=1):
    writer = PdfWriter()
    writer.add_page(page)

    output_path = os.path.join(output_dir, f"page_{i:03d}.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    # Progress reporting
    if i % 10 == 0 or i == total_pages:
        print(f"Processed {i}/{total_pages} pages ({i*100//total_pages}%)")
```

---

## Error Handling Best Practices

### Comprehensive Error Handling

```python
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError, PdfStreamError
import os
import sys

def split_pdf(input_path, output_dir):
    """Split PDF with comprehensive error handling"""

    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return False

    # Check if input is a file
    if not os.path.isfile(input_path):
        print(f"Error: Not a file: {input_path}")
        return False

    try:
        # Read PDF
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        if total_pages == 0:
            print("Error: PDF has no pages")
            return False

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Split pages
        for i, page in enumerate(reader.pages, start=1):
            try:
                writer = PdfWriter()
                writer.add_page(page)

                output_path = os.path.join(output_dir, f"page_{i:03d}.pdf")
                with open(output_path, "wb") as f:
                    writer.write(f)

            except Exception as e:
                print(f"Warning: Failed to write page {i}: {e}")
                continue

        print(f"Successfully split {total_pages} pages to {output_dir}/")
        return True

    except PdfReadError:
        print("Error: Corrupted or invalid PDF file")
        return False
    except PdfStreamError:
        print("Error: Problem reading PDF stream")
        return False
    except PermissionError:
        print("Error: Permission denied")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <pdf_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_directory = f"{base_name}_split"

    success = split_pdf(input_file, output_directory)
    sys.exit(0 if success else 1)
```

---

## Performance Considerations

### Memory Efficiency

For very large PDFs, process pages one at a time:

```python
# Good: Process pages individually
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    writer.write(...)
    # writer goes out of scope, memory freed

# Avoid: Loading all pages into memory
all_pages = list(reader.pages)  # Don't do this for large files
```

### Batch Processing Optimization

```python
import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter

def batch_split_pdfs(directory, pattern="*.pdf"):
    """Process multiple PDFs in a directory"""

    pdf_files = list(Path(directory).glob(pattern))
    total_files = len(pdf_files)

    print(f"Found {total_files} PDF files to process")

    for idx, pdf_path in enumerate(pdf_files, start=1):
        print(f"\n[{idx}/{total_files}] Processing: {pdf_path.name}")

        base_name = pdf_path.stem
        output_dir = pdf_path.parent / f"{base_name}_split"

        try:
            reader = PdfReader(pdf_path)
            os.makedirs(output_dir, exist_ok=True)

            for i, page in enumerate(reader.pages, start=1):
                writer = PdfWriter()
                writer.add_page(page)

                output_path = output_dir / f"page_{i:03d}.pdf"
                with open(output_path, "wb") as f:
                    writer.write(f)

            print(f"  ✓ Split {len(reader.pages)} pages")

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue

    print(f"\nCompleted processing {total_files} files")

# Usage
batch_split_pdfs("/path/to/pdfs")
```

---

## pypdf vs PyPDF2

### Library Comparison

| Feature | pypdf | PyPDF2 |
|---------|-------|--------|
| Status | Active, modern | Legacy, minimal updates |
| Python Version | 3.6+ | 2.7+ |
| Performance | Faster | Slower |
| API | Same API | Same API |
| Recommendation | Use this | Fallback only |

### Migration from PyPDF2

Code is nearly identical:

```python
# PyPDF2 (old)
from PyPDF2 import PdfReader, PdfWriter

# pypdf (new)
from pypdf import PdfReader, PdfWriter

# Everything else is the same
```

---

## Troubleshooting

### Common Issues

**Issue**: "PdfReadError: EOF marker not found"
- **Cause**: Corrupted or incomplete PDF
- **Solution**: Check if file downloaded completely, try repair tools

**Issue**: "PermissionError: Access denied"
- **Cause**: File open in another program or insufficient permissions
- **Solution**: Close PDF viewers, check file permissions

**Issue**: "ModuleNotFoundError: No module named 'pypdf'"
- **Cause**: Library not installed
- **Solution**: Run `pip install pypdf`

**Issue**: Empty pages or missing content
- **Cause**: PDF uses special encoding or embedded objects
- **Solution**: Use `page.extract_text()` to verify content, may need specialized handling

### Debugging Tips

```python
# Check PDF info before processing
reader = PdfReader("file.pdf")
print(f"Pages: {len(reader.pages)}")
print(f"Encrypted: {reader.is_encrypted}")
print(f"Metadata: {reader.metadata}")

# Test single page first
writer = PdfWriter()
writer.add_page(reader.pages[0])
with open("test_page.pdf", "wb") as f:
    writer.write(f)
print("Test page created successfully")
```

---

## External Resources

- Official pypdf documentation: https://pypdf.readthedocs.io/
- PyPI package: https://pypi.org/project/pypdf/
- GitHub repository: https://github.com/py-pdf/pypdf
- Migration guide from PyPDF2: https://pypdf.readthedocs.io/en/latest/user/migration-1-to-2.html
