"""
Watermarking UI Section
=======================
Streamlit UI for the watermarking feature.
Handles all visual components and user interactions for watermark application.
"""

import logging
from io import BytesIO
from typing import Optional
import streamlit as st
from PIL import Image

from .watermark import apply_text_watermark, apply_lsb_watermark, apply_alpha_blending_watermark
from src.ui.reusable_components import show_error, show_success, show_warning, show_info
from src.db.db_utils import log_activity

logger = logging.getLogger(__name__)


# ============================================================================
#                           HELPER FUNCTIONS
# ============================================================================

def render_section_header(icon, title, description):
    """Render a consistent section header."""
    st.markdown(f"""
        <div class="animate-fade-in-down">
            <h2>{icon} {title}</h2>
            <p style="color: #8B949E; margin-bottom: 1rem;">{description}</p>
        </div>
    """, unsafe_allow_html=True)


def render_step(step_num, title):
    """Render a step indicator."""
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="background: linear-gradient(135deg, #1F6FEB 0%, #0969DA 100%); 
                        color: white; width: 30px; height: 30px; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center; 
                        font-weight: bold; margin-right: 10px;">
                {step_num}
            </div>
            <h4 style="margin: 0;">{title}</h4>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
#                       MAIN WATERMARKING SECTION
# ============================================================================

def show_watermarking_section():
    """
    Display watermarking interface with professional SaaS-style design.
    
    Features:
    - Upload images
    - Configure watermark text, size, position, opacity, color
    - Apply watermarks
    - Download watermarked images
    - Before/after comparison
    
    This is the main entry point for the watermarking feature.
    """
    
    render_section_header(
        "💧",
        "Watermarking",
        "Add visible watermarks to protect your images with copyright information"
    )
    
    st.divider()
    
    # Create tabs for different workflows
    tab_apply, tab_advanced, tab_help = st.tabs([
        "🖼️ Apply Watermark",
        "⚙️ Advanced Options",
        "❓ Help"
    ])
    
    # =========================================================================
    # TAB 1: APPLY WATERMARK
    # =========================================================================
    with tab_apply:
        _show_basic_watermark_section()
    
    # =========================================================================
    # TAB 2: ADVANCED OPTIONS
    # =========================================================================
    with tab_advanced:
        _show_advanced_watermark_section()
    
    # =========================================================================
    # TAB 3: HELP
    # =========================================================================
    with tab_help:
        _show_watermark_help()


# ============================================================================
#                    BASIC WATERMARKING SECTION
# ============================================================================

