# PDF Splitter Script Templates

Reusable Python script templates that can be customized for specific use cases.

---

## Template 1: Basic PDF Splitter (Minimal)

**Purpose**: Simplest possible split script with minimal dependencies

**Use when**: User wants a quick, no-frills solution

```python
#!/usr/bin/env python3
from pypdf import PdfReader, PdfWriter
import os
import sys

def split_pdf(input_path):
    reader = PdfReader(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = f"{base_name}_split"
    os.makedirs(output_dir, exist_ok=True)

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        with open(f"{output_dir}/page_{i:03d}.pdf", "wb") as f:
            writer.write(f)

    print(f"Split {len(reader.pages)} pages → {output_dir}/")

if __name__ == "__main__":
    split_pdf(sys.argv[1] if len(sys.argv) > 1 else input("PDF file: "))
```

**Customization Points**:
- `output_dir` format
- File naming pattern (`page_{i:03d}.pdf`)
- Progress reporting

---

## Template 2: Robust PDF Splitter (Production-Ready)

**Purpose**: Full error handling, validation, and user feedback

**Use when**: User needs reliable script for repeated use

```python
#!/usr/bin/env python3
"""
{{ SCRIPT_DESCRIPTION }}

Usage: python {{ SCRIPT_NAME }}.py {{ USAGE_ARGS }}
"""

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
import os
import sys
from pathlib import Path

def split_pdf(input_path, output_dir=None, {{ CUSTOM_PARAMS }}):
    """
    {{ FUNCTION_DESCRIPTION }}

    Args:
        input_path: Path to input PDF file
        output_dir: Output directory (default: {filename}_split)
        {{ PARAM_DOCS }}

    Returns:
        bool: True if successful, False otherwise
    """

    # Validate input file
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return False

    if not input_path.is_file():
        print(f"Error: Not a file: {input_path}")
        return False

    # Read PDF with error handling
    try:
        reader = PdfReader(input_path)
    except PdfReadError:
        print(f"Error: Invalid or corrupted PDF file")
        return False
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False

    # Validate PDF has pages
    total_pages = len(reader.pages)
    if total_pages == 0:
        print("Error: PDF has no pages")
        return False

    # Create output directory
    if output_dir is None:
        output_dir = input_path.parent / f"{input_path.stem}_split"
    else:
        output_dir = Path(output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Error: Permission denied creating directory: {output_dir}")
        return False

    # Log operation start
    print(f"Processing: {input_path.name} ({total_pages} pages)")
    print(f"Output: {output_dir}/")

    # {{ MAIN_PROCESSING_LOGIC }}
    try:
        {{ SPLIT_IMPLEMENTATION }}

    except Exception as e:
        print(f"Error during split: {e}")
        return False

    # Success
    print(f"✓ Successfully created {{ OUTPUT_COUNT }} file(s)")
    return True

def main():
    """Main entry point with argument parsing"""

    {{ ARGUMENT_PARSING }}

    success = split_pdf({{ FUNCTION_ARGS }})
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

**Customization Points** (Replace `{{ PLACEHOLDERS }}`):
- `SCRIPT_DESCRIPTION` - What the script does
- `SCRIPT_NAME` - Script filename
- `USAGE_ARGS` - Command-line argument format
- `CUSTOM_PARAMS` - Additional function parameters
- `FUNCTION_DESCRIPTION` - Detailed function description
- `PARAM_DOCS` - Parameter documentation
- `ARGUMENT_PARSING` - sys.argv or argparse code
- `SPLIT_IMPLEMENTATION` - Core splitting logic
- `OUTPUT_COUNT` - Number of files created
- `FUNCTION_ARGS` - Arguments to pass to split_pdf()

---

## Template 3: Command-Line Interface (argparse)

**Purpose**: Professional CLI with arguments, flags, and help text

**Use when**: User wants a polished command-line tool

```python
#!/usr/bin/env python3
"""{{ SCRIPT_DESCRIPTION }}"""

from pypdf import PdfReader, PdfWriter
import os
import sys
import argparse

