---
description: Run the test suite with coverage
argument-hint: "[path] [-k filter]"
---

Run pytest with coverage reporting.

```bash
uv run pytest tests/ -v --cov=src/agent --cov-report=term-missing $ARGUMENTS
```

**Test modules:**
| File | Tests |
|------|-------|
| `test_credentials.py` | Crypto roundtrip, store CRUD, rotation |
| `test_scheduler.py` | Trigger parsing, registry, cron preview |
| `test_tasks.py` | Task execution, headless guards |
| `test_llm_client.py` | PromptBuilder, provider detection |
| `test_rust_ext.py` | Extension functions (skipped if not built) |

**Examples:**
```bash
# Run all tests
uv run pytest tests/ -v --cov=src/agent

# Run only credential tests
uv run pytest tests/test_credentials.py -v

# Filter by test name
uv run pytest tests/ -k "test_rotate" -v
```
