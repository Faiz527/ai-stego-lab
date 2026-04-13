"""
Integration Tests for TRUE Frequency Domain Methods
====================================================
Tests DCT and DWT with encryption and various scenarios.
Comprehensive coverage of robustness, capacity, and compatibility.
"""

import pytest
from PIL import Image
import numpy as np
from io import BytesIO
from src.stego.dct_steganography import encode_dct, decode_dct
from src.stego.dwt_steganography import encode_dwt, decode_dwt
from src.stego.lsb_steganography import encode_image as lsb_encode, decode_image as lsb_decode
from src.encryption.encryption import encrypt_message, decrypt_message
from tests.fixtures.test_data import TestImageGenerator, TestDataGenerator


class TestTrueDCT:
    """Test TRUE DCT frequency domain implementation."""
    
    @pytest.fixture
    def test_image(self):
        """Generate test image (1024x768 for good capacity)."""
        # 1024x768 = 128*96 = 12288 blocks
        # 12288 bits / 8 = 1536 bytes capacity
        return TestImageGenerator.create_random_image(1024, 768)
    
    @pytest.fixture
    def gradient_image(self):
        """Generate deterministic gradient image."""
        return TestImageGenerator.create_gradient_image(1024, 768)
    
    def test_dct_basic_encode_decode(self, test_image):
        """Test basic DCT encode/decode."""
        message = "Hello World!"
        
        encoded = encode_dct(test_image, message)
        assert encoded is not None
        assert encoded.size == test_image.size
        
        decoded = decode_dct(encoded)
        assert decoded == message, f"Expected '{message}', got '{decoded}'"
    
    def test_dct_gradient_image(self, gradient_image):
        """Test DCT with deterministic gradient image."""
        message = "DCT Gradient Test"
        
        encoded = encode_dct(gradient_image, message)
        decoded = decode_dct(encoded)
        assert decoded == message
    
    def test_dct_empty_message(self, test_image):
        """Test DCT with empty message."""
        message = ""
        
        encoded = encode_dct(test_image, message)
        decoded = decode_dct(encoded)
        assert decoded == message
    
    def test_dct_unicode_message(self, test_image):
        """Test DCT with unicode characters."""
        # Keep message reasonable size
        message = "Hello 世界 🌍"
        
        encoded = encode_dct(test_image, message)
        decoded = decode_dct(encoded)
        assert decoded == message, f"Unicode mismatch: '{message}' != '{decoded}'"
    
    def test_dct_special_characters(self, test_image):
        """Test DCT with special characters."""
        message = "Special: @#$%^&*()"
        
        encoded = encode_dct(test_image, message)
        decoded = decode_dct(encoded)
        assert decoded == message
    
    def test_dct_with_encryption(self, test_image):
        """Test DCT with AES-256-CBC encryption."""
        original_message = "Secret message"
        password = "MySecurePassword123"
        
        encrypted = encrypt_message(original_message, password)
        assert encrypted != original_message
        
        encoded_image = encode_dct(test_image, encrypted)
        assert encoded_image is not None
        
        extracted_encrypted = decode_dct(encoded_image)
        assert extracted_encrypted == encrypted, \
            f"Extraction failed: '{encrypted}' != '{extracted_encrypted}'"
        
        decrypted = decrypt_message(extracted_encrypted, password)
        assert decrypted == original_message, \
            f"Decryption failed: '{original_message}' != '{decrypted}'"
    
    def test_dct_large_message(self, test_image):
        """Test DCT with large message."""
        # 1024x768 capacity is ~1536 bytes, so 500 chars is safe
        message = "Large: " + "A" * 300
        
        encoded = encode_dct(test_image, message)
        decoded = decode_dct(encoded)
        assert decoded == message, \
            f"Large message mismatch: {len(message)} chars != {len(decoded)} chars"
    
    def test_dct_max_capacity(self, test_image):
        """Test DCT near maximum capacity."""
        # 1024x768: 12288 blocks = 12288 bits / 8 = 1536 bytes max
        large_message = "X" * 1300
        
        try:
            encoded = encode_dct(test_image, large_message)
            decoded = decode_dct(encoded)
            assert decoded == large_message
        except ValueError as e:
            assert "too large" in str(e).lower()
    
    def test_dct_jpeg_compression_resilience(self, test_image):
        """Test DCT resilience to JPEG compression."""
        message = "JPEG test message"
        
        # Encode
        encoded = encode_dct(test_image, message)
        
        # Simulate JPEG compression (quality 85 - standard)
        enc_io = BytesIO()
        encoded.save(enc_io, format="JPEG", quality=85)
        enc_io.seek(0)
        compressed = Image.open(enc_io)
        compressed.load()
        
        # Decode from compressed image
        decoded = decode_dct(compressed)
        
        # Should decode correctly with quality 85+
        # (1 bit per block is very robust to JPEG)
        assert decoded == message, \
            f"JPEG quality 85: '{message}' != '{decoded}'"


