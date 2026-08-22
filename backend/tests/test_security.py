"""Tests for the security module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch


class MockSettings:
    APP_SECRET_KEY = "test-secret-key-for-testing"


@patch("app.security.get_settings", return_value=MockSettings())
def test_encrypt_decrypt_roundtrip(mock_settings):
    from app.security import encrypt_api_key, decrypt_api_key
    original = "AIzaSyB1234567890abcdefghijklmnop"
    encrypted = encrypt_api_key(original)
    assert encrypted != original
    assert encrypted != ""
    decrypted = decrypt_api_key(encrypted)
    assert decrypted == original


@patch("app.security.get_settings", return_value=MockSettings())
def test_encrypt_empty_key(mock_settings):
    from app.security import encrypt_api_key
    assert encrypt_api_key("") == ""


@patch("app.security.get_settings", return_value=MockSettings())
def test_decrypt_empty_key(mock_settings):
    from app.security import decrypt_api_key
    assert decrypt_api_key("") == ""


def test_mask_api_key():
    from app.security import mask_api_key
    assert mask_api_key("AIzaSyB1234567890abcdef") == "AIza...cdef"
    assert mask_api_key("sk-abc") == "sk...c"
    assert mask_api_key("") == ""
    assert mask_api_key("ab") == "ab...b"
