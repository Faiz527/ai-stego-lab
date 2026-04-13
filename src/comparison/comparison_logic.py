"""
comparison_logic.py
===================
Logic for comparison testing and method analysis.

Handles encoding with all three methods and result compilation.
"""

import time
import logging
from io import BytesIO
from PIL import Image

from src.stego.lsb_steganography import encode_image as lsb_encode
from src.stego.dct_steganography import encode_dct as dct_encode
from src.stego.dwt_steganography import encode_dwt as dwt_encode

logger = logging.getLogger(__name__)

def run_comparison_test(image_file, message):
    """
    Run comparison test on all three steganography methods.
    
    Args:
        image_file: Uploaded image file
        message: Message to encode
    
    Returns:
        dict: Results for each method with timing and images
    """
    original = Image.open(image_file)
    results = {}
    
    methods = [
        ("LSB", lsb_encode),
        ("Hybrid DCT", dct_encode),
        ("Hybrid DWT", dwt_encode)
    ]
    
    for method_name, encode_func in methods:
        try:
            start_time = time.time()
            encoded_image = encode_func(original, message)
            elapsed_time = time.time() - start_time
            
            # Calculate size
            buf = BytesIO()
            encoded_image.save(buf, format="PNG")
            size_kb = len(buf.getvalue()) / 1024
            
            results[method_name] = {
                "success": True,
                "image": encoded_image,
                "time": elapsed_time,
                "size_kb": size_kb
            }
            
            logger.info(f"{method_name}: SUCCESS in {elapsed_time:.3f}s ({size_kb:.1f}KB)")
        
        except Exception as e:
            error_msg = str(e)
            results[method_name] = {
                "success": False,
                "error": error_msg
            }
            logger.error(f"{method_name}: FAILED - {error_msg}")
    
    return results


def get_method_details():
    """
    Get detailed markdown descriptions for each method.
    
    Returns:
        dict: Markdown descriptions keyed by method
    """
    return {
        "LSB": """
### LSB (Least Significant Bit)

**How it works:**
- Replaces the least significant bit of each pixel
- Works directly on RGB values (spatial domain)
- Simple and extremely fast

**Pros:**
- ✅ Very fast encoding/decoding
- ✅ High capacity (~3 bits per pixel)
- ✅ Simple implementation

**Cons:**
- ❌ Vulnerable to statistical analysis
- ❌ Destroyed by JPEG compression
- ❌ Easily detectable with proper tools

**Best use case:** Quick, temporary message hiding when security isn't critical

**Parameters:**
- Filter type: None (default), Blur, Sharpen, Grayscale
- Supports all image modes (RGB, RGBA, Grayscale)
""",
        
        "DCT": """
### Hybrid DCT (Discrete Cosine Transform)

**How it works:**
- Converts image to YCbCr color space
- Applies DCT to 8×8 blocks on Y channel
- Embeds data in AC coefficients
- Uses quantization-index modulation (QIM) for robustness

**Pros:**
- ✅ Survives JPEG compression (up to 90% quality)
- ✅ More secure than LSB
- ✅ Good balance of capacity and security
- ✅ Auto-downsamples large images for performance

**Cons:**
- ❌ Lower capacity than LSB (~1.5KB per 1MB@ image)
- ❌ Slightly slower (DCT computation overhead)
- ❌ Can introduce subtle artifacts

**Best use case:** When images may be JPEG compressed

**Parameters:**
- Quantization step: 25 (fixed for robustness)
- Block size: 8×8 (JPEG compatible)
- Auto-downsampling: Enabled for 4K+ images
""",
        
        "DWT": """
### Hybrid DWT (Discrete Wavelet Transform)

**How it works:**
- Applies Haar wavelet transform (single level)
- Embeds data in wavelet coefficients (cH, cV, cD)
- Uses 3 subbands for higher capacity
- Requires even image dimensions

**Pros:**
- ✅ Highest security level
- ✅ Excellent imperceptibility
- ✅ Resistant to many attacks
- ✅ Good robustness to noise

**Cons:**
- ❌ Lowest capacity (~2KB per 1MB image)
- ❌ Slower processing (wavelet decomposition)
- ❌ Not JPEG safe
- ❌ Requires even dimensions

**Best use case:** Maximum security requirements

**Parameters:**
- Wavelet: Haar (single level)
- Subbands: 3 (cH, cV, cD)
- Quantization step: 25
- Auto-crops to even dimensions
"""
    }


def get_capacity_comparison(image_width, image_height, lsb_bits=1):
    """
    Calculate and compare capacity for all methods.
    
    Args:
        image_width: Image width in pixels
        image_height: Image height in pixels
        lsb_bits: LSB bits (for LSB method)
    
    Returns:
        dict: Capacity in bits for each method
    """
    total_pixels = image_width * image_height
    
    return {
        "LSB": total_pixels * 3 * lsb_bits,  # 3 channels × lsb_bits
        "DCT": (image_width // 8) * (image_height // 8),  # 1 bit per 8×8 block
        "DWT": ((image_width // 2) * (image_height // 2)) * 3  # 3 subbands
    }


def get_speed_estimate(image_width, image_height, method):
    """
    Provide estimated execution time for a method.
    
    Args:
        image_width: Image width
        image_height: Image height
        method: Method name (LSB, DCT, DWT)
    
    Returns:
        str: Estimated time description
    """
    total_pixels = image_width * image_height
    
    if method == "LSB":
        return "Instant (< 100ms)"
    elif method == "DCT":
        if total_pixels > 2_000_000:
            return "Fast (< 2s) - with auto-downsampling"
        return "Medium (< 1s)"
    elif method == "DWT":
        return "Moderate (1-3s)"
    else:
        return "Unknown"