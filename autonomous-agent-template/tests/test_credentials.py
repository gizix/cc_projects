"""Tests for credential store and crypto."""

from __future__ import annotations

import pytest

from agent.credentials.crypto import decrypt, encrypt
from agent.credentials.store import CredentialStore


class TestCrypto:
    def test_roundtrip(self):
        plaintext = "my-secret-api-key-12345"
        password = "strong-password"
        ciphertext = encrypt(plaintext, password)
        assert decrypt(ciphertext, password) == plaintext

    def test_wrong_password_raises(self):
        ciphertext = encrypt("secret", "correct-password")
        with pytest.raises(Exception):
            decrypt(ciphertext, "wrong-password")

    def test_ciphertext_different_each_time(self):
        """Each encrypt call uses a random salt."""
        ct1 = encrypt("same", "pw")
        ct2 = encrypt("same", "pw")
        assert ct1 != ct2


class TestCredentialStore:
    def test_set_get(self, credential_store):
        credential_store.set("API_KEY", "super-secret")
        assert credential_store.get("API_KEY") == "super-secret"

    def test_get_missing_returns_none(self, credential_store):
        assert credential_store.get("NONEXISTENT") is None

    def test_delete(self, credential_store):
        credential_store.set("TO_DELETE", "value")
        assert credential_store.delete("TO_DELETE") is True
        assert credential_store.get("TO_DELETE") is None

    def test_delete_missing_returns_false(self, credential_store):
        assert credential_store.delete("NONEXISTENT") is False

    def test_list_names(self, credential_store):
        credential_store.set("B_KEY", "v1")
        credential_store.set("A_KEY", "v2")
        names = credential_store.list_names()
        assert "A_KEY" in names
        assert "B_KEY" in names
        assert names == sorted(names)

    def test_rotate_password(self, tmp_data):
        store = CredentialStore(tmp_data / ".creds_rotate.enc", "old-password")
        store.set("TOKEN", "abc123")
        store.rotate("new-password")

        # Old password should fail
        store_old = CredentialStore(tmp_data / ".creds_rotate.enc", "old-password")
        with pytest.raises(Exception):
            store_old.get("TOKEN")

        # New password should work
        store_new = CredentialStore(tmp_data / ".creds_rotate.enc", "new-password")
        assert store_new.get("TOKEN") == "abc123"
