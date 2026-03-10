"""Encrypted credential store backed by a Fernet-encrypted JSON file.

Values are NEVER written to the internal SQLite database.
Only metadata (name, description, timestamps) lives in CredentialRecord.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from agent.credentials.crypto import decrypt, encrypt


class CredentialStore:
    def __init__(self, credential_file: Path, master_password: str) -> None:
        self._file = credential_file
        self._password = master_password

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> dict[str, str]:
        if not self._file.exists():
            return {}
        data = decrypt(self._file.read_bytes(), self._password)
        return json.loads(data)

    def _save(self, creds: dict[str, str]) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._file.with_suffix(".enc.tmp")
        encrypted = encrypt(json.dumps(creds), self._password)
        tmp.write_bytes(encrypted)
        # Verify before replacing (atomic-ish)
        decrypt(tmp.read_bytes(), self._password)
        tmp.replace(self._file)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, name: str) -> str | None:
        return self._load().get(name)

    def set(self, name: str, value: str) -> None:
        creds = self._load()
        creds[name] = value
        self._save(creds)

    def delete(self, name: str) -> bool:
        creds = self._load()
        if name not in creds:
            return False
        del creds[name]
        self._save(creds)
        return True

    def list_names(self) -> list[str]:
        return sorted(self._load().keys())

    def rotate(self, new_password: str) -> None:
        """Re-encrypt all credentials with a new master password."""
        creds = self._load()
        self._password = new_password
        self._save(creds)


def get_store(password: str | None = None) -> CredentialStore:
    """Return a CredentialStore using settings defaults."""
    from agent.config import settings

    pwd = password or settings.master_password
    if not pwd:
        raise RuntimeError(
            "Master password not set. Pass --password or set MASTER_PASSWORD env var."
        )
    return CredentialStore(settings.credential_file, pwd)
