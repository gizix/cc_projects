---
name: transcript-formatting
description: SRT, VTT, JSON, and TXT transcript conversion and formatting patterns. Invoke when implementing new output formats, converting between transcript formats, or post-processing transcript content.
allowed-tools: Read, Edit, Write
---

# Transcript Formatting Skill

This skill covers patterns for formatting, converting, and post-processing Whisper transcription output.

## Timestamp Conversion Utilities

```python
def seconds_to_srt(seconds: float) -> str:
    """00:00:01,500 format"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def seconds_to_vtt(seconds: float) -> str:
    """00:00:01.500 format"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
```

## SRT Generation

```python
def to_srt(segments) -> str:
    blocks = []
    for i, seg in enumerate(segments, 1):
        start = seconds_to_srt(seg.start)
        end = seconds_to_srt(seg.end)
        blocks.append(f"{i}\n{start} --> {end}\n{seg.text.strip()}\n")
    return "\n".join(blocks)
```

## VTT Generation

```python
def to_vtt(segments) -> str:
    lines = ["WEBVTT", ""]
    for seg in segments:
        start = seconds_to_vtt(seg.start)
        end = seconds_to_vtt(seg.end)
        lines.extend([f"{start} --> {end}", seg.text.strip(), ""])
    return "\n".join(lines)
```

## JSON Schema

```json
{
  "file": "meeting.mp4",
  "language": "en",
  "language_probability": 0.9990,
  "duration": 3600.0,
  "model": "base",
  "segments": [
    {
      "id": 0,
      "start": 1.234,
      "end": 5.678,
      "text": "Hello, welcome to the meeting.",
      "avg_logprob": -0.2500,
      "no_speech_prob": 0.0100
    }
  ]
}
```

## Post-Processing Patterns

### Add speaker labels
```python
# Manual post-processing based on content
def add_speaker_hints(segments, speaker_map=None):
    result = []
    for seg in segments:
        text = seg.text.strip()
        # Simple heuristic: look for ":" patterns
        result.append(text)
    return "\n".join(result)
```

### Merge short segments
```python
def merge_short_segments(segments, min_duration=1.0):
    merged = []
    buffer = None
    for seg in segments:
        if buffer is None:
            buffer = seg
        elif (seg.start - buffer.end) < 0.5 and len(buffer.text) < 200:
            # Merge into buffer
            buffer.end = seg.end
            buffer.text += " " + seg.text.strip()
        else:
            merged.append(buffer)
            buffer = seg
    if buffer:
        merged.append(buffer)
    return merged
```

### Clean filler words
```python
import re

FILLERS = r'\b(um|uh|you know|like|basically|actually|literally)\b'

def remove_fillers(text: str) -> str:
    return re.sub(FILLERS, "", text, flags=re.IGNORECASE).strip()
```

## Integration with This Project

Use `src/formatter.py`:
```python
from src.formatter import format_result, save_transcript
from src.transcriber import TranscriptionResult

# Format in memory
srt_content = format_result(result, "srt")

# Save to file
output_path = save_transcript(result, fmt="srt", input_path="meeting.mp4")
# -> saves to meeting.srt

# Convert existing JSON transcript
from src.formatter import convert_transcript_file
output = convert_transcript_file("meeting.json", "srt")
```
