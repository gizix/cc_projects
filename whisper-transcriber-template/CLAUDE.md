# Whisper Transcriber — Claude Code Context

## Project Purpose

This project transcribes video/audio files locally using faster-whisper and ffmpeg. Primary use case: Microsoft Teams meeting recordings → formatted transcripts. No cloud APIs, fully offline.

## Architecture

```
Video File → ffmpeg (audio extraction) → WAV/MP3 → faster-whisper → Segments → Formatter → Output File

Browser/System Audio → sounddevice (loopback) → numpy buffer → WAV → faster-whisper → Segments → Formatter → Transcript
```

### Pipeline Components

1. **`src/audio_extractor.py`** — Uses ffmpeg to extract audio from video files
2. **`src/audio_recorder.py`** — Records live system audio via sounddevice WASAPI loopback
3. **`src/transcriber.py`** — Loads faster-whisper model, runs transcription, yields segments
4. **`src/formatter.py`** — Converts segment lists to txt/srt/vtt/json formats
5. **`src/cli.py`** — click CLI that ties everything together

## faster-whisper API Patterns

### Model Loading
```python
from faster_whisper import WhisperModel

# CPU (int8 = fastest on CPU)
model = WhisperModel("base", device="cpu", compute_type="int8")

# GPU (float16 = fastest on CUDA)
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
```

### Transcription
```python
segments, info = model.transcribe(
    audio_path,
    beam_size=5,
    language=None,       # None = auto-detect
    vad_filter=True,     # skip silence
    vad_parameters=dict(min_silence_duration_ms=500),
    word_timestamps=False,
)

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

### Key Parameters
- `beam_size`: 1 (fastest) to 10 (most accurate), default 5
- `vad_filter`: True removes silence, speeds up transcription
- `language`: ISO code ("en", "fr") or None for auto-detect
- `compute_type`: "int8" (CPU), "float16" (GPU), "int8_float16" (GPU, less VRAM)
- `word_timestamps`: True adds per-word timing (slower)

## ffmpeg Patterns

### Audio Extraction
```python
import subprocess

def extract_audio(video_path: str, output_path: str) -> None:
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",              # no video
        "-acodec", "pcm_s16le",  # 16-bit PCM WAV
        "-ar", "16000",     # 16kHz (Whisper's native sample rate)
        "-ac", "1",         # mono
        "-y",               # overwrite output
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
```

### Check ffmpeg Available
```python
import shutil
if not shutil.which("ffmpeg"):
    raise RuntimeError("ffmpeg not found on PATH. Install from https://ffmpeg.org")
```

## Output Format Conventions

### SRT Format
```
1
00:00:01,234 --> 00:00:05,678
Hello, this is the transcript text.

2
00:00:06,000 --> 00:00:10,500
Next segment here.
```

### VTT Format
```
WEBVTT

00:00:01.234 --> 00:00:05.678
Hello, this is the transcript text.
```

### JSON Schema
```json
{
  "file": "meeting.mp4",
  "language": "en",
  "duration": 3600.0,
  "model": "base",
  "segments": [
    {
      "id": 0,
      "start": 1.234,
      "end": 5.678,
      "text": "Hello, this is the transcript text.",
      "avg_logprob": -0.25
    }
  ]
}
```

## Model Selection Guide

| Model | Parameters | Speed (RTF) | Best Use Case |
|-------|-----------|-------------|---------------|
| tiny | 39M | ~32x | Quick previews, testing |
| base | 74M | ~16x | Default, good balance |
| small | 244M | ~6x | Better accuracy |
| medium | 769M | ~2x | Important meetings |
| large-v3 | 1550M | ~1x | Maximum accuracy |

RTF = Real-Time Factor (how many seconds of audio processed per second)

## Hardware Notes

### CPU (no GPU)
- Use `compute_type="int8"` for fastest CPU inference
- `base` model processes ~16x real-time on modern CPU
- `large-v3` on CPU is very slow — use `medium` at most

### NVIDIA GPU (CUDA)
- Use `compute_type="float16"` for best GPU performance
- Use `compute_type="int8_float16"` if VRAM is limited
- All models run well on GPU

### Apple Silicon (MPS)
- faster-whisper uses CTranslate2 which doesn't support MPS yet
- Use `device="cpu"` with `compute_type="int8"`

## File Naming Conventions

- Extracted audio: `{stem}_audio.wav` (e.g., `meeting_audio.wav`)
- Output transcripts: `{stem}.{format}` (e.g., `meeting.srt`, `meeting.json`)
- Temp files go in `./tmp/` and are cleaned up by `/clean`

## Common Troubleshooting

### ffmpeg not found
```bash
# Windows
winget install ffmpeg
# or download from https://ffmpeg.org/download.html

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### CUDA not available
```python
# Force CPU
model = WhisperModel("base", device="cpu", compute_type="int8")
```

