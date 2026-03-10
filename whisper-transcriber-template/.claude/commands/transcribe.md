---
description: Transcribe a video or audio file using faster-whisper
argument-hint: <video_file> [--model base|small|medium|large-v3] [--format txt|srt|vtt|json] [--language en]
---

Transcribe the file `$ARGUMENTS` using the whisper transcriber CLI.

Steps:
1. Check that the file exists and is a supported format
2. Run the transcription command: `uv run python -m src.cli transcribe $ARGUMENTS`
3. Show the output path and key metadata (language detected, segment count, duration)
4. If the user didn't specify a format, remind them they can use `--format srt` for subtitle files or `--format json` for timestamped data

If ffmpeg is not found, suggest running `/setup` first.
If the model is not specified, default to `base` and mention that `--model medium` or `--model large-v3` gives higher accuracy.
