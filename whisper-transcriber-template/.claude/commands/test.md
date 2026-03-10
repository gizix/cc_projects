---
description: Run the pytest test suite
---

Run the test suite for the whisper transcriber project.

Execute: `uv run python -m pytest tests/ -v`

After running:
- If all tests pass, confirm success
- If tests fail, analyze the failures and suggest fixes
- If faster-whisper is not installed, note that model-loading tests require it and suggest running `/setup`

The tests mock the WhisperModel so they don't require an actual GPU or model download.