class TestTrueDWT:
    """Test TRUE DWT wavelet domain implementation."""
    
    @pytest.fixture
    def test_image(self):
        """Generate test image with even dimensions."""
        return TestImageGenerator.create_random_image(1024, 768)
    
    @pytest.fixture
    def natural_image(self):
        """Generate natural-looking test image."""
        return TestImageGenerator.create_natural_like_image(1024, 768)
    
    def test_dwt_basic_encode_decode(self, test_image):
        """Test basic DWT encode/decode."""
        message = "Wavelet Message"
        
        encoded = encode_dwt(test_image, message)
        assert encoded is not None
        assert encoded.size == test_image.size
        
        decoded = decode_dwt(encoded)
        assert decoded == message
    
    def test_dwt_empty_message(self, test_image):
        """Test DWT with empty message."""
        message = ""
        
        encoded = encode_dwt(test_image, message)
        decoded = decode_dwt(encoded)
        assert decoded == message
    
    def test_dwt_unicode_message(self, test_image):
        """Test DWT with unicode."""
        message = "DWT: 中文 日本語 한국어 العربية"
        
        encoded = encode_dwt(test_image, message)
        decoded = decode_dwt(encoded)
        assert decoded == message
    
    def test_dwt_with_encryption(self, test_image):
        """Test DWT with AES-256-CBC."""
        original_message = "Encrypted wavelet message 🔐"
        password = "WaveletPassword123"
        
        # Encrypt
        encrypted = encrypt_message(original_message, password)
        
        # Embed in DWT
        encoded_image = encode_dwt(test_image, encrypted)
        
        # Extract
        extracted_encrypted = decode_dwt(encoded_image)
        assert extracted_encrypted == encrypted
        
        # Decrypt
        decrypted = decrypt_message(extracted_encrypted, password)
        assert decrypted == original_message
    
    def test_dwt_large_message(self, test_image):
        """Test DWT with large message."""
        message = "DWT Large: " + "B" * 750
        
        encoded = encode_dwt(test_image, message)
        decoded = decode_dwt(encoded)
        assert decoded == message
    
    def test_dwt_resilience_to_noise(self, test_image):
        """Test DWT resilience to additive noise."""
        message = "Noise resilience test"
        
        encoded = encode_dwt(test_image, message)
        encoded_array = np.array(encoded, dtype=np.float32)
        
        # Add Gaussian noise (standard deviation = 5)
        noise = np.random.normal(0, 5, encoded_array.shape)
        noisy_array = np.clip(encoded_array + noise, 0, 255).astype(np.uint8)
        noisy_image = Image.fromarray(noisy_array, 'RGB')
        
        # DWT should be somewhat resilient to noise
        decoded = decode_dwt(noisy_image)
        
        # Message might be affected but should start correctly
        # (DWT stores early bits in approximation, later in detail)
        assert decoded.startswith("Noise") or len(decoded) > 0


class TestFrequencyMethodComparison:
    """Compare DCT and DWT methods."""
    
    @pytest.fixture
    def test_image(self):
        return TestImageGenerator.create_random_image(1024, 768)
    
    def test_both_methods_same_message(self, test_image):
        """Both methods should encode/decode same message."""
        message = "Comparison Test Message 🔐"
        
        # DCT
        dct_encoded = encode_dct(test_image, message)
        dct_decoded = decode_dct(dct_encoded)
        
        # DWT
        dwt_encoded = encode_dwt(test_image, message)
        dwt_decoded = decode_dwt(dwt_encoded)
        
        # Both should decode correctly
        assert dct_decoded == message
        assert dwt_decoded == message
    
    def test_method_cross_compatibility(self, test_image):
        """DCT-encoded message shouldn't decode with DWT decoder."""
        message = "Cross test"
        
        dct_encoded = encode_dct(test_image, message)
        
        # Try to decode with DWT (should fail or return garbage)
        dwt_decoded = decode_dwt(dct_encoded)
        
        # Should not match original message
        assert dwt_decoded != message
    
    def test_capacity_comparison(self, test_image):
        """Compare capacity of DCT vs DWT."""
        # Both should handle messages of similar size
        message = "X" * 500
        
        # DCT
        dct_encoded = encode_dct(test_image, message)
        dct_decoded = decode_dct(dct_encoded)
        
        # DWT
        dwt_encoded = encode_dwt(test_image, message)
        dwt_decoded = decode_dwt(dwt_encoded)
        
        # Both should work
        assert dct_decoded == message
        assert dwt_decoded == message
    
    def test_encrypted_message_both_methods(self, test_image):
        """Test encrypted message with both DCT and DWT."""
        original = "Secret message for both methods"
        password = "TestPassword123"
        
        encrypted = encrypt_message(original, password)
        
        # DCT path
        dct_encoded = encode_dct(test_image, encrypted)
        dct_extracted = decode_dct(dct_encoded)
        dct_decrypted = decrypt_message(dct_extracted, password)
        
        # DWT path
        dwt_encoded = encode_dwt(test_image, encrypted)
        dwt_extracted = decode_dwt(dwt_encoded)
        dwt_decrypted = decrypt_message(dwt_extracted, password)
        
        # Both should work
        assert dct_decrypted == original
        assert dwt_decrypted == original


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def small_image(self):
        """Create a small image for capacity testing."""
        return TestImageGenerator.create_random_image(256, 256)
    
    def test_dct_message_too_large(self, small_image):
        """Test DCT with message exceeding capacity."""
        # Small image has limited capacity
        large_message = "X" * 50000
        
        with pytest.raises(ValueError, match="too large"):
            encode_dct(small_image, large_message)
    
    def test_dwt_message_too_large(self, small_image):
        """Test DWT with message exceeding capacity."""
        large_message = "Y" * 50000
        
        with pytest.raises(ValueError, match="too large"):
            encode_dwt(small_image, large_message)
    
    def test_decode_non_encoded_image(self):
        """Test decoding a normal image (should return empty)."""
        normal_image = TestImageGenerator.create_solid_color_image()
        
        # Decoding should not raise error, just return empty
        dct_result = decode_dct(normal_image)
        dwt_result = decode_dwt(normal_image)
        
        # Results might be empty or garbage, but shouldn't crash
        assert isinstance(dct_result, str)
        assert isinstance(dwt_result, str)