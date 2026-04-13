"""
LSB Steganography Module
=========================
Implements Least Significant Bit (LSB) steganography in spatial domain.
Supports optional image filtering for preprocessing.
"""

from PIL import Image, ImageFilter
import numpy as np


# ============================================================================
#                   IMAGE FILTERING (LSB Method)
# ============================================================================

def apply_filter(img, filter_type):
    """
    Apply optional image filter for preprocessing.
    
    Args:
        img (PIL.Image): Input image
        filter_type (str): Type of filter ('None', 'Blur', 'Sharpen', 'Grayscale')
    
    Returns:
        PIL.Image: Filtered image or original if filter_type is 'None'
    """
    if filter_type == "Blur":
        return img.filter(ImageFilter.GaussianBlur(radius=2))
    elif filter_type == "Sharpen":
        return img.filter(ImageFilter.SHARPEN)
    elif filter_type == "Grayscale":
        return img.convert('L').convert('RGB')
    else:  # "None" or default
        return img


# ============================================================================
#                          LSB METHOD (SPATIAL DOMAIN)
# ============================================================================

def encode_image(img, secret_text, filter_type="None"):
    """
    Encode secret message into image using LSB steganography.
    
    Args:
        img (PIL.Image): Input image
        secret_text (str): Message to encode
        filter_type (str): Filter type ('None', 'Blur', 'Sharpen', 'Grayscale')
    
    Returns:
        PIL.Image: Encoded image
    
    Raises:
        ValueError: If message is too large for image
    """
    # Apply optional filter
    img = apply_filter(img, filter_type)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Calculate capacity
    img_array = np.array(img)
    max_bytes = img_array.size // 8  # Total bits / 8
    
    # Encode message as UTF-8 bytes
    # Accept both str and bytes/bytearray input
    if isinstance(secret_text, (bytes, bytearray)):
        secret_bytes = bytes(secret_text)
    else:
        secret_bytes = secret_text.encode('utf-8')
    message_length = len(secret_bytes)
    
    # Check capacity: 2 bytes for length + message
    if message_length + 2 > max_bytes:
        raise ValueError(
            f"Message too large! Max: {max_bytes - 2} bytes, "
            f"got: {message_length} bytes"
        )
    
    # Flatten image array
    flat = img_array.flatten()
    
    # Prepare bit string: 16-bit length prefix + message bits
    bit_string = format(message_length, '016b')  # 16-bit length
    for byte in secret_bytes:
        bit_string += format(byte, '08b')
    
    # Add terminator (optional, helps with decoding)
    bit_string += '11111110'
    
    # Embed bits into LSBs
    for i, bit in enumerate(bit_string):
        if i < len(flat):
            flat[i] = (flat[i] & 0xFE) | int(bit)  # Replace LSB
    
    # Reshape and convert back to image
    encoded_array = flat.reshape(img_array.shape).astype(np.uint8)
    encoded_img = Image.fromarray(encoded_array, 'RGB')
    
    return encoded_img


def decode_image(img):
    """
    Decode secret message from LSB-encoded image.
    
    Args:
        img (PIL.Image): Encoded image
    
    Returns:
        str: Decoded message (empty string if no message found)
    """
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert image to array
    img_array = np.array(img)
    flat = img_array.flatten()
    
    # Extract bits
    bits = ''.join(str(pixel & 1) for pixel in flat)
    
    # Extract message length (first 16 bits)
    if len(bits) < 16:
        return ''
    
    message_length = int(bits[:16], 2)
    
    # Check if message length is valid
    if message_length == 0 or message_length > len(bits) // 8:
        return ''
    
    # Extract message bits
    message_bits = bits[16 : 16 + (message_length * 8)]
    
    # Convert bits to bytes
    message_bytes = bytearray()
    for i in range(0, len(message_bits), 8):
        byte_bits = message_bits[i : i + 8]
        if len(byte_bits) == 8:
            message_bytes.append(int(byte_bits, 2))
    
    # Decode from UTF-8
    try:
        message = message_bytes.decode('utf-8')
        return message
    except UnicodeDecodeError:
        # If UTF-8 decode fails, try with error handling
        return message_bytes.decode('utf-8', errors='replace')
