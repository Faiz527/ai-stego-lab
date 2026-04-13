"""
Streamlit Main Application
============================
Image Steganography Web Application.
Main entry point - orchestrates all UI components.
"""
from pathlib import Path
import sys
import logging

# Configure base path
BASE_PATH = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_PATH))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import streamlit as st
from src.db.db_utils import (
    initialize_database,
    add_user,
    verify_user,
    log_activity
)
from src.ui.ui_components import (
    show_encode_section,
    show_decode_section,
    show_comparison_section,
    show_auth_section,
    show_batch_processing_section,
    show_pixel_selector_section,
    show_redundancy_section
)
from src.detect_stego import show_steg_detector_section
from src.ui.styles import apply_dark_theme
from src.Watermarking.ui_section import show_watermarking_section

# ============================================================================
#                           PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="ITR - Image Steganography",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_dark_theme()

# ============================================================================
#                           SESSION STATE INITIALIZATION
# ============================================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ============================================================================
#                           DATABASE INITIALIZATION
# ============================================================================

try:
    db_available = initialize_database()
    if db_available:
        logger.info("✅ Database initialized successfully")
    else:
        logger.warning("⚠️ Database not available - some features disabled")
        st.warning("⚠️ Database connection unavailable. Authentication disabled.")
        st.info("Set up PostgreSQL and add credentials to .env (local) or .streamlit/secrets.toml (cloud)")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    st.warning(f"⚠️ Database unavailable: {str(e)[:100]}")
    logger.info("App will run without authentication")

# ============================================================================
#                           NAVIGATION CONFIG
# ============================================================================

NAV_ITEMS = {
    "main": [
        {"icon": "🏠", "label": "Home", "page": "Home"},
        {"icon": "🔐", "label": "Encode", "page": "Encode"},
        {"icon": "🔍", "label": "Decode", "page": "Decode"},
    ],
    "tools": [
        {"icon": "📊", "label": "Comparison", "page": "Comparison"},
        {"icon": "⚙️", "label": "Batch Processing", "page": "Batch"},
    ],
    "advanced": [
        {"icon": "🎯", "label": "Pixel Selector", "page": "Pixel"},
        {"icon": "🛡️", "label": "Error Correction", "page": "ErrorCorrection"},
        {"icon": "💧", "label": "Watermark", "page": "Watermark"},
        {"icon": "🔎", "label": "Detection", "page": "Detection"},
    ]
}

# ============================================================================
#                           SIDEBAR NAVIGATION
# ============================================================================

def render_sidebar():
    """Render application sidebar with grouped navigation."""
    with st.sidebar:
        # App branding
        st.markdown("""
            <div style="text-align: center; padding: 0.5rem 0 0.25rem 0;">
                <h1 style="margin: 0;">🔐 ITR Stego</h1>
            </div>
        """, unsafe_allow_html=True)
        st.caption("Advanced Image Steganography Toolbox")
        
        st.divider()
        
        if st.session_state.logged_in:
            # User info
            initial = st.session_state.username[0].upper() if st.session_state.username else "?"
            st.markdown(f"""
                <div class="sidebar-user-badge">
                    <div class="user-avatar">{initial}</div>
                    <div>
                        <div class="user-name">{st.session_state.username}</div>
                        <div class="user-status">● Online</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Navigation groups
            current = st.session_state.current_page
            
            # Main section
            st.markdown('<p style="color: #484F58; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-bottom: 0.25rem;">Main</p>', unsafe_allow_html=True)
            for item in NAV_ITEMS["main"]:
                _render_nav_button(item, current)
            
            st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
            
            # Tools section
            st.markdown('<p style="color: #484F58; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-bottom: 0.25rem;">Tools</p>', unsafe_allow_html=True)
            for item in NAV_ITEMS["tools"]:
                _render_nav_button(item, current)
            
            st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
            
            # Advanced section
            st.markdown('<p style="color: #484F58; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-bottom: 0.25rem;">Advanced</p>', unsafe_allow_html=True)
            for item in NAV_ITEMS["advanced"]:
                _render_nav_button(item, current)
            
            # Spacer + Logout
            st.divider()
            
            if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.user_id = None
                st.session_state.current_page = "Home"
                st.rerun()
            
            # Version
            st.markdown('<p style="text-align: center; color: #30363D; font-size: 0.7rem; margin-top: 1rem;">v1.0.0</p>', unsafe_allow_html=True)
            
        else:
            st.markdown("""
                <div style="text-align: center; padding: 1rem 0;">
                    <p style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔒</p>
                    <p style="color: #8B949E; font-size: 0.9rem;">Sign in to access<br>all features</p>
                </div>
            """, unsafe_allow_html=True)


def _render_nav_button(item, current_page):
    """Render a single navigation button with active state."""
    is_active = current_page == item["page"]
    label = f"{item['icon']}  {item['label']}"
    
    if is_active:
        # Show active indicator (non-clickable styled element)
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(35, 134, 54, 0.15), rgba(31, 111, 235, 0.08));
                border-left: 3px solid #238636;
                border-radius: 0 10px 10px 0;
                padding: 0.6rem 1rem;
                color: #3FB950;
                font-weight: 600;
                font-size: 0.92rem;
                margin-bottom: 2px;
            ">{label}</div>
        """, unsafe_allow_html=True)
    else:
        if st.button(label, use_container_width=True, key=f"nav_{item['page']}"):
            st.session_state.current_page = item["page"]
            st.rerun()

