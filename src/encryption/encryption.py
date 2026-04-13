"""
Encryption Module
=================
Handles message encryption and decryption using AES-256-CBC.

Security Features:
- AES-256 in CBC mode (256-bit key)
- PBKDF2-HMAC-SHA256 key derivation (100,000 iterations)
- Random 16-byte salt per encryption
- Random 16-byte IV per encryption
- HMAC-SHA256 authentication (encrypt-then-MAC)
- PKCS7 padding
- Constant-time MAC comparison

Wire format (base64-encoded):
    salt (16 B) || IV (16 B) || ciphertext (N B) || HMAC tag (32 B)
"""

import os
import hmac
import hashlib
import logging
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_SALT_LEN = 16          # bytes
_IV_LEN = 16            # AES block size
_KEY_LEN = 32           # 256 bits  →  AES-256
_HMAC_LEN = 32          # SHA-256 digest
_KDF_ITERATIONS = 100_000
_AES_BLOCK_BITS = 128   # for PKCS7 padder


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _derive_keys(password: str, salt: bytes) -> tuple:
    """
    Derive separate AES-256 encryption key and HMAC-SHA256 key from a
    password using PBKDF2-HMAC-SHA256.

    Returns:
        (enc_key, mac_key)  — each 32 bytes
    """
    # 64 bytes of key material: first half → AES key, second half → HMAC key
    key_material = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _KDF_ITERATIONS,
        dklen=_KEY_LEN * 2,
    )
    return key_material[:_KEY_LEN], key_material[_KEY_LEN:]


def _compute_mac(mac_key: bytes, data: bytes) -> bytes:
    """Return HMAC-SHA256 over *data*."""
    return hmac.new(mac_key, data, hashlib.sha256).digest()


# ---------------------------------------------------------------------------
# Public API  (signatures unchanged — drop-in replacement)
# ---------------------------------------------------------------------------

def encrypt_message(message, password):
    """
    Encrypt a message with AES-256-CBC + HMAC-SHA256.

    Args:
        message:  str or bytes — plaintext to encrypt.
        password: str or bytes — password used for key derivation.

    Returns:
        str — Base64-encoded ciphertext payload.

    Raises:
        ValueError: on any encryption failure.
    """
    try:
        # --- normalise inputs ------------------------------------------------
        if isinstance(password, bytes):
            password = password.decode("utf-8")
        if isinstance(message, bytes):
            message = message.decode("utf-8")

        # --- random nonces ---------------------------------------------------
        salt = os.urandom(_SALT_LEN)
        iv = os.urandom(_IV_LEN)

        # --- key derivation --------------------------------------------------
        enc_key, mac_key = _derive_keys(password, salt)

        # --- PKCS7 pad -------------------------------------------------------
        padder = sym_padding.PKCS7(_AES_BLOCK_BITS).padder()
        padded = padder.update(message.encode("utf-8")) + padder.finalize()

        # --- AES-256-CBC encrypt ---------------------------------------------
        cipher = Cipher(
            algorithms.AES(enc_key),
            modes.CBC(iv),
            backend=default_backend(),
        )
        ciphertext = cipher.encryptor().update(padded) + cipher.encryptor().finalize()

        # NOTE: encryptor must be used as a single context to avoid state issues
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()

        # --- encrypt-then-MAC ------------------------------------------------
        payload = salt + iv + ciphertext          # authenticated data
        tag = _compute_mac(mac_key, payload)

        # --- encode to base64 string -----------------------------------------
        result = base64.b64encode(payload + tag).decode("utf-8")

        logger.info("Message encrypted successfully with AES-256-CBC")
        return result

    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise ValueError(f"Encryption failed: {e}")


def decrypt_message(encrypted_text, password):
    """
    Decrypt a payload produced by :func:`encrypt_message`.

    Args:
        encrypted_text: str or bytes — Base64-encoded payload.
        password:       str or bytes — password for key derivation.

    Returns:
        str — decrypted plaintext.

    Raises:
        ValueError: wrong password, tampered data, or malformed input.
    """
    try:
        # --- normalise inputs ------------------------------------------------
        if isinstance(encrypted_text, bytes):
            encrypted_text = encrypted_text.decode("utf-8")
        if isinstance(password, bytes):
            password = password.decode("utf-8")

        # --- decode base64 ---------------------------------------------------
        raw = base64.b64decode(encrypted_text.encode("utf-8"))

        # minimum: salt + iv + one AES block + hmac
        _MIN_LEN = _SALT_LEN + _IV_LEN + 16 + _HMAC_LEN
        if len(raw) < _MIN_LEN:
            raise ValueError("Invalid encrypted data: payload too short")

        # --- split components ------------------------------------------------
        salt = raw[:_SALT_LEN]
        iv = raw[_SALT_LEN : _SALT_LEN + _IV_LEN]
        tag_received = raw[-_HMAC_LEN:]
        ciphertext = raw[_SALT_LEN + _IV_LEN : -_HMAC_LEN]
        payload = raw[:-_HMAC_LEN]                # salt + iv + ciphertext

        # --- key derivation --------------------------------------------------
        enc_key, mac_key = _derive_keys(password, salt)

        # --- verify HMAC (constant-time) -------------------------------------
        tag_computed = _compute_mac(mac_key, payload)
        if not hmac.compare_digest(tag_computed, tag_received):
            raise ValueError(
                "Authentication failed: wrong password or tampered data"
            )

        # --- AES-256-CBC decrypt ---------------------------------------------
        cipher = Cipher(
            algorithms.AES(enc_key),
            modes.CBC(iv),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # --- remove PKCS7 padding --------------------------------------------
        unpadder = sym_padding.PKCS7(_AES_BLOCK_BITS).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        logger.info("Message decrypted successfully with AES-256-CBC")
        return plaintext.decode("utf-8")

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError(f"Decryption failed: {e}")
