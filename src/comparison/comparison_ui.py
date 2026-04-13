"""
comparison_ui.py
================
Main UI components for the comparison section.

Provides the comparison section interface with tabs for overview, testing, and details.
"""

import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import time
import logging

from src.stego.lsb_steganography import encode_image as lsb_encode
from src.stego.dct_steganography import encode_dct as dct_encode
from src.stego.dwt_steganography import encode_dwt as dwt_encode
from src.ui.reusable_components import create_file_uploader, show_error, show_success
from .comparison_logic import run_comparison_test, get_method_details

logger = logging.getLogger(__name__)

def show_comparison_section():
    """Display method comparison with professional styling."""
    
    # Header
    st.markdown("""
        <div class="animate-fade-in-down">
            <h2>📊 Method Comparison</h2>
            <p style="color: #8B949E; margin-bottom: 1rem;">Compare steganography methods side by side</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main tabs
    tab_compare, tab_test, tab_details = st.tabs(["📋 Overview", "🧪 Test", "📖 Details"])
    
    with tab_compare:
        _show_comparison_overview()
    
    with tab_test:
        _show_comparison_test_section()
    
    with tab_details:
        _show_comparison_details()


def _show_comparison_overview():
    """Display comparison overview table and cards."""
    st.markdown('<div class="card animate-fade-in">', unsafe_allow_html=True)
    
    # Comparison data
    comparison_data = pd.DataFrame({
        "Feature": ["Speed", "Capacity", "Security", "JPEG Safe", "Best For"],
        "LSB": ["⚡ Very Fast", "📦 High (~180KB)", "🔓 Low", "❌ No", "Quick encoding"],
        "Hybrid DCT": ["⚡ Fast", "📦 Medium (~60KB)", "🛡️ Medium", "✅ Yes", "JPEG images"],
        "Hybrid DWT": ["⏱️ Moderate", "📦 Lower (~15KB)", "🔐 High", "❌ No", "Max security"]
    })
    
    st.dataframe(comparison_data, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Visual comparison cards
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


def _show_comparison_test_section():
    """Display comparison testing interface."""
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
            _run_and_display_comparison(test_image, test_message)


def _run_and_display_comparison(image_file, message):
    """Run comparison and display results."""
    try:
        results = run_comparison_test(image_file, message)
        
        # Display results
        st.divider()
        st.markdown("### Results")
        
        cols = st.columns(3)
        for col, (method_name, result) in zip(cols, results.items()):
            with col:
                if result["success"]:
                    st.markdown(f'<div class="card card-success">', unsafe_allow_html=True)
                    st.markdown(f"**✅ {method_name}**")
                    st.image(result["image"], use_container_width=True)
                    st.caption(f"⏱️ {result['time']:.3f}s | Size: {result['size_kb']:.1f}KB")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="card card-error">', unsafe_allow_html=True)
                    st.markdown(f"**❌ {method_name}**")
                    st.error(result["error"][:100])
                    st.markdown('</div>', unsafe_allow_html=True)
        
        show_success("Comparison complete! ✨")
        
    except Exception as e:
        logger.error(f"Comparison failed: {str(e)}")
        show_error(f"Comparison failed: {str(e)}")


def _show_comparison_details():
    """Show detailed method information."""
    st.markdown("""
        <div class="card">
            <div class="card-header">📖 Technical Details</div>
        </div>
    """, unsafe_allow_html=True)
    
    method_tabs = st.tabs(["LSB", "Hybrid DCT", "Hybrid DWT"])
    
    # Get details from logic module
    details = get_method_details()
    
    for tab, method_key in zip(method_tabs, ["LSB", "DCT", "DWT"]):
        with tab:
            st.markdown(details[method_key])