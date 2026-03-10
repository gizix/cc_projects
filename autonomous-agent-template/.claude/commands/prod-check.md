---
description: Automated pre-deployment checklist
---

Run a series of pre-deployment validations to catch common issues before going to production.

```bash
echo "=== Pre-deployment Checklist ===" && \
echo "" && \
echo "1. Environment variables..." && \
python -c "
import os, sys
required = ['MASTER_PASSWORD']
llm_vars = [
    ('AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT'),
    ('OPENAI_API_KEY',),
    ('OPENAI_BASE_URL',),
]
missing = [v for v in required if not os.environ.get(v)]
if missing:
    print(f'  FAIL: Missing required vars: {missing}')
    sys.exit(1)
llm_ok = any(all(os.environ.get(v) for v in group) for group in llm_vars)
if not llm_ok:
    print('  WARN: No LLM provider configured (Azure, OpenAI, or local)')
else:
    print('  OK: LLM provider configured')
print('  OK: Required env vars present')
" && \
echo "" && \
echo "2. Rust extension..." && \
python -c "
try:
    import agent_core_ext
    print(f'  OK: agent_core_ext {agent_core_ext.__version__}')
except ImportError:
    print('  WARN: Rust extension not built (run /build-extension for best performance)')
" && \
echo "" && \
echo "3. No plaintext secrets in source..." && \
grep -r "password\s*=\s*[\"'][^\"']\+[\"']" src/ tests/ --include="*.py" -l 2>/dev/null && echo "  WARN: Possible hardcoded passwords found above" || echo "  OK: No obvious hardcoded secrets" && \
echo "" && \
echo "4. Tests passing..." && \
uv run pytest tests/ -q --tb=no 2>&1 | tail -3 && \
echo "" && \
echo "5. Type check..." && \
uv run mypy src/agent/ --ignore-missing-imports --no-error-summary 2>&1 | tail -5 && \
echo "" && \
echo "=== Checklist complete ==="
