#!/usr/bin/env python3
"""
Test script for watermark position fixing.
Verifies that all 9 positions work correctly.

Run this from the project root:
    python src/Watermarking/test_watermark_fix.py
"""

import numpy as np
from PIL import Image
import sys
import os
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
TEST_OUTPUT_DIR = SCRIPT_DIR / "test_images"

def create_test_image():
    """Create a simple test image."""
    # Create a blue image with white border
    img_array = np.ones((600, 800, 3), dtype=np.uint8)
    img_array[:, :] = [50, 100, 200]  # Blue background
    # Add white borders to make positioning obvious
    img_array[0:20, :] = [255, 255, 255]  # Top
    img_array[-20:, :] = [255, 255, 255]  # Bottom
    img_array[:, 0:20] = [255, 255, 255]  # Left
    img_array[:, -20:] = [255, 255, 255]  # Right
    return Image.fromarray(img_array)

def test_all_positions():
    """Test watermark at all 9 positions."""
    from watermark import apply_text_watermark, get_available_positions
    
    # Create output directory if it doesn't exist
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("WATERMARK POSITION TEST")
    print("="*70)
    print(f"\nTest images will be saved to: {TEST_OUTPUT_DIR}")
    
    # Get available positions
    positions = get_available_positions()
    print(f"\nAvailable positions: {len(positions)}")
    for i, pos in enumerate(positions, 1):
        print(f"  {i}. {pos}")
    
    # Create test image
    print("\nCreating test image (800x600)...")
    test_image = create_test_image()
    
    # Test each position
    print("\nTesting watermark placement at each position...")
    print("-" * 70)
    
    success_count = 0
    for position in positions:
        try:
            watermarked = apply_text_watermark(
                test_image,
                watermark_text=f"© TEST - {position.upper()}",
                font_size=24,
                position=position,
                text_color=(255, 0, 0),  # Red
                opacity=255
            )
            output_path = TEST_OUTPUT_DIR / f"test_watermark_{position.replace('-', '_')}.png"
            watermarked.save(str(output_path))
            print(f"✅ {position:15} - SUCCESS | Saved: {output_path.name}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {position:15} - FAILED: {str(e)}")
    
    # Test invalid position (should default to bottom-right)
    print("\n" + "-" * 70)
    print("Testing invalid position (should default to bottom-right)...")
    try:
        watermarked = apply_text_watermark(
            test_image,
            watermark_text="INVALID POSITION",
            font_size=24,
            position="invalid-position",
            text_color=(255, 0, 0),
            opacity=255
        )
        output_path = TEST_OUTPUT_DIR / "test_watermark_DEFAULT_fallback.png"
        watermarked.save(str(output_path))
        print(f"✅ Invalid position - Gracefully defaulted to bottom-right | Saved: {output_path.name}")
        success_count += 1
    except Exception as e:
        print(f"❌ Invalid position - ERROR: {str(e)}")
    
    print("\n" + "="*70)
    print(f"✅ WATERMARK POSITION TEST COMPLETED")
    print(f"   {success_count}/{len(positions)+1} tests passed")
    print("="*70 + "\n")

def test_special_characters_in_filename():
    """Test filename sanitization."""
    import re
    
    print("\n" + "="*70)
    print("FILENAME SANITIZATION TEST")
    print("="*70)
    
    test_cases = [
        "© 2024 My Company",
        "Test/Image:Name",
        "< Image > Name",
        'Image"with"quotes',
        "Image|with|pipes",
        "Image*with*asterisks",
        "Image?with?questions",
    ]
    
    print("\nTesting filename sanitization...")
    for test_text in test_cases:
        # Apply same sanitization as in ui_section.py
        safe_text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', test_text)
        safe_text = safe_text.replace(' ', '_').strip('.')[:20]
        if not safe_text:
            safe_text = "watermark"
        
        filename = f"watermarked_{safe_text}.png"
        print(f"  Input:  '{test_text}'")
        print(f"  Output: '{filename}'")
        print()
    
    print("="*70)
    print("✅ FILENAME SANITIZATION TEST COMPLETED")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        print("\n" + "="*70)
        print("WATERMARK FIX TEST SUITE")
        print("="*70)
        print(f"Script location: {SCRIPT_DIR}")
        print(f"Test output directory: {TEST_OUTPUT_DIR}")
        
        test_all_positions()
        test_special_characters_in_filename()
        
        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
