"""
WHO AFRO Data Hub Analytics Website
Comprehensive web application for mortality analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict
from data_pipeline import MortalityDataPipeline
from analytics import MortalityAnalytics
from chatbot import MortalityChatbot
from chart_generator import ChartGenerator
from interactive_visualizer import InteractiveVisualizer
from llm_report_generator import LLMReportGenerator
from tb_data_pipeline import TBDataPipeline
from tb_analytics import TBAnalytics
from tb_chatbot import TBChatbot
from tb_chart_generator import TBChartGenerator
from tb_interactive_visualizer import TBInteractiveVisualizer
from translations import get_translation, TRANSLATIONS
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Load environment variables - try multiple paths
env_paths = [
    os.path.join(os.path.dirname(__file__), '.env'),
    os.path.join(os.getcwd(), '.env'),
    '.env'
]
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path, override=True)
        break
else:
    # Try loading from current directory without explicit path
    load_dotenv(override=True)


# Page configuration
st.set_page_config(
    page_title="Regional Health Data Hub - Analytics Section",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS for WHO AFRO branding with animations and gradients
st.markdown("""
<style>
    /* Language Selector - Top Right Corner - Very Small */
    .language-selector-top-right {
        position: fixed;
        top: 5px;
        right: 10px;
        z-index: 9999;
        background: white;
        padding: 2px 5px;
        border-radius: 3px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,102,204,0.2);
        font-size: 0.5rem;
        line-height: 0.5;
        max-height: 0.5rem;
    }
    .language-selector-label {
        font-size: 0.5rem;
        color: #666;
        margin: 0;
        padding: 0;
        line-height: 0.5;
    }
    /* Style the selectbox to be very small */
    .language-selector-top-right div[data-testid="stSelectbox"] {
        font-size: 0.5rem;
        line-height: 0.5;
        margin: 0;
        padding: 0;
    }
    .language-selector-top-right div[data-testid="stSelectbox"] > div > div {
        font-size: 0.5rem;
        padding: 1px 3px;
        line-height: 0.5;
        min-height: 0.5rem;
        height: 0.5rem;
    }
    .language-selector-top-right select {
        font-size: 0.5rem;
        padding: 0;
        height: 0.5rem;
        line-height: 0.5;
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #0066CC 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        min-height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .main-header video {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: 0;
        opacity: 0.4;
    }
    .main-header .header-content {
        position: relative;
        z-index: 1;
        width: 100%;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    .who-logo {
        font-size: 4rem;
        margin-bottom: 0.5rem;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3));
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    .green-circle {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #00CC66;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    /* Modern Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: none;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #0066CC, #00CC66, #FF6600);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,102,204,0.2);
    }
    .stat-card:hover::before {
        transform: scaleX(1);
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0066CC 0%, #00CC66 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
        letter-spacing: -1px;
    }
    .stat-label {
        color: #666;
        font-size: 0.95rem;
        margin-top: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(90deg, #0066CC 0%, #00CC66 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2rem;
        font-weight: 700;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
    }
    .section-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #0066CC, #00CC66);
        border-radius: 2px;
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #E8F4F8 0%, #F0F8FF 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #0066CC;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,102,204,0.1);
        transition: all 0.3s ease;
    }
    .info-box:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0,102,204,0.15);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0066CC 0%, #004499 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,102,204,0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #004499 0%, #0066CC 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,102,204,0.4);
    }
    
    /* Dashboard Cards */
    .dashboard-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
        border: 1px solid rgba(0,102,204,0.1);
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,102,204,0.15);
        border-color: rgba(0,102,204,0.3);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* Animated Background */
    .animated-bg {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glass Morphism Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        padding: 2rem;
    }
    
    /* Chart Container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }
    
    /* Badge/Indicator */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: linear-gradient(135deg, #00CC66, #00AA55);
        color: white;
    }
    
    /* Progress Bar */
    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #0066CC, #00CC66);
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: progress 2s ease;
    }
    @keyframes progress {
        from { width: 0%; }
    }
    
    /* Hover Effects */
    .hover-lift {
        transition: all 0.3s ease;
    }
    .hover-lift:hover {
        transform: translateY(-5px);
    }
    
    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, #0066CC 0%, #00CC66 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if 'analytics' not in st.session_state:
    st.session_state.analytics = None
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = None


def initialize_system(indicator_type: str = "Maternal Mortality"):
    """Initialize the data pipeline and analytics system
    
    Args:
        indicator_type: Type of indicator ("Tuberculosis", "Maternal Mortality", "Child Mortality")
    """
    try:
        with st.spinner(f"Loading {indicator_type} data and initializing system..."):
            if indicator_type == "Tuberculosis":
                # Initialize TB data pipeline
                try:
                    pipeline = TBDataPipeline()
                    # Load data first
                    pipeline.load_data()
                    
                    # Verify data loaded (notifications and outcomes are required)
                    if pipeline.tb_notifications is None or pipeline.tb_outcomes is None:
                        raise ValueError("TB notifications or outcomes data failed to load. Please check data files.")
                    
                    # Create analytics
                    analytics = TBAnalytics(pipeline)
                    
                    # Create TB visualizer and chatbot
                    visualizer = TBInteractiveVisualizer(analytics)
                    chatbot = TBChatbot(analytics, visualizer)
                    
                except Exception as e:
                    st.error(f"Error loading TB data: {str(e)}")
                    st.info("""
                    **Troubleshooting:**
                    - Ensure the `tuberculosis ` folder exists in the project directory
                    - Check that TB data files exist in `tuberculosis /case reported by countries/` and `tuberculosis /tb burden/`
                    - Verify file permissions
                    """)
                    return False
                
                # Store TB components
                st.session_state.tb_pipeline = pipeline
                st.session_state.tb_analytics = analytics
                st.session_state.tb_visualizer = visualizer
                st.session_state.tb_chatbot = chatbot
                st.session_state.pipeline = None
                st.session_state.analytics = None
                st.session_state.visualizer = None
                st.session_state.chatbot = None
                st.session_state.data_loaded = True
                st.session_state.indicator_type = "Tuberculosis"
            else:
                # Initialize Mortality data pipeline (for Maternal and Child Mortality)
                pipeline = MortalityDataPipeline()
                pipeline.load_data()
                
                analytics = MortalityAnalytics(pipeline)
                visualizer = InteractiveVisualizer(analytics)
                chatbot = MortalityChatbot(analytics, visualizer)
                
                st.session_state.pipeline = pipeline
                st.session_state.analytics = analytics
                st.session_state.chatbot = chatbot
                st.session_state.visualizer = visualizer
                st.session_state.data_loaded = True
                st.session_state.indicator_type = indicator_type
            
        return True
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return False


