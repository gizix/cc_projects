# Whisper Transcriber Template

A Claude Code project template for transcribing Microsoft Teams meeting videos (and any other video/audio files) locally using `faster-whisper` and `ffmpeg`. No cloud APIs required — all processing happens on your machine.

## What This Template Does

- Extracts audio from video files (MP4, MKV, MOV, WebM, AVI, and more)
- Transcribes audio using OpenAI's Whisper model (via faster-whisper)
- Outputs transcripts in multiple formats: plain text, SRT subtitles, VTT subtitles, JSON with timestamps
- Works entirely offline after initial model download

## Prerequisites

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/download.html) installed and on your PATH
- (Optional) NVIDIA GPU with CUDA for faster transcription

## Quick Setup

1. **Open this folder in VSCode**
2. **Launch Claude Code**
3. **Run `/setup`** — installs Python dependencies with uv and verifies ffmpeg

That's it. You're ready to transcribe.

## Usage

### Transcribe a single video
```
/transcribe meeting.mp4
```

### Transcribe all videos in a folder
```
/transcribe-batch ./recordings
```

### Extract audio without transcribing
```
/extract-audio meeting.mp4
```

### List available Whisper models
```
/list-models
```

### Convert transcript to different format
```
/convert-format transcript.txt srt
```

## Recording Browser Audio

Capture system audio in real-time — no file download needed. Play a video in your browser and record what your speakers output.

### How It Works

The recorder captures audio from a **loopback device** — a virtual input that mirrors your system's audio output. On Windows this is built in (WASAPI); on macOS/Linux you need a small driver.

### Platform Setup

**Windows** (WASAPI loopback — built in)
WASAPI loopback devices appear automatically as `Speakers (Device) [Loopback]`. If none show up, enable "Stereo Mix" via Sound settings → Recording tab → right-click → Show Disabled Devices.

**macOS** (BlackHole)
1. Install [BlackHole](https://existential.audio/blackhole/) (free, open source)
2. In Audio MIDI Setup, create a Multi-Output Device combining your speakers + BlackHole
3. Set your system output to the Multi-Output Device
4. BlackHole now appears as a recording device

**Linux** (PulseAudio)
Monitor sources (ending in `.monitor`) appear automatically. If using PipeWire:
```bash
pactl load-module module-loopback
```

### Workflow

```bash
# 1. Find your loopback device index
/list-devices

# 2. Start playing audio in your browser

# 3. Record (auto-detects loopback, or specify --device)
/record --duration 60

# 4. Ctrl+C to stop early — transcript saves automatically
```

### Record Command Examples

```bash
# Record 60 seconds, auto-transcribe
/record --duration 60

# Record from a specific device (index from list-devices)
/record --duration 30 --device 3

# Record until Ctrl+C, output SRT subtitles
/record --format srt

# Use a more accurate model
/record --duration 120 --model medium --format txt

# Save WAV only, skip transcription
/record --duration 60 --no-transcribe

# Save transcript to custom path
/record --duration 60 --output ./transcripts/meeting.txt
```

## CLI Usage

You can also use the CLI directly:

```bash
uv run python -m src.cli transcribe meeting.mp4
uv run python -m src.cli transcribe meeting.mp4 --model medium --language en --format srt
uv run python -m src.cli batch ./recordings --format json
uv run python -m src.cli extract-audio meeting.mp4
uv run python -m src.cli list-models
```

## Whisper Model Selection

| Model | Speed | Accuracy | VRAM | Best For |
|-------|-------|----------|------|----------|
| tiny | Fastest | Lower | ~1GB | Quick drafts, short clips |
| base | Fast | Good | ~1GB | Default — good balance |
| small | Moderate | Better | ~2GB | Better accuracy needed |
| medium | Slower | High | ~5GB | Important meetings |
| large-v3 | Slowest | Best | ~10GB | Maximum accuracy |

Default model is `base`. Override with `--model <name>`.

## Output Formats

- **txt** — Plain text transcript
- **srt** — SubRip subtitle format (for video players)
- **vtt** — WebVTT format (for web players)
- **json** — Structured JSON with timestamps, confidence scores, and segments

## Project Structure

```
whisper-transcriber-template/
├── src/
│   ├── transcriber.py      # faster-whisper integration
│   ├── audio_extractor.py  # ffmpeg audio extraction
│   ├── formatter.py        # output format converters
│   └── cli.py              # click CLI entrypoint
├── tests/
│   └── test_transcriber.py
└── .claude/
    ├── commands/           # /transcribe, /setup, etc.
    ├── agents/             # specialized subagents
    └── skills/             # reusable skill patterns
```

## Troubleshooting

**ffmpeg not found**: Install ffmpeg and ensure it's on your PATH. On Windows: `winget install ffmpeg`. On Mac: `brew install ffmpeg`. On Linux: `sudo apt install ffmpeg`.

**CUDA errors**: Set `--device cpu` to force CPU transcription. Add `--compute-type int8` for faster CPU inference.

**Out of memory**: Use a smaller model (`--model tiny` or `--model base`).

**Slow transcription**: Use `--compute-type int8` on CPU, or upgrade to a GPU.

## Dependencies

- `faster-whisper` — Whisper model inference (4x faster than openai-whisper)
- `ffmpeg-python` — Python bindings for ffmpeg
- `click` — CLI argument parsing
- `rich` — Progress bars and colored output
- `sounddevice` — Live audio recording via PortAudio/WASAPI
- `soundfile` — WAV file writing
- `numpy` — Audio buffer processing and mono downmix
