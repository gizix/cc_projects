# PDF Splitter Code Examples

Complete, working code examples for all PDF splitting modes.

---

## Example 1: Split All Pages Individually

**Scenario**: User has a 50-page document and wants each page as a separate PDF file.

**User Request**: "Split report.pdf into individual pages"

**Complete Script**:

```python
#!/usr/bin/env python3
"""
Split PDF into individual pages
Each page becomes a separate PDF file
"""

from pypdf import PdfReader, PdfWriter
import os
import sys

def split_pdf_individual_pages(input_path):
    """Split PDF into individual pages"""

    # Validate input
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return False

    try:
        # Read PDF
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        if total_pages == 0:
            print("Error: PDF has no pages")
            return False

        # Create output directory
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        input_dir = os.path.dirname(os.path.abspath(input_path))
        output_dir = os.path.join(input_dir, f"{base_name}_split")

        os.makedirs(output_dir, exist_ok=True)

        print(f"Splitting {total_pages} pages from {input_path}...")
        print(f"Output directory: {output_dir}")

        # Split each page
        for i, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)

            output_file = os.path.join(output_dir, f"page_{i:03d}.pdf")

            with open(output_file, "wb") as f:
                writer.write(f)

            # Progress reporting
            if i % 10 == 0 or i == total_pages:
                print(f"  Processed {i}/{total_pages} pages...")

        print(f"\n✓ Successfully split {total_pages} pages")
        print(f"  Files saved in: {output_dir}/")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_individual.py <pdf_file>")
        print("Example: python split_individual.py report.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    success = split_pdf_individual_pages(input_file)
    sys.exit(0 if success else 1)
```

**Usage**:
```bash
python split_individual.py report.pdf
```

**Output**:
```
report_split/
├── page_001.pdf
├── page_002.pdf
├── page_003.pdf
...
└── page_050.pdf
```

---

## Example 2: Split by Page Ranges

**Scenario**: User wants to extract specific page ranges from a document.

**User Request**: "Extract pages 1-5, 10-15, and 25-30 from document.pdf"

**Complete Script**:

```python
#!/usr/bin/env python3
"""
Split PDF by page ranges
Extract specific page ranges into separate PDF files
"""

from pypdf import PdfReader, PdfWriter
import os
import sys
import argparse

def parse_page_ranges(range_string):
    """
    Parse page range string into list of tuples
    Example: "1-5,10-15,25-30" -> [(1,5), (10,15), (25,30)]
    """
    ranges = []

    for part in range_string.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            ranges.append((int(start), int(end)))
        else:
            # Single page
            page = int(part)
            ranges.append((page, page))

    return ranges

def split_pdf_by_ranges(input_path, page_ranges):
    """Split PDF by specified page ranges"""

    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return False

    try:
        # Read PDF
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        if total_pages == 0:
            print("Error: PDF has no pages")
            return False

        print(f"PDF has {total_pages} pages total")

        # Create output directory
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        input_dir = os.path.dirname(os.path.abspath(input_path))
        output_dir = os.path.join(input_dir, f"{base_name}_split")

        os.makedirs(output_dir, exist_ok=True)

        print(f"Extracting {len(page_ranges)} page range(s)...")
        print(f"Output directory: {output_dir}")

        # Process each range
        for start, end in page_ranges:
            # Validate range
            if start < 1 or end > total_pages:
                print(f"  ⚠ Warning: Range {start}-{end} exceeds PDF bounds (1-{total_pages}), skipping")
                continue

            if start > end:
                print(f"  ⚠ Warning: Invalid range {start}-{end} (start > end), skipping")
                continue

            # Create writer for this range
            writer = PdfWriter()

            # Add pages in range (convert to 0-indexed)
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])

            # Determine output filename
            if start == end:
                output_file = os.path.join(output_dir, f"page_{start:03d}.pdf")
                range_desc = f"page {start}"
            else:
                output_file = os.path.join(output_dir, f"pages_{start:03d}-{end:03d}.pdf")
                range_desc = f"pages {start}-{end}"

            # Write output file
            with open(output_file, "wb") as f:
                writer.write(f)

            print(f"  ✓ Extracted {range_desc} → {os.path.basename(output_file)}")

        print(f"\n✓ Successfully processed {len(page_ranges)} range(s)")
        print(f"  Files saved in: {output_dir}/")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split PDF by page ranges")
    parser.add_argument("input_file", help="Input PDF file")
    parser.add_argument("ranges", help="Page ranges (e.g., '1-5,10-15,25-30')")

    args = parser.parse_args()

    # Parse ranges
    try:
        page_ranges = parse_page_ranges(args.ranges)
    except ValueError as e:
        print(f"Error parsing ranges: {e}")
        print("Format: '1-5,10-15,25-30' or '1,3,5-10'")
        sys.exit(1)

    # Split PDF
    success = split_pdf_by_ranges(args.input_file, page_ranges)
    sys.exit(0 if success else 1)
```

