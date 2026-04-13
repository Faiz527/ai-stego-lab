# make_demo_images.py (fixed)
from PIL import Image
import numpy as np
from pathlib import Path

outdir = Path("stegotool/data/dev_images")
outdir.mkdir(parents=True, exist_ok=True)

def make_gradient_noise(w, h, seed=0):
    rng = np.random.RandomState(seed)
    x = np.linspace(0, 255, w, dtype=np.uint8)
    y = np.linspace(0, 255, h, dtype=np.uint8)[:, None]
    grad = ((x + y) // 2).astype(np.uint8)
    for i in range(8):
        noise = (rng.randint(0, 60, (h, w))).astype(np.uint8)
        # use transforms that keep shape (h, w)
        ch0 = np.clip(grad + noise + i * 5, 0, 255)
        ch1 = np.clip(grad + noise[::-1, :] + i * 3, 0, 255)   # flip vertically
        ch2 = np.clip(grad + noise[:, ::-1] + i * 7, 0, 255)   # flip horizontally
        rgb = np.stack([ch0, ch1, ch2], axis=2).astype(np.uint8)
        Image.fromarray(rgb).save(outdir / f"demo_{i+1}.png")
    print("Wrote demo images to", outdir)

if __name__ == "__main__":
    make_gradient_noise(512, 384)
