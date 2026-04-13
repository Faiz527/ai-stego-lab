"""
Test Suite for AES-256-CBC Encryption Module
=============================================
Tests AES-256-CBC encryption/decryption with various inputs and edge cases.
"""

import pytest
import base64
from src.encryption.encryption import encrypt_message, decrypt_message


@pytest.mark.unit
class TestAES256Encryption:
    """Tests for AES-256-CBC encrypt & decrypt."""

    def test_encrypt_decrypt_basic(self):
        """Test basic encryption and decryption round-trip."""
        msg = "Hello, World!"
        pwd = "secretpassword"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_encrypt_decrypt_long_message(self):
        """Test with very long message (10,000 characters)."""
        msg = "A" * 10_000
        pwd = "longpassword123"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_encrypt_decrypt_special_characters(self):
        """Test with special characters and symbols."""
        msg = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        pwd = "sp3c!@l"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_encrypt_decrypt_unicode(self):
        """Test with Unicode characters and emojis."""
        msg = "こんにちは世界 🌍 مرحبا"
        pwd = "unicode_test"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_encrypt_decrypt_empty_message(self):
        """Test with empty message."""
        msg = ""
        pwd = "emptytest"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_wrong_password_raises_error(self):
        """Test that wrong password raises ValueError."""
        msg = "secret data"
        encrypted = encrypt_message(msg, "correct_password")
        with pytest.raises(ValueError, match="wrong password|tampered|failed"):
            decrypt_message(encrypted, "wrong_password")

    def test_corrupted_data_raises_error(self):
        """Test that corrupted ciphertext raises ValueError."""
        encrypted = encrypt_message("test", "password")
        # Flip a character in the middle
        mid = len(encrypted) // 2
        corrupted = encrypted[:mid] + ("A" if encrypted[mid] != "A" else "B") + encrypted[mid + 1:]
        with pytest.raises(ValueError):
            decrypt_message(corrupted, "password")

    def test_invalid_base64_raises_error(self):
        """Test that invalid base64 raises ValueError."""
        with pytest.raises(ValueError):
            decrypt_message("not-valid-base64!!!", "password")

    def test_bytes_input_password(self):
        """Test with bytes password instead of string."""
        msg = "bytes password test"
        pwd = b"bytespassword"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_bytes_input_message(self):
        """Test with bytes message instead of string."""
        msg = b"bytes message"
        pwd = "password"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == "bytes message"

    def test_bytes_input_both(self):
        """Test with both bytes message and bytes password."""
        msg = b"both bytes"
        pwd = b"both_pwd"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == "both bytes"

    def test_same_password_different_ciphertext(self):
        """Random salt + IV must produce different ciphertexts each time."""
        msg = "identical"
        pwd = "same_password"
        enc1 = encrypt_message(msg, pwd)
        enc2 = encrypt_message(msg, pwd)
        assert enc1 != enc2
        # But both decrypt to the same plaintext
        assert decrypt_message(enc1, pwd) == msg
        assert decrypt_message(enc2, pwd) == msg

    def test_very_long_password(self):
        """Test with very long password (10,000 characters)."""
        msg = "long password test"
        pwd = "p" * 10_000
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_numeric_only_message(self):
        """Test with numeric-only message."""
        msg = "1234567890" * 50
        pwd = "numtest"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_multiple_encryptions_consistency(self):
        """10 successive round-trips must all succeed."""
        for i in range(10):
            msg = f"consistency check #{i}"
            pwd = f"pass_{i}"
            encrypted = encrypt_message(msg, pwd)
            assert decrypt_message(encrypted, pwd) == msg


@pytest.mark.unit
class TestEncryptionEdgeCases:
    """Edge cases for encryption."""

    def test_too_short_encrypted_data(self):
        """Payload shorter than salt+IV+block+HMAC must be rejected."""
        short = base64.b64encode(b"tooshort").decode()
        with pytest.raises(ValueError, match="too short"):
            decrypt_message(short, "password")

    def test_whitespace_in_message(self):
        """Test message with leading/trailing whitespace."""
        msg = "   leading and trailing whitespace   "
        pwd = "ws_test"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_newlines_and_special_formatting(self):
        """Test with newlines and special formatting characters."""
        msg = "line1\nline2\ttab\r\nwindows"
        pwd = "fmt_test"
        encrypted = encrypt_message(msg, pwd)
        assert decrypt_message(encrypted, pwd) == msg

    def test_encrypted_output_is_base64_string(self):
        """Verify encrypted output is valid base64 string."""
        encrypted = encrypt_message("test", "password")
        assert isinstance(encrypted, str)
        # Must be valid base64
        decoded = base64.b64decode(encrypted)
        # salt(16) + iv(16) + ≥16 ciphertext + hmac(32) = ≥80
        assert len(decoded) >= 80

    def test_decrypt_returns_string(self):
        """Verify decrypt always returns string."""
        encrypted = encrypt_message("hello", "pwd")
        result = decrypt_message(encrypted, "pwd")
        assert isinstance(result, str)

    def test_tampered_hmac_rejected(self):
        """Flipping the last byte (HMAC) must fail authentication."""
        encrypted = encrypt_message("tamper test", "password")
        raw = bytearray(base64.b64decode(encrypted))
        raw[-1] ^= 0xFF  # flip last byte of HMAC
        tampered = base64.b64encode(bytes(raw)).decode()
        with pytest.raises(ValueError, match="wrong password|tampered|failed"):
            decrypt_message(tampered, "password")