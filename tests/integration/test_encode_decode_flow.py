"""
Integration Tests: End-to-End Encode/Decode Workflows
======================================================
Tests complete workflows combining steganography and encryption.
"""

import pytest
from src.stego.lsb_steganography import encode_image, decode_image
from src.stego.dct_steganography import encode_dct, decode_dct
from src.stego.dwt_steganography import encode_dwt, decode_dwt
from src.encryption.encryption import encrypt_message, decrypt_message


@pytest.mark.integration
class TestEncodeDecodeWithEncryption:
    """Test workflows combining steganography with encryption."""

    def test_lsb_with_encryption_roundtrip(self, test_image_800x600):
        """Test LSB encoding + message encryption complete workflow."""
        original_msg = "Secret message to encrypt"
        password = "encryption_password_123"
        
        # Step 1: Encrypt message
        encrypted_msg = encrypt_message(original_msg, password)
        
        # Step 2: Embed encrypted message using LSB
        encoded_image = encode_image(test_image_800x600, encrypted_msg, "None")
        
        # Step 3: Extract encrypted message from image
        extracted_encrypted = decode_image(encoded_image)
        
        # Step 4: Decrypt message
        decrypted_msg = decrypt_message(extracted_encrypted, password)
        
        # Verify: should match original
        assert decrypted_msg == original_msg

    def test_dct_with_encryption_roundtrip(self, test_image_800x600):
        """Test DCT encoding + message encryption complete workflow."""
        original_msg = "Another secret message"
        password = "another_password_456"
        
        encrypted_msg = encrypt_message(original_msg, password)
        encoded_image = encode_dct(test_image_800x600, encrypted_msg)
        extracted_encrypted = decode_dct(encoded_image)
        decrypted_msg = decrypt_message(extracted_encrypted, password)
        
        assert decrypted_msg == original_msg

    def test_dwt_with_encryption_roundtrip(self, test_image_800x600):
        """Test DWT encoding + message encryption complete workflow."""
        original_msg = "DWT with encryption test"
        password = "dwt_password_789"
        
        encrypted_msg = encrypt_message(original_msg, password)
        encoded_image = encode_dwt(test_image_800x600, encrypted_msg)
        extracted_encrypted = decode_dwt(encoded_image)
        decrypted_msg = decrypt_message(extracted_encrypted, password)
        
        assert decrypted_msg == original_msg

    def test_invalid_password_fails(self, test_image_800x600):
        """Test that decryption with wrong password fails."""
        msg = "Protected message"
        correct_pwd = "correct_password"
        wrong_pwd = "wrong_password"
        
        # Encrypt with correct password
        encrypted = encrypt_message(msg, correct_pwd)
        encoded = encode_image(test_image_800x600, encrypted, "None")
        extracted = decode_image(encoded)
        
        # Try to decrypt with wrong password (should fail)
        with pytest.raises(ValueError):
            decrypt_message(extracted, wrong_pwd)

    def test_all_methods_with_unicode(self, test_image_800x600):
        """Test all methods with Unicode content and encryption."""
        original_msg = "こんにちは世界 🌍"
        password = "unicode_password"
        
        encrypted = encrypt_message(original_msg, password)
        
        # Test each method
        methods = [
            (encode_image, decode_image, "LSB"),
            (encode_dct, decode_dct, "DCT"),
            (encode_dwt, decode_dwt, "DWT"),
        ]
        
        for encode_func, decode_func, method_name in methods:
            encoded = encode_func(test_image_800x600, encrypted)
            extracted = decode_func(encoded)
            decrypted = decrypt_message(extracted, password)
            assert decrypted == original_msg, f"{method_name} failed with Unicode"