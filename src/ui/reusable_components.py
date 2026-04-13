"""
Reusable UI Components
======================
Contains all reusable Streamlit components to reduce code duplication.
Includes Lottie animations, caching, and session state management.
"""

import streamlit as st
from io import BytesIO
from PIL import Image
from datetime import datetime
import logging
import requests

from .config_dict import (
    FORM_LABELS, FILE_UPLOAD_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES,
    BUTTON_LABELS, METHODS, METHOD_DETAILS, COLUMN_LAYOUTS, METRIC_LABELS,
    VALIDATION, DOWNLOAD_FILENAMES
)

logger = logging.getLogger(__name__)


# ============================================================================
#                           LOTTIE ANIMATIONS
# ============================================================================

@st.cache_data(ttl=3600)
def load_lottie_url(url: str):
    """
    Load Lottie animation from URL with caching.
    
    Args:
        url: URL to Lottie JSON file
    
    Returns:
        dict: Lottie animation data or None if failed
    """
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        logger.error(f"Failed to load Lottie animation: {e}")
        return None


# Predefined Lottie animation URLs
LOTTIE_ANIMATIONS = {
    "loading": "https://assets5.lottiefiles.com/packages/lf20_szlepvdh.json",
    "success": "https://assets4.lottiefiles.com/packages/lf20_jbrw3hcz.json",
    "error": "https://assets1.lottiefiles.com/packages/lf20_qpwbiyxf.json",
    "upload": "https://assets3.lottiefiles.com/packages/lf20_xlmz9xwm.json",
    "security": "https://assets9.lottiefiles.com/packages/lf20_ky24lkyk.json",
    "analysis": "https://assets2.lottiefiles.com/packages/lf20_kq5rGs.json",
    "encoding": "https://assets7.lottiefiles.com/packages/lf20_hzfmxrr7.json",
}


def show_lottie_animation(animation_key: str, height: int = 200, key: str = None):
    """
    Display a Lottie animation.
    
    Args:
        animation_key: Key from LOTTIE_ANIMATIONS dict
        height: Animation height in pixels
        key: Unique key for the animation
    """
    try:
        from streamlit_lottie import st_lottie
        
        url = LOTTIE_ANIMATIONS.get(animation_key)
        if url:
            animation = load_lottie_url(url)
            if animation:
                st_lottie(animation, height=height, key=key)
    except ImportError:
        # Fallback if streamlit-lottie not installed
        st.info(f"🎬 Animation: {animation_key}")
    except Exception as e:
        logger.error(f"Lottie animation error: {e}")


# ============================================================================
#                           SESSION STATE HELPERS
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "logged_in": False,
        "username": None,
        "user_id": None,
        "current_page": "🔐 Encode",
        "processed_images": {},
        "cached_results": {},
        "last_encoded_image": None,
        "last_decoded_message": None,
        "detection_results": None,
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def store_processed_image(key: str, image: Image.Image):
    """Store a processed image in session state."""
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = {}
    st.session_state.processed_images[key] = image


def get_processed_image(key: str) -> Image.Image:
    """Retrieve a processed image from session state."""
    return st.session_state.get("processed_images", {}).get(key)


def cache_result(key: str, result):
    """Cache a result in session state."""
    if "cached_results" not in st.session_state:
        st.session_state.cached_results = {}
    st.session_state.cached_results[key] = {
        "result": result,
        "timestamp": datetime.now()
    }


def get_cached_result(key: str, max_age_seconds: int = 300):
    """Get a cached result if not expired."""
    cached = st.session_state.get("cached_results", {}).get(key)
    if cached:
        age = (datetime.now() - cached["timestamp"]).total_seconds()
        if age < max_age_seconds:
            return cached["result"]
    return None


# ============================================================================
#                           FORM COMPONENTS
# ============================================================================

def create_text_input(label, placeholder="", password=False, key=None, max_chars=None):
    """Create a styled text input field."""
    input_type = "password" if password else "default"
    return st.text_input(
        label=label,
        placeholder=placeholder,
        type=input_type,
        key=key
    )


def create_text_area(label, max_chars=5000, key=None, placeholder="", height=200):
    """Create a styled text area."""
    return st.text_area(
        label=label,
        max_chars=max_chars,
        height=height,
        key=key,
        placeholder=placeholder
    )


def create_file_uploader(file_type="images", multiple=False, key=None):
    """Create a file uploader with predefined config."""
    config = FILE_UPLOAD_CONFIG.get(file_type, FILE_UPLOAD_CONFIG["images"])
    
    return st.file_uploader(
        label=config["label"],
        type=config["types"],
        accept_multiple_files=multiple,
        key=key
    )