# ============================================================================
#                           PAGE RENDERING
# ============================================================================

def render_page(page_name):
    """Render page based on current selection."""
    
    if page_name == "Home":
        render_home_page()
    elif page_name == "Encode":
        show_encode_section()
    elif page_name == "Decode":
        show_decode_section()
    elif page_name == "Comparison":
        show_comparison_section()
    elif page_name == "Batch":
        show_batch_processing_section()
    elif page_name == "Pixel":
        show_pixel_selector_section()
    elif page_name == "ErrorCorrection":
        show_redundancy_section()
    elif page_name == "Watermark":
        show_watermarking_section()
    elif page_name == "Detection":
        show_steg_detector_section()


def render_home_page():
    """Render home/dashboard page."""
    
    # Hero section
    st.markdown("""
        <div class="hero-section animate-fade-in">
            <div class="hero-title">🔐 ITR Steganography</div>
            <p class="hero-subtitle">
                Hide secret messages inside images using advanced steganography techniques.
                Secure, fast, and undetectable.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick action cards
    st.markdown("### ⚡ Quick Actions")
    
    cols = st.columns(4)
    
    quick_actions = [
        ("🔐", "Encode", "Hide a message", "Encode"),
        ("🔍", "Decode", "Extract a message", "Decode"),
        ("📊", "Compare", "Test methods", "Comparison"),
        ("🔎", "Detect", "Analyze images", "Detection"),
    ]
    
    for col, (icon, title, desc, page) in zip(cols, quick_actions):
        with col:
            st.markdown(f"""
                <div class="feature-card animate-fade-in-up">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {title}", use_container_width=True, key=f"quick_{page}"):
                st.session_state.current_page = page
                st.rerun()
    
    st.divider()
    
    # Methods overview
    st.markdown("### 🎯 Steganography Methods")
    
    method_cols = st.columns(3)
    
    methods_info = [
        ("⚡", "LSB", "Least Significant Bit", 
         "Fastest method with highest capacity. Modifies pixel values at the bit level.", 
         "#238636", "Fast", "High", "Basic"),
        ("🛡️", "Hybrid DCT", "Discrete Cosine Transform",
         "Frequency domain method. Survives JPEG compression with good security.",
         "#1F6FEB", "Medium", "Medium", "Strong"),
        ("🔐", "Hybrid DWT", "Discrete Wavelet Transform",
         "Wavelet-based method with highest imperceptibility and security.",
         "#8957E5", "Slower", "Lower", "Maximum"),
    ]
    
    for col, (icon, name, full_name, desc, color, speed, capacity, security) in zip(method_cols, methods_info):
        with col:
            st.markdown(f"""
                <div class="feature-card animate-fade-in-up" style="border-top: 3px solid {color}; text-align: left;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                        <span style="font-size: 1.5rem;">{icon}</span>
                        <div>
                            <div class="feature-title" style="margin: 0;">{name}</div>
                            <span style="color: #6E7681; font-size: 0.75rem;">{full_name}</span>
                        </div>
                    </div>
                    <p style="color: #8B949E; font-size: 0.85rem; line-height: 1.5; margin-bottom: 1rem;">{desc}</p>
                    <div style="display: flex; justify-content: space-between; padding-top: 0.75rem; border-top: 1px solid #21262D;">
                        <div style="text-align: center;">
                            <div style="color: #6E7681; font-size: 0.65rem; text-transform: uppercase;">Speed</div>
                            <div style="color: {color}; font-weight: 600; font-size: 0.8rem;">{speed}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="color: #6E7681; font-size: 0.65rem; text-transform: uppercase;">Capacity</div>
                            <div style="color: {color}; font-weight: 600; font-size: 0.8rem;">{capacity}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="color: #6E7681; font-size: 0.65rem; text-transform: uppercase;">Security</div>
                            <div style="color: {color}; font-weight: 600; font-size: 0.8rem;">{security}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Getting started
    st.markdown("### 🚀 Getting Started")
    
    steps = [
        ("1", "Sign in to your account", "Create an account or use existing credentials to access all features"),
        ("2", "Navigate to Encode", "Select the Encode page from the sidebar to begin hiding messages"),
        ("3", "Upload your image", "Choose a PNG image for best results. JPEG may cause data loss"),
        ("4", "Enter your message", "Type the secret message and optionally enable encryption"),
        ("5", "Download & share", "Save the encoded image and share it with your recipient"),
    ]
    
    for num, title, desc in steps:
        st.markdown(f"""
            <div class="getting-started-step animate-fade-in">
                <div class="step-circle">{num}</div>
                <div class="step-content">
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ============================================================================
#                           MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    # Render sidebar
    render_sidebar()
    
    # Show authentication if not logged in
    if not st.session_state.logged_in:
        # Welcome header
        st.markdown("""
            <div class="hero-section animate-fade-in">
                <div class="hero-title">🔐 ITR Steganography</div>
                <p class="hero-subtitle">
                    Sign in to access advanced image steganography tools
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        show_auth_section()
    else:
        # Render current page
        render_page(st.session_state.current_page)
        
        # Footer
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
        st.divider()
        
        footer_cols = st.columns(3)
        with footer_cols[0]:
            st.caption("🔐 End-to-end encrypted")
        with footer_cols[1]:
            st.caption("⚡ Real-time processing")
        with footer_cols[2]:
            st.caption("🎯 Multiple algorithms")


if __name__ == "__main__":
    main()