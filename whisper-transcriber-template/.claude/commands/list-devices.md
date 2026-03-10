---
description: List audio input devices and identify loopback/system audio sources
---

Show all available audio input devices and highlight loopback sources for system audio capture.

```bash
uv run python -m src.cli list-devices
```

Loopback devices are highlighted in bold. Use the device index with `/record --device <index>` to target a specific device.

**Platform notes:**
- **Windows**: WASAPI loopback appears as `Speakers (Device Name) [Loopback]` — enabled by default
- **macOS**: Install [BlackHole](https://existential.audio/blackhole/) or Soundflower for virtual loopback
- **Linux**: PulseAudio monitor sources (`.monitor` suffix) act as loopback

If no loopback device is listed, see the "Recording Browser Audio" section in README.md for setup instructions.
