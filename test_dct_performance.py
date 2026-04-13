"""
Quick test to verify DCT optimization is working.
"""
import time
from PIL import Image
import numpy as np
import sys
from pathlib import Path

# Add the project to path
BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH))

from src.stego.dct_steganography import encode_dct, decode_dct

def test_dct_encoding():
    """Test DCT encoding with progress tracking."""
    print("=" * 60)
    print("DCT ENCODING TEST")
    print("=" * 60)
    
    # Create a test image (large)
    print("\n1. Creating test image (1920x1080)...")
    test_img = Image.new('RGB', (1920, 1080), color=(128, 128, 128))
    test_message = "This is a secret message hidden in the image using DCT steganography!"
    
    # Test callback to track progress
    progress_updates = []
    def track_progress(fraction):
        progress_updates.append(fraction)
        print(f"   Progress: {fraction*100:.1f}%")
    
    # Encode with progress tracking
    print("\n2. Encoding message with progress tracking...")
    start_time = time.time()
    encoded_img = encode_dct(test_img, test_message, update_progress=track_progress)
    encode_time = time.time() - start_time
    
    print(f"\n✅ Encoding completed in {encode_time:.2f} seconds")
    print(f"   Progress updates received: {len(progress_updates)}")
    
    # Decode with progress tracking
    print("\n3. Decoding message with progress tracking...")
    progress_updates = []
    start_time = time.time()
    decoded_msg = decode_dct(encoded_img, update_progress=track_progress)
    decode_time = time.time() - start_time
    
    print(f"\n✅ Decoding completed in {decode_time:.2f} seconds")
    print(f"   Progress updates received: {len(progress_updates)}")
    print(f"   Decoded message: '{decoded_msg}'")
    print(f"   Message match: {decoded_msg == test_message}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Encode time: {encode_time:.2f}s")
    print(f"Decode time: {decode_time:.2f}s")
    print(f"Total time: {encode_time + decode_time:.2f}s")
    
    if decode_time > 5:
        print("⚠️  WARNING: Decode time is slow (expected < 5s for 1920x1080)")
    else:
        print("✅ Performance looks good!")
    
    if decoded_msg == test_message:
        print("✅ Message integrity verified")
    else:
        print("❌ Message corruption detected!")
    
    return encode_time, decode_time

if __name__ == "__main__":
    test_dct_encoding()
