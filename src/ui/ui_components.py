"""
Main UI Components
==================
Contains the main section components for the application interface.
Professional SaaS-style design with consistent styling across all tabs.
"""

import logging
import time
import pandas as pd
import numpy as np
from io import BytesIO
from PIL import Image
import streamlit as st

from src.stego.lsb_steganography import encode_image as lsb_encode, decode_image as lsb_decode
from src.stego.dct_steganography import encode_dct as dct_encode, decode_dct as dct_decode
from src.stego.dwt_steganography import encode_dwt as dwt_encode, decode_dwt as dwt_decode
from src.encryption.encryption import encrypt_message, decrypt_message
from src.db.db_utils import log_activity
from src.Watermarking.ui_section import show_watermarking_section as _show_watermarking_section
from .reusable_components import (
    create_text_input, create_text_area, create_file_uploader,
    create_method_selector, create_checkbox, show_error, show_success,
    show_warning, show_info, display_image_comparison, display_decoded_message,
    create_primary_button, display_results_summary, show_divider,
    show_method_details, create_comparison_table, show_activity_search,
    create_batch_upload_section, create_batch_options_section,
    display_batch_results, display_detailed_results, render_step,
    show_lottie_animation, create_metric_cards
)
from .config_dict import FORM_LABELS, SECTION_HEADERS, TAB_NAMES, ERROR_MESSAGES, SUCCESS_MESSAGES

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ============================================================================
#                    HELPER FUNCTIONS
# ============================================================================

def is_valid_message(message):
    """Validate if extracted message is valid (non-empty string)."""
    if not isinstance(message, str):
        return False
    return len(message.strip()) > 0


def render_card(content, card_type="default", header=None):
    """Render a styled card container."""
    card_class = f"card card-{card_type}" if card_type != "default" else "card"
    header_html = f'<div class="card-header">{header}</div>' if header else ""
    st.markdown(f'<div class="{card_class}">{header_html}{content}</div>', unsafe_allow_html=True)


def render_section_header(icon, title, description):
    """Render a consistent section header."""
    st.markdown(f"""
        <div class="animate-fade-in-down">
            <h2>{icon} {title}</h2>
            <p style="color: #8B949E; margin-bottom: 1rem;">{description}</p>
        </div>
    """, unsafe_allow_html=True)


def render_help_section(title, description, tips):
    """Render a help section in an expander."""
    with st.expander(f"❓ {title}", expanded=False):
        st.markdown(description)
        st.markdown("**Tips:**")
        for tip in tips:
            st.markdown(f"• {tip}")


# ============================================================================
#                           AUTHENTICATION SECTION
# ============================================================================