def create_method_selector(key=None, index=0, disabled=False):
    """Create a method selection dropdown."""
    return st.selectbox(
        label="Steganography Method",
        options=METHODS,
        index=index,
        key=key,
        disabled=disabled
    )


def create_checkbox(label, key=None, value=False):
    """Create a styled checkbox."""
    return st.checkbox(label=label, key=key, value=value)


# ============================================================================
#                           MESSAGE COMPONENTS
# ============================================================================

def show_error(message, icon="❌"):
    """Display error message with animation."""
    st.error(f"{icon} {message}")


def show_success(message, icon="✅"):
    """Display success message with animation."""
    st.success(f"{icon} {message}")


def show_warning(message, icon="⚠️"):
    """Display warning message."""
    st.warning(f"{icon} {message}")


def show_info(message, icon="ℹ️"):
    """Display info message."""
    st.info(f"{icon} {message}")


def validate_credentials(username, password, min_length=VALIDATION["min_password_length"]):
    """Validate login credentials."""
    if not username or not password:
        return False, ERROR_MESSAGES["empty_fields"]
    if len(password) < min_length:
        return False, ERROR_MESSAGES["min_password_length"]
    return True, ""


def validate_registration(username, password, confirm_password):
    """Validate registration form."""
    if not username or not password or not confirm_password:
        return False, ERROR_MESSAGES["fields_required"]
    if password != confirm_password:
        return False, ERROR_MESSAGES["passwords_mismatch"]
    if len(password) < VALIDATION["min_password_length"]:
        return False, ERROR_MESSAGES["min_password_length"]
    return True, ""


# ============================================================================
#                           LAYOUT COMPONENTS
# ============================================================================

def create_two_column_layout(left_title=None, right_title=None):
    """Create a two-column layout."""
    col1, col2 = st.columns(2)
    
    if left_title:
        with col1:
            st.markdown(f"#### {left_title}")
    if right_title:
        with col2:
            st.markdown(f"#### {right_title}")
    
    return col1, col2


def create_three_column_layout(titles=None):
    """Create a three-column layout."""
    cols = st.columns(3)
    
    if titles:
        for col, title in zip(cols, titles):
            with col:
                st.markdown(f"#### {title}")
    
    return cols


def create_metric_cards(metrics):
    """Create metric cards in a row."""
    cols = st.columns(len(metrics))
    
    for i, (col, (label, value)) in enumerate(zip(cols, metrics.items())):
        with col:
            animation_class = f"animate-fade-in stagger-{i+1}"
            st.markdown(f"""
                <div class="metric-card {animation_class}">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
            """, unsafe_allow_html=True)


# ============================================================================
#                           IMAGE COMPONENTS
# ============================================================================

def display_image_comparison(original_img, encoded_img, method=""):
    """Display side-by-side image comparison with styled containers."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="image-compare-container">
                <div class="image-label">📷 Original Image</div>
            </div>
        """, unsafe_allow_html=True)
        st.image(original_img, use_container_width=True)
        st.caption(f"Size: {original_img.size[0]}×{original_img.size[1]}")
    
    with col2:
        st.markdown("""
            <div class="image-compare-container">
                <div class="image-label">🔐 Encoded Image</div>
            </div>
        """, unsafe_allow_html=True)
        st.image(encoded_img, use_container_width=True)
        
        # Download button
        buf = BytesIO()
        encoded_img.save(buf, format="PNG")
        buf.seek(0)
        
        st.download_button(
            label="⬇️ Download Encoded Image",
            data=buf.getvalue(),
            file_name=DOWNLOAD_FILENAMES["encoded_image"].format(
                method=method.replace(' ', '_').lower()
            ),
            mime="image/png",
            use_container_width=True
        )


def display_encoded_image(img):
    """Display encoded image."""
    st.image(img, use_container_width=True)


def display_decoded_message(message, height=150):
    """Display decoded message in a styled container."""
    st.markdown("""
        <div class="card card-success">
            <div class="card-header">🔓 Decoded Message</div>
        </div>
    """, unsafe_allow_html=True)
    st.text_area(
        "Message Content",
        value=message,
        height=height,
        disabled=True,
        label_visibility="collapsed"
    )


# ============================================================================
#                           BUTTON COMPONENTS
# ============================================================================

def create_primary_button(label, key=None, use_full_width=True):
    """Create a primary action button."""
    return st.button(
        label=label,
        key=key,
        use_container_width=use_full_width,
        type="primary"
    )


def create_download_button(label, data, filename, mime_type="application/octet-stream", key=None):
    """Create a download button."""
    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type,
        use_container_width=True,
        key=key
    )


def create_tab_section(tab_names, tab_contents=None):
    """Create tabs with optional content."""
    tabs = st.tabs(tab_names)
    
    if tab_contents:
        for tab, content in zip(tabs, tab_contents):
            with tab:
                content()
    
    return tabs