def _show_basic_watermark_section():
    """Display basic watermarking interface with step-by-step workflow."""
    
    col1, col2 = st.columns([1.2, 0.8])
    
    # =========================================================================
    # COLUMN 1: IMAGE UPLOAD & PREVIEW
    # =========================================================================
    with col1:
        render_step(1, "Upload Image")
        
        st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
        
        # File uploader
        image_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png", "bmp", "tiff"],
            label_visibility="collapsed",
            key="watermark_image_upload"
        )
        
        if image_file:
            try:
                original_image = Image.open(image_file)
                st.image(original_image, caption="Selected Image", use_container_width=True)
                
                # Image info
                width, height = original_image.size
                file_format = original_image.format or "Unknown"
                
                st.markdown(f"""
                    <div class="card card-info" style="margin-top: 0.75rem; padding: 0.75rem; border-radius: 6px;">
                        📐 **{width}×{height}** | 
                        🎨 **{original_image.mode}** | 
                        📁 **{file_format}**
                    </div>
                """, unsafe_allow_html=True)
                
                if file_format == "JPEG":
                    show_warning("💡 PNG format recommended for better watermark quality")
                    
            except Exception as e:
                show_error(f"Error loading image: {str(e)}")
                image_file = None
        else:
            st.markdown("""
                <div style="text-align: center; padding: 2rem; color: #8B949E; border: 2px dashed #30363D; border-radius: 8px;">
                    <p style="font-size: 2.5rem; margin-bottom: 0.5rem;">📤</p>
                    <p style="margin: 0; font-weight: 500;">Drag and drop an image or click to browse</p>
                    <p style="font-size: 0.85rem; color: #6E7681; margin-top: 0.5rem;">PNG, JPG, BMP, TIFF supported</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # COLUMN 2: WATERMARK SETTINGS
    # =========================================================================
    with col2:
        render_step(2, "Watermark Settings")
        
        st.markdown('<div class="card animate-fade-in stagger-1">', unsafe_allow_html=True)
        
        # Text input
        watermark_text = st.text_input(
            "Watermark Text",
            value="© Your Name",
            placeholder="Enter watermark text",
            max_chars=100,
            key="watermark_text_input"
        )
        
        st.divider()
        
        # Font size
        font_size = st.slider(
            "Font Size",
            min_value=10,
            max_value=100,
            value=30,
            step=2,
            key="watermark_font_size"
        )
        
        # Position selector
        position = st.selectbox(
            "Position",
            ["top-left", "top-center", "top-right", 
             "middle-left", "center", "middle-right",
             "bottom-left", "bottom-center", "bottom-right"],
            index=8,  # Default: bottom-right
            key="watermark_position"
        )
        
        st.divider()
        
        # Opacity slider
        opacity = st.slider(
            "Opacity",
            min_value=50,
            max_value=255,
            value=180,
            step=5,
            key="watermark_opacity",
            help="50 = very transparent, 255 = fully opaque"
        )
        
        # Color picker
        text_color_hex = st.color_picker(
            "Watermark Color",
            value="#FFFFFF",
            key="watermark_color"
        )
        text_color = tuple(int(text_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # =====================================================================
        # APPLY BUTTON
        # =====================================================================
        st.markdown("<br>", unsafe_allow_html=True)
        
        apply_button = st.button(
            "💧 Apply Watermark",
            use_container_width=True,
            type="primary",
            disabled=not (image_file and watermark_text),
            key="watermark_apply_btn"
        )
        
        if apply_button:
            _apply_watermark_workflow(
                image_file=image_file,
                watermark_text=watermark_text,
                font_size=font_size,
                position=position,
                text_color=text_color,
                opacity=opacity
            )


# ============================================================================
#                    ADVANCED WATERMARKING SECTION
# ============================================================================

def _show_advanced_watermark_section():
    """Display advanced watermarking options."""
    
    st.info("⚙️ Advanced watermarking features (planned for future versions)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔒 Invisible LSB Watermark
        
        Embed an invisible watermark that can only be detected programmatically.
        
        **Features:**
        - Completely invisible to human eye
        - Can be detected with special tools
        - Perfect for copyright enforcement
        
        **Status:** Coming soon...
        """)
    
    with col2:
        st.markdown("""
        ### 🎨 Batch Watermarking
        
        Apply watermarks to multiple images at once.
        
        **Features:**
        - Upload ZIP with multiple images
        - Same settings for all
        - Download watermarked ZIP
        
        **Status:** Coming soon...
        """)
    
    st.divider()
    
    st.markdown("""
    ### Logo Watermarking
    
    Soon you'll be able to upload logo images and overlay them with alpha blending.
    """)


# ============================================================================
#                      WATERMARK HELP SECTION
# ============================================================================