def show_auth_section():
    """Display authentication interface with professional styling."""
    
    render_section_header("🔐", "Welcome", "Sign in to access your steganography workspace")
    
    st.divider()
    
    # Center the auth forms
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔓 Sign In", "📝 Create Account"])
        
        with auth_tab1:
            _show_login_form()
        
        with auth_tab2:
            _show_register_form()
    
    # Features showcase
    st.divider()
    st.markdown("### ✨ Features")
    
    cols = st.columns(3)
    features = [
        ("🔐", "Encode", "Hide messages in images"),
        ("🔍", "Decode", "Extract hidden messages"),
        ("📊", "Compare", "Test all methods")
    ]
    
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
                <div class="feature-card animate-fade-in">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
            """, unsafe_allow_html=True)


def _show_login_form():
    """Display login form with card styling."""
    st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("#### Sign in to your account")
        
        username = create_text_input(
            label="Username",
            placeholder="Enter your username"
        )
        password = create_text_input(
            label="Password",
            placeholder="Enter your password",
            password=True
        )
        
        if st.form_submit_button("🔓 Sign In", use_container_width=True, type="primary"):
            if username and password:
                with st.spinner("Signing in..."):
                    try:
                        from src.db.db_utils import verify_user, RateLimitError
                        user_data = verify_user(username, password)
                        
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.username = user_data['username']
                            st.session_state.user_id = user_data['user_id']
                            show_success("Welcome back!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            show_error("❌ Invalid username or password. Please check and try again.")
                    except RateLimitError:
                        show_error("❌ Too many login attempts. Please wait 5 minutes and try again.")
                    except Exception as e:
                        show_error(f"❌ Login error: {str(e)}")
            else:
                show_error("❌ Please enter both username and password")
    
    st.markdown('</div>', unsafe_allow_html=True)


def _show_register_form():
    """Display registration form with card styling."""
    st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
    
    with st.form("register_form"):
        st.markdown("#### Create a new account")
        
        username = create_text_input(
            label="Username",
            placeholder="Choose a username"
        )
        password = create_text_input(
            label="Password",
            placeholder="Create a strong password",
            password=True
        )
        confirm_password = create_text_input(
            label="Confirm Password",
            placeholder="Confirm your password",
            password=True
        )
        
        if st.form_submit_button("📝 Create Account", use_container_width=True, type="primary"):
            if not (username and password and confirm_password):
                show_error("Please fill all fields")
            elif password != confirm_password:
                show_error("Passwords do not match")
            elif len(password) < 8:
                show_error("Password must be at least 8 characters")
            elif len(username) < 3:
                show_error("Username must be at least 3 characters")
            else:
                with st.spinner("Creating account..."):
                    try:
                        from src.db.db_utils import add_user
                        success = add_user(username, password)
                        if success:
                            show_success("Account created! You can now sign in.")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            show_error("Failed to create account. Username may already exist or password doesn't meet requirements.")
                    except Exception as e:
                        show_error(f"Registration error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
#                           ENCODE SECTION
# ============================================================================

def show_encode_section():
    """Display encoding interface with professional styling."""
    
    render_section_header("🔐", "Encode Message", "Hide secret messages inside images using steganography")
    
    st.divider()
    
    # Main tabs for workflow
    tab_encode, tab_results, tab_help = st.tabs(["📝 Encode", "✅ Results", "❓ Help"])
    
    with tab_encode:
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            # Step 1: Upload Image
            render_step(1, "Upload Your Image")
            
            st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
            
            image_file = create_file_uploader(file_type="images", key="encode_image")
            
            if image_file:
                try:
                    original_image = Image.open(image_file)
                    st.image(original_image, caption="Selected Image", use_container_width=True)
                    
                    # Image info
                    file_format = original_image.format or "Unknown"
                    st.markdown(f"""
                        <div class="card card-info" style="margin-top: 0.5rem; padding: 0.75rem;">
                            📐 <strong>{original_image.size[0]}×{original_image.size[1]}</strong> | 
                            🎨 <strong>{original_image.mode}</strong> | 
                            📁 <strong>{file_format}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if file_format == "JPEG":
                        show_warning("JPG uses lossy compression. PNG recommended for best results.")
                        
                except Exception as e:
                    show_error(f"Error loading image: {str(e)}")
            else:
                st.markdown("""
                    <div style="text-align: center; padding: 2rem; color: #8B949E;">
                        <p style="font-size: 2rem;">📤</p>
                        <p>Drag and drop an image or click to browse</p>
                        <p style="font-size: 0.85rem; color: #6E7681;">PNG, JPG, BMP supported</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 2: Enter Message
            render_step(2, "Enter Your Secret Message")
            
            st.markdown('<div class="card animate-fade-in stagger-1">', unsafe_allow_html=True)
            message = st.text_area(
                "Secret Message",
                placeholder="Type your secret message here...",
                height=150,
                max_chars=5000,
                key="encode_message"
            )
            if message:
                st.caption(f"📝 {len(message)} characters")
                
                # Check capacity warning (if file exists)
                if image_file:
                    try:
                        from stegotool.modules.module6_redundancy.ui_section import check_capacity_and_warn
                        original_image = Image.open(image_file)
                        ecc_config = st.session_state.get('ecc_config', {'use_ecc': False, 'ecc_strength': 32})
                        check_capacity_and_warn(
                            original_image.size,
                            message,
                            use_ecc=ecc_config.get('use_ecc', False),
                            ecc_strength=ecc_config.get('ecc_strength', 32)
                        )
                    except (ImportError, Exception) as e:
                        logger.debug(f"Capacity check skipped: {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Step 3: Settings
            render_step(3, "Configure Settings")
            
            st.markdown('<div class="card animate-fade-in stagger-2">', unsafe_allow_html=True)
            
            method = create_method_selector(key="encode_method")
            
            # Method info
            method_info = {
                "LSB": ("⚡ Fast", "Spatial domain", "#238636"),
                "Hybrid DCT": ("🛡️ Secure", "Frequency domain", "#1F6FEB"),
                "Hybrid DWT": ("🔐 Robust", "Wavelet domain", "#8957E5")
            }
            info = method_info.get(method, ("", "", "#8B949E"))
            st.markdown(f"""
                <div style="padding: 0.5rem; background: rgba(0,0,0,0.2); border-radius: 6px; border-left: 3px solid {info[2]};">
                    <strong>{info[0]}</strong> - {info[1]}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 4: Encryption
            render_step(4, "Security Options")
            
            st.markdown('<div class="card animate-fade-in stagger-3">', unsafe_allow_html=True)
            
            use_encryption = st.checkbox("🔒 Encrypt message (recommended)", key="encode_encrypt")
            encryption_password = None
            
            if use_encryption:
                encryption_password = st.text_input(
                    "Encryption Password",
                    type="password",
                    placeholder="Create a strong password",
                    key="encode_encryption_pass"
                )
                st.caption("🔐 AES-256 encryption will be applied")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 5: ECC
            ecc_config = {'use_ecc': False, 'ecc_strength': 32}
            try:
                from stegotool.modules.module6_redundancy.ui_section import show_ecc_encode_section
                ecc_config = show_ecc_encode_section()
            except (ImportError, Exception) as e:
                logger.debug(f"ECC section not available: {e}")
                st.markdown('<div class="card animate-fade-in stagger-4">', unsafe_allow_html=True)
                st.markdown('<p style="color: #8B949E; font-size: 0.9rem;">ℹ️ Error Correction not available</p>', 
                            unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.session_state['ecc_config'] = ecc_config
            
            # Encode Button
            st.markdown("<br>", unsafe_allow_html=True)
            
            encode_btn = st.button(
                "🔐 Encode Message",
                use_container_width=True,
                type="primary",
                disabled=not (image_file and message)
            )
            
            if encode_btn:
                _perform_encoding(
                    image_file, 
                    message, 
                    method, 
                    use_encryption, 
                    encryption_password,
                    use_ecc=ecc_config.get('use_ecc', False),
                    ecc_strength=ecc_config.get('ecc_strength', 32)
                )
    
    with tab_results:
        if "last_encoded_image" in st.session_state and st.session_state.last_encoded_image:
            _display_encode_results()
        else:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 3rem;">
                    <p style="font-size: 3rem;">📷</p>
                    <p style="color: #8B949E;">No encoding results yet</p>
                    <p style="color: #6E7681; font-size: 0.9rem;">Encode a message to see results here</p>
                </div>
            """, unsafe_allow_html=True)
    
    with tab_help:
        _show_encode_help()


def _perform_encoding(image_file, message, method, use_encryption, encryption_password,
                     use_ecc=False, ecc_strength=32):
    """Perform the encoding operation with optional ECC."""
    try:
        progress = st.progress(0)
        status = st.empty()
        
        status.text("Loading image...")
        progress.progress(10)
        
        original_image = Image.open(image_file)
        file_format = original_image.format
        
        # Check compatibility
        if file_format == "JPEG" and method in ["Hybrid DCT", "Hybrid DWT"]:
            show_error(f"{method} doesn't work well with JPG. Please use PNG.")
            return
        
        status.text("Preparing message...")
        progress.progress(25)
        
        # Start with original message as string
        message_to_embed = message
        
        # Step 1: Encrypt if needed (produces string output)
        if use_encryption and encryption_password:
            message_to_embed = encrypt_message(message, encryption_password)
            # encrypt_message returns a string
        
        # Step 2: Add ECC if enabled (produces bytes/bytearray output)
        if use_ecc:
            status.text(f"Adding error correction ({ecc_strength} parity bytes)...")
            progress.progress(40)
            
            try:
                from stegotool.modules.module6_redundancy.ui_section import encode_message_with_ecc
                
                message_to_embed = encode_message_with_ecc(
                    message_to_embed,
                    use_ecc=True,
                    nsym=ecc_strength
                )
                # message_to_embed is now bytes or bytearray
                
            except ImportError:
                logger.warning("ECC module not available, skipping ECC")
            except ValueError as e:
                show_error(f"ECC encoding failed: {str(e)}")
                return
        
        status.text(f"Encoding with {method}...")
        progress.progress(60)
        
        # Create progress callback for DCT/DWT methods
        def update_encoding_progress(fraction):
            """Update progress bar during encoding (0.0 to 1.0)."""
            # Scale from 60-90% for the actual encoding phase
            current_progress = 60 + int(fraction * 30)
            progress.progress(current_progress)
        
        # Stego functions now accept both str and bytes
        if method == "LSB":
            encoded_image = lsb_encode(original_image, message_to_embed)
        elif method == "Hybrid DCT":
            encoded_image = dct_encode(original_image, message_to_embed, update_progress=update_encoding_progress)
        elif method == "Hybrid DWT":
            encoded_image = dwt_encode(original_image, message_to_embed, update_progress=update_encoding_progress)
        else:
            encoded_image = lsb_encode(original_image, message_to_embed)
        
        status.text("Finalizing...")
        progress.progress(90)
        
        # Store in session state
        st.session_state.last_encoded_image = encoded_image
        st.session_state.last_original_image = original_image
        st.session_state.last_encode_method = method
        st.session_state.last_encode_encrypted = use_encryption
        st.session_state.last_encode_ecc = use_ecc
        st.session_state.last_encode_nsym = ecc_strength
        
        progress.progress(100)
        status.empty()
        progress.empty()
        
        # Log activity
        ecc_info = f" (ECC: {ecc_strength} bytes)" if use_ecc else ""
        if hasattr(st.session_state, 'user_id') and st.session_state.user_id:
            log_activity(st.session_state.user_id, "ENCODE", f"Encoded with {method}{ecc_info}")
        
        show_success(f"Message encoded successfully! (ECC: {'ON' if use_ecc else 'OFF'})")
        
    except Exception as e:
        show_error(f"Encoding failed: {str(e)}")
        logger.error(f"Encoding error: {str(e)}", exc_info=True)


def _display_encode_results():
    """Display encoding results with detection method info."""
    encoded = st.session_state.last_encoded_image
    original = st.session_state.get("last_original_image")
    method = st.session_state.get("last_encode_method", "Unknown")
    encrypted = st.session_state.get("last_encode_encrypted", False)
    
    # Success banner
    st.markdown(f"""
        <div class="result-container animate-scale-in" style="text-align: center; margin-bottom: 1.5rem;">
            <p style="font-size: 3rem; margin-bottom: 0.5rem;">✅</p>
            <h3 style="color: #3FB950; margin: 0;">Encoding Successful!</h3>
            <p style="color: #8B949E;">Your message has been hidden in the image</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Image comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📷 Original Image**")
        if original:
            st.image(original, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card card-success">', unsafe_allow_html=True)
        st.markdown("**🔐 Encoded Image**")
        st.image(encoded, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Info metrics
    metrics = {
        "Method": method,
        "Encrypted": "Yes" if encrypted else "No",
        "Format": "PNG"
    }
    
    cols = st.columns(3)
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label, value)
    
    # Download button
    st.divider()
    
    buf = BytesIO()
    encoded.save(buf, format="PNG")
    buf.seek(0)
    
    st.download_button(
        label="⬇️ Download Encoded Image",
        data=buf.getvalue(),
        file_name=f"encoded_{method.lower().replace(' ', '_')}.png",
        mime="image/png",
        use_container_width=True,
        type="primary"
    )
    
    st.caption("💡 Always save as PNG to preserve the hidden message")


def _show_encode_help():
    """Show encoding help section."""
    st.markdown("""
        <div class="card">
            <div class="card-header">📖 How Encoding Works</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### What is Steganography?
    
    Steganography is the practice of hiding secret information within ordinary data. 
    In image steganography, we hide messages inside image files without visibly changing them.
    
    ---
    
    ### Methods Explained
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **⚡ LSB (Least Significant Bit)**
        - Fastest method
        - Works in spatial domain
        - High capacity
        - Best for: Quick encoding
        """)
    
    with col2:
        st.markdown("""
        **🛡️ Hybrid DCT**
        - Frequency domain method
        - More robust to compression
        - Medium capacity
        - Best for: Security needs
        """)
    
    with col3:
        st.markdown("""
        **🔐 Hybrid DWT**
        - Wavelet transform based
        - High imperceptibility
        - Lower capacity
        - Best for: Maximum security
        """)
    
    st.divider()
    
    st.markdown("""
    ### Best Practices
    
    1. **Use PNG format** - JPEG compression destroys hidden data
    2. **Enable encryption** - Adds another layer of security
    3. **Keep original safe** - You might need to compare
    4. **Don't resize** - Resizing destroys the hidden message
    5. **Avoid screenshots** - They recompress the image
    """)


def _display_decode_results():
    """Display decoding results with extracted message."""
    result = st.session_state.get('decode_result', {})
    message = result.get('message', '')
    method = result.get('method', 'Unknown')
    
    # Success banner
    st.markdown(f"""
        <div class="result-container animate-scale-in" style="text-align: center; margin-bottom: 1.5rem;">
            <p style="font-size: 3rem; margin-bottom: 0.5rem;">📩</p>
            <h3 style="color: #3FB950; margin: 0;">Message Extracted Successfully!</h3>
            <p style="color: #8B949E;">Your hidden message has been recovered</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display the extracted message
    st.markdown('<div class="card card-success">', unsafe_allow_html=True)
    st.markdown("**🔓 Extracted Message**")
    st.code(message, language="text")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Info metrics
    cols = st.columns(3)
    with cols[0]:
        st.metric("Method", method)
    with cols[1]:
        st.metric("Length", f"{len(message)} chars")
    with cols[2]:
        st.metric("Status", "✅ Success")
    
    # Copy button
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.toast("Message copied!")
    
    with col2:
        st.download_button(
            label="⬇️ Download Message",
            data=message,
            file_name="decoded_message.txt",
            mime="text/plain",
            use_container_width=True
        )


def _show_decode_help():
    """Show decoding help section."""
    st.markdown("""
        <div class="card">
            <div class="card-header">📖 How Decoding Works</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### What is Decoding?
    
    Decoding is the process of extracting hidden messages from steganographic images.
    The decoder automatically detects which method was used.
    
    ---
    
    ### How It Works
    
    1. **Method Detection** - System tries all steganography methods
    2. **Quality Scoring** - Best match is selected based on confidence
    3. **Message Extraction** - Hidden data is recovered
    4. **Decryption** - If encrypted, password decrypts the message
    
    ---
    
    ### Methods Comparison
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **⚡ LSB Decoding**
        - Fastest extraction
        - Works on spatial domain
        - Detection: Automatic
        - Speed: Instant
        """)
    
    with col2:
        st.markdown("""
        **🛡️ DCT Decoding**
        - Frequency analysis
        - More secure extraction
        - Detection: Automatic
        - Speed: Fast
        """)
    
    with col3:
        st.markdown("""
        **🔐 DWT Decoding**
        - Wavelet coefficient analysis
        - Highest security
        - Detection: Automatic
        - Speed: Moderate
        """)
    
    st.divider()
    
    st.markdown("""
    ### Troubleshooting
    
    **"No message found"**
    - Image doesn't contain hidden data
    - Image was compressed/modified
    - Try using the original PNG file
    
    **"Decryption failed"**
    - Wrong password entered
    - Data corrupted during transfer
    - Try re-uploading the image
    
    **Best Practices**
    
    1. **Use original files** - Don't modify or screenshot
    2. **Keep PNG format** - JPEG compression corrupts data
    3. **Correct password** - Encryption password is case-sensitive
    4. **Check file integrity** - Ensure image wasn't altered
    5. **Try all methods** - System auto-detects, but manual try helps
    """)


# ============================================================================
#                           DECODE SECTION
# ============================================================================

def show_decode_section():
    """Display decoding interface with ECC recovery."""
    
    render_section_header("🔍", "Decode Message", "Extract hidden messages from steganographic images")
    
    st.divider()
    
    tab_decode, tab_results, tab_help = st.tabs(["🔓 Decode", "📩 Results", "❓ Help"])
    
    with tab_decode:
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            render_step(1, "Upload Encoded Image")
            
            st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
            
            image_file = create_file_uploader(file_type="images", key="decode_image")
            
            if image_file:
                try:
                    image = Image.open(image_file)
                    st.image(image, caption="Uploaded Image", use_container_width=True)
                    
                    file_format = image.format or "Unknown"
                    st.markdown(f"""
                        <div class="card card-info" style="margin-top: 0.5rem; padding: 0.75rem;">
                            📐 <strong>{image.size[0]}×{image.size[1]}</strong> | 
                            📁 <strong>{file_format}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if file_format == "JPEG":
                        show_warning("JPG compression may have corrupted hidden data. ECC recovery can help!")
                        
                except Exception as e:
                    show_error(f"Error loading image: {str(e)}")
            else:
                st.markdown("""
                    <div style="text-align: center; padding: 2rem; color: #8B949E;">
                        <p style="font-size: 2rem;">📥</p>
                        <p>Upload an image with a hidden message</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Step 2: Select Decoding Method
            render_step(2, "Select Decoding Method")
            
            st.markdown('<div class="card animate-fade-in stagger-1">', unsafe_allow_html=True)
            
            decode_method = st.selectbox(
                "Decoding Method",
                ["LSB", "Hybrid DCT", "Hybrid DWT"],
                key="decode_method_select",
                help="Choose the same method that was used to encode the image"
            )
            
            # Method info badges
            method_info = {
                "LSB": ("⚡ Fast", "Spatial domain — use if encoded with LSB", "#238636"),
                "Hybrid DCT": ("🛡️ Secure", "Frequency domain — use if encoded with DCT", "#1F6FEB"),
                "Hybrid DWT": ("🔐 Robust", "Wavelet domain — use if encoded with DWT", "#8957E5")
            }
            info = method_info.get(decode_method, ("", "", "#8B949E"))
            st.markdown(f"""
                <div style="padding: 0.5rem; background: rgba(0,0,0,0.2); border-radius: 6px; border-left: 3px solid {info[2]};">
                    <strong>{info[0]}</strong> — {info[1]}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 3: Decryption Settings
            render_step(3, "Decryption Settings")
            
            st.markdown('<div class="card animate-fade-in stagger-2">', unsafe_allow_html=True)
            
            use_encryption = st.checkbox("🔓 Message is encrypted", key="decode_encrypt")
            decryption_password = None
            
            if use_encryption:
                decryption_password = st.text_input(
                    "Decryption Password",
                    type="password",
                    placeholder="Enter the encryption password",
                    key="decode_pass"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 4: ECC Recovery
            try:
                from stegotool.modules.module6_redundancy.ui_section import show_ecc_decode_section
                ecc_config = show_ecc_decode_section()
            except ImportError:
                # Fallback if module not available
                ecc_config = {'use_ecc_recovery': False, 'ecc_strength': 0}
            
            # Decode button
            st.markdown("<br>", unsafe_allow_html=True)
            
            decode_btn = st.button(
                "🔍 Extract Message",
                use_container_width=True,
                type="primary",
                disabled=not image_file
            )
            
            if decode_btn:
                _perform_decoding(
                    image_file, 
                    decode_method, 
                    use_encryption, 
                    decryption_password,
                    use_ecc_recovery=ecc_config.get('use_ecc_recovery', False),
                    ecc_strength=ecc_config.get('ecc_strength', 32)
                )
    
    with tab_results:
        if "decode_result" in st.session_state and st.session_state.get('decode_result', {}).get('success'):
            _display_decode_results()
        else:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 3rem;">
                    <p style="font-size: 3rem;">📩</p>
                    <p style="color: #8B949E;">No decoded messages yet</p>
                    <p style="color: #6E7681; font-size: 0.9rem;">Decode an image to see results here</p>
                </div>
            """, unsafe_allow_html=True)
    
    with tab_help:
        _show_decode_help()


def _perform_decoding(image_file, decode_method, use_encryption, decryption_password,
                     use_ecc_recovery=False, ecc_strength=32):
    """Perform decoding with optional ECC recovery."""
    try:
        progress = st.progress(0, text="Loading image...")
        
        image = Image.open(image_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        progress.progress(30, text=f"Decoding with {decode_method}...")
        
        # Create progress callback for DCT/DWT decoding
        def update_decoding_progress(fraction):
            """Update progress bar during decoding (0.0 to 1.0)."""
            # Scale from 30-70% for the actual decoding phase
            current_progress = 30 + int(fraction * 40)
            progress.progress(current_progress)
        
        decoded_message = ""
        
        # Decode using the selected method
        if decode_method == "LSB":
            decoded_message = lsb_decode(image)
        elif decode_method == "Hybrid DCT":
            decoded_message = dct_decode(image, update_progress=update_decoding_progress)
        elif decode_method == "Hybrid DWT":
            decoded_message = dwt_decode(image, update_progress=update_decoding_progress)
        
        progress.progress(70, text="Validating message...")
        
        if not decoded_message or not decoded_message.strip():
            progress.empty()
            show_error(
                f"No hidden message found using **{decode_method}** method.\n\n"
                "**Possible causes:**\n"
                "- Wrong decoding method selected\n"
                "- Image was not encoded with this tool\n"
                "- Image was compressed or modified after encoding\n\n"
                "💡 **Tip:** Try a different method or enable ECC recovery."
            )
            return
        
        progress.progress(85, text="Processing recovery...")
        
        # Attempt ECC recovery if enabled
        if use_ecc_recovery:
            try:
                from stegotool.modules.module6_redundancy.ui_section import decode_message_with_ecc_recovery
                
                recovered_msg, status = decode_message_with_ecc_recovery(
                    decoded_message,
                    use_ecc_recovery=True,
                    nsym=ecc_strength,
                    use_encryption=use_encryption,
                    decryption_password=decryption_password
                )
                decoded_message = recovered_msg
                
                if status == 'ecc_recovered':
                    show_info(f"✅ ECC recovery successful! (~{ecc_strength//2} byte errors corrected)")
            
            except ImportError:
                logger.warning("ECC recovery module not available")
            except ValueError as e:
                # Fall back to normal decryption
                logger.warning(f"ECC recovery failed, trying normal decryption: {e}")
                if use_encryption and decryption_password:
                    try:
                        decoded_message = decrypt_message(decoded_message, decryption_password)
                    except Exception as decrypt_err:
                        progress.empty()
                        show_error(f"Decryption failed: {str(decrypt_err)}")
                        return
        else:
            # Normal decryption without ECC
            if use_encryption:
                if not decryption_password:
                    progress.empty()
                    show_error("Please enter the decryption password.")
                    return
                try:
                    decoded_message = decrypt_message(decoded_message, decryption_password)
                except Exception as e:
                    progress.empty()
                    show_error(f"Decryption failed. Wrong password? Error: {str(e)}")
                    return
        
        progress.progress(100, text="Done!")
        progress.empty()
        
        # Store results
        st.session_state['decode_result'] = {
            'message': decoded_message,
            'method': decode_method,
            'ecc_recovery_used': use_ecc_recovery,
            'success': True
        }
        
        recovery_info = " (with ECC recovery)" if use_ecc_recovery else ""
        show_success(f"✅ Message extracted successfully using **{decode_method}** method{recovery_info}!")
        
        # Log activity
        try:
            if st.session_state.get('logged_in') and st.session_state.get('user_id'):
                log_activity(
                    st.session_state['user_id'],
                    "decode",
                    f"Decoded using {decode_method}{recovery_info}"
                )
        except Exception:
            pass
    
    except Exception as e:
        show_error(f"Decoding failed: {str(e)}")
        logger.error(f"Decoding error: {e}", exc_info=True)


# ============================================================================
#                           COMPARISON SECTION
# ============================================================================

from src.comparison import show_comparison_section

def show_comparison_section():
    """Display method comparison with professional styling."""
    
    render_section_header("📊", "Method Comparison", "Compare steganography methods side by side")
    
    st.divider()
    
    tab_compare, tab_test, tab_details = st.tabs(["📋 Overview", "🧪 Test", "📖 Details"])
    
    with tab_compare:
        # Comparison table
        st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
        
        comparison_data = pd.DataFrame({
            "Feature": ["Speed", "Capacity", "Security", "JPEG Safe", "Best For"],
            "LSB": ["⚡ Very Fast", "📦 High (~180KB)", "🔓 Low", "❌ No", "Quick encoding"],
            "Hybrid DCT": ["⚡ Fast", "📦 Medium (~60KB)", "🛡️ Medium", "✅ Yes", "JPEG images"],
            "Hybrid DWT": ["⏱️ Moderate", "📦 Lower (~15KB)", "🔐 High", "❌ No", "Max security"]
        })
        
        st.dataframe(comparison_data, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Visual comparison
        st.markdown("### Quick Comparison")
        
        cols = st.columns(3)
        methods = [
            ("LSB", "⚡", "Fastest", "Best capacity, lower security", "#238636"),
            ("Hybrid DCT", "🛡️", "Balanced", "JPEG compatible, good security", "#1F6FEB"),
            ("Hybrid DWT", "🔐", "Most Secure", "Highest security, lower capacity", "#8957E5")
        ]
        
        for col, (name, icon, title, desc, color) in zip(cols, methods):
            with col:
                st.markdown(f"""
                    <div class="feature-card" style="border-top: 3px solid {color};">
                        <div class="feature-icon">{icon}</div>
                        <div class="feature-title">{name}</div>
                        <div class="feature-desc">{title}</div>
                        <p style="font-size: 0.8rem; color: #6E7681; margin-top: 0.5rem;">{desc}</p>
                    </div>
                """, unsafe_allow_html=True)
    
    with tab_test:
        st.markdown("### Test All Methods")
        st.markdown("Upload an image and message to see how each method performs.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            test_image = create_file_uploader(file_type="images", key="compare_test_img")
            
            if test_image:
                img = Image.open(test_image)
                st.image(img, caption="Test Image", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            test_message = st.text_area(
                "Test Message",
                value="This is a test message for comparison.",
                height=100,
                key="compare_test_msg"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        if test_image and test_message:
            if st.button("🔄 Run Comparison", use_container_width=True, type="primary"):
                _run_comparison_test(test_image, test_message)
    
    with tab_details:
        _show_comparison_details()


def _run_comparison_test(image_file, message):
    """Run comparison test on all methods."""
    try:
        with st.spinner("Testing all methods..."):
            original = Image.open(image_file)
            results = {}
            
            progress = st.progress(0)
            
            methods = [
                ("LSB", lsb_encode),
                ("Hybrid DCT", dct_encode),
                ("Hybrid DWT", dwt_encode)
            ]
            
            for i, (name, func) in enumerate(methods):
                try:
                    start = time.time()
                    encoded = func(original, message)
                    elapsed = time.time() - start
                    results[name] = {"image": encoded, "time": elapsed, "success": True}
                except Exception as e:
                    results[name] = {"error": str(e), "success": False}
                
                progress.progress((i + 1) / len(methods))
            
            progress.empty()
            
            # Display results
            st.divider()
            st.markdown("### Results")
            
            cols = st.columns(3)
            for col, (name, result) in zip(cols, results.items()):
                with col:
                    if result["success"]:
                        st.markdown(f'<div class="card card-success">', unsafe_allow_html=True)
                        st.markdown(f"**✅ {name}**")
                        st.image(result["image"], use_container_width=True)
                        st.caption(f"⏱️ {result['time']:.3f}s")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="card card-error">', unsafe_allow_html=True)
                        st.markdown(f"**❌ {name}**")
                        st.error(result["error"][:50])
                        st.markdown('</div>', unsafe_allow_html=True)
            
            show_success("Comparison complete!")
            
    except Exception as e:
        show_error(f"Comparison failed: {str(e)}")


def _show_comparison_details():
    """Show detailed method information."""
    st.markdown("""
        <div class="card">
            <div class="card-header">📖 Technical Details</div>
        </div>
    """, unsafe_allow_html=True)
    
    method_tabs = st.tabs(["LSB", "Hybrid DCT", "Hybrid DWT"])
    
    with method_tabs[0]:
        st.markdown("""
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
        """)
    
    with method_tabs[1]:
        st.markdown("""
        ### Hybrid DCT (Discrete Cosine Transform)
        
        **How it works:**
        - Converts image to YCbCr color space
        - Applies DCT to 8×8 blocks on Y channel
        - Embeds data in AC coefficients
        
        **Pros:**
        - ✅ Survives JPEG compression
        - ✅ More secure than LSB
        - ✅ Good balance of capacity and security
        
        **Cons:**
        - ❌ Lower capacity than LSB
        - ❌ Slightly slower
        - ❌ Can introduce visible artifacts
        
        **Best use case:** When images may be JPEG compressed
        """)
    
    with method_tabs[2]:
        st.markdown("""
        ### Hybrid DWT (Discrete Wavelet Transform)
        
        **How it works:**
        - Applies Haar wavelet transform
        - Embeds data in wavelet coefficients
        - Higher resistance to attacks
        
        **Pros:**
        - ✅ Highest security level
        - ✅ Excellent imperceptibility
        - ✅ Resistant to many attacks
        
        **Cons:**
        - ❌ Lowest capacity
        - ❌ Slower processing
        - ❌ Not JPEG safe
        
        **Best use case:** Maximum security requirements
        """)


# ============================================================================
#                           BATCH PROCESSING SECTION
# ============================================================================

def show_batch_processing_section():
    """Display batch processing with professional styling."""
    
    render_section_header("⚙️", "Batch Processing", "Process multiple images at once")
    
    st.divider()
    
    # Mode selection
    batch_mode = st.radio(
        "Select Operation",
        ["📤 Batch Encode", "📥 Batch Decode"],
        horizontal=True,
        key="batch_mode_select"
    )
    
    st.divider()
    
    if "Encode" in batch_mode:
        _show_batch_encode_section()
    else:
        _show_batch_decode_section()


def _show_batch_encode_section():
    """Show batch encoding interface."""
    tab_setup, tab_results, tab_help = st.tabs(["⚙️ Setup", "📊 Results", "❓ Help"])
    
    with tab_setup:
        # Mode selection
        st.markdown("### Encoding Mode")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="card" style="cursor: pointer;">
                    <h4>🔄 Basic Mode</h4>
                    <p style="color: #8B949E;">Same message in ALL images</p>
                    <p style="font-size: 0.85rem;">Each image can be decoded independently</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="card" style="cursor: pointer;">
                    <h4>📦 Advanced Mode</h4>
                    <p style="color: #8B949E;">Split message across images</p>
                    <p style="font-size: 0.85rem;">ALL images required to decode</p>
                </div>
            """, unsafe_allow_html=True)
        
        encoding_mode = st.radio(
            "Choose mode:",
            ["🔄 Basic Mode", "📦 Advanced Mode"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        is_advanced = "Advanced" in encoding_mode
        
        if is_advanced:
            show_warning("Advanced Mode: Message will be split. ALL images needed for decoding!")
        
        st.divider()
        
        # File upload
        render_step(1, "Upload Images")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        upload_type, uploaded_files = create_batch_upload_section()
        
        file_count = 0
        if uploaded_files:
            if isinstance(uploaded_files, list):
                file_count = len(uploaded_files)
            else:
                file_count = 1
            
            st.success(f"✅ {file_count} file(s) selected")
            
            if is_advanced and file_count < 2:
                show_error("Advanced Mode requires at least 2 images")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Settings
        render_step(2, "Configure Encoding")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            method, message, use_encryption, encryption_password = create_batch_options_section()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("**📋 Summary**")
            st.write(f"• Mode: {'Advanced' if is_advanced else 'Basic'}")
            st.write(f"• Method: {method}")
            st.write(f"• Encrypted: {'Yes' if use_encryption else 'No'}")
            st.write(f"• Images: {file_count}")
            if message:
                st.write(f"• Message: {len(message)} chars")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Process button
        if st.button("▶️ Start Batch Encoding", use_container_width=True, type="primary"):
            if not uploaded_files or not message:
                show_error("Please upload images and enter a message")
            elif is_advanced:
                _perform_advanced_batch_encode(uploaded_files, upload_type, message, method, 
                                               use_encryption, encryption_password, file_count)
            else:
                _perform_basic_batch_encode(uploaded_files, message, method, 
                                           use_encryption, encryption_password)
    
    with tab_results:
        if "batch_encode_results" in st.session_state:
            st.markdown("### Batch Results")
            results = st.session_state.batch_encode_results
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info("📊 Results will appear here after batch encoding")
    
    with tab_help:
        st.markdown("""
        ### Batch Encoding Help
        
        **Basic Mode:**
        - Same message embedded in every image
        - Each image can be decoded on its own
        - Good for: Redundancy, multiple recipients
        
        **Advanced Mode:**
        - Message split into packets
        - One packet per image
        - ALL images needed to reconstruct
        - Good for: Maximum security
        """)


def _show_batch_decode_section():
    """Show batch decoding interface."""
    tab_setup, tab_results, tab_help = st.tabs(["⚙️ Setup", "📩 Results", "❓ Help"])
    
    with tab_setup:
        st.markdown("### Auto-Detection")
        st.info("The system automatically detects if images contain Basic or Advanced mode encoding.")
        
        st.divider()
        
        render_step(1, "Upload Encoded Images")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        upload_type, uploaded_files = create_batch_upload_section()
        
        if uploaded_files:
            if isinstance(uploaded_files, list):
                st.success(f"✅ {len(uploaded_files)} files selected")
            else:
                st.success("✅ ZIP file uploaded")
        st.markdown('</div>', unsafe_allow_html=True)
        
        render_step(2, "Decryption (Optional)")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        use_encryption = st.checkbox("🔐 Messages are encrypted", key="batch_dec_encrypt")
        decryption_password = None
        if use_encryption:
            decryption_password = st.text_input("Password", type="password", key="batch_dec_pass")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("▶️ Start Batch Decoding", use_container_width=True, type="primary"):
            if uploaded_files:
                _perform_batch_decode(uploaded_files, upload_type, use_encryption, decryption_password)
            else:
                show_error("Please upload files first")
    
    with tab_results:
        if "batch_decode_results" in st.session_state:
            st.markdown("### Decoded Messages")
            # Display results
        else:
            st.info("📩 Decoded messages will appear here")
    
    with tab_help:
        st.markdown("""
        ### Batch Decoding Help
        
        The decoder automatically handles:
        - **Basic Mode:** Shows each message separately
        - **Advanced Mode:** Reconstructs the full message
        
        **Tips:**
        - Upload ALL images for Advanced mode
        - Use correct decryption password
        - Original PNG files work best
        """)


def _perform_basic_batch_encode(uploaded_files, message, method, use_encryption, encryption_password):
    """Perform basic batch encoding (same message in all images)."""
    try:
        results = []
        progress = st.progress(0)
        
        for i, image_file in enumerate(uploaded_files):
            status_text = f"Processing {i+1}/{len(uploaded_files)}..."
            st.write(status_text)
            
            try:
                original_image = Image.open(image_file)
                message_to_embed = message
                
                if use_encryption and encryption_password:
                    message_to_embed = encrypt_message(message, encryption_password)
                
                if method == "LSB":
                    encoded_image = lsb_encode(original_image, message_to_embed)
                elif method == "Hybrid DCT":
                    encoded_image = dct_encode(original_image, message_to_embed)
                elif method == "Hybrid DWT":
                    encoded_image = dwt_encode(original_image, message_to_embed)
                else:
                    encoded_image = lsb_encode(original_image, message_to_embed)
                
                results.append({
                    "filename": image_file.name,
                    "status": "✅ Success",
                    "method": method
                })
                
            except Exception as e:
                results.append({
                    "filename": image_file.name,
                    "status": f"❌ Error: {str(e)[:30]}",
                    "method": method
                })
            
            progress.progress((i + 1) / len(uploaded_files))
        
        st.session_state.batch_encode_results = results
        show_success(f"Batch encoding complete! {len([r for r in results if '✅' in r['status']])}/{len(uploaded_files)} successful")
        
    except Exception as e:
        show_error(f"Batch encoding failed: {str(e)}")


def _perform_advanced_batch_encode(uploaded_files, upload_type, message, method, 
                                    use_encryption, encryption_password, file_count):
    """Perform advanced batch encoding (message split across images)."""
    try:
        results = []
        progress = st.progress(0)
        
        message_to_split = message
        if use_encryption and encryption_password:
            message_to_split = encrypt_message(message, encryption_password)
        
        # Split message into chunks
        chunk_size = len(message_to_split) // file_count
        message_chunks = [
            message_to_split[i*chunk_size:(i+1)*chunk_size] 
            for i in range(file_count)
        ]
        
        for i, (image_file, chunk) in enumerate(zip(uploaded_files, message_chunks)):
            status_text = f"Processing {i+1}/{len(uploaded_files)}..."
            st.write(status_text)
            
            try:
                original_image = Image.open(image_file)
                
                if method == "LSB":
                    encoded_image = lsb_encode(original_image, chunk)
                elif method == "Hybrid DCT":
                    encoded_image = dct_encode(original_image, chunk)
                elif method == "Hybrid DWT":
                    encoded_image = dwt_encode(original_image, chunk)
                else:
                    encoded_image = lsb_encode(original_image, chunk)
                
                results.append({
                    "filename": image_file.name,
                    "status": "✅ Success",
                    "method": method,
                    "chunk": i+1
                })
                
            except Exception as e:
                results.append({
                    "filename": image_file.name,
                    "status": f"❌ Error: {str(e)[:30]}",
                    "method": method,
                    "chunk": i+1
                })
            
            progress.progress((i + 1) / len(uploaded_files))
        
        st.session_state.batch_encode_results = results
        show_success(f"Advanced batch encoding complete! {len([r for r in results if '✅' in r['status']])}/{len(uploaded_files)} successful")
        
    except Exception as e:
        show_error(f"Advanced batch encoding failed: {str(e)}")


def _perform_batch_decode(uploaded_files, upload_type, use_encryption, decryption_password):
    """Perform batch decoding."""
    try:
        results = []
        progress = st.progress(0)
        
        for i, image_file in enumerate(uploaded_files):
            st.write(f"Processing {i+1}/{len(uploaded_files)}...")
            
            try:
                image = Image.open(image_file)
                decoded_message = None
                method_used = None
                
                methods = [
                    ("LSB", lsb_decode),
                    ("Hybrid DCT", dct_decode),
                    ("Hybrid DWT", dwt_decode)
                ]
                
                for method_name, method_func in methods:
                    try:
                        extracted = method_func(image)
                        if extracted and is_valid_message(extracted):
                            decoded_message = extracted
                            method_used = method_name
                            break
                    except:
                        continue
                
                if decoded_message and method_used:
                    if use_encryption and decryption_password:
                        try:
                            decoded_message = decrypt_message(decoded_message, decryption_password)
                        except:
                            decoded_message = "[Decryption failed]"
                    
                    results.append({
                        "filename": image_file.name,
                        "status": "✅ Found",
                        "method": method_used,
                        "message": decoded_message[:50] + ("..." if len(decoded_message) > 50 else "")
                    })
                else:
                    results.append({
                        "filename": image_file.name,
                        "status": "❌ No message found",
                        "method": "N/A",
                        "message": ""
                    })
                
            except Exception as e:
                results.append({
                    "filename": image_file.name,
                    "status": f"❌ Error",
                    "method": "N/A",
                    "message": str(e)[:30]
                })
            
            progress.progress((i + 1) / len(uploaded_files))
        
        st.session_state.batch_decode_results = results
        show_success(f"Batch decoding complete!")
        
    except Exception as e:
        show_error(f"Batch decoding failed: {str(e)}")


# ============================================================================
#                    MODULE 3: PIXEL SELECTOR
# ============================================================================

def show_pixel_selector_section():
    """Display pixel selector with professional styling."""
    
    render_section_header("🎯", "Intelligent Pixel Selection", "Find optimal pixels for message hiding")
    
    st.divider()
    
    tab_analyze, tab_results, tab_help = st.tabs(["🔬 Analyze", "📊 Results", "❓ Help"])
    
    with tab_analyze:
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            render_step(1, "Upload Image")
            
            st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
            image_file = create_file_uploader(file_type="images", key="pixel_img")
            
            if image_file:
                image = Image.open(image_file)
                st.image(image, caption="Image to Analyze", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            render_step(2, "Configure Analysis")
            
            st.markdown('<div class="card animate-fade-in stagger-1">', unsafe_allow_html=True)
            
            payload_bits = st.number_input(
                "Payload size (bits)",
                min_value=8, max_value=100000, value=256, step=8,
                help="How many bits to hide"
            )
            
            patch_size = st.slider(
                "Analysis detail",
                min_value=3, max_value=9, value=5, step=2,
                help="Lower = more detailed"
            )
            
            lsb_bits = st.selectbox(
                "Bits per channel",
                [1, 2, 4, 8], index=0,
                help="1 = safest"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if image_file:
                if st.button("🔬 Analyze Pixels", use_container_width=True, type="primary"):
                    _run_pixel_analysis(image_file, payload_bits, patch_size, lsb_bits)
    
    with tab_results:
        if "pixel_analysis_results" in st.session_state:
            _display_pixel_results()
        else:
            st.info("📊 Analysis results will appear here")
    
    with tab_help:
        st.markdown("""
        ### How It Works
        
        The pixel selector analyzes your image to find the best pixels for hiding data:
        
        1. **Texture Analysis** - High-texture areas hide data better
        2. **Edge Detection** - Pixels near edges are less noticeable when changed
        3. **Entropy Calculation** - Higher entropy = better hiding spots
        
        ### Best Practices
        
        - Use images with lots of detail/texture
        - Avoid flat color areas
        - Natural photos work better than graphics
        """)


def _run_pixel_analysis(image_file, payload_bits, patch_size, lsb_bits):
    """Run pixel analysis with timeout protection and progress feedback."""
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
    import threading
    
    try:
        # Convert image first (before threading)
        image = Image.open(image_file)
        arr = np.array(image.convert("RGB"))
        h, w, _ = arr.shape
        
        # Create progress placeholder
        progress_placeholder = st.empty()
        
        def analyze_pixels():
            """Worker function for threaded analysis."""
            from stegotool.modules.module3_pixel_selector.selector_baseline import select_pixels
            return select_pixels(
                arr, payload_bits=payload_bits,
                patch_size=patch_size, lsb_bits=lsb_bits, seed=0
            )
        
        # Execute with timeout (30 seconds)
        with ThreadPoolExecutor(max_workers=1) as executor:
            with progress_placeholder.container():
                st.info("🔬 Analyzing image quality and texture patterns...")
                progress_bar = st.progress(0, text="Scanning pixels...")
                
                # Start analysis in background
                future = executor.submit(analyze_pixels)
                
                # Monitor progress
                max_wait = 30
                for i in range(max_wait * 4):  # Check every 0.25 seconds for 30 seconds
                    try:
                        # Check if done
                        if future.done():
                            selected_coords = future.result(timeout=0.1)
                            progress_bar.progress(100, text="Analysis complete!")
                            break
                        
                        # Update progress bar (even if stuck, gives user feedback)
                        progress = min(100, i * 100 // (max_wait * 4))
                        progress_bar.progress(progress, text=f"Processing... {progress}%")
                        
                        # Sleep briefly
                        import time
                        time.sleep(0.25)
                        
                    except Exception:
                        continue
                else:
                    # Timeout occurred
                    future.cancel()
                    raise TimeoutError("Pixel analysis took too long (>30s). Falling back to random selection.")
        
        # Store results
        st.session_state.pixel_analysis_results = {
            "coords": selected_coords,
            "image": arr,
            "width": w,
            "height": h
        }
        
        show_success("✅ Analysis complete! Check the Results tab.")
        
    except TimeoutError as e:
        # Fallback: use random selection
        st.warning(f"⏱️ {str(e)}")
        st.info("Using random pixel selection as fallback...")
        
        # Fallback random selection
        capacity_per_pixel = 3 * lsb_bits
        pixels_needed = int(np.ceil(payload_bits / capacity_per_pixel))
        total_pixels = h * w
        
        # Randomly select pixels
        np.random.seed(0)
        if pixels_needed < total_pixels:
            flat_indices = np.random.choice(total_pixels, pixels_needed, replace=False)
            selected_coords = [(int(idx % w), int(idx // w)) for idx in flat_indices]
        else:
            selected_coords = [(int(x), int(y)) for y in range(h) for x in range(w)]
        
        st.session_state.pixel_analysis_results = {
            "coords": selected_coords,
            "image": arr,
            "width": w,
            "height": h
        }
        
        show_warning("Fallback random selection applied. Results may be suboptimal.")
        
    except FuturesTimeoutError:
        show_error("Analysis timed out after 30 seconds.")
    except Exception as e:
        show_error(f"Analysis error: {str(e)}")


def _display_pixel_results():
    """Display pixel analysis results."""
    results = st.session_state.pixel_analysis_results
    coords = results["coords"]
    arr = results["image"]
    w, h = results["width"], results["height"]
    
    # Metrics
    cols = st.columns(4)
    with cols[0]:
        st.metric("Image Size", f"{w}×{h}")
    with cols[1]:
        st.metric("Total Pixels", f"{w*h:,}")
    with cols[2]:
        st.metric("Best Pixels", len(coords))
    with cols[3]:
        coverage = (len(coords) / (w * h)) * 100
        st.metric("Coverage", f"{coverage:.1f}%")
    
    st.divider()
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Original Image**")
        st.image(arr, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card card-success">', unsafe_allow_html=True)
        st.markdown("**Best Pixels (Red)**")
        overlay = arr.copy()
        for x, y in coords[:200]:
            if 0 <= x < w and 0 <= y < h:
                overlay[y, x] = [255, 0, 0]
        st.image(overlay, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
#                    MODULE 6: ERROR CORRECTION
# ============================================================================

def show_redundancy_section():
    """Display error correction with professional styling."""
    # Import from the proper module
    try:
        from stegotool.modules.module6_redundancy.ui_section import show_redundancy_section as show_ecc_ui
        show_ecc_ui()
    except ImportError:
        # Fallback if module not available
        st.error("Error Correction module not available. Please install required dependencies.")
        logger.error("Failed to import ECC UI section")