**Usage**:
```bash
python split_ranges.py document.pdf "1-5,10-15,25-30"
```

**Output**:
```
document_split/
├── pages_001-005.pdf  (pages 1-5)
├── pages_010-015.pdf  (pages 10-15)
└── pages_025-030.pdf  (pages 25-30)
```

---

## Example 3: Split into Chunks

**Scenario**: User wants to split a large PDF into smaller chunks of N pages each.

**User Request**: "Split handbook.pdf into 10-page chunks"

**Complete Script**:

```python
#!/usr/bin/env python3
"""
Split PDF into chunks
Divide PDF into multiple files with N pages each
"""

from pypdf import PdfReader, PdfWriter
import os
import sys
import argparse

def split_pdf_into_chunks(input_path, chunk_size):
    """Split PDF into chunks of specified size"""

    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return False

    if chunk_size < 1:
        print(f"Error: Chunk size must be at least 1 (got {chunk_size})")
        return False

    try:
        # Read PDF
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        if total_pages == 0:
            print("Error: PDF has no pages")
            return False

        # Calculate number of chunks
        num_chunks = (total_pages + chunk_size - 1) // chunk_size  # Ceiling division

        print(f"Splitting {total_pages} pages into chunks of {chunk_size} pages...")
        print(f"This will create {num_chunks} file(s)")

        # Create output directory
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        input_dir = os.path.dirname(os.path.abspath(input_path))
        output_dir = os.path.join(input_dir, f"{base_name}_split")

        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory: {output_dir}")

        # Process chunks
        chunk_num = 1
        for start_page in range(0, total_pages, chunk_size):
            writer = PdfWriter()

            # Calculate end page for this chunk
            end_page = min(start_page + chunk_size, total_pages)
            pages_in_chunk = end_page - start_page

            # Add pages to this chunk
            for page_idx in range(start_page, end_page):
                writer.add_page(reader.pages[page_idx])

            # Generate output filename
            output_file = os.path.join(output_dir, f"chunk_{chunk_num:03d}.pdf")

            # Write chunk
            with open(output_file, "wb") as f:
                writer.write(f)

            # Report progress
            page_range = f"{start_page + 1}-{end_page}" if pages_in_chunk > 1 else f"{start_page + 1}"
            print(f"  ✓ Chunk {chunk_num}: pages {page_range} ({pages_in_chunk} page(s)) → {os.path.basename(output_file)}")

            chunk_num += 1

        print(f"\n✓ Successfully created {num_chunks} chunk(s)")
        print(f"  Files saved in: {output_dir}/")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split PDF into chunks")
    parser.add_argument("input_file", help="Input PDF file")
    parser.add_argument("chunk_size", type=int, help="Number of pages per chunk")

    args = parser.parse_args()

    success = split_pdf_into_chunks(args.input_file, args.chunk_size)
    sys.exit(0 if success else 1)
```

**Usage**:
```bash
python split_chunks.py handbook.pdf 10
```

**Output** (for a 47-page PDF):
```
handbook_split/
├── chunk_001.pdf  (pages 1-10)
├── chunk_002.pdf  (pages 11-20)
├── chunk_003.pdf  (pages 21-30)
├── chunk_004.pdf  (pages 31-40)
└── chunk_005.pdf  (pages 41-47, last chunk has 7 pages)
```

---

## Example 4: Batch Process Multiple PDFs

**Scenario**: User has a directory with multiple PDFs and wants to split them all.

**User Request**: "Split all PDFs in the reports/ directory into individual pages"

**Complete Script**:

