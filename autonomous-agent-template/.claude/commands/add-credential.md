---
description: Securely store an encrypted credential (value prompted, no echo)
argument-hint: "<name> [--description 'text']"
---

Store a secret in the encrypted credential store. The value is prompted interactively — it never appears in shell history or logs.

```bash
uv run agent credential set $ARGUMENTS
```

**Examples:**
```bash
uv run agent credential set AZURE_OPENAI_API_KEY
uv run agent credential set MY_DATABASE_PASSWORD --description "Production DB"
uv run agent credential set WEBHOOK_SECRET
```

**Security notes:**
- Values are encrypted with Fernet (AES-128 + HMAC-SHA256)
- Key derived via PBKDF2-HMAC-SHA256 (600k iterations) from your master password
- Encrypted file: `data/.credentials.enc` (never readable by Claude Code)
- Set `MASTER_PASSWORD` env var to avoid repeated prompts

**View stored names (not values):** `/list-credentials`
