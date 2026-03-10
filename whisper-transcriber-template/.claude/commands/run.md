---
description: Show CLI help and available transcription commands
---

Show the CLI help and guide the user on how to use the transcriber.

Run: `uv run python -m src.cli --help`

Then list the available slash commands:
- `/transcribe <file>` — Transcribe a single video/audio file
- `/transcribe-batch <dir>` — Transcribe all videos in a directory
- `/extract-audio <file>` — Extract audio only (no transcription)
- `/list-models` — Show Whisper model comparison table
- `/convert-format <file> <fmt>` — Convert existing transcript format
- `/setup` — Install dependencies and verify ffmpeg
- `/test` — Run pytest test suite
- `/lint` — Run ruff linter
- `/format` — Run ruff formatter
- `/clean` — Remove temporary extracted audio files

Ask the user what they'd like to do.
