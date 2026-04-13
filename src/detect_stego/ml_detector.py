"""
Machine Learning-based Steganography Detector
==============================================
Uses Random Forest to detect hidden messages in images.
Single source of truth for ML detection.
"""

import numpy as np
import logging
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from scipy.fftpack import dct
from PIL import Image

logger = logging.getLogger(__name__)

# Model paths
MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / "stego_detector_rf.pkl"
SCALER_PATH = MODEL_DIR / "stego_detector_scaler.pkl"

# Global detector instance
_detector_instance = None


def get_detector():
    """Get or initialize the detector instance (singleton pattern)."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = StegoDetectorML()
        if not _detector_instance.load_model():
            logger.warning("Pre-trained model not found. Run: python train_ml_detector.py")
    return _detector_instance


def analyze_image_for_steganography(img_array, sensitivity):
    """
    Analyze image for steganography using ML model.
    
    Args:
        img_array: numpy array of image (RGB)
        sensitivity: Detection sensitivity (1-10)
    
    Returns:
        tuple: (detection_score, analysis_data)
            - detection_score: 0-100, higher = more likely stego
    """
    try:
        detector = get_detector()
        
        # Check if model is actually trained
        if not detector.is_trained or detector.model is None:
            return 0, [{
                "Metric": "Status", 
                "Value": "⚠️ Model not trained"
            }, {
                "Metric": "Action Required",
                "Value": "Train model first: Go to 'Train Model' tab"
            }]
        
        # Make prediction
        prediction, confidence = detector.predict(img_array, return_confidence=True)
        
        # confidence = stego probability (0-100%)
        # prediction=0 (clean), prediction=1 (stego)
        #
        # CALIBRATION: Power law scaling to compress unrealistic model confidences
        # The model trained on synthetic data outputs poorly calibrated probabilities
        # Power transformation aggressively compresses low-mid range scores
        # Formula: scaled = (raw/100)^2 * 100
        # Examples: 28% → ~8%, 50% → 25%, 70% → 49%, 85% → 72%
        try:
            confidence_normalized = confidence / 100.0
            confidence_scaled = (confidence_normalized ** 2) * 100
            confidence_calibrated = confidence_scaled
        except:
            confidence_calibrated = confidence
        
        # Use calibrated confidence as the score
        confidence = confidence_calibrated

        # Determine thresholds based on calibrated confidence scores
        # After power law scaling: 28% → 8%, so we can use lower thresholds
        # Sensitivity adjusts detection aggressiveness:
        #   sensitivity=1  → very aggressive (low threshold = 25%)
        #   sensitivity=5  → medium           (default threshold = 45%)
        #   sensitivity=10 → very conservative (high threshold = 70%)
        threshold_base = 45.0  # Default threshold at sensitivity=5 (after calibration)
        threshold_adjusted = threshold_base + (5 - sensitivity) * 5  # Adjust by ±25
        high_threshold = min(threshold_adjusted, 100)
        low_threshold = max(high_threshold - 30, 0)

        # Use calibrated confidence as the final score
        final_score = confidence

        # Determine verdict based on adjusted thresholds
        if final_score >= high_threshold:
            verdict = "STEGO DETECTED ⚠️"
        elif final_score >= low_threshold:
            verdict = "SUSPICIOUS 🟡"
        else:
            verdict = "CLEAN IMAGE ✅"
        
        analysis_data = [
            {
                "Metric": "ML Prediction",
                "Value": verdict
            },
            {
                "Metric": "Stego Probability",
                "Value": f"{confidence:.1f}%"
            },
            {
                "Metric": "Detection Score",
                "Value": f"{final_score:.1f}/100"
            },
            {
                "Metric": "Sensitivity Setting",
                "Value": f"{sensitivity}/10"
            }
        ]
        
        # Add feature analysis
        try:
            features = detector.extract_features(img_array)
            features_scaled = detector.scaler.transform(features)[0]
            
            feature_names = [
                "LSB Entropy",
                "LSB Ratio",
                "LSB Autocorr",
                "ASCII Ratio",
                "Chi-Square",
                "DCT Mean",
                "DCT Variance",
                "High-Freq Energy",
                "Histogram Var"
            ]
            
            for name, value in zip(feature_names, features_scaled):
                analysis_data.append({
                    "Metric": f"Feature: {name}",
                    "Value": f"{value:.4f}"
                })
        except Exception as e:
            logger.warning(f"Feature analysis failed: {e}")
        
        return final_score, analysis_data
        
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return 0, [{"Metric": "Error", "Value": str(e)}]


class StegoDetectorML:
    """Machine Learning-based steganography detector using Random Forest."""
    
    def __init__(self):
        """Initialize the detector."""
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, img_array):
        """
        Extract features from image for ML model.
        Returns: numpy array: Feature vector (1D, shape=(1, 9))
        """
        features = []
        
        try:
            # Ensure RGB
            if len(img_array.shape) == 2:
                img_array = np.stack([img_array]*3, axis=-1)
            elif img_array.shape[2] == 4:
                img_array = img_array[:, :, :3]
            
            # ✅ Normalize image values to 0-255 range
            if img_array.max() <= 1.0:
                img_array = (img_array * 255).astype(np.uint8)
            else:
                img_array = np.clip(img_array, 0, 255).astype(np.uint8)
            
            # Feature 1: LSB Entropy (0-1, higher = more random LSBs)
            lsb_plane = (img_array & 1).flatten()
            unique, counts = np.unique(lsb_plane, return_counts=True)
            probs = counts / len(lsb_plane)
            lsb_entropy = -np.sum(probs * np.log2(probs + 1e-10))
            # Normalize to 0-1 range
            lsb_entropy = min(lsb_entropy / 1.0, 1.0)
            features.append(lsb_entropy)
            
            # Feature 2: LSB 0/1 Ratio deviation from 0.5
            ones_count = np.sum(lsb_plane)
            lsb_ratio = ones_count / len(lsb_plane)
            # Clean images should be ~0.5, deviation indicates possible data
            features.append(abs(lsb_ratio - 0.5))
            
            # Feature 3: LSB Autocorrelation
            if len(lsb_plane) > 1000:
                try:
                    autocorr = np.corrcoef(lsb_plane[:-1], lsb_plane[1:])[0, 1]
                    if np.isnan(autocorr):
                        autocorr = 0
                    features.append(abs(autocorr))
                except:
                    features.append(0)
            else:
                features.append(0)
            
            # Feature 4: ASCII Characters in LSB Extraction
            # ✅ FIX: Only check first 1000 pixels to avoid false positives
            binary_data = ''
            flat_array = img_array.reshape(-1, 3)
            pixel_sample = min(1000, len(flat_array))  # Sample only 1000 pixels
            
            for pixel in flat_array[:pixel_sample]:
                for channel in range(3):
                    binary_data += str(pixel[channel] & 1)
            
            ascii_count = 0
            total_bytes = 0
            for i in range(0, min(len(binary_data) - 8, 8000), 8):
                byte_val = int(binary_data[i:i+8], 2)
                total_bytes += 1
                # Printable ASCII range
                if 32 <= byte_val <= 126 or byte_val in [10, 13, 9]:
                    ascii_count += 1
            
            ascii_ratio = ascii_count / total_bytes if total_bytes > 0 else 0
            features.append(ascii_ratio)
            
            # Feature 5: Chi-Square Statistic
            hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
            chi_sum = 0
            for i in range(0, 256, 2):
                expected = (hist[i] + hist[i+1]) / 2 + 0.1
                chi_sum += ((hist[i] - expected) ** 2 + (hist[i+1] - expected) ** 2) / expected
            chi_normalized = chi_sum / 128
            # ✅ FIX: Normalize to reasonable range
            chi_normalized = min(chi_normalized / 10.0, 1.0)
            features.append(chi_normalized)
            
            # Feature 6 & 7: DCT Coefficient Distribution
            try:
                if img_array.shape[0] >= 8 and img_array.shape[1] >= 8:
                    sample_block = img_array[:8, :8, 0].astype(np.float32)
                    dct_block = dct(dct(sample_block.T, norm='ortho').T, norm='ortho')
                    dct_mean = np.mean(np.abs(dct_block))
                    dct_var = np.var(np.abs(dct_block))
                    # Normalize
                    dct_mean = min(dct_mean / 50.0, 1.0)
                    dct_var = min(dct_var / 500.0, 1.0)
                    features.append(dct_mean)
                    features.append(dct_var)
                else:
                    features.append(0.5)
                    features.append(0.5)
            except:
                features.append(0.5)
                features.append(0.5)
            
            # Feature 8: High-Frequency Component Energy Ratio
            try:
                y_channel = np.mean(img_array, axis=2).astype(np.float32)
                if y_channel.shape[0] >= 8 and y_channel.shape[1] >= 8:
                    dct_y = dct(dct(y_channel[:16, :16].T, norm='ortho').T, norm='ortho')
                    low_freq_energy = np.sum(dct_y[:4, :4] ** 2) + 1e-10
                    high_freq_energy = np.sum(dct_y[4:, 4:] ** 2)
                    freq_ratio = high_freq_energy / low_freq_energy
                    # Normalize
                    freq_ratio = min(freq_ratio / 5.0, 1.0)
                    features.append(freq_ratio)
                else:
                    features.append(0.3)
            except:
                features.append(0.3)
            
            # Feature 9: Histogram Variance (normalized)
            hist_var = np.var(hist)
            hist_var_norm = min(hist_var / 50000.0, 1.0)
            features.append(hist_var_norm)
            
            # ✅ FIX: Ensure we have exactly 9 features
            assert len(features) == 9, f"Expected 9 features, got {len(features)}"
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            # Return neutral features (0.5) if extraction fails
            return np.full((1, 9), 0.5)
    
    def predict(self, img_array, return_confidence=False):
        """
        Predict if image contains steganography.
        
        Args:
            img_array: Image array (RGB)
            return_confidence: If True, return confidence scores
        
        Returns:
            tuple or int: (prediction, confidence) or prediction
        """
        try:
            # ✅ FIX: Check if model exists and is trained
            if self.model is None or not self.is_trained:
                logger.error("Model not trained. Train the model first.")
                if return_confidence:
                    return 0, 0.0  # Return clean image with 0% confidence
                else:
                    return 0
            
            features = self.extract_features(img_array)
            
            # ✅ FIX: Check scaler is fitted
            try:
                features_scaled = self.scaler.transform(features)
            except Exception as e:
                logger.warning(f"Scaler not fitted: {e}. Using features as-is.")
                features_scaled = features
            
            prediction = self.model.predict(features_scaled)[0]
            confidence = self.model.predict_proba(features_scaled)[0]
            
            # confidence[0] = prob of class 0 (clean), confidence[1] = prob of class 1 (stego)
            stego_confidence = confidence[1] * 100
            
            if return_confidence:
                return int(prediction), stego_confidence
            else:
                return int(prediction)
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            if return_confidence:
                return 0, 0.0
            else:
                return 0
    
    def load_model(self, path=None):
        """Load trained model and scaler from disk (PKL)."""
        try:
            path = path or MODEL_PATH
            
            if not Path(path).exists():
                logger.warning(f"Model file not found: {path}")
                self.is_trained = False
                return False
            
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            
            scaler_path = Path(path).parent / (Path(path).stem + '_scaler.pkl')
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"Scaler loaded from {scaler_path}")
            else:
                logger.warning("Scaler file not found. Fitting new scaler...")
                # Will be fitted during training
            
            self.is_trained = True
            logger.info(f"Random Forest model loaded from {path}")
            logger.info(f"Model is trained: {self.is_trained}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.is_trained = False
            return False
    
    def save_model(self, path=None):
        """Save the trained model and scaler to disk as PKL."""
        try:
            path = path or MODEL_PATH
            
            # ✅ FIX: Check if model is actually trained
            if self.model is None or not self.is_trained:
                logger.error("No trained model to save. Train the model first.")
                return False
            
            model_dir = Path(path).parent
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Save model
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to {path}")
            
            # Save scaler
            scaler_path = model_dir / (Path(path).stem + '_scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            logger.info(f"Scaler saved to {scaler_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def get_feature_importance(self):
        """Get feature importance from Random Forest model."""
        if self.model is None or not self.is_trained:
            return {}
        
        feature_names = [
            "LSB Entropy",
            "LSB 0/1 Ratio",
            "LSB Autocorrelation",
            "ASCII Ratio",
            "Chi-Square Stat",
            "DCT Mean",
            "DCT Variance",
            "High-Freq Energy",
            "Histogram Variance"
        ]
        
        try:
            # Get feature importance from Random Forest
            importance = self.model.feature_importances_
            importance = importance / (importance.sum() + 1e-10)
            
            return dict(zip(feature_names, importance))
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}

    def train(self, cover_images, stego_images, validation_split=0.2, n_estimators=200):
        """
        Train the Random Forest model on cover and stego images.
        
        Args:
            cover_images: list of numpy arrays (clean images)
            stego_images: list of numpy arrays (images with hidden data)
            validation_split: fraction of data for validation (0.0-1.0)
            n_estimators: number of trees in the forest
        
        Returns:
            dict: Training metrics with ALL key variants for compatibility
        """
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        
        try:
            logger.info(f"Training with {len(cover_images)} cover + {len(stego_images)} stego images")
            
            # Step 1: Extract features from all images
            X = []
            y = []
            
            logger.info("Extracting features from cover images...")
            for i, img in enumerate(cover_images):
                try:
                    if isinstance(img, Image.Image):
                        img = np.array(img)
                    features = self.extract_features(img)
                    X.append(features.flatten())
                    y.append(0)  # 0 = clean
                except Exception as e:
                    logger.warning(f"Failed to extract features from cover image {i}: {e}")
            
            logger.info("Extracting features from stego images...")
            for i, img in enumerate(stego_images):
                try:
                    if isinstance(img, Image.Image):
                        img = np.array(img)
                    features = self.extract_features(img)
                    X.append(features.flatten())
                    y.append(1)  # 1 = stego
                except Exception as e:
                    logger.warning(f"Failed to extract features from stego image {i}: {e}")
            
            X = np.array(X)
            y = np.array(y)
            
            logger.info(f"Total samples: {len(X)} (cover: {np.sum(y==0)}, stego: {np.sum(y==1)})")
            
            if len(X) < 10:
                raise ValueError(f"Not enough valid samples for training: {len(X)}")
            
            # Step 2: Split into train/validation
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42, stratify=y
            )
            
            logger.info(f"Train: {len(X_train)}, Validation: {len(X_val)}")
            
            # Step 3: Fit scaler on training data
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
            
            # Step 4: Train Random Forest
            self.model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
            
            self.model.fit(X_train_scaled, y_train)
            self.is_trained = True
            
            # Step 5: Evaluate on TRAINING set
            y_train_pred = self.model.predict(X_train_scaled)
            train_accuracy = accuracy_score(y_train, y_train_pred)
            train_precision = precision_score(y_train, y_train_pred, zero_division=0)
            train_recall = recall_score(y_train, y_train_pred, zero_division=0)
            train_f1 = f1_score(y_train, y_train_pred, zero_division=0)
            train_cm = confusion_matrix(y_train, y_train_pred)
            
            # Step 6: Evaluate on VALIDATION set
            y_pred = self.model.predict(X_val_scaled)
            
            val_accuracy = accuracy_score(y_val, y_pred)
            val_precision = precision_score(y_val, y_pred, zero_division=0)
            val_recall = recall_score(y_val, y_pred, zero_division=0)
            val_f1 = f1_score(y_val, y_pred, zero_division=0)
            val_cm = confusion_matrix(y_val, y_pred)
            
            # Feature importance
            importance = self.get_feature_importance()
            
            # ── Build metrics dict with ALL possible key variants ──
            # This ensures compatibility with train_ml_detector.py,
            # ui_section.py, and any other caller.
            metrics = {
                # === train_ prefixed keys ===
                'train_accuracy': train_accuracy,
                'train_precision': train_precision,
                'train_recall': train_recall,
                'train_f1': train_f1,
                'train_f1_score': train_f1,
                'train_confusion_matrix': train_cm.tolist(),
                
                # === val_ prefixed keys ===
                'val_accuracy': val_accuracy,
                'val_precision': val_precision,
                'val_recall': val_recall,
                'val_f1': val_f1,
                'val_f1_score': val_f1,
                'val_confusion_matrix': val_cm.tolist(),
                
                # === Generic keys (no prefix) ===
                'accuracy': val_accuracy,
                'precision': val_precision,
                'recall': val_recall,
                'f1': val_f1,
                'f1_score': val_f1,
                'confusion_matrix': val_cm.tolist(),
                
                # === Dataset info ===
                'train_samples': len(X_train),
                'val_samples': len(X_val),
                'total_samples': len(X),
                'cover_samples': int(np.sum(y == 0)),
                'stego_samples': int(np.sum(y == 1)),
                'n_estimators': n_estimators,
                'feature_importance': importance,
                
                # === Status ===
                'success': True,
                'model_path': str(MODEL_PATH),
            }
            
            logger.info(f"Training complete!")
            logger.info(f"  Train Accuracy:  {train_accuracy:.4f}")
            logger.info(f"  Val Accuracy:    {val_accuracy:.4f}")
            logger.info(f"  Val Precision:   {val_precision:.4f}")
            logger.info(f"  Val Recall:      {val_recall:.4f}")
            logger.info(f"  Val F1 Score:    {val_f1:.4f}")
            logger.info(f"  Confusion Matrix: {val_cm.tolist()}")
            
            # Step 7: Auto-save model
            self.save_model()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            self.is_trained = False
            raise ValueError(f"Training failed: {str(e)}")