# ============================================================================
#                           PROGRESS COMPONENTS
# ============================================================================

def show_processing_spinner(message="Processing..."):
    """Create a spinner context manager."""
    return st.spinner(message)


def show_progress_bar(progress, text=""):
    """Display a progress bar with text."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(progress)
    with col2:
        st.caption(text)


def display_progress_indicator(current, total, message="Processing..."):
    """Display progress with status message."""
    progress = current / total if total > 0 else 0
    progress_bar = st.progress(progress)
    status_text = st.empty()
    status_text.text(f"{message} ({current}/{total})")
    return progress_bar, status_text


# ============================================================================
#                           SUMMARY/STATS COMPONENTS
# ============================================================================

def display_results_summary(results_dict, animate=True):
    """Display a summary of results in metric cards."""
    cols = st.columns(len(results_dict))
    
    for i, (col, (label, value)) in enumerate(zip(cols, results_dict.items())):
        with col:
            animation_class = f"animate-fade-in stagger-{i+1}" if animate else ""
            st.markdown(f"""
                <div class="metric-card {animation_class}">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
            """, unsafe_allow_html=True)


# ============================================================================
#                           BATCH PROCESSING COMPONENTS
# ============================================================================

def create_batch_upload_section():
    """Create upload method selector and file uploader."""
    upload_type = st.radio(
        "Upload Method",
        options=["📦 ZIP File", "🖼️ Multiple Images"],
        horizontal=True
    )
    
    if "ZIP" in upload_type:
        uploaded_files = create_file_uploader(file_type="zip", key="batch_upload_zip")
    else:
        uploaded_files = create_file_uploader(
            file_type="multiple_images",
            multiple=True,
            key="batch_upload_images"
        )
    
    return upload_type, uploaded_files


def create_batch_options_section(include_encryption=True):
    """Create encoding/decoding options."""
    method = create_method_selector()
    message = create_text_area(
        label=FORM_LABELS["message"]["label"],
        max_chars=FORM_LABELS["message"]["max_chars"]
    )
    
    use_encryption = create_checkbox("🔒 Encrypt message before embedding")
    encryption_password = None
    
    if use_encryption:
        encryption_password = create_text_input(
            label=FORM_LABELS["encryption_password"]["label"],
            password=True
        )
    
    return method, message, use_encryption, encryption_password


def display_batch_results(results_summary):
    """Display batch processing results."""
    metrics = {
        "Total Images": results_summary.get("total", 0),
        "Successful": results_summary.get("success", 0),
        "Failed": results_summary.get("failed", 0)
    }
    display_results_summary(metrics)


def display_detailed_results(results, result_type="encode"):
    """Display detailed results for batch operations."""
    with st.expander("📋 View Detailed Results", expanded=False):
        for result in results:
            if result.get('status', '').lower().startswith('success'):
                st.success(
                    f"✅ {result['filename']}: "
                    f"{result.get('encoding_time', result.get('message_length', 'OK'))}"
                )
            else:
                st.error(f"❌ {result['filename']}: {result.get('status', 'Unknown error')}")


# ============================================================================
#                           UTILITY COMPONENTS
# ============================================================================

def show_divider():
    """Show a styled divider."""
    st.markdown("<hr>", unsafe_allow_html=True)


def show_method_details():
    """Display detailed information about all methods in expander."""
    with st.expander("📖 Method Details", expanded=False):
        tabs = st.tabs(METHODS)
        
        for tab, method in zip(tabs, METHODS):
            with tab:
                details = METHOD_DETAILS[method]
                st.markdown(details["description"])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Capacity", details["capacity"])
                with col2:
                    st.metric("Speed", details["speed"])
                with col3:
                    st.metric("Security", details["security"])


def create_comparison_table(table_data):
    """Display comparison table."""
    st.dataframe(table_data, use_container_width=True, hide_index=True)


def show_activity_search(dataframe):
    """Show searchable activity log."""
    with st.expander("🔍 Search Activity Log"):
        search_term = st.text_input("Search for action or details", key="activity_search")
        
        if search_term and not dataframe.empty:
            filtered_df = dataframe[
                dataframe['Action'].str.contains(search_term, case=False, na=False) |
                dataframe['Details'].str.contains(search_term, case=False, na=False)
            ]
            st.dataframe(filtered_df, use_container_width=True)
        elif search_term:
            show_info("No matching activities found")


def create_sections_menu(sections):
    """Create a menu of sections."""
    return st.radio("Select Section", options=sections, horizontal=True)


def render_step(step_number, title):
    """Render a step header with number."""
    st.markdown(f"""
        <div class="step-indicator animate-fade-in">
            <div class="step-number">{step_number}</div>
            <div class="step-title">{title}</div>
        </div>
    """, unsafe_allow_html=True)