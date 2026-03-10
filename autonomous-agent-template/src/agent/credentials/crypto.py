"""Fernet-based encryption with optional Rust extension acceleration."""

from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet

# Attempt to use the Rust extension for key derivation; fall back gracefully.
try:
    from agent_core_ext import derive_key as _rust_derive_key  # type: ignore[import]

    _HAS_RUST_EXT = True
except ImportError:
    _HAS_RUST_EXT = False

_ITERATIONS = 600_000
_SALT_SIZE = 16


def derive_fernet_key(password: str, salt: bytes) -> bytes:
    """Derive a URL-safe base64-encoded 32-byte key from a password + salt."""
    if _HAS_RUST_EXT:
        raw = _rust_derive_key(password, salt, _ITERATIONS)
    else:
        raw = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return base64.urlsafe_b64encode(raw)


def make_fernet(password: str, salt: bytes) -> Fernet:
    key = derive_fernet_key(password, salt)
    return Fernet(key)


def encrypt(plaintext: str, password: str) -> bytes:
    """Encrypt a string. Returns salt + ciphertext as raw bytes."""
    salt = os.urandom(_SALT_SIZE)
    f = make_fernet(password, salt)
    ct = f.encrypt(plaintext.encode())
    return salt + ct


def decrypt(data: bytes, password: str) -> str:
    """Decrypt bytes produced by :func:`encrypt`."""
    salt, ct = data[:_SALT_SIZE], data[_SALT_SIZE:]
    f = make_fernet(password, salt)
    return f.decrypt(ct).decode()
