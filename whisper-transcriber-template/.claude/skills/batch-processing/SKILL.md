---
name: batch-processing
description: Multi-file transcription processing patterns with progress tracking and error handling. Invoke when implementing batch workflows, processing directories of videos, or setting up automated transcription pipelines.
allowed-tools: Read, Edit, Write, Bash
---

# Batch Processing Skill

This skill covers patterns for efficiently processing multiple video/audio files for transcription.

## Simple Batch Pattern

```python
from pathlib import Path
from src.transcriber import Transcriber
from src.audio_extractor import extract_audio, is_audio_file, is_supported_file
from src.formatter import save_transcript

def batch_transcribe(directory: str, model_size="base", fmt="txt"):
    dir_path = Path(directory)
    files = [f for f in dir_path.iterdir() if f.is_file() and is_supported_file(f)]

    transcriber = Transcriber(model_size=model_size)
    results = []

    for file_path in files:
        try:
            if not is_audio_file(file_path):
                audio = extract_audio(file_path)
                result = transcriber.transcribe(audio)
                audio.unlink()  # cleanup
            else:
                result = transcriber.transcribe(file_path)

            output = save_transcript(result, fmt=fmt, input_path=file_path)
            results.append({"file": str(file_path), "status": "ok", "output": str(output)})
        except Exception as e:
            results.append({"file": str(file_path), "status": "error", "error": str(e)})

    return results
```

## With Rich Progress Display

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

def batch_with_progress(files, transcriber, fmt="txt"):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
    ) as progress:
        task = progress.add_task("Transcribing...", total=len(files))

        for file_path in files:
            progress.update(task, description=f"[cyan]{file_path.name}[/cyan]")
            # process file
            progress.advance(task)
```

## Resume Interrupted Batch

```python
def get_pending_files(directory: Path, fmt: str) -> list[Path]:
    """Return files that don't yet have a transcript."""
    all_files = [f for f in directory.iterdir() if is_supported_file(f)]
    return [f for f in all_files if not f.with_suffix(f".{fmt}").exists()]

# Usage
pending = get_pending_files(Path("./recordings"), "txt")
print(f"Resuming: {len(pending)} files remaining")
```

## Error Logging

```python
import json
from datetime import datetime

def batch_with_error_log(files, transcriber, fmt="txt", log_path="batch_errors.json"):
    errors = []
    success = 0

    for file_path in files:
        try:
            result = transcriber.transcribe(file_path)
            save_transcript(result, fmt=fmt, input_path=file_path)
            success += 1
        except Exception as e:
            errors.append({
                "file": str(file_path),
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })

    if errors:
        Path(log_path).write_text(json.dumps(errors, indent=2))
        print(f"Errors logged to {log_path}")

    print(f"Complete: {success} ok, {len(errors)} failed")
```

## Parallel Processing (CPU)

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def transcribe_file(args):
    file_path, model_size, fmt = args
    transcriber = Transcriber(model_size=model_size)
    # ... transcribe and save

files = list(Path("./recordings").glob("*.mp4"))
args = [(f, "base", "txt") for f in files]

# 2 workers is usually optimal on CPU (more causes memory contention)
with ProcessPoolExecutor(max_workers=2) as executor:
    futures = {executor.submit(transcribe_file, a): a[0] for a in args}
    for future in as_completed(futures):
        file = futures[future]
        try:
            future.result()
        except Exception as e:
            print(f"Failed: {file.name}: {e}")
```

**Warning**: Don't use GPU parallelism without careful VRAM management — multiple model instances will OOM.

## Organizing Output

```python
# Flat: transcripts next to source files (default)
output = file_path.with_suffix(f".{fmt}")

# Organized: all transcripts in output directory
output_dir = Path("./transcripts")
output_dir.mkdir(exist_ok=True)
output = output_dir / f"{file_path.stem}.{fmt}"
```

## Integration with This Project

The `src/cli.py` `batch` command handles the standard case:
```bash
uv run python -m src.cli batch ./recordings --format json --model base
```

For custom batch workflows, compose `Transcriber`, `extract_audio`, and `save_transcript` directly from the source modules.
