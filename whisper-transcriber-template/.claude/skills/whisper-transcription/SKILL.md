---
name: whisper-transcription
description: Complete faster-whisper transcription pipeline patterns. Invoke when implementing transcription features, integrating Whisper into new code, or troubleshooting transcription output quality.
allowed-tools: Read, Edit, Write, Bash
---

# Whisper Transcription Skill

This skill provides complete implementation patterns for faster-whisper transcription pipelines.

## Core Pattern

```python
from faster_whisper import WhisperModel

# 1. Load model (do this once, reuse for multiple files)
model = WhisperModel(
    "base",             # tiny, base, small, medium, large-v3
    device="auto",      # cpu, cuda, auto
    compute_type="int8" # int8 for CPU, float16 for GPU
)

# 2. Transcribe
segments, info = model.transcribe(
    "audio.wav",
    beam_size=5,
    language=None,          # None = auto-detect
    vad_filter=True,        # skip silence regions
    word_timestamps=False,  # True for per-word timing
)

# 3. Process segments (generator — iterate once)
result = []
for segment in segments:
    result.append({
        "start": segment.start,
        "end": segment.end,
        "text": segment.text.strip(),
    })

print(f"Language: {info.language} ({info.language_probability:.0%})")
print(f"Duration: {info.duration:.1f}s")
```

## Model Loading Strategies

### Singleton (recommended for CLI tools)
```python
_model_cache = {}

def get_model(size="base", device="auto", compute_type="int8"):
    key = (size, device, compute_type)
    if key not in _model_cache:
        _model_cache[key] = WhisperModel(size, device=device, compute_type=compute_type)
    return _model_cache[key]
```

### Context Manager (for scripts that run once)
```python
# Just instantiate directly — WhisperModel handles cleanup
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.wav")
```

## Streaming vs Batch

```python
# Streaming (progress display, lower memory peak)
for segment in segments:
    print(f"[{segment.start:.1f}s] {segment.text}")

# Batch (all at once, needed for formatting)
all_segments = list(segments)  # forces full transcription
```

## Language Handling

```python
# Auto-detect (default)
segments, info = model.transcribe("audio.wav", language=None)
print(f"Detected: {info.language}")  # e.g., "en", "fr"

# Force language (faster, avoids detection errors)
segments, info = model.transcribe("audio.wav", language="en")
```

## VAD Parameters

```python
# Aggressive silence removal (noisy recordings)
vad_params = {
    "min_silence_duration_ms": 1000,  # 1 second silence = new segment
    "speech_pad_ms": 400,
}

# Conservative (preserve more context)
vad_params = {
    "min_silence_duration_ms": 300,
    "speech_pad_ms": 100,
}

segments, info = model.transcribe("audio.wav", vad_filter=True, vad_parameters=vad_params)
```

## Error Handling

```python
try:
    segments, info = model.transcribe(audio_path)
    result = list(segments)
except Exception as e:
    if "CUDA" in str(e):
        # Fall back to CPU
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path)
        result = list(segments)
    else:
        raise
```

## Integration with This Project

The `Transcriber` class in `src/transcriber.py` wraps these patterns. Use it directly:

```python
from src.transcriber import Transcriber

t = Transcriber(model_size="base", device="auto")
result = t.transcribe("audio.wav", language="en", vad_filter=True)
print(result.full_text)
```