def _show_watermark_help():
    """Display comprehensive help documentation for watermarking."""
    
    st.markdown("""
        <div class="card">
            <div class="card-header">📖 Watermarking Guide</div>
        </div>
    """, unsafe_allow_html=True)
    
    help_tabs = st.tabs([
        "🤔 What is Watermarking?",
        "💡 Best Practices",
        "🎨 Design Tips",
        "❓ FAQ"
    ])
    
    # =========================================================================
    # HELP TAB 1: WHAT IS WATERMARKING
    # =========================================================================
    with help_tabs[0]:
        st.markdown("""
        ## What is Watermarking?
        
        A **watermark** is a visible or invisible mark embedded in an image to:
        
        ### ✅ Uses
        
        1. **Copyright Protection**
           - Establish ownership of content
           - Prevent unauthorized use
           
        2. **Brand Identity**
           - Add company logos
           - Maintain brand consistency
           
        3. **Authentication**
           - Verify image authenticity
           - Detect tampering
           
        4. **Licensing**
           - Indicate usage rights
           - Show attribution
        
        ### Types of Watermarks
        
        | Type | Visibility | Robustness | Use Case |
        |------|------------|-----------|----------|
        | **Text** | Visible | Medium | Copyright notice |
        | **Logo** | Visible | Medium | Brand watermark |
        | **LSB** | Invisible | Low | Copyright info |
        | **DCT** | Invisible | High | JPEG files |
        | **DWT** | Invisible | High | High security |
        """)
    
    # =========================================================================
    # HELP TAB 2: BEST PRACTICES
    # =========================================================================
    with help_tabs[1]:
        st.markdown("""
        ## Best Practices for Watermarking
        
        ### ✅ DO:
        
        1. **Use Semi-Transparent Watermarks**
           - Opacity 150-200 works well
           - Keep image visible underneath
           - Balance protection vs. usability
        
        2. **Position Strategically**
           - Top-left or bottom-right corners (standard)
           - Center for important images
           - Avoid critical image areas
        
        3. **Choose Contrasting Colors**
           - White on dark images
           - Black on light images
           - High contrast = better visibility
        
        4. **Keep Text Readable**
           - Font size 25-50 for most images
           - Simple, clean fonts work best
           - Avoid fancy/decorative fonts
        
        5. **Different Watermarks for Different Uses**
           - Social media: smaller, subtle
           - Prints: larger, bold
           - Galleries: medium, balanced
        
        ### ❌ DON'T:
        
        1. ❌ Use fully opaque watermarks (blocks content)
        2. ❌ Place watermark on important parts
        3. ❌ Use too small font (unreadable)
        4. ❌ Use too many watermarks
        5. ❌ Watermark low-quality images
        6. ❌ Use hard-to-read colors/fonts
        """)
    
    # =========================================================================
    # HELP TAB 3: DESIGN TIPS
    # =========================================================================
    with help_tabs[2]:
        st.markdown("""
        ## Design Tips for Professional Watermarks
        
        ### 🎨 Color Selection
        
        **White Watermarks:**
        - Best for dark/blue-toned images
        - High contrast and visibility
        - Professional appearance
        
        **Black Watermarks:**
        - Best for light/bright images
        - Good contrast on light backgrounds
        - Classic look
        
        **Colored Watermarks:**
        - Use brand colors for consistency
        - Ensure sufficient contrast
        - Test on preview before applying
        
        ### 📝 Text Guidelines
        
        | Font Size | Image Size | Best For |
        |-----------|-----------|----------|
        | 10-15 | 400×300 | Small thumbnails |
        | 20-30 | 800×600 | Social media |
        | 40-50 | 1200×900 | Prints |
        | 60+ | 2000×1500 | Large displays |
        
        ### 📍 Position Recommendations
        
        **For Protection:**
        - Bottom-right corner (standard)
        - Harder to crop out
        - Doesn't block main content
        
        **For Branding:**
        - Top-left or center
        - More prominent placement
        - Works as logo
        
        **For Subtle:**
        - Center with low opacity
        - Barely noticeable
        - Doesn't distract
        
        ### 🔤 Text Examples
        
        ```
        © 2024 Your Company Name
        © Your Name - All Rights Reserved
        www.yourwebsite.com
        Photography by [Your Name]
        Confidential - Do Not Reproduce
        ```
        """)
    
    # =========================================================================
    # HELP TAB 4: FAQ
    # =========================================================================
    with help_tabs[3]:
        st.markdown("""
        ## Frequently Asked Questions
        
        ### Q: Can watermarks be removed?
        **A:** Text watermarks can technically be removed with advanced image editing. 
        For maximum protection, use invisible watermarks (advanced feature).
        
        ### Q: What's the best image format?
        **A:** PNG works best for maintaining watermark quality. 
        JPG is acceptable but may lose some quality.
        
        ### Q: How transparent should my watermark be?
        **A:** 
        - 150-180 opacity: Standard (good balance)
        - 100-150 opacity: Very subtle
        - 200-255 opacity: Very prominent
        
        ### Q: Can I watermark already watermarked images?
        **A:** Yes, but stacking watermarks can look unprofessional. 
        Better to recreate from original image.
        
        ### Q: Does watermarking affect file size?
        **A:** Slightly. PNG files might be ~5-10% larger due to added data.
        
        ### Q: What's the difference between watermarks and steganography?
        **A:**
        - **Watermark:** Visible (or easily detectable) mark for protection
        - **Steganography:** Hidden data that's difficult to find
        
        ### Q: Can I use custom fonts?
        **A:** Currently limited to system fonts. Future versions will support custom fonts.
        
        ### Q: How do I handle batch watermarking?
        **A:** Coming soon! For now, apply watermarks one at a time.
        """)


