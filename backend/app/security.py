"""
Security Utilities

Handles API key encryption/decryption and masking.
Uses Fernet symmetric encryption derived from APP_SECRET_KEY.
"""

import base64
import hashlib

from cryptography.fernet import Fernet

from app.config import get_settings


def _get_fernet() -> Fernet:
    """Create a Fernet cipher from the app secret key."""
    settings = get_settings()
    # Derive a 32-byte key from the app secret
    key = hashlib.sha256(settings.APP_SECRET_KEY.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


def encrypt_api_key(plain_key: str) -> str:
    """Encrypt an API key for storage."""
    if not plain_key:
        return ""
    f = _get_fernet()
    return f.encrypt(plain_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage."""
    if not encrypted_key:
        return ""
    f = _get_fernet()
    return f.decrypt(encrypted_key.encode()).decode()


def mask_api_key(plain_key: str) -> str:
    """
    Mask an API key for safe display.

    Examples:
        "AIzaSyB1234567890abcdef" → "AIza...cdef"
        "sk-abc123" → "sk-a...3"
        "" → ""
    """
    if not plain_key:
        return ""
    if len(plain_key) <= 8:
        return plain_key[:2] + "..." + plain_key[-1:]
    return plain_key[:4] + "..." + plain_key[-4:]
