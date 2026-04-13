"""
Train ML Steganography Detector
================================
Generates synthetic training data and trains Random Forest model.
Creates both cover and stego images for classification.
"""

import numpy as np
import logging
from pathlib import Path
from PIL import Image
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.detect_stego.ml_detector import StegoDetectorML, MODEL_PATH
from src.stego.lsb_steganography import encode_image as lsb_encode
from src.stego.dct_steganography import encode_dct
from src.stego.dwt_steganography import encode_dwt

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ============================================================================
#  Synthetic Data Generation
# ============================================================================

def generate_random_image(size=(256, 256), seed=None):
    """
    Generate a random cover image with natural patterns.
    
    Args:
        size: tuple - (height, width)
        seed: int - Random seed for reproducibility
    
    Returns:
        numpy array - RGB image
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Method 1: Perlin-like noise (using random with smoothing)
    method = np.random.choice(['noise', 'gradient', 'mixed'])
    
    if method == 'noise':
        # Natural noise pattern
        img = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
        # Smooth it
        from scipy.ndimage import gaussian_filter
        img = gaussian_filter(img.astype(float), sigma=2)
        img = np.clip(img, 0, 255).astype(np.uint8)
    
    elif method == 'gradient':
        # Gradient pattern (like sky or landscape)
        h, w = size
        img = np.zeros((*size, 3), dtype=np.uint8)
        
        for c in range(3):
            gradient = np.linspace(50, 200, w, dtype=np.uint8)
            img[:, :, c] = np.tile(gradient, (h, 1))
        
        # Add some noise
        noise = np.random.randint(-20, 20, (*size, 3), dtype=np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    else:  # mixed
        # Combination of patterns
        img = np.random.randint(100, 180, (*size, 3), dtype=np.uint8)
        
        # Add some structured patterns
        for i in range(size[0]):
            for j in range(size[1]):
                if (i + j) % 10 == 0:
                    img[i, j] = np.clip(img[i, j] + 30, 0, 255)
    
    return img


def generate_stego_image(cover_img, method='lsb', seed=None):
    """
    Generate a stego image by embedding data in cover image.
    
    Args:
        cover_img: numpy array - Cover image
        method: str - Steganography method ('lsb', 'dct', 'dwt')
        seed: int - Random seed
    
    Returns:
        numpy array - Stego image, or None if embedding fails
    """
    try:
        if seed is not None:
            np.random.seed(seed)
        
        # Generate random secret message
        msg_len = np.random.randint(50, 500)
        secret_msg = ''.join(
            chr(np.random.randint(32, 126)) for _ in range(msg_len)
        )
        
        # Convert to PIL Image for embedding
        cover_pil = Image.fromarray(cover_img)
        
        # Embed using selected method
        if method == 'lsb':
            try:
                stego_pil = lsb_encode(cover_pil, secret_msg)
                return np.array(stego_pil)
            except Exception as e:
                logger.debug(f"LSB encoding failed: {e}")
                return None
        
        elif method == 'dct':
            try:
                stego_pil = encode_dct(cover_pil, secret_msg)
                return np.array(stego_pil)
            except Exception as e:
                logger.debug(f"DCT encoding failed: {e}")
                return None
        
        elif method == 'dwt':
            try:
                stego_pil = encode_dwt(cover_pil, secret_msg)
                return np.array(stego_pil)
            except Exception as e:
                logger.debug(f"DWT encoding failed: {e}")
                return None
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    except Exception as e:
        logger.debug(f"Stego generation error: {e}")
        return None


def generate_training_data(n_samples=200, image_size=(256, 256)):
    """
    Generate balanced dataset of cover and stego images.
    
    Args:
        n_samples: int - Total samples to generate (will be split 50/50)
        image_size: tuple - Image dimensions
    
    Returns:
        tuple: (cover_images, stego_images)
    """
    logger.info(f"Generating {n_samples} training image pairs...")
    
    cover_images = []
    stego_images = []
    
    methods = ['lsb', 'dct', 'dwt']
    
    for i in range(n_samples):
        # Generate cover image
        cover_img = generate_random_image(image_size, seed=i)
        cover_images.append(cover_img)
        
        # Generate stego image using random method
        method = methods[i % len(methods)]
        stego_img = generate_stego_image(cover_img, method=method, seed=i)
        
        if stego_img is not None:
            stego_images.append(stego_img)
        else:
            # If stego generation fails, try different method
            for backup_method in methods:
                if backup_method != method:
                    stego_img = generate_stego_image(cover_img, method=backup_method, seed=i+1000)
                    if stego_img is not None:
                        stego_images.append(stego_img)
                        break
        
        if (i + 1) % 25 == 0:
            logger.info(f"Generated {i + 1}/{n_samples} image pairs")
    
    logger.info(f"Successfully generated {len(cover_images)} cover and {len(stego_images)} stego images")
    return cover_images, stego_images


# ============================================================================
#  Model Training
# ============================================================================

def train_detector(n_samples=200, image_size=(256, 256), save_path=None):
    """
    Train Random Forest steganography detector.
    
    Args:
        n_samples: int - Number of training image pairs
        image_size: tuple - Image dimensions
        save_path: str - Path to save model (optional)
    
    Returns:
        dict: Training metrics
    """
    logger.info("=" * 70)
    logger.info("Starting ML Model Training")
    logger.info("=" * 70)
    
    try:
        # Generate training data
        logger.info(f"Step 1: Generating synthetic training data...")
        cover_imgs, stego_imgs = generate_training_data(n_samples, image_size)
        
        if len(cover_imgs) == 0 or len(stego_imgs) == 0:
            error_msg = "Failed to generate training data"
            logger.error(error_msg)
            return {"error": error_msg}
        
        logger.info(f"  ✓ Generated {len(cover_imgs)} cover images")
        logger.info(f"  ✓ Generated {len(stego_imgs)} stego images")
        
        # Initialize detector
        logger.info(f"\nStep 2: Initializing detector...")
        detector = StegoDetectorML()
        logger.info(f"  ✓ Detector initialized")
        
        # Train model
        logger.info(f"\nStep 3: Training Random Forest model...")
        logger.info(f"  - Algorithm: Random Forest")
        logger.info(f"  - Estimators: 200")
        logger.info(f"  - Features: 9 statistical features")
        logger.info(f"  - Samples: {len(cover_imgs) + len(stego_imgs)}")
        
        metrics = detector.train(cover_imgs, stego_imgs, validation_split=0.2)
        
        if "error" in metrics:
            logger.error(f"Training failed: {metrics['error']}")
            return metrics
        
        logger.info(f"\nStep 4: Training Results")
        logger.info(f"  ✓ Train Accuracy: {metrics['train_accuracy']:.1%}")
        logger.info(f"  ✓ Validation Accuracy: {metrics['val_accuracy']:.1%}")
        logger.info(f"  ✓ Precision: {metrics['val_precision']:.1%}")
        logger.info(f"  ✓ Recall: {metrics['val_recall']:.1%}")
        logger.info(f"  ✓ F1 Score: {metrics['val_f1']:.4f}")
        
        # Save model
        logger.info(f"\nStep 5: Saving model...")
        save_location = save_path or MODEL_PATH
        success = detector.save_model(save_location)
        
        if success:
            logger.info(f"  ✓ Model saved to {save_location}")
        else:
            logger.warning(f"  ⚠ Failed to save model")
        
        # Get feature importance
        logger.info(f"\nStep 6: Feature Importance")
        importance = detector.get_feature_importance()
        for feature, importance_val in sorted(importance.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {feature}: {importance_val:.4f}")
        
        logger.info("\n" + "=" * 70)
        logger.info("Training Complete! ✓")
        logger.info("=" * 70)
        
        return metrics
    
    except Exception as e:
        logger.error(f"Training error: {str(e)}", exc_info=True)
        return {"error": str(e)}


# ============================================================================
#  CLI Interface
# ============================================================================

def main():
    """CLI interface for training the detector."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Train ML Steganography Detector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train_ml_detector.py                    # Train with 200 samples
  python train_ml_detector.py --samples 500      # Train with 500 samples
  python train_ml_detector.py --samples 100 --size 128  # Custom size
        """
    )
    
    parser.add_argument(
        '--samples',
        type=int,
        default=200,
        help='Number of image pairs to generate (default: 200)'
    )
    
    parser.add_argument(
        '--size',
        type=int,
        default=256,
        help='Image size (size×size pixels, default: 256)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Save path for model (default: src/detect_stego/models/stego_detector_rf.pkl)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Train detector
    metrics = train_detector(
        n_samples=args.samples,
        image_size=(args.size, args.size),
        save_path=args.output
    )
    
    # Print summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)
    
    if "error" in metrics:
        print(f"❌ Training failed: {metrics['error']}")
        sys.exit(1)
    else:
        print(f"✅ Training successful!")
        print(f"\n📊 Metrics:")
        print(f"   Train Accuracy:  {metrics['train_accuracy']:.1%}")
        print(f"   Val Accuracy:    {metrics['val_accuracy']:.1%}")
        print(f"   Precision:       {metrics['val_precision']:.1%}")
        print(f"   Recall:          {metrics['val_recall']:.1%}")
        print(f"   F1 Score:        {metrics['val_f1']:.4f}")
        print("\n🎉 Model trained and saved!")
        sys.exit(0)


if __name__ == "__main__":
    main()