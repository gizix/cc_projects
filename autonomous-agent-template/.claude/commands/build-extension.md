---
description: Build the Rust performance extension with maturin
argument-hint: "[--release]"
---

Compile the PyO3/Maturin Rust extension and verify it imports correctly.

```bash
# Development build (fast compile, debug symbols)
maturin develop --manifest-path rust_ext/Cargo.toml

# Production build (optimised)
# maturin build --release --manifest-path rust_ext/Cargo.toml

# Verify import
python -c "import agent_core_ext; print('Version:', agent_core_ext.__version__)"
```

**What the extension provides:**
| Function | Purpose | Benefit |
|---|---|---|
| `hash_task_id(s)` | SHA-256 job ID generation | Fast hot path |
| `cron_next_fire(expr, ts, n)` | Cron schedule preview | Used in `/schedule-task` |
| `derive_key(pwd, salt, iters)` | PBKDF2 key derivation | ~10× faster vs hashlib |

**Fallback:** If the extension is not built, all features work with pure-Python fallbacks. Only `cron_next_fire` preview and key derivation speed are affected — a warning is logged.

**Prerequisites:** Rust toolchain (`rustup`), Python dev headers.
