"""
demo_hide_extract.py
Complete steganography demo: hide secret message, corrupt, extract, recover
"""
from pathlib import Path
from PIL import Image
import numpy as np
from typing import List, Tuple

# Module imports
from stegotool.modules.module3_pixel_selector.selector_baseline import select_pixels
from stegotool.modules.module6_redundancy.rs_wrapper import add_redundancy, recover_redundancy
from stegotool.modules.module6_redundancy.corruption_simulator import recompress_and_reload
from stegotool.modules.module6_redundancy.capacity_checker import can_fit_payload

# =============================================================================
# Helper: Generate demo images if they don't exist
# =============================================================================

def generate_demo_images_if_needed():
    """Create synthetic demo images if directory is empty."""
    outdir = Path("stegotool/data/dev_images")
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Check if images already exist
    existing = list(outdir.glob("*.png")) + list(outdir.glob("*.jpg"))
    if existing:
        print(f"✓ Found {len(existing)} existing images in {outdir}")
        return outdir / existing[0].name
    
    print(f"⚠ No images found in {outdir}. Generating demo images...")
    
    def make_gradient_noise(w, h, seed=0):
        rng = np.random.RandomState(seed)
        x = np.linspace(0, 255, w, dtype=np.uint8)
        y = np.linspace(0, 255, h, dtype=np.uint8)[:, None]
        grad = ((x + y) // 2).astype(np.uint8)
        for i in range(8):
            noise = (rng.randint(0, 60, (h, w))).astype(np.uint8)
            ch0 = np.clip(grad + noise + i * 5, 0, 255).astype(np.uint8)
            ch1 = np.clip(grad + noise[::-1, :] + i * 3, 0, 255).astype(np.uint8)
            ch2 = np.clip(grad + noise[:, ::-1] + i * 7, 0, 255).astype(np.uint8)
            rgb = np.stack([ch0, ch1, ch2], axis=2).astype(np.uint8)
            Image.fromarray(rgb).save(outdir / f"demo_{i+1}.png")
        print(f"✓ Generated 8 demo images in {outdir}")
    
    make_gradient_noise(512, 384)
    return outdir / "demo_1.png"

# =============================================================================
# Minimal LSB embedding/extraction (from generate_labels_robust.py)
# =============================================================================

def _bytes_to_bits(b: bytes) -> List[int]:
    bits = []
    for byte in b:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits

def _bits_to_bytes(bits: List[int]) -> bytes:
    while len(bits) % 8 != 0:
        bits.append(0)
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | (bits[i + j] & 1)
        out.append(byte)
    return bytes(out)

def embed_bytes_into_pixels(image_pil: Image.Image, payload: bytes, 
                            coords: List[Tuple[int,int]], lsb_bits: int = 1) -> Image.Image:
    """Embed payload bits into specified pixel coordinates."""
    arr = np.array(image_pil, dtype=np.uint8).copy()  # H x W x 3
    h, w, c = arr.shape
    assert c == 3
    
    capacity_bits = len(coords) * 3 * lsb_bits
    payload_bits = _bytes_to_bits(payload)
    
    if len(payload_bits) > capacity_bits:
        raise ValueError(f"Payload too large: {len(payload_bits)} bits vs capacity {capacity_bits}")
    
    # Pad payload bits
    payload_bits += [0] * (capacity_bits - len(payload_bits))
    
    bit_idx = 0
    for (x, y) in coords:
        for ch in range(3):
            for b in range(lsb_bits):
                bit = int(payload_bits[bit_idx])
                mask = 1 << b
                # FIX: Clear the bit at position b, then set it to the payload bit
                arr[y, x, ch] = np.uint8((int(arr[y, x, ch]) & (255 - mask)) | (bit << b))
                bit_idx += 1
    
    return Image.fromarray(arr)

def extract_bytes_from_pixels(image_pil: Image.Image, num_payload_bytes: int, 
                              coords: List[Tuple[int,int]], lsb_bits: int = 1) -> bytes:
    """Extract payload bits from specified pixel coordinates."""
    arr = np.array(image_pil)
    h, w, c = arr.shape
    
    capacity_bits = len(coords) * 3 * lsb_bits
    needed_bits = num_payload_bytes * 8
    
    if needed_bits > capacity_bits:
        raise ValueError("Requested more bytes than capacity of coords")
    
    bits = []
    bit_idx = 0
    for (x, y) in coords:
        for ch in range(3):
            for b in range(lsb_bits):
                if bit_idx >= needed_bits:
                    break
                val = (int(arr[y, x, ch]) >> b) & 1
                bits.append(int(val))
                bit_idx += 1
            if bit_idx >= needed_bits:
                break
        if bit_idx >= needed_bits:
            break
    
    return _bits_to_bytes(bits)

# =============================================================================
# Main Demo
# =============================================================================

def main():
    print("=" * 70)
    print("STEGANOGRAPHY DEMO: Hide → Compress → Extract → Recover")
    print("=" * 70)
    
    # Generate demo images if needed
    img_path = generate_demo_images_if_needed()
    
    # Load image
    print(f"\n[1] Loading image: {img_path}")
    img = Image.open(img_path).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    print(f"    Image size: {w}×{h}")
    
    # Secret message
    secret_msg = b"Hello Stego World! This is a hidden message."
    print(f"\n[2] Secret message: {secret_msg.decode()}")
    print(f"    Original size: {len(secret_msg)} bytes")
    
    # Step 1: Add ECC (error correction)
    nsym = 32  # Reed-Solomon parity bytes
    print(f"\n[3] Adding Reed-Solomon ECC (nsym={nsym})...")
    ecc_payload = add_redundancy(secret_msg, nsym=nsym)
    print(f"    With ECC: {len(ecc_payload)} bytes")
    
    # Step 2: Select pixels
    print(f"\n[4] Selecting pixels for embedding...")
    payload_bits = len(ecc_payload) * 8
    coords = select_pixels(arr, payload_bits=payload_bits, patch_size=5, lsb_bits=1)
    print(f"    Pixels selected: {len(coords)}")
    print(f"    Capacity: {len(coords) * 3 * 1} bits = {len(coords) * 3 // 8} bytes")
    
    # Step 3: Check capacity
    print(f"\n[5] Checking capacity...")
    fits, available = can_fit_payload((w, h), len(secret_msg), nsym=nsym)
    print(f"    Fits: {fits}")
    print(f"    Available capacity: {available} bytes")
    
    # Step 4: Embed
    print(f"\n[6] Embedding secret message...")
    stego_img = embed_bytes_into_pixels(img, ecc_payload, coords, lsb_bits=1)
    stego_path = Path("stego_output.png")
    stego_img.save(stego_path)
    print(f"    Stego image saved: {stego_path}")
    
    # Step 5: Simulate corruption (JPEG recompression)
    print(f"\n[7] Simulating JPEG compression (quality=75)...")
    corrupted_img = recompress_and_reload(stego_img, quality=75)
    corrupted_path = Path("stego_corrupted.png")
    corrupted_img.save(corrupted_path)
    print(f"    Corrupted image saved: {corrupted_path}")
    
    # Step 6: Extract encoded payload
    print(f"\n[8] Extracting encoded payload from corrupted image...")
    extracted_ecc = extract_bytes_from_pixels(corrupted_img, len(ecc_payload), coords, lsb_bits=1)
    print(f"    Extracted {len(extracted_ecc)} bytes")
    
    # Step 7: Check for bit errors
    bit_errors = sum(bin(a ^ b).count('1') for a, b in zip(ecc_payload, extracted_ecc))
    print(f"    Bit errors detected: {bit_errors}/{len(ecc_payload)*8}")
    
    # Step 8: Recover with ECC
    print(f"\n[9] Recovering message with Reed-Solomon ECC...")
    try:
        recovered_msg = recover_redundancy(extracted_ecc, nsym=nsym)
        print(f"    ✓ Recovery successful!")
        print(f"    Recovered message: {recovered_msg.decode()}")
        
        if recovered_msg == secret_msg:
            print(f"\n" + "=" * 70)
            print("✓✓✓ SUCCESS: Message perfectly recovered after JPEG compression! ✓✓✓")
            print("=" * 70)
        else:
            print("\n⚠ WARNING: Message mismatch!")
            
    except Exception as e:
        print(f"    ✗ Recovery failed: {e}")
        print(f"    This can happen if corruption exceeded ECC capability")

if __name__ == "__main__":
    main()