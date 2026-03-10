---
description: Record system audio in real-time and transcribe it with Whisper
argument-hint: [--duration 60] [--device <index|name>] [--model base] [--format txt|srt|vtt|json] [--output path] [--no-transcribe]
---

Record live system/browser audio and transcribe it with faster-whisper.

**Prerequisites**: Play a video in your browser or any audio source before running.

```bash
uv run python -m src.cli record $ARGUMENTS
```

**Examples:**
- Record 60 seconds then auto-transcribe: `/record --duration 60`
- Record from a specific device: `/record --duration 30 --device 3`
- Save WAV only, no transcription: `/record --duration 60 --no-transcribe`
- Record until Ctrl+C, use large model: `/record --model large-v3 --format srt`

**Tips:**
- Run `/list-devices` first to find the loopback device index
- On Windows, WASAPI loopback devices appear as "Speakers [Loopback]"
- Whisper's VAD filter automatically skips silence
- Stop recording at any time with Ctrl+C — the WAV is always saved before transcribing