def render_home_page():
    """Render the home page"""
    import os
    
    # Language Selector - Initialize
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    
    current_lang = st.session_state.selected_language
    languages = {
        "English": ("🇬🇧", "ENG"),
        "French": ("🇫🇷", "FR"),
        "Portuguese": ("🇵🇹", "PT"),
        "Spanish": ("🇪🇸", "ES")
    }
    
    # Header with video background
    video_file = "vid-for-rdhub-herosection.mp4"
    if os.path.exists(video_file):
        # Use HTML5 video with proper styling for background
        st.markdown("""
        <style>
        .hero-video-container {
            position: relative;
            width: 100%;
            min-height: 400px;
            overflow: hidden;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }
        .hero-video-container video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100% !important;
            height: 100% !important;
            min-width: 100% !important;
            min-height: 100% !important;
            object-fit: cover !important;
            z-index: 0;
            margin: 0;
            padding: 0;
        }
        .hero-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.75) 0%, rgba(118, 75, 162, 0.75) 50%, rgba(0, 102, 204, 0.75) 100%);
            z-index: 1;
        }
        .hero-content {
            position: relative;
            z-index: 2;
            padding: 3rem 2rem;
            text-align: center;
            min-height: 400px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .hero-language-selector {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 3;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Encode video to base64 for embedding
        @st.cache_data
        def load_video_base64(file_path):
            try:
                with open(file_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception as e:
                return None
        
        import base64
        video_base64 = load_video_base64(video_file)
        
        if video_base64:
            video_data_url = f"data:video/mp4;base64,{video_base64}"
            video_source = f'<source src="{video_data_url}" type="video/mp4">'
        else:
            # Fallback to file path
            video_source = f'<source src="{video_file}" type="video/mp4">'
        
        st.markdown(f"""
        <div class="hero-video-container">
            <video autoplay muted loop playsinline style="position: absolute; top: 0; left: 0; width: 100% !important; height: 100% !important; min-width: 100% !important; min-height: 100% !important; object-fit: cover !important; z-index: 0; margin: 0; padding: 0;">
                {video_source}
            </video>
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <div class="who-logo">🌍</div>
                <h1 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); margin: 0.5rem 0;">{get_translation("home_title", current_lang)}</h1>
                <p style="font-size: 1.1rem; opacity: 0.95; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.7); margin: 0.5rem 0; font-weight: 600;">{get_translation("home_subtitle", current_lang)}</p>
                <p style="font-size: 0.95rem; opacity: 0.9; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.7); margin: 1rem 0; line-height: 1.6;">
                    {get_translation("transforming_data", current_lang)}<br>
                    <strong>{get_translation("for_africa", current_lang)}</strong><br>
                    <span style="font-size: 0.85rem;">{get_translation("platform_description", current_lang)}</span>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Language selector inside hero card
        st.markdown("""
        <style>
        .hero-lang-container {
            position: relative;
            margin-top: -380px;
            margin-bottom: 360px;
            text-align: right;
            padding-right: 15px;
            z-index: 999;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create container for language selector positioned at top-right of hero
        col_spacer, col_lang = st.columns([10, 1])
        with col_lang:
            st.markdown('<div class="hero-lang-container">', unsafe_allow_html=True)
            lang_options = list(languages.keys())
            current_index = lang_options.index(current_lang) if current_lang in lang_options else 0
            
            selected_lang = st.selectbox(
                "",
                options=lang_options,
                index=current_index,
                format_func=lambda x: f"{languages[x][0]} {languages[x][1]}",
                key="hero_language_selector",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Update session state if language changed
            if selected_lang != current_lang:
                st.session_state.selected_language = selected_lang
                st.rerun()
        
        # Add CSS to style the hero language selector
        st.markdown("""
        <style>
        div[data-testid="stSelectbox"]:has(select[id*="hero_language_selector"]) {
            width: fit-content !important;
            min-width: auto !important;
            font-size: 0.7rem !important;
            background: rgba(255, 255, 255, 0.95) !important;
            padding: 3px 6px !important;
            border-radius: 6px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
            backdrop-filter: blur(5px) !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="hero_language_selector"]) > div {
            width: fit-content !important;
            min-width: auto !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="hero_language_selector"]) > div > div {
            font-size: 0.7rem !important;
            padding: 3px 8px !important;
            min-height: auto !important;
            height: auto !important;
            white-space: nowrap !important;
            width: fit-content !important;
            min-width: auto !important;
            line-height: 1.3 !important;
            font-weight: 600 !important;
            color: #0066CC !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="hero_language_selector"]) select {
            font-size: 0.7rem !important;
            padding: 3px 6px !important;
            width: fit-content !important;
            min-width: auto !important;
            height: auto !important;
            font-weight: 600 !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="hero_language_selector"]) > label {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Also add video using Streamlit's component as fallback
        with st.container():
            st.markdown("""
            <style>
            .stVideo {
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 100% !important;
                z-index: 0 !important;
                opacity: 0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        # Fallback to original header if video not found
        # Get current language for translations
        current_lang = st.session_state.get("selected_language", "English")
        
        st.markdown(f"""
        <div class="main-header">
            <div class="who-logo">🌍</div>
            <h1>{get_translation("home_title", current_lang)}</h1>
            <p style="font-size: 1.1rem; opacity: 0.95; font-weight: 600;">{get_translation("home_subtitle", current_lang)}</p>
            <p style="font-size: 0.95rem; opacity: 0.9; margin: 1rem 0; line-height: 1.6;">
                {get_translation("transforming_data", current_lang)}<br>
                <strong>{get_translation("for_africa", current_lang)}</strong><br>
                <span style="font-size: 0.85rem;">{get_translation("platform_description", current_lang)}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Language selector inside fallback hero card
        st.markdown("""
        <style>
        .fallback-hero-lang-container {
            position: relative;
            margin-top: -280px;
            margin-bottom: 260px;
            text-align: right;
            padding-right: 15px;
            z-index: 999;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create container for language selector positioned at top-right of fallback hero
        col_spacer, col_lang = st.columns([10, 1])
        with col_lang:
            st.markdown('<div class="fallback-hero-lang-container">', unsafe_allow_html=True)
            lang_options = list(languages.keys())
            current_index = lang_options.index(current_lang) if current_lang in lang_options else 0
            
            selected_lang = st.selectbox(
                "",
                options=lang_options,
                index=current_index,
                format_func=lambda x: f"{languages[x][0]} {languages[x][1]}",
                key="fallback_hero_language_selector",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Update session state if language changed
            if selected_lang != current_lang:
                st.session_state.selected_language = selected_lang
                st.rerun()
        
        # Add CSS to style the fallback hero language selector
        st.markdown("""
        <style>
        div[data-testid="stSelectbox"]:has(select[id*="fallback_hero_language_selector"]) {
            width: fit-content !important;
            min-width: auto !important;
            font-size: 0.7rem !important;
            background: rgba(255, 255, 255, 0.95) !important;
            padding: 3px 6px !important;
            border-radius: 6px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
            backdrop-filter: blur(5px) !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="fallback_hero_language_selector"]) > div {
            width: fit-content !important;
            min-width: auto !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="fallback_hero_language_selector"]) > div > div {
            font-size: 0.7rem !important;
            padding: 3px 8px !important;
            min-height: auto !important;
            height: auto !important;
            white-space: nowrap !important;
            width: fit-content !important;
            min-width: auto !important;
            line-height: 1.3 !important;
            font-weight: 600 !important;
            color: #0066CC !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="fallback_hero_language_selector"]) select {
            font-size: 0.7rem !important;
            padding: 3px 6px !important;
            width: fit-content !important;
            min-width: auto !important;
            height: auto !important;
            font-weight: 600 !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="fallback_hero_language_selector"]) > label {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Get current health topic
    indicator_type = st.session_state.get("indicator_type", "Maternal Mortality")
    
    # Update About text based on health topic
    current_lang = st.session_state.get("selected_language", "English")
    if indicator_type == "Tuberculosis":
        about_text = f"""
        <div class="info-box">
            <h3>{get_translation("about_who_afro", current_lang)}</h3>
            <p>{get_translation("about_description_tb", current_lang)}</p>
        </div>
        """
    else:
        about_text = f"""
        <div class="info-box">
            <h3>{get_translation("about_who_afro", current_lang)}</h3>
            <p>{get_translation("about_description_mortality", current_lang)}</p>
        </div>
        """
    
    st.markdown(about_text, unsafe_allow_html=True)
    
    # Key statistics - handle both TB and Mortality data
    if st.session_state.data_loaded:
        # Get summary based on indicator type
        if indicator_type == "Tuberculosis" and hasattr(st.session_state, 'tb_pipeline') and st.session_state.tb_pipeline is not None:
            summary = st.session_state.tb_pipeline.get_data_summary()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{summary['countries']}</div>
                    <div class="stat-label">{get_translation("afro_countries", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{summary['indicators']}</div>
                    <div class="stat-label">{get_translation("tb_indicators", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{summary['tb_burden_records']:,}</div>
                    <div class="stat-label">{get_translation("tb_burden_records", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                year_range = summary.get('year_range', (None, None))
                year_text = f"{year_range[0]}-{year_range[1]}" if year_range[0] and year_range[1] else "N/A"
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{year_text}</div>
                    <div class="stat-label">Year Range</div>
                </div>
                """, unsafe_allow_html=True)
        elif hasattr(st.session_state, 'pipeline') and st.session_state.pipeline is not None:
            summary = st.session_state.pipeline.get_data_summary()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{summary['countries']}</div>
                    <div class="stat-label">{get_translation("afro_countries", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{summary['indicators']}</div>
                    <div class="stat-label">{get_translation("indicators", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                records_key = 'mortality_records' if 'mortality_records' in summary else 'tb_burden_records'
                records_value = summary.get(records_key, 0)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{records_value:,}</div>
                    <div class="stat-label">{get_translation("mortality_records", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                mmr_records = summary.get('mmr_records', 0)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{mmr_records:,}</div>
                    <div class="stat-label">{get_translation("mmr_records", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Key Features - update based on indicator type
    if indicator_type == "Tuberculosis":
        features_text = f"""
        ### {get_translation("key_features", current_lang)}
        
        - 📊 **{get_translation("comprehensive_tb_analytics", current_lang)}**: {get_translation("comprehensive_tb_analytics_desc", current_lang)}
        - 🤖 **{get_translation("ai_powered_chatbot", current_lang)}**: {get_translation("ai_chatbot_desc", current_lang)}
        - 📈 **{get_translation("trend_analysis_feature", current_lang)}**: {get_translation("trend_analysis_desc", current_lang)}
        - 📋 **{get_translation("report_generation", current_lang)}**: {get_translation("report_generation_desc", current_lang)}
        - 🌍 **{get_translation("multi_country_comparison", current_lang)}**: {get_translation("multi_country_desc", current_lang)}
        
        ### {get_translation("available_indicators", current_lang)}
        """
    else:
        features_text = f"""
        ### {get_translation("key_features", current_lang)}
        
        - 📊 **{get_translation("comprehensive_analytics", current_lang)}**: {get_translation("comprehensive_analytics_desc", current_lang)}
        - 🤖 **{get_translation("ai_powered_chatbot", current_lang)}**: {get_translation("ai_chatbot_desc", current_lang)}
        - 📈 **{get_translation("trend_analysis_feature", current_lang)}**: {get_translation("trend_analysis_desc", current_lang)}
        - 🔮 **{get_translation("projections_feature", current_lang)}**: {get_translation("projections_desc", current_lang)}
        - 📋 **{get_translation("report_generation", current_lang)}**: {get_translation("report_generation_desc", current_lang)}
        - 🌍 **{get_translation("multi_country_comparison", current_lang)}**: {get_translation("multi_country_desc", current_lang)}
        
        ### {get_translation("available_indicators", current_lang)}
        """
    
    st.markdown(features_text, unsafe_allow_html=True)
    
    # Additional indicators list
    if indicator_type != "Tuberculosis":
        st.markdown("""
        - Neonatal mortality rate
        - Infant mortality rate
        - Under-five mortality rate
        - Maternal Mortality Ratio (MMR)
        - Mortality rates by age groups
        - Stillbirth rate
        """)
    
    st.markdown(f"""
    ### {get_translation("getting_started", current_lang)}
    
    1. {get_translation("getting_started_1", current_lang)}
    2. {get_translation("getting_started_2", current_lang)}
    3. {get_translation("getting_started_3", current_lang)}
    """)


def render_tb_dashboard(analytics, pipeline):
    """Render specialized TB dashboard with interactive analytics for notifications"""
    try:
        import plotly.graph_objects as go
        import plotly.express as px
    except ImportError:
        st.error("Plotly is required for TB dashboard. Please install: pip install plotly")
        return
    
    # Get current language for translations
    current_lang = st.session_state.get("selected_language", "English")
    
    st.markdown(f'<h2 class="section-header">{get_translation("tb_notifications", current_lang)} Analytics Dashboard</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="margin-bottom: 2rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>Focus:</strong> TB Case Notifications and Treatment Outcomes for WHO AFRO Region (47 countries)
            <br>Data based on Global Tuberculosis Report 2024 indicators
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    summary = analytics.get_regional_summary()
    
    # Get current language for translations
    current_lang = st.session_state.get("selected_language", "English")
    
    # Regional Overview Cards
    st.markdown(f"""
    <div class="dashboard-card">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">{get_translation("regional_overview", current_lang)} - WHO AFRO</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{summary['total_countries']}</div>
            <div class="stat-label">{get_translation("countries", current_lang)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        latest_year = summary.get('latest_year', 'N/A')
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{latest_year}</div>
            <div class="stat-label">{get_translation("latest_year", current_lang)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if summary.get('regional_totals'):
            total_notif = summary['regional_totals'].get('total_notifications', 0)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_notif:,.0f}</div>
                <div class="stat-label">{get_translation("total_notifications", current_lang)}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if summary.get('regional_totals'):
            total_sp = summary['regional_totals'].get('total_smear_positive', 0)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_sp:,.0f}</div>
                <div class="stat-label">{get_translation("smear_positive", current_lang)}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Key TB Indicators from Report 2024
    # Get current language and health topic
    current_lang = st.session_state.get("selected_language", "English")
    health_topic = st.session_state.get("indicator_type", "Tuberculosis")
    
    st.markdown(f"""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">{get_translation("key_indicators", current_lang)} ({get_translation("latest_year", current_lang)})</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display key indicators in a grid
    indicators_list = list(summary.get('indicators', {}).items())
    if indicators_list:
        cols = st.columns(2)
        for idx, (indicator_name, data) in enumerate(indicators_list[:6]):
            col_idx = idx % 2
            with cols[col_idx]:
                mean_val = data.get('mean_value', 0)
                median_val = data.get('median_value', 0)
                total_regional = data.get('total_regional', 0)
                
                # For TB notifications: Show only total cases (no mean/median)
                # For TB treatment outcomes: Show percentages (median)
                # For Mortality: Show only median (not mean)
                is_percentage = '%' in indicator_name or 'Rate' in indicator_name
                is_tb_notification = health_topic == "Tuberculosis" and not is_percentage
                
                st.markdown(f"""
                <div class="info-box hover-lift">
                    <h4 style="color: #0066CC; margin-bottom: 0.5rem; font-size: 1.1rem;">{indicator_name}</h4>
                    {f'<p style="margin: 0.25rem 0; font-size: 0.95rem;"><strong>{get_translation("total_new_cases", current_lang)}:</strong> <span style="color: #0066CC; font-weight: 600;">{total_regional:,.0f}</span></p>' if total_regional > 0 and is_tb_notification else ''}
                    {f'<p style="margin: 0.25rem 0; font-size: 0.95rem;"><strong>Median:</strong> <span style="color: #0066CC; font-weight: 600;">{median_val:.2f}%</span></p>' if is_percentage and health_topic == "Tuberculosis" else ''}
                    {f'<p style="margin: 0.25rem 0; font-size: 0.95rem;"><strong>Median:</strong> <span style="color: #0066CC; font-weight: 600;">{median_val:.2f}</span></p>' if not is_tb_notification and health_topic != "Tuberculosis" else ''}
                    <p style="margin: 0.25rem 0; font-size: 0.9rem; color: #666;">
                        Range: {data.get('min_value', 0):.2f}{'%' if is_percentage else ''} - {data.get('max_value', 0):.2f}{'%' if is_percentage else ''}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Get current language for translations
    current_lang = st.session_state.get("selected_language", "English")
    
    # Interactive Trend Analysis
    st.markdown(f"""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">{get_translation("trend_analysis", current_lang)}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        available_indicators = [
            "TB Notifications (Total New Cases)",
            "New Smear-Positive Cases",
            "New Smear-Negative Cases",
            "New Extrapulmonary Cases",
            "Treatment Success Rate - New Cases (%)",
            "Treatment Success Rate (%)"
        ]
        selected_indicator = st.selectbox(
            get_translation("select_indicator", current_lang),
            available_indicators,
            index=0
        )
    
    with col2:
        chart_type = st.selectbox(
            get_translation("chart_type", current_lang),
            ["Line Chart", "Bar Chart"],
            index=0
        )
    
    with col3:
        year_range = st.slider(
            get_translation("year_range", current_lang),
            min_value=2000,
            max_value=2023,
            value=(2015, 2023)
        )
    
    # Get trend analysis
    try:
        if hasattr(analytics, 'get_trend_analysis'):
            trend_data = analytics.get_trend_analysis(
                selected_indicator,
                start_year=year_range[0],
                end_year=year_range[1]
            )
        else:
            st.warning("Trend analysis not available for this health topic.")
            trend_data = {"error": "Method not available"}
        
        if 'error' not in trend_data and trend_data.get('yearly_totals'):
            # Create trend chart
            df_trend = pd.DataFrame(trend_data['yearly_totals'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_trend['year'],
                y=df_trend['total_value'],
                mode='lines+markers',
                name='Regional Total',
                line=dict(color='#0066CC', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title=f'{selected_indicator} - Regional Trend (AFRO)',
                xaxis_title='Year',
                yaxis_title='Value',
                hovermode='x unified',
                template='plotly_white',
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display trend summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Percentage Change", f"{trend_data.get('percentage_change', 0):.1f}%")
            with col2:
                st.metric("Trend Direction", trend_data.get('trend', 'N/A'))
            with col3:
                st.metric("Period", f"{trend_data.get('start_year', 'N/A')} - {trend_data.get('end_year', 'N/A')}")
        else:
            st.info(f"No trend data available for {selected_indicator}")
    except Exception as e:
        st.warning(f"Could not generate trend analysis: {str(e)}")
    
    # Regional Outlook Section
    st.markdown("""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">Regional Outlook - WHO AFRO</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        if hasattr(analytics, 'get_regional_outlook'):
            outlook = analytics.get_regional_outlook()
        else:
            outlook = {"error": "Method not available"}
        
        if 'error' not in outlook:
            # Regional Performance Summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if outlook.get('regional_totals', {}).get('total_notifications'):
                    st.metric(
                        "Total Notifications",
                        f"{outlook['regional_totals']['total_notifications']:,.0f}",
                        help="Total TB cases notified in AFRO region"
                    )
            
            with col2:
                if outlook.get('countries_with_data', {}).get('notifications'):
                    st.metric(
                        "Countries Reporting",
                        f"{outlook['countries_with_data']['notifications']}/{outlook['total_countries']}",
                        help="Number of countries with notification data"
                    )
            
            with col3:
                if outlook.get('performance_summary', {}).get('treatment_success_rate'):
                    tsr = outlook['performance_summary']['treatment_success_rate']
                    st.metric(
                        "Mean Treatment Success Rate",
                        f"{tsr['mean']:.1f}%",
                        help=f"Range: {tsr['min']:.1f}% - {tsr['max']:.1f}%"
                    )
            
            with col4:
                if outlook.get('performance_summary', {}).get('treatment_success_rate'):
                    tsr = outlook['performance_summary']['treatment_success_rate']
                    above_target = tsr.get('countries_above_85', 0)
                    st.metric(
                        "Countries ≥85% TSR",
                        f"{above_target}/{outlook['total_countries']}",
                        help="WHO target: ≥85% treatment success rate"
                    )
            
            # Trend Analysis
            if outlook.get('trends', {}).get('notifications_5year'):
                trend_5y = outlook['trends']['notifications_5year']
                st.markdown("### 5-Year Trend Analysis")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("5-Year Change", f"{trend_5y['percentage_change']:.1f}%")
                with col2:
                    st.metric("Direction", trend_5y['direction'])
                with col3:
                    st.metric("5 Years Ago", f"{trend_5y['value_5y_ago']:,.0f}")
            
            # Performance Distribution
            if outlook.get('performance_summary', {}).get('notification_distribution'):
                dist = outlook['performance_summary']['notification_distribution']
                st.markdown("### Country Performance Distribution")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Low", dist['low'])
                with col2:
                    st.metric("Medium-Low", dist['medium_low'])
                with col3:
                    st.metric("Medium-High", dist['medium_high'])
                with col4:
                    st.metric("High", dist['high'])
    except Exception as e:
            st.warning(f"Could not generate regional outlook: {str(e)}")
    
    # Age Group Analysis (Post-2011)
    st.markdown(f"""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">{get_translation("age_groups", current_lang)} - TB Cases by Age Group (Post-2011)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Country selection for age group chart
    countries = pipeline.get_countries()
    selected_country_age = st.selectbox(
        f"{get_translation('select_country', current_lang)} for Age Group Analysis",
        countries,
        index=0 if countries else None,
        key="age_group_country"
    )
    
    if selected_country_age:
        try:
            from tb_chart_generator import TBChartGenerator
            chart_gen = TBChartGenerator(analytics)
            age_chart = chart_gen.create_age_group_chart(selected_country_age)
            if age_chart:
                st.plotly_chart(age_chart, use_container_width=True)
            else:
                st.info(f"No age group data available for {selected_country_age} (data available post-2011)")
        except AttributeError as e:
            if "'TBChartGenerator' object has no attribute" in str(e):
                st.error(f"Chart generator method missing. Please ensure tb_chart_generator.py has the create_age_group_chart method.")
            else:
                st.warning(f"Could not generate age group chart: {str(e)}")
        except Exception as e:
            st.warning(f"Could not generate age group chart: {str(e)}")
    
    # Notification Types Breakdown
    st.markdown(f"""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">{get_translation("notification_types", current_lang)} - Breakdown</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Country selection for notification types
    selected_country_notif = st.selectbox(
        f"{get_translation('select_country', current_lang)} for Notification Types",
        countries,
        index=0 if countries else None,
        key="notif_types_country"
    )
    
    if selected_country_notif:
        try:
            from tb_chart_generator import TBChartGenerator
            chart_gen = TBChartGenerator(analytics)
            notif_chart = chart_gen.create_notification_types_chart(selected_country_notif)
            if notif_chart:
                st.plotly_chart(notif_chart, use_container_width=True)
                st.info("Note: Notification types should sum to c_newinc (Total New Cases). Note: Case definition for new smear-positive changed after 2012.")
            else:
                st.info(f"No notification type data available for {selected_country_notif}")
        except AttributeError as e:
            if "'TBChartGenerator' object has no attribute" in str(e):
                st.error(f"Chart generator method missing. Please ensure tb_chart_generator.py has the create_notification_types_chart method.")
            else:
                st.warning(f"Could not generate notification types chart: {str(e)}")
        except Exception as e:
            st.warning(f"Could not generate notification types chart: {str(e)}")
    
    # Top Countries Analysis
    st.markdown("""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">Top Countries Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_indicator = st.selectbox(
            "Select Indicator",
            available_indicators[:4],  # Only notifications indicators
            index=0,
            key="top_indicator"
        )
        
        try:
            if hasattr(analytics, 'get_top_countries'):
                top_countries = analytics.get_top_countries(top_indicator, n=10, ascending=False)
            else:
                top_countries = {"error": "Method not available"}
            if 'error' not in top_countries and top_countries.get('countries'):
                df_top = pd.DataFrame(top_countries['countries'])
                
                fig = px.bar(
                    df_top,
                    x='value',
                    y='country',
                    orientation='h',
                    title=f'Top 10 Countries - {top_indicator}',
                    labels={'value': 'Value', 'country': 'Country'},
                    color='value',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate top countries: {str(e)}")
    
    with col2:
        try:
            if hasattr(analytics, 'get_top_countries'):
                bottom_countries = analytics.get_top_countries(top_indicator, n=10, ascending=True)
            else:
                bottom_countries = {"error": "Method not available"}
            if 'error' not in bottom_countries and bottom_countries.get('countries'):
                df_bottom = pd.DataFrame(bottom_countries['countries'])
                
                fig = px.bar(
                    df_bottom,
                    x='value',
                    y='country',
                    orientation='h',
                    title=f'Bottom 10 Countries - {top_indicator}',
                    labels={'value': 'Value', 'country': 'Country'},
                    color='value',
                    color_continuous_scale='Reds_r'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total descending'})
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate bottom countries: {str(e)}")


def render_dashboard_page():
    """Render the modern analytics dashboard"""
    current_lang = st.session_state.get("selected_language", "English")
    st.markdown(f'<h2 class="section-header">{get_translation("analytics_dashboard", current_lang)}</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning(get_translation("please_initialize", current_lang))
        return
    
    # Get analytics and pipeline based on indicator type
    indicator_type = st.session_state.get("indicator_type", "Maternal Mortality")
    
    if indicator_type == "Tuberculosis" and hasattr(st.session_state, 'tb_analytics') and st.session_state.tb_analytics is not None:
        analytics = st.session_state.tb_analytics
        pipeline = st.session_state.tb_pipeline
        # Render specialized TB dashboard
        render_tb_dashboard(analytics, pipeline)
        return
    
    elif hasattr(st.session_state, 'analytics') and st.session_state.analytics is not None:
        analytics = st.session_state.analytics
        pipeline = st.session_state.pipeline
    else:
        current_lang = st.session_state.get("selected_language", "English")
        st.error(f"Analytics system not initialized for {indicator_type}. {get_translation('please_initialize', current_lang)}")
        return
    
    if analytics is None:
        current_lang = st.session_state.get("selected_language", "English")
        st.error(f"Analytics object is None. {get_translation('please_initialize', current_lang)}")
        return
    
    # Regional Summary with Modern Cards
    st.markdown(f"""
    <div class="dashboard-card">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">{get_translation("regional_overview", current_lang)}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    summary = analytics.get_regional_summary()
    
    # Key Statistics Cards with Modern Design
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{summary['total_countries']}</div>
            <div class="stat-label">Countries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(summary['indicators'])}</div>
            <div class="stat-label">Indicators</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if summary.get("mmr_summary"):
            mmr = summary["mmr_summary"]
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{mmr.get('median_mmr', mmr.get('mean_mmr', 0)):.0f}</div>
                <div class="stat-label">Median MMR</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if summary.get("mmr_summary"):
            mmr = summary["mmr_summary"]
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{mmr['min_mmr']:.0f}</div>
                <div class="stat-label">Best MMR</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Key Indicators with Modern Layout
    st.markdown("""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">Key Indicators Summary</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Get current language for translations
    current_lang = st.session_state.get("selected_language", "English")
    
    with col1:
        for indicator, data in list(summary["indicators"].items())[:5]:
            # For Mortality: Show only Median (not Mean)
            median_val = data.get('median_value', 0)
            st.markdown(f"""
            <div class="info-box hover-lift">
                <h4 style="color: #0066CC; margin-bottom: 0.5rem; font-size: 1.1rem;">{indicator}</h4>
                <p style="margin: 0.25rem 0; font-size: 0.95rem;"><strong>Median:</strong> <span style="color: #0066CC; font-weight: 600;">{median_val:.2f}</span></p>
                <p style="margin: 0.25rem 0; font-size: 0.95rem;"><strong>Range:</strong> {data['min_value']:.2f} - {data['max_value']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if summary.get("mmr_summary"):
            mmr = summary["mmr_summary"]
            st.markdown(f"""
            <div class="glass-card hover-lift">
                <h4 style="color: #0066CC; margin-bottom: 1rem; font-size: 1.2rem;">Maternal Mortality Ratio</h4>
                <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #0066CC 0%, #00CC66 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{mmr['mean_mmr']:.0f}</div>
                        <div style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">Mean</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #00CC66 0%, #0066CC 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{mmr['median_mmr']:.0f}</div>
                        <div style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">Median</div>
                    </div>
                </div>
                <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 2px solid rgba(0,102,204,0.1);">
                    <div style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">Range</div>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #0066CC;">
                        {mmr['min_mmr']:.2f} - {mmr['max_mmr']:.2f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Top Countries Analysis with Modern Charts
    st.markdown("""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">🏆 Top Countries Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container hover-lift">
            <h4 style="color: #CC0000; margin-bottom: 1rem; font-size: 1.2rem;">⚠️ Highest Under-Five Mortality</h4>
        </div>
        """, unsafe_allow_html=True)
        top_high = analytics.get_top_countries_by_indicator("Under-five mortality rate", 10, ascending=False)
        if len(top_high) > 0:
            st.bar_chart(top_high.set_index('country')['value'], height=300)
            st.dataframe(
                top_high[['country', 'value']].rename(columns={'value': 'Rate'}),
                use_container_width=True,
                hide_index=True
            )
    
    with col2:
        st.markdown("""
        <div class="chart-container hover-lift">
            <h4 style="color: #00CC66; margin-bottom: 1rem; font-size: 1.2rem;"><span class="green-circle"></span>Lowest Under-Five Mortality</h4>
        </div>
        """, unsafe_allow_html=True)
        top_low = analytics.get_top_countries_by_indicator("Under-five mortality rate", 10, ascending=True)
        if len(top_low) > 0:
            st.bar_chart(top_low.set_index('country')['value'], height=300)
            st.dataframe(
                top_low[['country', 'value']].rename(columns={'value': 'Rate'}),
                use_container_width=True,
                hide_index=True
            )
    
    # Projections Analysis with Modern Metrics
    st.markdown("""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">2030 Projections Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    proj_analysis = analytics.analyze_projections()
    
    if proj_analysis.get("mmr_projections"):
        mmr_proj = proj_analysis["mmr_projections"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card hover-lift">
                <div style="font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem;">{mmr_proj['on_track_count']}</div>
                <div style="font-size: 1.2rem; opacity: 0.95; font-weight: 500;">On Track</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card hover-lift" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div style="font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem;">{mmr_proj['off_track_count']}</div>
                <div style="font-size: 1.2rem; opacity: 0.95; font-weight: 500;">Off Track</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card hover-lift" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <div style="font-size: 2.8rem; font-weight: 800; margin-bottom: 0.5rem;">{mmr_proj['avg_proj_2030']:.0f}</div>
                <div style="font-size: 1.1rem; opacity: 0.95; font-weight: 500;">Avg Projected MMR 2030</div>
            </div>
            """, unsafe_allow_html=True)
        
        if mmr_proj.get("countries_on_track"):
            st.markdown("""
            <div class="info-box hover-lift" style="margin-top: 1.5rem;">
                <h4 style="color: #0066CC; margin-bottom: 0.5rem; font-size: 1.1rem;"><span class="green-circle"></span>Countries On Track</h4>
                <p style="margin: 0; font-size: 0.95rem;">""" + ", ".join(mmr_proj['countries_on_track']) + """</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Country Comparison with Interactive Chart
    st.markdown("""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">Country Comparison</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_countries = st.multiselect(
            "Select countries to compare",
            pipeline.get_countries(),
            default=pipeline.get_countries()[:5] if len(pipeline.get_countries()) >= 5 else pipeline.get_countries(),
            label_visibility="collapsed"
        )
    
    with col2:
        indicator_select = st.selectbox(
            "Select indicator",
            ["Under-five mortality rate", "Infant mortality rate", "Neonatal mortality rate"],
            label_visibility="collapsed"
        )
    
    if selected_countries:
        comparison_data = []
        for country in selected_countries:
            stats = analytics.get_country_statistics(country)
            if indicator_select in stats["indicators"]:
                comparison_data.append({
                    "country": country,
                    "value": stats["indicators"][indicator_select]["latest_value"]
                })
        
        if comparison_data:
            comp_df = pd.DataFrame(comparison_data)
            st.markdown("""
            <div class="chart-container hover-lift">
            """, unsafe_allow_html=True)
            st.bar_chart(comp_df.set_index('country')['value'], height=400)
            st.markdown("</div>", unsafe_allow_html=True)


def render_chatbot_page():
    """Render the chatbot page"""
    # Get current health topic and language
    health_topic = st.session_state.get("indicator_type", "Maternal Mortality")
    selected_language = st.session_state.get("selected_language", "English")
    
    # Display current settings
    st.markdown(f"""
    <div style="margin-bottom: 1rem; padding: 1rem; background: linear-gradient(135deg, #0066CC 0%, #004499 100%); border-radius: 10px; color: white;">
        <strong>Health Topic:</strong> {health_topic} | <strong>Language:</strong> {selected_language}
    </div>
    """, unsafe_allow_html=True)
    
    # Use translations
    current_lang = st.session_state.get("selected_language", "English")
    
    st.markdown(f'<h2 class="section-header">{get_translation("chatbot", current_lang)}</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning(f"{get_translation('initialize_system', current_lang)}")
        return
    
    # Get chatbot based on health topic
    chatbot = None
    if health_topic == "Tuberculosis" and hasattr(st.session_state, 'tb_chatbot') and st.session_state.tb_chatbot is not None:
        chatbot = st.session_state.tb_chatbot
    elif hasattr(st.session_state, 'chatbot') and st.session_state.chatbot is not None:
        chatbot = st.session_state.chatbot
    
    if chatbot is None:
        st.error(f"{get_translation('chatbot', current_lang)} not initialized. {get_translation('please_initialize', current_lang)}")
        return
    
    # Link to Interactive Visualizer
    st.markdown("""
    <div class="info-box" style="margin-bottom: 1.5rem;">
        <h4 style="color: #0066CC; margin-bottom: 0.5rem;">💡 Want More Control?</h4>
        <p style="margin: 0;">For customizable charts with prediction methods, maps, and full control over visualizations, 
        check out the <strong>📈 Interactive Charts</strong> page in the sidebar!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Update prompt based on health topic
    if health_topic == "Tuberculosis":
        prompt_text = """
        Ask questions about TB data in natural language. The chatbot can help you:
        - Get TB statistics for specific countries (with charts)
        - Compare TB indicators across countries (with charts)
        - Analyze TB trends (with charts)
        - View TB notifications and outcomes
        - Generate TB reports
        """
    else:
        prompt_text = """
        Ask questions about mortality data in natural language. The chatbot can help you:
        - Get statistics for specific countries (with charts)
        - Compare countries (with charts)
        - Analyze trends (with charts)
        - View projections (with charts)
        - Generate reports
        """
    
    st.markdown(prompt_text)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                # Handle both old format (string) and new format (dict with chart)
                if isinstance(message["content"], dict):
                    st.write(message["content"].get("text", ""))
                    
                    # Display single chart
                    if message["content"].get("chart"):
                        st.plotly_chart(message["content"]["chart"], use_container_width=True)
                    
                    # Display multiple charts if available
                    if message["content"].get("charts"):
                        for chart in message["content"]["charts"]:
                            st.plotly_chart(chart, use_container_width=True)
                    
                    # Add link to interactive visualizer for country queries
                    text_content = message["content"].get("text", "").lower()
                    if any(keyword in text_content for keyword in ["statistics for", "country", "chart", "visualize"]):
                        st.markdown("""
                        <div style="margin-top: 1rem; padding: 1rem; background: #E8F4F8; border-radius: 10px; border-left: 4px solid #0066CC;">
                            <strong>💡 Want more control?</strong> Visit <strong>📈 Interactive Charts</strong> in the sidebar for:
                            <ul style="margin: 0.5rem 0 0 1.5rem; padding: 0;">
                                <li>Customizable prediction methods</li>
                                <li>Map visualizations</li>
                                <li>Year range controls (2000-2023 observed, 2024-2030 projected)</li>
                                <li>Projection shading</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write(message["content"])
    
    # Chat input - adapt placeholder based on health topic
    if health_topic == "Tuberculosis":
        placeholder = "Ask a question about TB data..."
    else:
        placeholder = "Ask a question about mortality data..."
    
    user_query = st.chat_input(placeholder)
    
    if user_query:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query
        })
        
        # Get response from chatbot
        with st.spinner("Analyzing and generating charts..."):
            response = chatbot.process_query(user_query)
        
        # Handle response format (dict with text and chart)
        if isinstance(response, dict):
            response_content = response
        else:
            # Backward compatibility: convert string to dict format
            response_content = {"text": response, "chart": None}
        
        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_content
        })
        
        st.rerun()
    
    # Quick Access to Interactive Visualizer
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("📈 Open Interactive Visualizer", use_container_width=True, help="Go to Interactive Charts page for full customization"):
            st.session_state.current_page = 'Visualizer'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem;">
            <small style="color: #666;">For customizable charts<br>with full control</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Country Statistics (with charts):**
        - What are the statistics for Kenya?
        - Show me charts for Angola
        - Visualize data for Nigeria
        
        **Comparisons (with charts):**
        - Compare Kenya and Uganda
        - Compare Kenya, Uganda, and Tanzania
        
        **Trends (with charts):**
        - What is the trend for neonatal mortality in Angola?
        - Show trend chart for Kenya
        
        **Projections (with charts):**
        - Show me projections for 2030
        - Projections for Kenya
        
        **Top Countries (with charts):**
        - Top 10 countries by under-five mortality rate
        
        **Reports:**
        - Generate a summary report for Nigeria
        """)


def _collect_statistics_for_llm(analytics, pipeline, country: str = None, indicator_type: str = "Maternal Mortality") -> Dict:
    """Collect key statistics for LLM report generation
    
    Args:
        analytics: Analytics instance (MortalityAnalytics or TBAnalytics)
        pipeline: Pipeline instance (MortalityDataPipeline or TBDataPipeline)
        country: Optional country name
        indicator_type: Type of indicator ("Tuberculosis", "Maternal Mortality", "Child Mortality")
    """
    statistics = {}
    statistics["indicator_type"] = indicator_type
    
    if indicator_type == "Tuberculosis":
        # TB-specific statistics collection
        if country:
            stats = analytics.get_country_statistics(country)
            statistics["country_stats"] = stats
        else:
            regional_summary = analytics.get_regional_summary()
            statistics["regional_summary"] = regional_summary
    else:
        # Mortality-specific statistics collection
        if country:
            # Country-specific statistics
            stats = analytics.get_country_statistics(country)
            statistics["country_stats"] = stats
            
            # Get projections for the country
            try:
                proj_analysis = analytics.analyze_projections(country)
                statistics["projections"] = proj_analysis
            except:
                pass
            
            # Add trend analysis for key indicators
            trend_analyses = {}
            try:
                indicators = pipeline.get_indicators()
                for indicator in indicators[:3]:  # Top 3 indicators
                    try:
                        trend_analysis = analytics.get_trend_analysis(country, indicator)
                        if "error" not in trend_analysis:
                            trend_analyses[indicator] = trend_analysis
                    except:
                        pass
                
                if trend_analyses:
                    statistics["trend_analyses"] = trend_analyses
            except:
                pass
        else:
            # Regional statistics
            regional_summary = analytics.get_regional_summary()
            statistics["regional_summary"] = regional_summary
            
            # Regional projections
            try:
                proj_analysis = analytics.analyze_projections()
                statistics["projections"] = proj_analysis
            except:
                pass
        
            # Get top countries for key indicators with values
            top_countries = {}
            try:
                indicators = pipeline.get_indicators()
                for indicator in indicators[:5]:  # Top 5 indicators
                    try:
                        top_df = analytics.get_top_countries_by_indicator(indicator, top_n=5, ascending=False)
                        bottom_df = analytics.get_top_countries_by_indicator(indicator, top_n=5, ascending=True)
                        
                        top_countries[indicator] = {
                            "top": {
                                "countries": top_df['country'].tolist() if len(top_df) > 0 else [],
                                "values": top_df['value'].tolist() if len(top_df) > 0 else []
                            },
                            "bottom": {
                                "countries": bottom_df['country'].tolist() if len(bottom_df) > 0 else [],
                                "values": bottom_df['value'].tolist() if len(bottom_df) > 0 else []
                            }
                        }
                    except:
                        pass
                
                if top_countries:
                    statistics["top_countries"] = top_countries
            except:
                pass
    
    # Add SDG targets context
    statistics["sdg_targets"] = {
        "MMR": {"target": 70, "unit": "per 100,000 live births", "description": "Maternal mortality ratio target"},
        "Under-five mortality": {"target": 25, "unit": "per 1,000 live births", "description": "Under-five mortality rate target"},
        "Neonatal mortality": {"target": 12, "unit": "per 1,000 live births", "description": "Neonatal mortality rate target"}
    }
    
    return statistics


def render_reports_page():
    """Render the reports page"""
    # Get current health topic and language
    health_topic = st.session_state.get("indicator_type", "Maternal Mortality")
    selected_language = st.session_state.get("selected_language", "English")
    
    # Display current settings
    st.markdown(f"""
    <div style="margin-bottom: 1rem; padding: 1rem; background: linear-gradient(135deg, #0066CC 0%, #004499 100%); border-radius: 10px; color: white;">
        <strong>Health Topic:</strong> {health_topic} | <strong>Language:</strong> {selected_language}
    </div>
    """, unsafe_allow_html=True)
    
    current_lang = st.session_state.get("selected_language", "English")
    st.markdown(f'<h2 class="section-header">{get_translation("generate_reports", current_lang)}</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning(get_translation("please_initialize", current_lang))
        return
    
    # Get analytics and pipeline based on health topic
    if health_topic == "Tuberculosis" and hasattr(st.session_state, 'tb_analytics') and st.session_state.tb_analytics is not None:
        analytics = st.session_state.tb_analytics
        pipeline = st.session_state.tb_pipeline
    elif hasattr(st.session_state, 'analytics') and st.session_state.analytics is not None:
        analytics = st.session_state.analytics
        pipeline = st.session_state.pipeline
    else:
        st.error(f"Analytics system not initialized for {health_topic}. {get_translation('please_initialize', current_lang)}")
        return
    
    if analytics is None or pipeline is None:
        st.error(f"Analytics or Pipeline object is None. {get_translation('please_initialize', current_lang)}")
        return
    
    st.markdown(f"### {get_translation('generate_llm_report', current_lang)}")
    st.info(f"💡 {get_translation('reports_info', current_lang)}")
    
    # API Key configuration (load from environment variable or Streamlit secrets)
    if "openrouter_api_key" not in st.session_state:
        api_key = None
        
        # Method 1: Try Streamlit secrets (for Streamlit Cloud deployment)
        try:
            if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
                api_key = st.secrets['OPENROUTER_API_KEY']
        except Exception:
            pass
        
        # Method 2: Try environment variable
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Method 3: Try to read directly from .env file (for local development)
        if not api_key:
            env_paths = [
                os.path.join(os.path.dirname(__file__), '.env'),
                os.path.join(os.getcwd(), '.env'),
                '.env'
            ]
            
            for env_path in env_paths:
                if os.path.exists(env_path):
                    try:
                        with open(env_path, 'r') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    if line.startswith('OPENROUTER_API_KEY='):
                                        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                                        break
                        if api_key:
                            break
                    except Exception as e:
                        continue
        
        if not api_key:
            st.error("⚠️ OPENROUTER_API_KEY not found.")
            st.info("""
            **For Local Development:**
            - Create a `.env` file in the project root
            - Add: `OPENROUTER_API_KEY=your_key_here`
            
            **For Streamlit Cloud:**
            - Go to Settings → Secrets
            - Add: `OPENROUTER_API_KEY = "your_key_here"`
            """)
            st.stop()
        
        st.session_state.openrouter_api_key = api_key
    
    # Custom prompt input
    st.markdown("#### Customize Your Report")
    custom_prompt = st.text_area(
        "Specify what you need in the report (optional)",
        placeholder="Example: Focus on trends, compare with regional averages, highlight countries off-track for 2030 targets, provide actionable recommendations for policymakers...",
        height=100,
        help="Describe what specific aspects you want the report to cover. The AI will tailor the report accordingly."
    )
    
    # Report language selector syncs with main language selector
    # No need for separate selector - use the main one from session state
    report_language = selected_language
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Get countries based on health topic
        if health_topic == "Tuberculosis" and hasattr(st.session_state, 'tb_pipeline'):
            countries = st.session_state.tb_pipeline.get_countries()
        else:
            countries = pipeline.get_countries()
        
        selected_country = st.selectbox(
            "Select Country (optional - leave blank for regional report)",
            [None] + sorted(countries)
        )
    
    with col2:
        report_type = st.selectbox(
            "Report Type",
            ["comprehensive", "summary", "executive"],
            index=0
        )
    
    with col3:
        st.write("")  # Spacing
        generate_btn = st.button("📋 Generate Report", use_container_width=True)
    
    if generate_btn:
        try:
            # Initialize LLM report generator
            llm_generator = LLMReportGenerator(st.session_state.openrouter_api_key)
            
            # Collect statistics based on health topic
            with st.spinner("Collecting statistics..."):
                statistics = _collect_statistics_for_llm(analytics, pipeline, selected_country, health_topic)
            
            # Generate report using LLM with selected language from session state
            with st.spinner(f"🤖 Generating AI-powered report in {selected_language}... This may take a moment."):
                report = llm_generator.generate_report(
                    statistics=statistics,
                    report_type=report_type,
                    country=selected_country,
                    custom_requirements=custom_prompt if custom_prompt else None,
                    language=selected_language  # Use language from session state
                )
            
            st.markdown("### Generated Report")
            st.markdown("---")
            
            # Display AI disclaimer notice before report
            current_lang = st.session_state.get("selected_language", "English")
            disclaimer_texts = {
                "English": "**AI-Generated Content**: This report was generated using artificial intelligence. Please review all content for accuracy and verify any critical information.",
                "French": "**Contenu Généré par IA** : Ce rapport a été généré à l'aide de l'intelligence artificielle. Veuillez examiner tout le contenu pour vérifier son exactitude.",
                "Portuguese": "**Conteúdo Gerado por IA**: Este relatório foi gerado usando inteligência artificial. Por favor, revise todo o conteúdo para verificar a precisão.",
                "Spanish": "**Contenido Generado por IA**: Este informe fue generado usando inteligencia artificial. Por favor, revise todo el contenido para verificar la precisión."
            }
            st.info(disclaimer_texts.get(current_lang, disclaimer_texts["English"]))
            
            # Generate and display charts/maps for the report
            if health_topic == "Tuberculosis":
                # TB-specific charts
                try:
                    from tb_chart_generator import TBChartGenerator
                    tb_chart_gen = TBChartGenerator(analytics)
                    
                    # Show trend chart if country selected
                    if selected_country:
                        indicator = "TB Notifications (Total New Cases)"
                        trend_chart = tb_chart_gen.create_trend_chart(selected_country, indicator)
                        if trend_chart:
                            st.plotly_chart(trend_chart, use_container_width=True)
                    
                    # Show regional map
                    map_chart = tb_chart_gen.create_map_chart("TB Notifications (Total New Cases)")
                    if map_chart:
                        st.plotly_chart(map_chart, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not generate charts: {str(e)}")
            else:
                # Mortality charts
                try:
                    from chart_generator import ChartGenerator
                    chart_gen = ChartGenerator(analytics)
                    
                    if selected_country:
                        indicator = "Under-five mortality rate"
                        trend_chart = chart_gen.create_trend_chart(selected_country, indicator)
                        if trend_chart:
                            st.plotly_chart(trend_chart, use_container_width=True)
                except Exception as e:
                    pass  # Charts optional
            
            # Display report with markdown rendering
            st.markdown(report)
            
            # Download button
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"mortality_report_{selected_country or 'regional'}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            st.info("Falling back to basic report generation...")
            
            # Fallback to basic report
            with st.spinner("Generating basic report..."):
                report = analytics.generate_summary_report(selected_country)
            
            st.markdown("### Report (Basic)")
            st.text_area("Report Content", report, height=400)
            
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"mortality_report_{selected_country or 'regional'}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )


def render_visualizer_page():
    """Render the interactive visualizer page"""
    # Get current health topic and language
    health_topic = st.session_state.get("indicator_type", "Maternal Mortality")
    selected_language = st.session_state.get("selected_language", "English")
    
    # Display current settings
    st.markdown(f"""
    <div style="margin-bottom: 1rem; padding: 1rem; background: linear-gradient(135deg, #0066CC 0%, #004499 100%); border-radius: 10px; color: white;">
        <strong>Health Topic:</strong> {health_topic} | <strong>Language:</strong> {selected_language}
    </div>
    """, unsafe_allow_html=True)
    
    current_lang = st.session_state.get("selected_language", "English")
    st.markdown(f'<h2 class="section-header">{get_translation("interactive_visualizer", current_lang)}</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning(get_translation("please_initialize", current_lang))
        return
    
    # Get visualizer, analytics, and pipeline based on health topic
    if health_topic == "Tuberculosis" and hasattr(st.session_state, 'tb_visualizer') and st.session_state.tb_visualizer is not None:
        visualizer = st.session_state.tb_visualizer
        analytics = st.session_state.tb_analytics
        pipeline = st.session_state.tb_pipeline
    elif hasattr(st.session_state, 'visualizer') and st.session_state.visualizer is not None:
        visualizer = st.session_state.visualizer
        analytics = st.session_state.analytics
        pipeline = st.session_state.pipeline
    else:
        st.error(f"Visualizer system not initialized for {health_topic}. {get_translation('please_initialize', current_lang)}")
        return
    
    if visualizer is None or analytics is None or pipeline is None:
        st.error(f"System not properly initialized. {get_translation('please_initialize', current_lang)}")
        return
    
    # Update description based on health topic
    if health_topic == "Tuberculosis":
        description = """
        Create customized TB visualizations with full control over:
        - Country selection (47 AFRO countries)
        - TB indicator selection (Notifications, Outcomes)
        - Prediction methods
        - Chart types (Chart or Map)
        - Year ranges
        """
    else:
        description = """
        Create customized visualizations with full control over:
        - Country selection
        - Indicator selection
        - Prediction methods
        - Chart types (Chart or Map)
        - Year ranges
        """
    
    st.markdown(description)
    
    # Control Panel
    with st.expander("⚙️ Chart Controls", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Country selection
            countries = pipeline.get_countries()
            selected_country = st.selectbox(
                "Select Country",
                countries,
                index=0 if countries else None
            )
            
            # Indicator selection - adapt based on health topic
            if health_topic == "Tuberculosis":
                indicators = [
                    "TB Notifications (Total New Cases)",
                    "New Smear-Positive Cases",
                    "New Smear-Negative Cases",
                    "New Extrapulmonary Cases",
                    "Treatment Success Rate - New Cases (%)",
                    "Treatment Success Rate (%)"
                ]
            else:
                indicators = pipeline.get_indicators()
            selected_indicator = st.selectbox(
                "Select Indicator",
                indicators,
                index=0 if indicators else None
            )
        
        with col2:
            # Visualization type
            viz_type = st.radio(
                "Visualization Type",
                ["Chart", "Map"],
                horizontal=True
            )
            
            # Prediction method (for charts)
            if viz_type == "Chart":
                prediction_method = st.selectbox(
                    "Prediction Method",
                    ["linear", "exponential", "polynomial", "moving_average"],
                    help="Choose how to predict future values"
                )
            else:
                prediction_method = None
        
        # Additional options for charts
        if viz_type == "Chart":
            col3, col4 = st.columns(2)
            
            with col3:
                show_projection = st.checkbox(
                    "Show Projections (2024-2030)",
                    value=True,
                    help="Display projected values with light shading"
                )
            
            with col4:
                start_year = st.slider(
                    "Start Year (Observed)",
                    min_value=2000,
                    max_value=2023,
                    value=2000,
                    help="Start year for observed data"
                )
            
            end_year = st.slider(
                "End Year (Projections)",
                min_value=2024,
                max_value=2030,
                value=2030,
                help="End year for projections"
            )
    
    # Generate visualization
    if selected_country and selected_indicator:
        if viz_type == "Chart":
            st.markdown("### Customized Trend Chart")
            
            chart = visualizer.create_custom_trend_chart(
                country=selected_country,
                indicator=selected_indicator,
                prediction_method=prediction_method,
                show_projection=show_projection,
                start_year=start_year,
                end_year=end_year
            )
            
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                
                # Chart information
                st.info(f"""
                **Chart Details:**
                - **Country:** {selected_country}
                - **Indicator:** {selected_indicator}
                - **Observed Period:** {start_year}-2023 (blue line)
                - **Projection Period:** 2024-{end_year} (orange dashed line with light shading)
                - **Prediction Method:** {prediction_method.title()}
                """)
            else:
                st.warning(f"No data available for {selected_indicator} in {selected_country}")
        
        else:  # Map
            st.markdown("### Country Map Visualization")
            
            map_year = st.slider(
                "Select Year for Map",
                min_value=2000,
                max_value=2023,
                value=2023
            )
            
            # Use appropriate method based on visualizer type
            if health_topic == "Tuberculosis":
                map_chart = visualizer.create_map(
                    indicator=selected_indicator,
                    year=map_year
                )
            else:
                map_chart = visualizer.create_country_map(
                    indicator=selected_indicator,
                    year=map_year
                )
            
            if map_chart:
                st.plotly_chart(map_chart, use_container_width=True)
                
                st.info(f"""
                **Map Details:**
                - **Indicator:** {selected_indicator}
                - **Year:** {map_year}
                - **Color Scale:** Darker colors indicate higher values
                """)
            else:
                st.warning(f"No map data available for {selected_indicator}")
    
    # Multi-country comparison option
    st.markdown("---")
    st.markdown("### Multi-Country Comparison")
    
    compare_countries = st.multiselect(
        "Select Countries to Compare",
        countries,
        default=countries[:3] if len(countries) >= 3 else countries
    )
    
    if len(compare_countries) > 0 and selected_indicator:
        compare_chart = visualizer.create_multi_country_comparison(
            countries=compare_countries,
            indicator=selected_indicator,
            show_projection=show_projection if viz_type == "Chart" else True,
            prediction_method=prediction_method if viz_type == "Chart" else "linear"
        )
        
        if compare_chart:
            st.plotly_chart(compare_chart, use_container_width=True)


def render_about_page():
    """Render the about page"""
    current_lang = st.session_state.get("selected_language", "English")
    st.markdown(f'<h2 class="section-header">{get_translation("about_who_afro_title", current_lang)}</h2>', unsafe_allow_html=True)
    
    st.markdown(f"""
    ### {get_translation("mission", current_lang)}
    
    {get_translation("mission_desc", current_lang)}
    
    ### {get_translation("data_sources", current_lang)}
    
    {get_translation("data_sources_desc", current_lang)}
    - {get_translation("data_source_1", current_lang)}
    - {get_translation("data_source_2", current_lang)}
    - {get_translation("data_source_3", current_lang)}
    - {get_translation("data_source_4", current_lang)}
    
    ### {get_translation("indicators_tracked", current_lang)}
    
    - **{get_translation("neonatal_mortality", current_lang)}**: {get_translation("neonatal_desc", current_lang)}
    - **{get_translation("infant_mortality", current_lang)}**: {get_translation("infant_desc", current_lang)}
    - **{get_translation("under_five_mortality", current_lang)}**: {get_translation("under_five_desc", current_lang)}
    - **{get_translation("maternal_mortality", current_lang)}**: {get_translation("maternal_desc", current_lang)}
    - **{get_translation("stillbirth_rate", current_lang)}**: {get_translation("stillbirth_desc", current_lang)}
    
    ### {get_translation("targets_2030", current_lang)}
    
    {get_translation("targets_desc", current_lang)}
    - {get_translation("target_neonatal", current_lang)}
    - {get_translation("target_under_five", current_lang)}
    - {get_translation("target_maternal", current_lang)}
    
    ### {get_translation("contact", current_lang)}
    
    {get_translation("contact_desc", current_lang)}
    
    ### {get_translation("technical_info", current_lang)}
    
    - **{get_translation("platform", current_lang)}**: Streamlit
    - **{get_translation("data_processing", current_lang)}**: Python, Pandas
    - **{get_translation("analytics_engine", current_lang)}**: Custom-built mortality analytics
    - **{get_translation("ai_chatbot_tech", current_lang)}**: Natural language processing for data queries
    """)


def main():
    """Main application"""
    
    # Render header
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### WHO AFRO")
        st.markdown("**Data Hub Analytics**")
        
        # Health Topic Selection
        st.markdown("### Health Topic")
        indicator_type = st.selectbox(
            "Select Health Topic",
            ["Tuberculosis", "Maternal Mortality", "Child Mortality"],
            index=1,  # Default to Maternal Mortality
            key="indicator_type_select",
            help="Choose the health topic to analyze"
        )
        
        # Reinitialize if indicator type changed
        if "indicator_type" not in st.session_state:
            st.session_state.indicator_type = indicator_type
        elif st.session_state.indicator_type != indicator_type:
            st.session_state.data_loaded = False
            st.session_state.indicator_type = indicator_type
        
        current_lang = st.session_state.get("selected_language", "English")
        st.markdown(f"### {get_translation('navigation', current_lang)}")
        
        if st.button(f"🏠 {get_translation('home', current_lang)}", use_container_width=True, key="nav_home"):
            st.session_state.current_page = 'Home'
            st.rerun()
        
        if st.button(f"📊 {get_translation('dashboard', current_lang)}", use_container_width=True, key="nav_dashboard"):
            st.session_state.current_page = 'Dashboard'
            st.rerun()
        
        if st.button(f"🤖 {get_translation('chatbot', current_lang)}", use_container_width=True, key="nav_chatbot"):
            st.session_state.current_page = 'Chatbot'
            st.rerun()
        
        if st.button(f"📋 {get_translation('reports', current_lang)}", use_container_width=True, key="nav_reports"):
            st.session_state.current_page = 'Reports'
            st.rerun()
        
        if st.button(f"📈 {get_translation('visualizer', current_lang)}", use_container_width=True, key="nav_visualizer"):
            st.session_state.current_page = 'Visualizer'
            st.rerun()
        
        if st.button(f"ℹ️ {get_translation('about', current_lang)}", use_container_width=True, key="nav_about"):
            st.session_state.current_page = 'About'
            st.rerun()
        
        st.markdown("---")
        
        # System status
        current_lang = st.session_state.get("selected_language", "English")
        st.markdown(f"### {get_translation('system_status', current_lang)}")
        if not st.session_state.data_loaded:
            if st.button(f"🚀 {get_translation('initialize_system', current_lang)}", use_container_width=True):
                if initialize_system(indicator_type):
                    st.success(f"{indicator_type} {get_translation('system_ready', current_lang).lower()}!")
                    st.rerun()
        else:
            st.markdown(f'<div style="display: flex; align-items: center; color: green;"><span class="green-circle"></span><span style="margin-left: 8px;">{get_translation("system_ready", current_lang)}</span></div>', unsafe_allow_html=True)
            current_indicator = st.session_state.get("indicator_type", indicator_type)
            st.caption(f"{get_translation('health_topic', current_lang)}: {current_indicator}")
            
            if current_indicator == "Tuberculosis" and hasattr(st.session_state, 'tb_pipeline'):
                summary = st.session_state.tb_pipeline.get_data_summary()
                st.caption(f"Region: {summary.get('region', 'AFRO')}")
                st.caption(f"Countries: {summary['countries']}")
                st.caption(f"Indicators: {summary['indicators']}")
                st.caption(f"Notifications Records: {summary['tb_notifications_records']:,}")
                st.caption(f"Outcomes Records: {summary['tb_outcomes_records']:,}")
            elif hasattr(st.session_state, 'pipeline') and st.session_state.pipeline:
                summary = st.session_state.pipeline.get_data_summary()
                st.caption(f"Countries: {summary['countries']}")
                st.caption(f"Indicators: {summary['indicators']}")
                st.caption(f"Records: {summary['mortality_records']:,}")
        
        st.markdown("---")
        current_lang = st.session_state.get("selected_language", "English")
        st.markdown(f"### {get_translation('quick_links', current_lang)}")
        st.markdown("""
        - [WHO AFRO Website](https://www.afro.who.int/)
        - [Global Health Observatory](https://www.who.int/data/gho)
        - [SDG Targets](https://www.who.int/sdg/targets/en/)
        """)
    
    # Language selector - appears on all pages
    # Initialize language in session state if not exists
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    
    # Only show top-right language selector on non-home pages (home has it in hero card)
    if st.session_state.current_page != 'Home':
        current_lang = st.session_state.selected_language
        languages = {
            "English": ("🇬🇧", "ENG"),
            "French": ("🇫🇷", "FR"),
            "Portuguese": ("🇵🇹", "PT"),
            "Spanish": ("🇪🇸", "ES")
        }
        
        # Create fixed position language selector
        col_spacer, col_lang = st.columns([10, 1])
        with col_lang:
            lang_options = list(languages.keys())
            current_index = lang_options.index(current_lang) if current_lang in lang_options else 0
            
            selected_lang = st.selectbox(
                "",
                options=lang_options,
                index=current_index,
                format_func=lambda x: f"{languages[x][0]} {languages[x][1]}",
                key="global_language_selector",
                label_visibility="collapsed"
            )
            
            # Update session state if language changed
            if selected_lang != current_lang:
                st.session_state.selected_language = selected_lang
                st.rerun()
        
        # Add CSS to style the global language selector
        st.markdown("""
        <style>
        div[data-testid="stSelectbox"]:has(select[id*="global_language_selector"]) {
            position: fixed !important;
            top: 8px !important;
            right: 8px !important;
            z-index: 9999 !important;
            width: fit-content !important;
            min-width: auto !important;
            font-size: 0.7rem !important;
            background: rgba(255, 255, 255, 0.98) !important;
            padding: 3px 6px !important;
            border-radius: 6px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="global_language_selector"]) > div {
            width: fit-content !important;
            min-width: auto !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="global_language_selector"]) > div > div {
            font-size: 0.7rem !important;
            padding: 3px 8px !important;
            min-height: auto !important;
            height: auto !important;
            white-space: nowrap !important;
            width: fit-content !important;
            min-width: auto !important;
            line-height: 1.3 !important;
            font-weight: 600 !important;
            color: #0066CC !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="global_language_selector"]) select {
            font-size: 0.7rem !important;
            padding: 3px 6px !important;
            width: fit-content !important;
            min-width: auto !important;
            height: auto !important;
            font-weight: 600 !important;
        }
        div[data-testid="stSelectbox"]:has(select[id*="global_language_selector"]) > label {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Render current page
    if st.session_state.current_page == 'Home':
        render_home_page()
    elif st.session_state.current_page == 'Dashboard':
        render_dashboard_page()
    elif st.session_state.current_page == 'Chatbot':
        render_chatbot_page()
    elif st.session_state.current_page == 'Reports':
        render_reports_page()
    elif st.session_state.current_page == 'Visualizer':
        render_visualizer_page()
    elif st.session_state.current_page == 'About':
        render_about_page()


if __name__ == "__main__":
    main()

