---
description: Convert an existing JSON transcript to a different format (srt, vtt, txt)
argument-hint: <transcript.json> <format>
---

Convert the transcript file to a different format.

Usage: `/convert-format transcript.json srt`

Steps:
1. Verify the input file exists and is a JSON transcript
2. Run: `uv run python -m src.cli convert-format $ARGUMENTS`
3. Show the path of the converted output file

Important notes:
- Full format conversion (with timestamps) requires a JSON source file
- JSON transcripts contain all metadata (timestamps, language, confidence scores)
- TXT, SRT, and VTT files cannot be converted back to JSON (timestamps are lost)

Available target formats: `txt`, `srt`, `vtt`, `json`