# ============================================================================
#                    WATERMARK WORKFLOW EXECUTION
# ============================================================================

def _apply_watermark_workflow(image_file, watermark_text, font_size, position, 
                             text_color, opacity):
    """
    Execute the watermark application workflow.
    
    Args:
        image_file: Uploaded image file
        watermark_text: Text to display
        font_size: Size of watermark font
        position: Position on image
        text_color: RGB color tuple
        opacity: Transparency (0-255)
    """
    try:
        # Progress tracking
        progress_container = st.container()
        results_container = st.container()
        
        with progress_container:
            progress = st.progress(0)
            status = st.empty()
        
        # Step 1: Load image
        status.text("📷 Loading image...")
        progress.progress(20)
        
        original_image = Image.open(image_file)
        original_mode = original_image.mode
        
        # Step 2: Apply watermark
        status.text("💧 Applying watermark...")
        progress.progress(50)
        
        try:
            watermarked_image = apply_text_watermark(
                image=original_image,
                watermark_text=watermark_text,
                font_size=font_size,
                position=position,
                text_color=text_color,
                opacity=opacity
            )
        except Exception as e:
            show_error(f"Watermark application failed: {str(e)}")
            progress.empty()
            status.empty()
            return
        
        # Step 3: Prepare results
        status.text("📦 Preparing results...")
        progress.progress(80)
        
        # Store in session state for results display
        st.session_state.last_watermarked_image = watermarked_image
        st.session_state.last_original_image = original_image
        st.session_state.last_watermark_settings = {
            "text": watermark_text,
            "font_size": font_size,
            "position": position,
            "opacity": opacity,
            "color": text_color
        }
        
        progress.progress(100)
        status.text("✅ Complete!")
        
        import time
        time.sleep(0.5)
        progress.empty()
        status.empty()
        
        # Log activity
        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
            log_activity(
                user_id=st.session_state.user_id,
                action="WATERMARK",
                details=f"Applied watermark: {watermark_text[:30]}"
            )
        
        # Display results
        with results_container:
            _display_watermark_results(original_image, watermarked_image, watermark_text)
            show_success("✅ Watermark applied successfully!")
        
    except Exception as e:
        show_error(f"Watermarking workflow error: {str(e)}")
        logger.error(f"Watermark error: {str(e)}")


def _display_watermark_results(original, watermarked, watermark_text):
    """Display before/after comparison and download options."""
    
    st.divider()
    
    # Success banner
    st.markdown("""
        <div class="result-container animate-scale-in" style="text-align: center; margin-bottom: 1.5rem;">
            <p style="font-size: 3rem; margin-bottom: 0.5rem;">💧</p>
            <h3 style="color: #3FB950; margin: 0;">Watermark Applied</h3>
            <p style="color: #8B949E; margin-top: 0.5rem;">Comparison and download options below</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Before/After comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📷 Original Image")
        st.image(original, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card card-success">', unsafe_allow_html=True)
        st.markdown("### 💧 Watermarked Image")
        st.image(watermarked, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Watermark info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Watermark Text", watermark_text[:20] + ("..." if len(watermark_text) > 20 else ""))
    with col2:
        st.metric("Image Size", f"{watermarked.size[0]}×{watermarked.size[1]}")
    with col3:
        st.metric("Format", watermarked.format or "Unknown")
    
    st.divider()
    
    # Download button
    st.markdown("### 💾 Download")
    
    buf = BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Sanitize filename: remove special characters that are invalid in filenames
        import re
        safe_text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', watermark_text)
        safe_text = safe_text.replace(' ', '_').strip('.')[:20]
        if not safe_text:
            safe_text = "watermark"
        
        st.download_button(
            label="⬇️ Download Watermarked Image",
            data=buf.getvalue(),
            file_name=f"watermarked_{safe_text}.png",
            mime="image/png",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        if st.button("🔄 Apply New Watermark", use_container_width=True):
            st.rerun()
    
    st.caption("💡 Always save as PNG to preserve watermark quality")