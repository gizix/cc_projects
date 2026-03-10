---
name: credential-management
description: Provides CredentialStore.get() patterns, env_bridge injection, and rotation workflow when a task needs to consume a secret. Activates when a task needs to read API keys, tokens, or passwords.
allowed-tools: Read, Write, Edit
---

You provide patterns for safely consuming credentials in tasks and subprocesses.

## When to Activate

- User says "the task needs an API key" or "inject a credential"
- User is creating a task that calls an external service
- User asks about credential rotation
- User is writing a subprocess task that needs a secret

## Pattern 1: Direct Credential Read (In-Process)

Use when the task Python code needs the value directly:

```python
def run(self) -> TaskResult:
    cred_name = self.config.get("credential_name", "MY_API_KEY")

    try:
        from agent.credentials.store import get_store
        store = get_store()  # uses MASTER_PASSWORD env var
        token = store.get(cred_name)
    except RuntimeError:
        return TaskResult(status="error", message="Master password not configured")

    if token is None:
        return TaskResult(
            status="error",
            message=f"Credential '{cred_name}' not found. Run: agent credential set {cred_name}",
        )

    # Use token — NEVER log it
    response = httpx.get(url, headers={"Authorization": f"Bearer {token}"})
    ...
```

## Pattern 2: Subprocess Injection via env_bridge

Use when a subprocess or external script needs the credential:

```python
def run(self) -> TaskResult:
    inject_names = self.config.get("inject_credentials", [])

    try:
        from agent.credentials.store import get_store
        from agent.credentials.env_bridge import inject_credentials

        store = get_store()
        env = inject_credentials(store, inject_names)
    except Exception as exc:
        return TaskResult(status="error", message=str(exc))

    result = subprocess.run(
        ["my-script", "--run"],
        env=env,          # credentials available as env vars
        capture_output=True,
        text=True,
    )
    ...
```

**Config example:**
```json
{
  "inject_credentials": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
  "command": "aws s3 sync ./data s3://my-bucket"
}
```

## CLI: Store a Credential

```bash
# Interactive (value prompted, hidden)
uv run agent credential set MY_API_KEY
uv run agent credential set MY_API_KEY --description "Production API key"

# View stored names (never values)
uv run agent credential list

# Use in task config
uv run agent schedule add http_request "interval:300" \
  '{"url": "https://api.example.com/data", "credential_name": "MY_API_KEY"}'
```

## Rotation Workflow

```python
# Rotate master password
from agent.credentials.store import get_store

old_store = get_store(old_password)
old_store.rotate(new_password)

# Verify
new_store = get_store(new_password)
assert new_store.get("MY_KEY") is not None  # still accessible
```

## Security Rules (Never Violate)

1. **Never log credential values** — use `logger.debug("Using credential '%s'", name)`
2. **Never store in SQLite** — `CredentialRecord` contains only name + metadata
3. **Never pass as CLI arg** — always inject via env or read in-process
4. **Never in f-strings in exceptions** — `raise ValueError(f"Invalid token: {token}")` is WRONG
5. **Never in `self.config` logging** — config might contain sensitive fields

## Testing Without Real Credentials

```python
def test_task_with_credential(monkeypatch, credential_store):
    credential_store.set("TEST_API_KEY", "fake-value-for-tests")

    # Patch get_store to return the test store
    monkeypatch.setattr(
        "agent.credentials.store.get_store",
        lambda *args, **kwargs: credential_store,
    )

    from agent.tasks.my_task import MyTask
    task = MyTask({"credential_name": "TEST_API_KEY"})
    result = task.run()
    assert result.status == "success"
```
