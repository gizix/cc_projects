---
description: Extract audio track from a video file (without transcribing)
argument-hint: <video_file> [--output output.wav]
---

Extract the audio track from `$ARGUMENTS` using ffmpeg.

Steps:
1. Verify the file exists
2. Run: `uv run python -m src.cli extract-audio $ARGUMENTS`
3. Confirm the output WAV file was created and show its path

The extracted audio will be:
- Format: 16-bit PCM WAV
- Sample rate: 16000 Hz (optimal for Whisper)
- Channels: Mono

If ffmpeg is not found, suggest running `/setup` first.