```python
#!/usr/bin/env python3
"""
Batch process multiple PDF files
Split multiple PDFs at once with configurable split mode
"""

from pypdf import PdfReader, PdfWriter
import os
import sys
import argparse
from pathlib import Path

def split_single_pdf_individual(input_path, output_dir):
    """Split single PDF into individual pages"""
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        os.makedirs(output_dir, exist_ok=True)

        for i, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)

            output_file = os.path.join(output_dir, f"page_{i:03d}.pdf")
            with open(output_file, "wb") as f:
                writer.write(f)

        return True, total_pages

    except Exception as e:
        return False, str(e)

def split_single_pdf_chunks(input_path, output_dir, chunk_size):
    """Split single PDF into chunks"""
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)

        os.makedirs(output_dir, exist_ok=True)

        chunk_num = 1
        for start in range(0, total_pages, chunk_size):
            writer = PdfWriter()
            end = min(start + chunk_size, total_pages)

            for i in range(start, end):
                writer.add_page(reader.pages[i])

            output_file = os.path.join(output_dir, f"chunk_{chunk_num:03d}.pdf")
            with open(output_file, "wb") as f:
                writer.write(f)

            chunk_num += 1

        return True, total_pages

    except Exception as e:
        return False, str(e)

def batch_split_pdfs(directory, mode="individual", chunk_size=None, pattern="*.pdf"):
    """
    Batch process multiple PDFs in a directory

    Args:
        directory: Directory containing PDF files
        mode: "individual" or "chunks"
        chunk_size: Pages per chunk (for chunks mode)
        pattern: Glob pattern for finding PDF files
    """

    # Find all PDF files
    directory_path = Path(directory)

    if not directory_path.exists():
        print(f"Error: Directory not found: {directory}")
        return False

    pdf_files = sorted(directory_path.glob(pattern))

    if not pdf_files:
        print(f"No PDF files found matching pattern '{pattern}' in {directory}")
        return False

    total_files = len(pdf_files)
    print(f"Found {total_files} PDF file(s) to process")
    print(f"Split mode: {mode}")
    if mode == "chunks" and chunk_size:
        print(f"Chunk size: {chunk_size} pages")
    print()

    # Process each PDF
    successful = 0
    failed = 0

    for idx, pdf_path in enumerate(pdf_files, start=1):
        print(f"[{idx}/{total_files}] Processing: {pdf_path.name}")

        # Create output directory
        base_name = pdf_path.stem
        output_dir = pdf_path.parent / f"{base_name}_split"

        # Split based on mode
        if mode == "individual":
            success, result = split_single_pdf_individual(str(pdf_path), str(output_dir))
        elif mode == "chunks":
            if chunk_size is None:
                print("  ✗ Error: Chunk size not specified")
                failed += 1
                continue
            success, result = split_single_pdf_chunks(str(pdf_path), str(output_dir), chunk_size)
        else:
            print(f"  ✗ Error: Unknown mode '{mode}'")
            failed += 1
            continue

        if success:
            print(f"  ✓ Split {result} pages → {output_dir.name}/")
            successful += 1
        else:
            print(f"  ✗ Failed: {result}")
            failed += 1

        print()

    # Summary
    print("=" * 60)
    print(f"Batch processing complete:")
    print(f"  Total files: {total_files}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    return failed == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch split multiple PDF files")
    parser.add_argument("directory", help="Directory containing PDF files")
    parser.add_argument(
        "--mode",
        choices=["individual", "chunks"],
        default="individual",
        help="Split mode (default: individual)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Pages per chunk (required for chunks mode)"
    )
    parser.add_argument(
        "--pattern",
        default="*.pdf",
        help="File pattern to match (default: *.pdf)"
    )

    args = parser.parse_args()

    # Validate chunk size for chunks mode
    if args.mode == "chunks" and not args.chunk_size:
        print("Error: --chunk-size is required for chunks mode")
        sys.exit(1)

    success = batch_split_pdfs(
        args.directory,
        mode=args.mode,
        chunk_size=args.chunk_size,
        pattern=args.pattern
    )

    sys.exit(0 if success else 1)
```

**Usage Examples**:

```bash
# Split all PDFs in reports/ directory into individual pages
python batch_split.py reports/

# Split all PDFs into 5-page chunks
python batch_split.py reports/ --mode chunks --chunk-size 5

# Only process PDFs matching specific pattern
python batch_split.py reports/ --pattern "report_*.pdf"
```

**Output** (for 3 PDF files in reports/):
```
reports/
├── report1.pdf
├── report1_split/
│   ├── page_001.pdf
│   ├── page_002.pdf
│   └── ...
├── report2.pdf
├── report2_split/
│   ├── page_001.pdf
│   ├── page_002.pdf
│   └── ...
├── report3.pdf
└── report3_split/
    ├── page_001.pdf
    ├── page_002.pdf
    └── ...
```

---

## Example 5: Interactive Script

**Scenario**: User wants an interactive script that asks for split mode and parameters.

**Complete Script**:

