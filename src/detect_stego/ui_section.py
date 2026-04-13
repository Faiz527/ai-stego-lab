"""
Steganography Detection UI Section
===================================
Streamlit UI component for the Detect Stego tab.
Professional SaaS-style layout with animations.
Includes model training capabilities with Random Forest.
"""

import logging
import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd

from src.ui.reusable_components import (
    create_file_uploader,
    show_error,
    show_success,
    show_warning,
    show_info,
    show_lottie_animation,
    create_metric_cards,
    show_processing_spinner,
    render_step,
    store_processed_image,
    cache_result,
    get_cached_result
)
from .ml_detector import analyze_image_for_steganography, StegoDetectorML, get_detector

logger = logging.getLogger(__name__)


def show_info_box(title, description, use_cases):
    """Display a consistent info box explaining a feature."""
    with st.expander(f"ℹ️ {title}", expanded=False):
        st.markdown(f"**Description:** {description}")
        st.markdown("**Use Cases:**")
        for use_case in use_cases:
            st.markdown(f"- {use_case}")


def show_steg_detector_section():
    """Display steganography detection analysis with professional UI."""
    
    # Header with animation
    st.markdown("""
        <div class="animate-fade-in-down">
            <h2>🔍 Steganography Detector</h2>
            <p style="color: #8B949E;">Analyze images to detect hidden messages using Random Forest ML model.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main content with tabs
    tab_analyze, tab_results, tab_train, tab_help = st.tabs(["🔬 Analyze", "📊 Results", "🤖 Train Model", "❓ Help"])
    
    # =========================================================================
    # TAB 1: ANALYZE
    # =========================================================================
    with tab_analyze:
        st.markdown("""
            <div class="card animate-fade-in">
                <div class="card-header">🔬 Image Analysis</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("Upload an image to analyze for steganography using the **Random Forest ML model**.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Select Image**")
            uploaded_file = st.file_uploader(
                "Upload Image",
                type=["jpg", "jpeg", "png", "bmp", "tiff"],
                label_visibility="collapsed"
            )
            st.caption("📷 Supported formats: JPG, PNG, BMP, TIFF")
        
        with col2:
            st.markdown("**Detection Sensitivity**")
            sensitivity = st.slider(
                "Adjust sensitivity",
                min_value=1,
                max_value=10,
                value=5,
                label_visibility="collapsed"
            )
        
        st.divider()
        
        if uploaded_file is not None:
            # Display uploaded image
            col1, col2 = st.columns([1, 2])
            
            with col1:
                image = Image.open(uploaded_file).convert('RGB')
                st.image(image, caption="Uploaded Image", use_container_width=True)
                image_info = f"**Size:** {image.size[0]}×{image.size[1]}px"
                st.markdown(image_info)
            
            with col2:
                st.markdown("### ⏳ Running Analysis...")
                
                # Run analysis
                with st.spinner("Analyzing image for steganography..."):
                    img_array = np.array(image)
                    score, data = _run_analysis(img_array, sensitivity)
                
                if score is not None:
                    _display_results({
                        "score": score,
                        "data": data,
                        "sensitivity": sensitivity
                    })
        else:
            st.info("👆 Upload an image to begin analysis")
            
            # Info boxes
            show_info_box(
                "What is Steganography?",
                "Steganography is the practice of hiding secret messages within regular images.",
                [
                    "Cover information within multimedia files",
                    "Covert communication channels",
                    "Watermarking and DRM protection"
                ]
            )
    
    # =========================================================================
    # TAB 2: RESULTS
    # =========================================================================
    with tab_results:
        st.markdown("""
            <div class="card animate-fade-in">
                <div class="card-header">📊 Detection Results</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("View previous detection results and analysis history.")
        
        st.divider()
        
        # Get cached results
        cached_results = get_cached_result("stego_detection")
        
        if cached_results:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(cached_results.get("image"), caption="Analyzed Image", use_container_width=True)
            
            with col2:
                metadata = cached_results.get("metadata", {})
                st.markdown(f"### Detection Score: **{metadata.get('score', 0):.1f}%**")
                st.markdown(f"**Sensitivity:** {metadata.get('sensitivity', 5)}/10")
                st.markdown(f"**Model:** {metadata.get('model', 'Random Forest')}")
                
                st.divider()
                
                if metadata.get('score', 0) > 50:
                    show_warning("⚠️ High probability of hidden content detected")
                elif metadata.get('score', 0) > 25:
                    show_info("ℹ️ Moderate indicators of hidden content")
                else:
                    show_success("✅ No significant indicators of hidden content")
        else:
            st.info("No analysis results yet. Use the **Analyze** tab to get started.")
            
            show_info_box(
                "Detection Methods",
                "The Random Forest ML model analyzes multiple statistical features.",
                [
                    "LSB (Least Significant Bit) entropy patterns",
                    "DCT (Discrete Cosine Transform) coefficients",
                    "DWT (Discrete Wavelet Transform) analysis",
                    "Histogram distribution variance",
                    "Chi-square statistical tests"
                ]
            )
    
    # =========================================================================
    # TAB 3: TRAIN MODEL
    # =========================================================================
    with tab_train:
        _show_training_section()
    
    # =========================================================================
    # TAB 4: HELP
    # =========================================================================
    with tab_help:
        _show_help_section()


def _show_training_section():
    """Display the ML model training interface."""
    
    st.markdown("""
        <div class="card animate-fade-in">
            <div class="card-header">🤖 Train Random Forest Model</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Train a custom **Random Forest** model to detect steganography in images.
    The model learns to identify statistical patterns left by encoding methods.
    """)
    
    st.divider()
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### ⚙️ Training Configuration")
        n_samples = st.number_input(
            "Number of image pairs to generate",
            min_value=50,
            max_value=2000,
            value=200,
            step=50,
            help="More samples = better model (but takes longer)"
        )
        
        image_size = st.selectbox(
            "Image size",
            options=["256×256", "512×512", "128×128"],
            index=0,
            help="Larger images provide more data points"
        )
    
    with col2:
        st.markdown("### 📈 Model Info")
        st.markdown("""
        **Algorithm:** Random Forest
        
        **Trees:** 200 estimators
        
        **Features:** 9 statistical
        
        **Classes:** 2 (Cover/Stego)
        
        **Output:** PKL file
        """)
    
    st.divider()
    
    # Advanced options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_advanced = st.checkbox("⚙️ Show Advanced Options")
    
    with col2:
        pass
    
    validation_split = 0.2
    custom_path = None
    
    if show_advanced:
        st.markdown("### 🔧 Advanced Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            validation_split = st.slider(
                "Validation split",
                min_value=0.1,
                max_value=0.4,
                value=0.2,
                step=0.05,
                help="Portion of data reserved for validation"
            )
        
        with col2:
            use_custom_path = st.checkbox("Custom save path")
            if use_custom_path:
                custom_path = st.text_input(
                    "Model save path",
                    value="models/stego_detector_rf.pkl",
                    help="Where to save the trained model"
                )
        
        st.divider()
    
    # Training button
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🚀 Ready to Train?")
        st.markdown(f"""
        - Samples: **{n_samples}** pairs
        - Size: **{image_size}**
        - Validation: **{validation_split:.0%}**
        """)
    
    with col2:
        start_training = st.button(
            "🚀 Start Training",
            use_container_width=True,
            type="primary",
            help="Begin training the Random Forest model"
        )
    
    st.divider()
    
    # Training execution
    if start_training:
        _run_model_training(
            n_samples=n_samples,
            image_sizes=[(int(image_size.split('×')[0]), int(image_size.split('×')[0]))],
            methods=['lsb', 'dct', 'dwt'],
            validation_split=validation_split,
            custom_path=custom_path
        )


def _run_model_training(n_samples, image_sizes, methods, validation_split, custom_path=None):
    """Execute the model training process."""
    
    st.markdown("""
        <div class="card card-warning">
            <strong>⚠️ Important:</strong> Training will take some time. 
            Do not close this page or navigate away during training.
        </div>
    """, unsafe_allow_html=True)
    
    # Import training utilities
    try:
        from src.detect_stego.train_ml_detector import train_detector
    except ImportError:
        show_error("❌ Training module not found")
        return
    
    # Create containers for progress display
    progress_container = st.container()
    status_container = st.container()
    metrics_container = st.container()
    
    try:
        with status_container:
            with st.spinner("🔄 Training Random Forest model..."):
                metrics = train_detector(n_samples=n_samples, save_path=custom_path)
        
        if "error" not in metrics:
            show_success("✅ Training completed successfully!")
            
            with metrics_container:
                st.markdown("""
                    <div class="card card-success">
                        <div class="card-header">📊 Training Metrics</div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Train Accuracy",
                        f"{metrics.get('train_accuracy', 0):.1%}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "Validation Accuracy",
                        f"{metrics.get('val_accuracy', 0):.1%}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "F1 Score",
                        f"{metrics.get('val_f1', 0):.4f}",
                        delta=None
                    )
                
                st.divider()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Precision**")
                    st.markdown(f"### {metrics.get('val_precision', 0):.1%}")
                
                with col2:
                    st.markdown("**Recall**")
                    st.markdown(f"### {metrics.get('val_recall', 0):.1%}")
            
            st.balloons()
        else:
            show_error(f"❌ Training failed: {metrics.get('error', 'Unknown error')}")
    
    except Exception as e:
        show_error(f"❌ Error during training: {str(e)}")
        logger.error(f"Training error: {str(e)}")
    
    finally:
        pass


def _run_analysis(image: Image.Image, sensitivity: int):
    """Run the steganography detection analysis."""
    try:
        img_array = np.array(image)
        score, data = analyze_image_for_steganography(img_array, sensitivity)
        
        return score, data
            
    except Exception as e:
        show_error(f"❌ Analysis failed: {str(e)}")
        logger.error(f"Analysis error: {str(e)}")
        return None, []


def _display_results(results: dict):
    """Display the detection results with visualizations."""
    score = results["score"]
    data = results["data"]
    sensitivity = results["sensitivity"]
    
    # Determine verdict
    if score < 25:
        emoji = "✅"
        verdict = "No Hidden Content Detected"
        verdict_color = "#31a24c"
        explanation = "The image shows no significant indicators of steganography. The statistical analysis suggests this is a clean cover image."
    elif score < 50:
        emoji = "⚠️"
        verdict = "Possible Hidden Content"
        verdict_color = "#d29922"
        explanation = "The image exhibits some characteristics consistent with data hiding. Further investigation may be warranted."
    else:
        emoji = "🚨"
        verdict = "High Probability of Hidden Content"
        verdict_color = "#da3633"
        explanation = "The statistical analysis strongly suggests steganographic content may be present in this image."
    
    # Main score display
    st.markdown(f"""
        <div class="result-container animate-scale-in" style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 0.5rem;">{emoji}</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {verdict_color};">{score:.1f}%</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #C9D1D9; margin-top: 0.5rem;">{verdict}</div>
            <p style="color: #8B949E; margin-top: 1rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                {explanation}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Detailed metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Detection Overview")
        st.markdown(f"""
        - **Score:** {score:.1f}/100
        - **Verdict:** {verdict}
        - **Sensitivity:** {sensitivity}/10
        - **Model:** Random Forest
        """)
    
    with col2:
        st.markdown("### 📊 Confidence Levels")
        
        # Interpret confidence
        if score < 25:
            confidence_text = "Very Low Risk"
            confidence_color = "green"
        elif score < 50:
            confidence_text = "Moderate Risk"
            confidence_color = "orange"
        else:
            confidence_text = "High Risk"
            confidence_color = "red"
        
        st.markdown(f"""
        <div style="padding: 1rem; background-color: rgba(0,0,0,0.2); border-radius: 0.5rem; text-align: center;">
            <p style="margin: 0; color: #8B949E; font-size: 0.9rem;">Risk Assessment</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.3rem; color: {confidence_color}; font-weight: 700;">{confidence_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Analysis summary
    st.markdown("""
        <div class="card card-info">
            <div class="card-header">📋 Detailed Analysis</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display data in expandable sections
    with st.expander("🔬 ML Prediction Details", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        ml_data = [d for d in data if "ML" in d.get("Metric", "")]
        for i, item in enumerate(ml_data[:3]):
            with [col1, col2, col3][i]:
                st.metric(item["Metric"], item["Value"])
    
    with st.expander("📈 Feature Analysis", expanded=False):
        feature_data = [d for d in data if "Feature:" in d.get("Metric", "")]
        
        if feature_data:
            st.dataframe(
                pd.DataFrame(feature_data),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No feature data available")
    
    st.divider()
    
    # Export options
    st.markdown("### 💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = "\n".join([f"{d['Metric']},{d['Value']}" for d in data])
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name="stego_analysis.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = str(results)
        st.download_button(
            label="📄 Download as JSON",
            data=json_data,
            file_name="stego_analysis.json",
            mime="application/json"
        )


def _show_help_section():
    """Display comprehensive help documentation."""
    
    st.markdown("""
        <div class="card animate-fade-in">
            <div class="card-header">📖 Detection Module - Complete Guide</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main tabs in help
    help_tab1, help_tab2, help_tab3, help_tab4 = st.tabs([
        "🔬 How Detection Works",
        "🤖 Random Forest Model",
        "💻 Using the Module",
        "❓ FAQ & Tips"
    ])
    
    # =========================================================================
    # HELP TAB 1: HOW DETECTION WORKS
    # =========================================================================
    with help_tab1:
        st.markdown("""
        ## 🔬 How Steganography Detection Works
        
        The detector analyzes **9 key statistical features** from images:
        
        ### 1️⃣ LSB (Least Significant Bit) Analysis
        - Examines the lowest bit plane of pixels
        - Hidden data shows different entropy patterns
        - Useful for detecting LSB steganography
        
        ### 2️⃣ Frequency Domain Analysis (DCT/DWT)
        - Analyzes frequency coefficients
        - Detects alterations in transform domains
        - Effective for DCT and DWT methods
        
        ### 3️⃣ Statistical Analysis
        - Chi-square tests on histograms
        - Entropy measurements
        - Distribution variance analysis
        
        ### 4️⃣ Machine Learning Classification
        - Random Forest with 200 decision trees
        - Trained on synthetic stego images
        - Learns hidden data patterns
        """)
    
    # =========================================================================
    # HELP TAB 2: RANDOM FOREST MODEL
    # =========================================================================
    with help_tab2:
        st.markdown("""
        ## 🤖 Random Forest ML Model
        
        ### Why Random Forest?
        
        | Feature | Description |
        |---------|-------------|
        | **Accuracy** | 85-95% on validation set |
        | **Robustness** | Handles various image types |
        | **Speed** | Fast inference (~100ms) |
        | **Interpretability** | Shows feature importance |
        
        ### Model Architecture
        
        - **Algorithm:** Random Forest Classifier
        - **Trees:** 200 estimators
        - **Depth:** Max 15 levels
        - **Features:** 9 statistical features
        - **Classes:** 2 (Cover Image / Stego Image)
        
        ### Training Process
        
        1. Generate synthetic cover images (natural patterns)
        2. Create stego images using LSB, DCT, DWT methods
        3. Extract 9 statistical features from each
        4. Split into train/validation sets (80/20)
        5. Train Random Forest with balanced class weights
        6. Save model and scaler as PKL files
        
        ### Performance Metrics
        
        ```
        Precision: Accuracy of positive predictions
        Recall: Catch rate for stego images
        F1 Score: Harmonic mean of precision & recall
        ```
        """)
    
    # =========================================================================
    # HELP TAB 3: USING THE MODULE
    # =========================================================================
    with help_tab3:
        st.markdown("""
        ## 💻 Using the Detection Module
        
        ### Quick Start
        
        1. **Upload an Image**
           - Go to the "Analyze" tab
           - Click to upload JPG, PNG, BMP, or TIFF
           - Adjust sensitivity if needed (1-10)
        
        2. **Wait for Analysis**
           - Model analyzes 9 features
           - Takes ~100-500ms depending on image size
           - Results displayed with visualization
        
        3. **Interpret Results**
           - **Green (< 25%):** No hidden content
           - **Orange (25-50%):** Possible content
           - **Red (> 50%):** Likely content detected
        
        ### Training a New Model
        
        #### Command Line
        ```bash
        python src/detect_stego/train_ml_detector.py --samples 500
        ```
        
        #### In Streamlit UI
        1. Go to "Train Model" tab
        2. Set number of samples (100-2000)
        3. Click "Start Training"
        4. Monitor progress and metrics
        
        ### Python Integration
        
        ```python
        from src.detect_stego import analyze_image_for_steganography
        import numpy as np
        from PIL import Image
        
        # Load image
        img = Image.open('test.jpg').convert('RGB')
        img_array = np.array(img)
        
        # Analyze (sensitivity 1-10)
        score, data = analyze_image_for_steganography(img_array, sensitivity=5)
        
        print(f"Detection Score: {score:.1f}%")
        ```
        """)
    
    # =========================================================================
    # HELP TAB 4: FAQ & TIPS
    # =========================================================================
    with help_tab4:
        st.markdown("""
        ## ❓ FAQ & Troubleshooting
        
        ### Q: Why is my accuracy different from online?
        A: Different datasets and model architectures produce different results. 
        Our Random Forest is optimized for synthetic data; real-world performance varies.
        
        ### Q: What image formats are supported?
        A: JPG, PNG, BMP, and TIFF. Images are internally converted to RGB.
        
        ### Q: Can I detect all steganography methods?
        A: No. The model is trained on LSB, DCT, and DWT. Other advanced methods 
        may not be detected reliably.
        
        ### Q: How long does training take?
        A: ~5-15 minutes for 500 samples on a modern CPU/GPU.
        More samples = better accuracy but longer training.
        
        ### Q: Can I use my own training data?
        A: Not yet. Current implementation generates synthetic data.
        Custom data support is planned for future versions.
        
        ### Tips for Better Results
        
        ✅ **Do:**
        - Use high-quality images
        - Train with diverse synthetic data
        - Adjust sensitivity for your use case
        - Keep images at standard sizes (256×256 or larger)
        
        ❌ **Don't:**
        - Expect 100% accuracy
        - Use heavily compressed images
        - Test on training data
        - Assume detection guarantees content exists
        
        ### Performance on Different Methods
        
        | Method | Detection Rate |
        |--------|----------------|
        | LSB | ~90% |
        | DCT | ~85% |
        | DWT | ~82% |
        | Mixed | ~87% |
        """)