def {{ FUNCTION_NAME }}(input_path, {{ PARAMETERS }}):
    """{{ FUNCTION_DOCSTRING }}"""

    reader = PdfReader(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    input_dir = os.path.dirname(os.path.abspath(input_path))
    output_dir = os.path.join(input_dir, f"{base_name}_split")
    os.makedirs(output_dir, exist_ok=True)

    {{ IMPLEMENTATION }}

    return True

def main():
    parser = argparse.ArgumentParser(
        description="{{ DESCRIPTION }}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  {{ EXAMPLE_1 }}
  {{ EXAMPLE_2 }}
  {{ EXAMPLE_3 }}
        """
    )

    # Required arguments
    parser.add_argument(
        "input_file",
        help="Input PDF file to split"
    )

    # Optional arguments
    {{ OPTIONAL_ARGUMENTS }}

    # Flags
    {{ FLAGS }}

    args = parser.parse_args()

    # Execute
    try:
        success = {{ FUNCTION_NAME }}(args.input_file, {{ ARG_VALUES }})
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Common Optional Arguments**:

```python
# Output directory
parser.add_argument(
    "-o", "--output",
    help="Output directory (default: {filename}_split/)"
)

# Chunk size
parser.add_argument(
    "-c", "--chunk-size",
    type=int,
    default=1,
    help="Pages per chunk (default: 1)"
)

# Page ranges
parser.add_argument(
    "-r", "--ranges",
    help="Page ranges to extract (e.g., '1-5,10-15')"
)

# Verbosity
parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Enable verbose output"
)

# Quiet mode
parser.add_argument(
    "-q", "--quiet",
    action="store_true",
    help="Suppress all output except errors"
)

# Overwrite existing
parser.add_argument(
    "-f", "--force",
    action="store_true",
    help="Overwrite existing output directory"
)

# Dry run
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Show what would be done without actually doing it"
)
```

---

## Template 4: Batch Processing Script

**Purpose**: Process multiple PDF files from a directory

**Use when**: User has multiple PDFs to process

```python
#!/usr/bin/env python3
"""Batch process multiple PDF files"""

from pypdf import PdfReader, PdfWriter
import os
import sys
from pathlib import Path

def {{ SPLIT_FUNCTION }}(input_path, output_dir):
    """{{ SPLIT_DESCRIPTION }}"""
    try:
        reader = PdfReader(input_path)
        os.makedirs(output_dir, exist_ok=True)

        {{ SPLIT_LOGIC }}

        return True, len(reader.pages)
    except Exception as e:
        return False, str(e)

def batch_process(directory, pattern="*.pdf", {{ BATCH_OPTIONS }}):
    """
    Process multiple PDF files in a directory

    Args:
        directory: Directory containing PDF files
        pattern: Glob pattern for matching files
        {{ BATCH_OPTION_DOCS }}

    Returns:
        tuple: (successful_count, failed_count)
    """

    directory_path = Path(directory)

    if not directory_path.exists():
        print(f"Error: Directory not found: {directory}")
        return 0, 0

    # Find PDF files
    pdf_files = sorted(directory_path.glob(pattern))

    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return 0, 0

    total_files = len(pdf_files)
    print(f"Found {total_files} PDF file(s) to process\n")

    successful = 0
    failed = 0

    # Process each file
    for idx, pdf_path in enumerate(pdf_files, start=1):
        print(f"[{idx}/{total_files}] {pdf_path.name}")

        # Create output directory
        output_dir = pdf_path.parent / f"{pdf_path.stem}_split"

        # Process
        success, result = {{ SPLIT_FUNCTION }}(str(pdf_path), str(output_dir))

        if success:
            print(f"  ✓ Split {result} pages\n")
            successful += 1
        else:
            print(f"  ✗ Failed: {result}\n")
            failed += 1

    # Summary
    print("=" * 60)
    print(f"Complete: {successful} successful, {failed} failed")

    return successful, failed

def main():
    {{ BATCH_ARGUMENT_PARSING }}

    successful, failed = batch_process({{ BATCH_ARGS }})

    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
```

**Batch Processing Variations**:

```python
# Parallel processing (for large batches)
from concurrent.futures import ProcessPoolExecutor, as_completed

def batch_process_parallel(directory, pattern="*.pdf", workers=4):
    """Process PDFs in parallel using multiple processes"""

    pdf_files = list(Path(directory).glob(pattern))
    total = len(pdf_files)

    print(f"Processing {total} files with {workers} workers...\n")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(process_single_pdf, str(pdf)): pdf
            for pdf in pdf_files
        }

        # Collect results
        successful = 0
        for future in as_completed(futures):
            pdf_file = futures[future]
            try:
                result = future.result()
                if result:
                    successful += 1
                    print(f"✓ {pdf_file.name}")
                else:
                    print(f"✗ {pdf_file.name}")
            except Exception as e:
                print(f"✗ {pdf_file.name}: {e}")

    print(f"\nProcessed {successful}/{total} successfully")
```

---

## Template 5: Progress Bar Script (for Large PDFs)

**Purpose**: Show progress bar for long-running operations

**Use when**: User is processing large PDFs (100+ pages)

```python
#!/usr/bin/env python3
"""PDF splitter with progress bar"""

from pypdf import PdfReader, PdfWriter
import os
import sys

def progress_bar(current, total, bar_length=40):
    """Display a progress bar"""
    percent = current / total
    filled = int(bar_length * percent)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f'\r  Progress: |{bar}| {current}/{total} ({percent*100:.1f}%)', end='', flush=True)

def split_pdf_with_progress(input_path):
    """Split PDF with visual progress indicator"""

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = f"{base_name}_split"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Splitting {total_pages} pages from {input_path}")

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        output_file = os.path.join(output_dir, f"page_{i:03d}.pdf")
        with open(output_file, "wb") as f:
            writer.write(f)

        # Update progress bar
        progress_bar(i, total_pages)

    print()  # New line after progress bar
    print(f"✓ Complete! {total_pages} files created in {output_dir}/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_with_progress.py <pdf_file>")
        sys.exit(1)

    split_pdf_with_progress(sys.argv[1])
```

**Alternative: Using tqdm library** (if available):

```python
from tqdm import tqdm

for i, page in enumerate(tqdm(reader.pages, desc="Splitting pages"), start=1):
    writer = PdfWriter()
    writer.add_page(page)
    # ... write file
```

---

## Template 6: Configuration File Script

**Purpose**: Use JSON/YAML config file for complex operations

**Use when**: User has recurring batch jobs with specific settings

**Config File** (`split_config.json`):
```json
{
  "input_directory": "./pdfs",
  "output_base": "./output",
  "mode": "chunks",
  "chunk_size": 10,
  "file_pattern": "*.pdf",
  "preserve_metadata": true,
  "naming_pattern": "page_{num:03d}.pdf",
  "exclude_files": [
    "temp_*.pdf",
    "draft_*.pdf"
  ]
}
```

**Script Template**:
```python
#!/usr/bin/env python3
"""PDF splitter with configuration file support"""

from pypdf import PdfReader, PdfWriter
import json
import sys
from pathlib import Path

def load_config(config_path):
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)

def split_with_config(config):
    """Split PDFs according to configuration"""

    input_dir = Path(config['input_directory'])
    output_base = Path(config['output_base'])
    mode = config.get('mode', 'individual')
    chunk_size = config.get('chunk_size', 1)
    pattern = config.get('file_pattern', '*.pdf')

    # Find files
    pdf_files = input_dir.glob(pattern)

    # Filter excluded files
    exclude_patterns = config.get('exclude_files', [])

    for pdf_file in pdf_files:
        # Check exclusions
        if any(pdf_file.match(pattern) for pattern in exclude_patterns):
            continue

        # Process based on mode
        reader = PdfReader(pdf_file)
        output_dir = output_base / f"{pdf_file.stem}_split"
        output_dir.mkdir(parents=True, exist_ok=True)

        if mode == 'individual':
            for i, page in enumerate(reader.pages, start=1):
                writer = PdfWriter()
                writer.add_page(page)

                # Use naming pattern from config
                naming = config.get('naming_pattern', 'page_{num:03d}.pdf')
                filename = naming.format(num=i)

                with open(output_dir / filename, 'wb') as f:
                    writer.write(f)

        elif mode == 'chunks':
            # Implement chunk logic
            pass

        print(f"✓ Processed {pdf_file.name}")

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "split_config.json"

    try:
        config = load_config(config_file)
        split_with_config(config)
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Template 7: Dry Run / Preview Script

**Purpose**: Show what would be done without actually doing it

**Use when**: User wants to verify operation before executing

```python
#!/usr/bin/env python3
"""PDF splitter with dry-run mode"""

from pypdf import PdfReader, PdfWriter
import os
import sys
import argparse

def split_pdf(input_path, dry_run=False):
    """
    Split PDF with optional dry-run mode

    Args:
        input_path: Input PDF file
        dry_run: If True, only show what would be done
    """

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = f"{base_name}_split"

    if dry_run:
        print("[DRY RUN - No files will be created]")
        print(f"\nWould process: {input_path}")
        print(f"Total pages: {total_pages}")
        print(f"Output directory: {output_dir}/")
        print(f"\nFiles that would be created:")

        for i in range(1, total_pages + 1):
            print(f"  - {output_dir}/page_{i:03d}.pdf")

        print(f"\nTotal files: {total_pages}")
        return True

    # Actual processing
    os.makedirs(output_dir, exist_ok=True)

    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)

        output_file = os.path.join(output_dir, f"page_{i:03d}.pdf")
        with open(output_file, "wb") as f:
            writer.write(f)

    print(f"✓ Split {total_pages} pages → {output_dir}/")
    return True

def main():
    parser = argparse.ArgumentParser(description="Split PDF with dry-run support")
    parser.add_argument("input_file", help="Input PDF file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")

    args = parser.parse_args()

    split_pdf(args.input_file, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
```

---

## Quick Template Selection Guide

| User Need | Template | Key Features |
|-----------|----------|--------------|
| Quick one-off split | Template 1 (Minimal) | Simple, fast, no dependencies |
| Production use | Template 2 (Robust) | Full error handling |
| Professional CLI tool | Template 3 (argparse) | Arguments, flags, help |
| Multiple PDFs | Template 4 (Batch) | Directory processing |
| Large PDFs (100+ pages) | Template 5 (Progress) | Visual feedback |
| Recurring jobs | Template 6 (Config) | JSON configuration |
| Verify before running | Template 7 (Dry Run) | Preview mode |

---

## Customization Checklist

When adapting a template:
- [ ] Replace all `{{ PLACEHOLDERS }}` with actual values
- [ ] Update docstrings with specific descriptions
- [ ] Customize file naming patterns
- [ ] Add error handling for specific edge cases
- [ ] Include progress reporting for large operations
- [ ] Add logging if needed for debugging
- [ ] Test with sample PDFs of various sizes
- [ ] Verify output directory creation
- [ ] Check file permissions handling
- [ ] Validate page number ranges
