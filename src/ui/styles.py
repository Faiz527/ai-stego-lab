"""
UI Styles Module
================
Contains all custom CSS styling for dark mode theme.
Professional SaaS-style layout with animations.
"""

import streamlit as st


def apply_dark_theme():
    """
    Apply dark theme styling to the entire application.
    """
    st.markdown("""
<style>
    /* ================================================================
       MAIN CONTAINER & BACKGROUND
       ================================================================ */
    .main { background-color: #0E1117; }
    .stApp { background-color: #0E1117; }
    
    /* ================================================================
       TYPOGRAPHY
       ================================================================ */
    h1, h2, h3, h4, h5, h6 { 
        color: #C9D1D9 !important; 
        font-weight: 700; 
    }
    
    h1 { font-size: 2.2rem !important; letter-spacing: -0.5px; }
    h2 { font-size: 1.6rem !important; }
    h3 { font-size: 1.3rem !important; }
    
    p, span, label { color: #8B949E; }
    
    /* ================================================================
       MAIN HEADER
       ================================================================ */
    .main-header {
        text-align: center;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #238636 0%, #1a6b2b 40%, #1f6feb 100%);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        animation: fadeInDown 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.08) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .main-header h1 {
        font-size: 2.8rem !important;
        margin: 0;
        color: #FFFFFF !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        letter-spacing: -1px;
    }
    
    .main-header p {
        color: #E6EDF3 !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* ================================================================
       SIDEBAR STYLING
       ================================================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1117 0%, #161B22 100%) !important;
        border-right: 1px solid #21262D !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1 {
        background: linear-gradient(135deg, #3FB950, #58A6FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.6rem !important;
        margin-bottom: 0 !important;
    }
    
    /* Sidebar nav buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: #8B949E !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        text-align: left !important;
        box-shadow: none !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 2px !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(35, 134, 54, 0.12) !important;
        color: #3FB950 !important;
        border-color: rgba(35, 134, 54, 0.3) !important;
        transform: translateX(4px) !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:active {
        background: rgba(35, 134, 54, 0.2) !important;
        transform: translateX(4px) !important;
    }
    
    /* Active nav indicator */
    .nav-active {
        background: linear-gradient(135deg, rgba(35, 134, 54, 0.15), rgba(31, 111, 235, 0.1)) !important;
        border-left: 3px solid #238636 !important;
        color: #3FB950 !important;
    }
    
    /* Sidebar divider */
    [data-testid="stSidebar"] hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #30363D, transparent) !important;
        margin: 0.75rem 0 !important;
    }
    
    /* Sidebar user badge */
    .sidebar-user-badge {
        background: linear-gradient(135deg, rgba(35, 134, 54, 0.15), rgba(35, 134, 54, 0.05));
        border: 1px solid rgba(35, 134, 54, 0.3);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-user-badge .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #238636, #1f6feb);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .sidebar-user-badge .user-name {
        color: #C9D1D9;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .sidebar-user-badge .user-status {
        color: #3FB950;
        font-size: 0.75rem;
    }
    
    /* ================================================================
       CARD CONTAINERS
       ================================================================ */
    .card {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #30363D;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1rem;
    }
    
    .card:hover {
        border-color: #484F58;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transform: translateY(-1px);
    }
    
    .card-header {
        font-size: 1.05rem;
        font-weight: 600;
        color: #C9D1D9;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #21262D;
    }
    
    .card-success {
        border-left: 3px solid #238636;
    }
    
    .card-warning {
        border-left: 3px solid #D29922;
    }
    
    .card-error {
        border-left: 3px solid #F85149;
    }
    
    .card-info {
        border-left: 3px solid #1F6FEB;
    }
    
    /* Glass card variant */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(48, 54, 61, 0.5);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }
    
    /* ================================================================
       FEATURE CARDS (Grid Layout)
       ================================================================ */
    .feature-card {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border-radius: 14px;
        padding: 1.75rem 1.25rem;
        border: 1px solid #30363D;
        text-align: center;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #238636, #1f6feb);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: #238636;
        transform: translateY(-6px);
        box-shadow: 0 16px 32px rgba(0, 0, 0, 0.3);
    }
    
    .feature-card:hover::after {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        display: block;
    }
    
    .feature-title {
        color: #C9D1D9;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #8B949E;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    
    /* ================================================================
       HOME HERO SECTION
       ================================================================ */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #0D1117 0%, #161B22 50%, #0D1117 100%);
        border-radius: 20px;
        border: 1px solid #21262D;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at 30% 40%, rgba(35, 134, 54, 0.06) 0%, transparent 50%),
                    radial-gradient(circle at 70% 60%, rgba(31, 111, 235, 0.04) 0%, transparent 50%);
        pointer-events: none;
        animation: heroGlow 8s ease-in-out infinite alternate;
    }
    
    @keyframes heroGlow {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-5%, -5%); }
    }
    
    .hero-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #C9D1D9 0%, #3FB950 50%, #58A6FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        color: #8B949E !important;
        font-size: 1.15rem;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* ================================================================
       METRIC CARDS
       ================================================================ */
    .metric-card {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border-radius: 14px;
        padding: 1.25rem;
        border: 1px solid #30363D;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card:hover {
        border-color: #238636;
        box-shadow: 0 8px 24px rgba(35, 134, 54, 0.15);
        transform: translateY(-3px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #238636;
        margin: 6px 0;
        letter-spacing: -0.5px;
    }
    
    .metric-label {
        color: #8B949E;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    /* ================================================================
       STATUS BADGES
       ================================================================ */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background-color: rgba(35, 134, 54, 0.15);
        color: #3FB950;
        border: 1px solid rgba(35, 134, 54, 0.4);
    }
    
    .badge-warning {
        background-color: rgba(210, 153, 34, 0.15);
        color: #E3B341;
        border: 1px solid rgba(210, 153, 34, 0.4);
    }
    
    .badge-error {
        background-color: rgba(248, 81, 73, 0.15);
        color: #F85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
    }
    
    .badge-info {
        background-color: rgba(31, 111, 235, 0.15);
        color: #58A6FF;
        border: 1px solid rgba(31, 111, 235, 0.4);
    }
    
    /* ================================================================
       BUTTONS - MAIN CANVAS
       ================================================================ */
    .main .stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2EA043 100%) !important;
        color: white !important;
        padding: 0.7rem 1.5rem !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.25) !important;
        letter-spacing: 0.2px;
    }
    
    .main .stButton > button:hover {
        background: linear-gradient(135deg, #2EA043 0%, #3FB950 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(35, 134, 54, 0.35) !important;
    }
    
    .main .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(35, 134, 54, 0.2) !important;
    }
    
    /* Disabled button */
    .main .stButton > button:disabled {
        background: #21262D !important;
        color: #484F58 !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }
    
    /* ================================================================
       TABS
       ================================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #0D1117;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #21262D;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        color: #8B949E !important;
        border: none !important;
        transition: all 0.25s ease !important;
        font-weight: 500 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #C9D1D9 !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #238636 0%, #2EA043 100%) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(35, 134, 54, 0.3) !important;
    }
    
    /* ================================================================
       FORM INPUTS
       ================================================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #0D1117 !important;
        border: 1px solid #30363D !important;
        color: #C9D1D9 !important;
        border-radius: 10px !important;
        transition: all 0.25s ease !important;
        font-size: 0.95rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #238636 !important;
        box-shadow: 0 0 0 3px rgba(35, 134, 54, 0.12) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #484F58 !important;
    }
    
    /* ================================================================
       SELECTBOX / DROPDOWN
       ================================================================ */
    .stSelectbox > div > div {
        background-color: #0D1117 !important;
        border: 1px solid #30363D !important;
        border-radius: 10px !important;
    }
    
    /* ================================================================
       EXPANDERS
       ================================================================ */
    .streamlit-expanderHeader {
        background-color: #161B22 !important;
        border-radius: 10px !important;
        border: 1px solid #21262D !important;
        color: #C9D1D9 !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #30363D !important;
        background-color: #1C2128 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #0D1117 !important;
        border: 1px solid #21262D !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }
    
    /* ================================================================
       ALERTS / MESSAGES
       ================================================================ */
    .stSuccess {
        background-color: rgba(35, 134, 54, 0.08) !important;
        border: 1px solid rgba(35, 134, 54, 0.2) !important;
        border-left: 4px solid #238636 !important;
        border-radius: 10px !important;
        padding: 1rem 1.25rem !important;
        color: #3FB950 !important;
        animation: slideInFade 0.35s ease-out;
    }
    
    .stError {
        background-color: rgba(248, 81, 73, 0.08) !important;
        border: 1px solid rgba(248, 81, 73, 0.2) !important;
        border-left: 4px solid #F85149 !important;
        border-radius: 10px !important;
        padding: 1rem 1.25rem !important;
        color: #F85149 !important;
        animation: slideInFade 0.35s ease-out;
    }
    
    .stWarning {
        background-color: rgba(210, 153, 34, 0.08) !important;
        border: 1px solid rgba(210, 153, 34, 0.2) !important;
        border-left: 4px solid #D29922 !important;
        border-radius: 10px !important;
        padding: 1rem 1.25rem !important;
        color: #E3B341 !important;
        animation: slideInFade 0.35s ease-out;
    }
    
    .stInfo {
        background-color: rgba(31, 111, 235, 0.08) !important;
        border: 1px solid rgba(31, 111, 235, 0.2) !important;
        border-left: 4px solid #1F6FEB !important;
        border-radius: 10px !important;
        padding: 1rem 1.25rem !important;
        color: #58A6FF !important;
        animation: slideInFade 0.35s ease-out;
    }
    
    /* ================================================================
       PROGRESS BAR
       ================================================================ */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #238636 0%, #3FB950 50%, #238636 100%) !important;
        background-size: 200% 100% !important;
        animation: shimmer 2s ease infinite !important;
        border-radius: 6px !important;
    }
    
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* ================================================================
       FILE UPLOADER
       ================================================================ */
    .stFileUploader > div > div > div {
        background-color: #0D1117 !important;
        border: 2px dashed #30363D !important;
        border-radius: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > div > div:hover {
        border-color: #238636 !important;
        background-color: rgba(35, 134, 54, 0.03) !important;
    }
    
    /* ================================================================
       DATAFRAME / TABLES
       ================================================================ */
    .dataframe {
        background-color: #161B22 !important;
        border-radius: 10px !important;
        border: 1px solid #21262D !important;
    }
    
    /* ================================================================
       CHECKBOX
       ================================================================ */
    .stCheckbox label {
        color: #C9D1D9 !important;
        font-weight: 500 !important;
    }
    
    /* ================================================================
       RADIO
       ================================================================ */
    .stRadio label {
        color: #C9D1D9 !important;
    }
    
    /* ================================================================
       SLIDER
       ================================================================ */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #238636 0%, #3FB950 100%) !important;
    }
    
    /* ================================================================
       METRIC
       ================================================================ */
    [data-testid="stMetricValue"] {
        color: #C9D1D9 !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8B949E !important;
    }
    
    /* ================================================================
       DIVIDER
       ================================================================ */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #21262D, transparent) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* ================================================================
       SCROLLBAR
       ================================================================ */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0D1117;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #30363D;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #484F58;
    }
    
    /* ================================================================
       DOWNLOAD BUTTON
       ================================================================ */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1F6FEB 0%, #388BFD 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.25) !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #388BFD 0%, #58A6FF 100%) !important;
        box-shadow: 0 8px 24px rgba(31, 111, 235, 0.35) !important;
        transform: translateY(-2px) !important;
    }
    
    /* ================================================================
       RESULT CONTAINER
       ================================================================ */
    .result-container {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border-radius: 14px;
        padding: 1.75rem;
        border: 1px solid rgba(35, 134, 54, 0.3);
        box-shadow: 0 4px 24px rgba(35, 134, 54, 0.1);
        animation: scaleIn 0.35s ease-out;
    }
    
    /* ================================================================
       IMAGE COMPARISON CONTAINER
       ================================================================ */
    .image-compare-container {
        background: #0D1117;
        border-radius: 12px;
        padding: 0.75rem;
        border: 1px solid #21262D;
    }
    
    .image-label {
        text-align: center;
        color: #8B949E;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        padding: 0.4rem 0.75rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
    }
    
    /* ================================================================
       STEP INDICATOR
       ================================================================ */
    .step-indicator {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
        padding: 0.25rem 0;
    }
    
    .step-number {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: linear-gradient(135deg, #238636 0%, #2EA043 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 0.75rem;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(35, 134, 54, 0.3);
    }
    
    .step-title {
        color: #C9D1D9;
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* ================================================================
       GETTING STARTED STEPS
       ================================================================ */
    .getting-started-step {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 0.75rem 0;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        min-width: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #238636, #1f6feb);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .step-content h4 {
        margin: 0 0 0.25rem 0;
        color: #C9D1D9 !important;
        font-size: 1rem !important;
    }
    
    .step-content p {
        margin: 0;
        color: #8B949E;
        font-size: 0.9rem;
    }
    
    /* ================================================================
       ANIMATIONS
       ================================================================ */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInFade {
        from { opacity: 0; transform: translateX(-8px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.96); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Animation classes */
    .animate-fade-in { animation: fadeIn 0.4s ease-out; }
    .animate-fade-in-down { animation: fadeInDown 0.4s ease-out; }
    .animate-fade-in-up { animation: fadeInUp 0.4s ease-out; }
    .animate-slide-in-left { animation: slideInLeft 0.4s ease-out; }
    .animate-scale-in { animation: scaleIn 0.3s ease-out; }
    .animate-pulse { animation: pulse 2s infinite; }
    
    .stagger-1 { animation-delay: 0.05s; }
    .stagger-2 { animation-delay: 0.1s; }
    .stagger-3 { animation-delay: 0.15s; }
    .stagger-4 { animation-delay: 0.2s; }
    
    /* ================================================================
       LOTTIE ANIMATION CONTAINER
       ================================================================ */
    .lottie-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1rem;
    }
    
    /* ================================================================
       TOOLTIP
       ================================================================ */
    .tooltip-text {
        color: #6E7681;
        font-size: 0.8rem;
        font-style: italic;
    }
</style>
    """, unsafe_allow_html=True)


# ============================================================================
#                    REUSABLE HTML COMPONENTS
# ============================================================================

def render_card(content, card_type="default", header=None):
    """Render a styled card container."""
    card_class = f"card card-{card_type}" if card_type != "default" else "card"
    header_html = f'<div class="card-header">{header}</div>' if header else ""
    st.markdown(f'<div class="{card_class}">{header_html}{content}</div>', unsafe_allow_html=True)


def render_metric_card(label, value, icon=""):
    """Render a metric card."""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def render_feature_card(icon, title, description):
    """Render a feature card."""
    st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{description}</div>
        </div>
    """, unsafe_allow_html=True)


def render_badge(text, badge_type="info"):
    """Render a status badge."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'


def render_step_header(step_number, title):
    """Render a step indicator."""
    st.markdown(f"""
        <div class="step-indicator animate-fade-in">
            <div class="step-number">{step_number}</div>
            <div class="step-title">{title}</div>
        </div>
    """, unsafe_allow_html=True)


def render_result_container(content):
    """Render a result container."""
    st.markdown(f'<div class="result-container">{content}</div>', unsafe_allow_html=True)
