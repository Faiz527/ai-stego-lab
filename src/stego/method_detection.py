"""
Steganography Method Detection
================================
Automatically detects which steganography method was used.
Analyzes image characteristics to determine encoding method.
"""

import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def detect_encoding_method(image):
    """
    Auto-detect which steganography method was used.
    
    Strategy: Try actual decoding with each method (with timeout logic).
    Return the first method that produces a valid message.
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    logger.info("Attempting to detect encoding method...")
    
    results = {}
    
    # Strategy 1: Try LSB first (fastest)
    logger.debug("Attempting LSB decode...")
    from src.stego.lsb_steganography import decode_image as lsb_decode
    try:
        decoded = lsb_decode(image)
        if _is_valid_message(decoded):
            logger.info("✓ Detected: LSB method")
            results['LSB'] = decoded
    except Exception as e:
        logger.debug(f"LSB decode failed: {e}")
    
    # Strategy 2: Try DCT
    logger.debug("Attempting DCT decode...")
    from src.stego.dct_steganography import decode_dct
    try:
        decoded = decode_dct(image)
        if _is_valid_message(decoded):
            logger.info("✓ Detected: DCT method")
            results['DCT'] = decoded
    except Exception as e:
        logger.debug(f"DCT decode failed: {e}")
    
    # Strategy 3: Try DWT
    logger.debug("Attempting DWT decode...")
    from src.stego.dwt_steganography import decode_dwt
    try:
        decoded = decode_dwt(image)
        if _is_valid_message(decoded):
            logger.info("✓ Detected: DWT method")
            results['DWT'] = decoded
    except Exception as e:
        logger.debug(f"DWT decode failed: {e}")
    
    # Pick the best result — prefer the one with highest printable ratio
    if results:
        best_method = max(results.keys(), key=lambda m: _message_quality_score(results[m]))
        logger.info(f"✓ Best detection: {best_method}")
        return best_method
    
    # Default to LSB
    logger.info("✓ No valid message found, defaulting to LSB")
    return 'LSB'


def _message_quality_score(text):
    """Score a decoded message by how 'real' it looks."""
    if not text:
        return 0
    printable = sum(1 for c in text if 32 <= ord(c) < 127)
    return printable / len(text)


def _is_valid_message(decoded_text):
    """
    Check if decoded text looks like valid UTF-8 message.
    
    Args:
        decoded_text (str): Text to validate
    
    Returns:
        bool: True if looks like valid message
    """
    if not decoded_text:
        return False
    
    # Check length (reasonable message)
    if len(decoded_text) < 2 or len(decoded_text) > 100_000:
        return False
    
    # Check if mostly printable characters
    printable_chars = sum(1 for c in decoded_text if 32 <= ord(c) < 127 or ord(c) > 127)
    printable_ratio = printable_chars / len(decoded_text)
    
    if printable_ratio < 0.7:
        return False
    
    return True