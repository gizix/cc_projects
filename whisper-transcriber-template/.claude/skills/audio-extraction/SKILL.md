---
name: audio-extraction
description: ffmpeg audio extraction patterns for various video formats. Invoke when implementing audio extraction, handling new video formats, or troubleshooting ffmpeg pipeline issues.
allowed-tools: Read, Edit, Bash
---

# Audio Extraction Skill

This skill provides ffmpeg command patterns for extracting audio from video files for Whisper transcription.

## Standard Extraction (Whisper-optimized)

```bash
ffmpeg -i input.mp4 \
  -vn \                    # no video
  -acodec pcm_s16le \      # 16-bit PCM WAV
  -ar 16000 \              # 16kHz sample rate (Whisper native)
  -ac 1 \                  # mono channel
  -y \                     # overwrite output
  output.wav
```

## Python Integration

```python
import subprocess
import shutil
from pathlib import Path

def extract_audio(video_path: str, output_path: str) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH")

    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", "-y",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")
```

## Format-Specific Commands

### Microsoft Teams MP4
```bash
ffmpeg -i teams_recording.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

### Teams WebM (web recordings)
```bash
ffmpeg -i recording.webm -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

### MKV with multiple audio tracks
```bash
# List streams
ffprobe -v quiet -show_streams -select_streams a recording.mkv

# Extract specific stream (e.g., track 1)
ffmpeg -i recording.mkv -map 0:a:0 -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

### MOV (QuickTime / macOS screen recording)
```bash
ffmpeg -i screen_recording.mov -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav
```

## Audio Quality Improvements

### Normalize volume (quiet recordings)
```bash
ffmpeg -i quiet.wav -af loudnorm -ar 16000 -ac 1 normalized.wav
```

### Remove background noise
```bash
ffmpeg -i noisy.wav -af "afftdn=nf=-25" -ar 16000 -ac 1 clean.wav
```

### High-pass filter (remove low rumble)
```bash
ffmpeg -i audio.wav -af "highpass=f=200" filtered.wav
```

## Checking Video/Audio Info

```bash
# Full stream info
ffprobe -v error -show_streams input.mp4

# Duration only
ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp4

# Audio codec info
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels input.mp4
```

## Supported Input Formats

ffmpeg supports virtually all video formats including:
- `.mp4` (H.264/H.265)
- `.mkv` (Matroska)
- `.mov` (QuickTime)
- `.webm` (VP8/VP9)
- `.avi` (older recordings)
- `.wmv` (Windows Media)
- `.ts`, `.mts` (transport streams)

Native audio (no extraction needed):
- `.wav`, `.mp3`, `.flac`, `.aac`, `.ogg`, `.m4a`

## Integration with This Project

Use `src/audio_extractor.py`:
```python
from src.audio_extractor import extract_audio, check_ffmpeg, is_audio_file

if not check_ffmpeg():
    raise RuntimeError("Install ffmpeg first")

if not is_audio_file(video_path):
    audio_path = extract_audio(video_path)
else:
    audio_path = video_path  # already audio, use directly
```