```python
#!/usr/bin/env python3
"""
Interactive PDF splitter
Prompts user for input and split preferences
"""

from pypdf import PdfReader, PdfWriter
import os
import sys

def get_split_mode():
    """Prompt user for split mode"""
    print("\nSelect split mode:")
    print("  1. Individual pages (each page → separate PDF)")
    print("  2. Page ranges (extract specific ranges)")
    print("  3. Chunks (split into N-page chunks)")

    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            return int(choice)
        print("Invalid choice. Please enter 1, 2, or 3.")

def split_individual(reader, output_dir):
    """Split into individual pages"""
    total_pages = len(reader.pages)

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        output_file = os.path.join(output_dir, f"page_{i:03d}.pdf")
        with open(output_file, "wb") as f:
            writer.write(f)

        if i % 10 == 0 or i == total_pages:
            print(f"  Progress: {i}/{total_pages} pages...")

    print(f"✓ Created {total_pages} individual PDF files")

def split_ranges(reader, output_dir):
    """Split by page ranges"""
    total_pages = len(reader.pages)
    print(f"\nPDF has {total_pages} pages")
    print("Enter page ranges (e.g., '1-5,10-15' or '1,3,5-10')")

    range_input = input("Ranges: ").strip()

    # Parse ranges
    ranges = []
    for part in range_input.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            ranges.append((start, end))
        else:
            page = int(part)
            ranges.append((page, page))

    # Extract ranges
    for start, end in ranges:
        if start < 1 or end > total_pages:
            print(f"⚠ Warning: Range {start}-{end} out of bounds, skipping")
            continue

        writer = PdfWriter()
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])

        if start == end:
            output_file = os.path.join(output_dir, f"page_{start:03d}.pdf")
        else:
            output_file = os.path.join(output_dir, f"pages_{start:03d}-{end:03d}.pdf")

        with open(output_file, "wb") as f:
            writer.write(f)

        print(f"  ✓ Extracted pages {start}-{end}")

    print(f"✓ Created {len(ranges)} PDF file(s)")

def split_chunks(reader, output_dir):
    """Split into chunks"""
    total_pages = len(reader.pages)
    print(f"\nPDF has {total_pages} pages")

    while True:
        try:
            chunk_size = int(input("Pages per chunk: ").strip())
            if chunk_size > 0:
                break
            print("Chunk size must be positive")
        except ValueError:
            print("Please enter a valid number")

    chunk_num = 1
    for start in range(0, total_pages, chunk_size):
        writer = PdfWriter()
        end = min(start + chunk_size, total_pages)

        for i in range(start, end):
            writer.add_page(reader.pages[i])

        output_file = os.path.join(output_dir, f"chunk_{chunk_num:03d}.pdf")
        with open(output_file, "wb") as f:
            writer.write(f)

        pages_in_chunk = end - start
        print(f"  ✓ Chunk {chunk_num}: {pages_in_chunk} page(s)")
        chunk_num += 1

    num_chunks = (total_pages + chunk_size - 1) // chunk_size
    print(f"✓ Created {num_chunks} chunk(s)")

def main():
    """Main interactive function"""
    print("=" * 60)
    print("PDF Splitter - Interactive Mode")
    print("=" * 60)

    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("\nEnter PDF file path: ").strip()

    # Validate file
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    # Read PDF
    try:
        reader = PdfReader(input_file)
        total_pages = len(reader.pages)
        print(f"\n✓ Loaded: {os.path.basename(input_file)} ({total_pages} pages)")
    except Exception as e:
        print(f"Error reading PDF: {e}")
        sys.exit(1)

    # Get split mode
    mode = get_split_mode()

    # Create output directory
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    input_dir = os.path.dirname(os.path.abspath(input_file))
    output_dir = os.path.join(input_dir, f"{base_name}_split")

    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    print("\nProcessing...")

    # Execute split
    try:
        if mode == 1:
            split_individual(reader, output_dir)
        elif mode == 2:
            split_ranges(reader, output_dir)
        elif mode == 3:
            split_chunks(reader, output_dir)

        print(f"\n✓ Complete! Files saved in: {output_dir}/")

    except Exception as e:
        print(f"\nError during split: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
# With file argument
python interactive_split.py document.pdf

# Without argument (will prompt)
python interactive_split.py
```

**Interactive Session**:
```
============================================================
PDF Splitter - Interactive Mode
============================================================

✓ Loaded: document.pdf (50 pages)

Select split mode:
  1. Individual pages (each page → separate PDF)
  2. Page ranges (extract specific ranges)
  3. Chunks (split into N-page chunks)

Enter choice (1-3): 3

Output directory: /path/to/document_split

PDF has 50 pages
Pages per chunk: 10

Processing...
  ✓ Chunk 1: 10 page(s)
  ✓ Chunk 2: 10 page(s)
  ✓ Chunk 3: 10 page(s)
  ✓ Chunk 4: 10 page(s)
  ✓ Chunk 5: 10 page(s)
✓ Created 5 chunk(s)

✓ Complete! Files saved in: /path/to/document_split/
```

---

## Quick Reference: Command Patterns

| Mode | Command Example |
|------|-----------------|
| Individual pages | `python split_individual.py report.pdf` |
| Page ranges | `python split_ranges.py doc.pdf "1-5,10-15"` |
| Chunks | `python split_chunks.py handbook.pdf 10` |
| Batch individual | `python batch_split.py reports/` |
| Batch chunks | `python batch_split.py reports/ --mode chunks --chunk-size 5` |
| Interactive | `python interactive_split.py document.pdf` |

---

All examples include:
- ✅ Error handling
- ✅ Progress reporting
- ✅ Input validation
- ✅ Clear output messages
- ✅ Proper file naming conventions
- ✅ Zero-padded numbering for sorting
