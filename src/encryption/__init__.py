"""
Encryption Module
=================
Implements AES-256-CBC encryption with PBKDF2 key derivation.
Provides secure message encryption/decryption with authentication.
"""

from .encryption import encrypt_message, decrypt_message

__all__ = [
    'encrypt_message',
    'decrypt_message',
]
