---
description: Transcribe all video/audio files in a directory
argument-hint: <directory> [--model base] [--format txt] [--language en]
---

Batch transcribe all video and audio files in the directory `$ARGUMENTS`.

Steps:
1. Verify the directory exists
2. Run: `uv run python -m src.cli batch $ARGUMENTS`
3. Show a summary of files processed, successes, and any failures
4. If any files failed, explain likely causes and how to fix them

Tips to share with the user:
- Use `--format json` to preserve timestamps for all files
- Use `--model small` or `--model medium` for better accuracy on important meetings
- Large directories may take significant time on CPU — suggest GPU if available
- Processed transcripts are saved next to the original files by default
