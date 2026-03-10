---
description: Install Python dependencies and verify ffmpeg is available
---

Set up the whisper transcriber project environment using uv.

Steps:
1. Install Python dependencies with uv:
   ```
   uv sync
   ```
   Or install dev dependencies:
   ```
   uv sync --extra dev
   ```

2. Check ffmpeg is available:
   ```
   ffmpeg -version
   ```
   If not found, provide installation instructions:
   - Windows: `winget install ffmpeg` or download from https://ffmpeg.org/download.html
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or `sudo dnf install ffmpeg`

3. Copy `.env.example` to `.env` if `.env` doesn't exist yet

4. Confirm setup is complete and suggest running `/list-models` to see available models

Note: faster-whisper models are downloaded automatically on first use. The `base` model (~75MB) is downloaded when you first run `/transcribe`.
