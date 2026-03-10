---
description: Show available Whisper models with speed, accuracy, and VRAM requirements
---

Show the available Whisper models and help the user choose the right one.

Run: `uv run python -m src.cli list-models`

After displaying the table, ask the user about their use case:
- Speed priority → recommend `tiny` or `base`
- Accuracy priority → recommend `medium` or `large-v3`
- CPU only → warn that `large-v3` will be very slow; suggest `small` or `medium` at most
- Have GPU → any model works; `large-v3` for best accuracy

Also mention:
- The default model is `base` (good balance of speed and accuracy)
- Model is set via `--model` flag or `WHISPER_MODEL` environment variable in `.env`
- Models are downloaded automatically on first use (~75MB for base, ~3GB for large-v3)