### Out of memory (GPU)
- Switch to smaller model
- Use `compute_type="int8_float16"` instead of `float16`

### Slow transcription
- Enable `vad_filter=True` to skip silence
- Use smaller model
- Use GPU if available
- Reduce `beam_size` to 1-3

## Testing Patterns

```python
# tests/test_transcriber.py
import pytest
from unittest.mock import patch, MagicMock
from src.transcriber import Transcriber

def test_transcriber_loads_model():
    with patch("src.transcriber.WhisperModel") as mock_model:
        t = Transcriber(model_size="base", device="cpu")
        mock_model.assert_called_once_with("base", device="cpu", compute_type="int8")
```

## Running Commands

All Python commands should use `uv run`:
```bash
uv run python -m src.cli transcribe meeting.mp4
uv run pytest tests/ -v
uv run ruff check src/
```

## Live Recording Architecture

### sounddevice Patterns

```python
import sounddevice as sd
import soundfile as sf
import numpy as np
import queue

# List devices — filter input-only (max_input_channels > 0)
devices = sd.query_devices()

# WASAPI loopback devices have "Loopback" in the name on Windows
# macOS: BlackHole, Soundflower, Loopback App
# Linux: PulseAudio monitor sources (name ends with .monitor)

# Record via callback → queue pattern
audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())

with sd.InputStream(
    samplerate=16000,
    channels=1,
    dtype="int16",
    device=device_index,   # MUST be explicit — None defaults to microphone
    callback=callback,
) as stream:
    # drain queue on main thread
    chunks = []
    while recording:
        chunk = audio_queue.get(timeout=0.1)
        chunks.append(chunk)

audio = np.concatenate(chunks, axis=0)

# Stereo → mono downmix
if audio.ndim > 1 and audio.shape[1] > 1:
    audio = audio.mean(axis=1).astype(np.int16)

sf.write("output.wav", audio, 16000, subtype="PCM_16")
```

### Key Notes

- **Always pass `device=index` explicitly** — `device=None` uses the default microphone, not loopback
- **WASAPI loopback records silence if nothing is playing** — Whisper's VAD filter skips it automatically
- **PortAudio error -9985** (Invalid device) = another app has exclusive mode → disable exclusive mode in Sound settings
- All sounddevice/soundfile/numpy imports are **lazy** (inside functions) so startup doesn't fail if deps aren't installed
- `KeyboardInterrupt` is caught cleanly — WAV is always written before transcription starts

## Development Commands

- `/transcribe <file>` — Transcribe a video/audio file
- `/transcribe-batch <dir>` — Batch transcribe all videos in directory
- `/extract-audio <file>` — Extract audio only (no transcription)
- `/list-models` — Show Whisper model comparison
- `/list-devices` — List audio input devices, highlight loopback sources
- `/record [options]` — Record live system/browser audio and transcribe
- `/convert-format <file> <fmt>` — Convert transcript format
- `/setup` — Install dependencies and verify ffmpeg
- `/test` — Run pytest
- `/lint` — Run ruff linter
- `/format` — Run ruff formatter
- `/clean` — Remove temporary audio files
