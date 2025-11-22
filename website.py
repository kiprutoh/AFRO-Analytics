"""
WHO AFRO Data Hub Analytics Website
Comprehensive web application for mortality analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
from data_pipeline import MortalityDataPipeline
from analytics import MortalityAnalytics
from chatbot import MortalityChatbot
from chart_generator import ChartGenerator
from interactive_visualizer import InteractiveVisualizer
from datetime import datetime
import sys


# Page configuration
st.set_page_config(
    page_title="WHO AFRO Data Hub - Mortality Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS for WHO AFRO branding with animations and gradients
st.markdown("""
<style>
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


def initialize_system():
    """Initialize the data pipeline and analytics system"""
    try:
        with st.spinner("Loading data and initializing system..."):
            pipeline = MortalityDataPipeline()
            pipeline.load_data()
            
            analytics = MortalityAnalytics(pipeline)
            chatbot = MortalityChatbot(analytics)
            visualizer = InteractiveVisualizer(analytics)
            
            st.session_state.pipeline = pipeline
            st.session_state.analytics = analytics
            st.session_state.chatbot = chatbot
            st.session_state.visualizer = visualizer
            st.session_state.data_loaded = True
            
        return True
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return False


def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <div class="who-logo">🌍</div>
        <h1>WHO AFRO Data Hub</h1>
        <h2>Mortality Analytics Platform</h2>
        <p>Comprehensive data analysis and insights for maternal and child mortality in Africa</p>
    </div>
    """, unsafe_allow_html=True)


def render_home_page():
    """Render the home page"""
    st.markdown("## Welcome to WHO AFRO Data Hub")
    
    st.markdown("""
    <div class="info-box">
        <h3>About WHO AFRO</h3>
        <p>The World Health Organization Regional Office for Africa (WHO AFRO) is committed to improving 
        health outcomes across the African continent. This platform provides comprehensive analytics and 
        insights into maternal and child mortality data to support evidence-based decision making.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key statistics
    if st.session_state.data_loaded:
        summary = st.session_state.pipeline.get_data_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{summary['countries']}</div>
                <div class="stat-label">Countries</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{summary['indicators']}</div>
                <div class="stat-label">Indicators</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{summary['mortality_records']:,}</div>
                <div class="stat-label">Mortality Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{summary['mmr_records']:,}</div>
                <div class="stat-label">MMR Records</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Key Features
    
    - 📊 **Comprehensive Analytics**: Analyze mortality trends across African countries
    - 🤖 **AI-Powered Chatbot**: Ask questions in natural language
    - 📈 **Trend Analysis**: Track progress over time
    - 🔮 **Projections**: Monitor progress towards 2030 targets
    - 📋 **Report Generation**: Generate detailed summary reports
    - 🌍 **Multi-Country Comparison**: Compare performance across countries
    
    ### Available Indicators
    
    - Neonatal mortality rate
    - Infant mortality rate
    - Under-five mortality rate
    - Maternal Mortality Ratio (MMR)
    - Mortality rates by age groups
    - Stillbirth rate
    
    ### Getting Started
    
    1. Navigate to the **Analytics Dashboard** to explore data visualizations
    2. Use the **AI Chatbot** to ask questions about the data
    3. Generate **Reports** for specific countries or regions
    """)


def render_dashboard_page():
    """Render the modern analytics dashboard"""
    st.markdown('<h2 class="section-header">📊 Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning("Please initialize the system first from the sidebar.")
        return
    
    analytics = st.session_state.analytics
    pipeline = st.session_state.pipeline
    
    # Regional Summary with Modern Cards
    st.markdown("""
    <div class="dashboard-card">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">🌍 Regional Overview</h3>
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
                <div class="stat-value">{mmr['mean_mmr']:.0f}</div>
                <div class="stat-label">Mean MMR</div>
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
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">📈 Key Indicators Summary</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        for indicator, data in list(summary["indicators"].items())[:5]:
            st.markdown(f"""
            <div class="info-box hover-lift">
                <h4 style="color: #0066CC; margin-bottom: 0.5rem; font-size: 1.1rem;">{indicator}</h4>
                <p style="margin: 0.25rem 0; font-size: 0.95rem;"><strong>Mean:</strong> <span style="color: #0066CC; font-weight: 600;">{data['mean_value']:.2f}</span></p>
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
            <h4 style="color: #00CC66; margin-bottom: 1rem; font-size: 1.2rem;">✅ Lowest Under-Five Mortality</h4>
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
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">🔮 2030 Projections Analysis</h3>
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
                <h4 style="color: #0066CC; margin-bottom: 0.5rem; font-size: 1.1rem;">✅ Countries On Track</h4>
                <p style="margin: 0; font-size: 0.95rem;">""" + ", ".join(mmr_proj['countries_on_track']) + """</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Country Comparison with Interactive Chart
    st.markdown("""
    <div class="dashboard-card" style="margin-top: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1.5rem; font-size: 1.5rem;">📊 Country Comparison</h3>
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
    st.markdown('<h2 class="section-header">AI Analytics Chatbot</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning("Please initialize the system first from the sidebar.")
        return
    
    chatbot = st.session_state.chatbot
    
    st.markdown("""
    Ask questions about mortality data in natural language. The chatbot can help you:
    - Get statistics for specific countries
    - Compare countries
    - Analyze trends
    - View projections
    - Generate reports
    """)
    
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
                    if message["content"].get("chart"):
                        st.plotly_chart(message["content"]["chart"], use_container_width=True)
                else:
                    st.write(message["content"])
    
    # Chat input
    user_query = st.chat_input("Ask a question about mortality data...")
    
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
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        - What are the statistics for Kenya?
        - Compare Kenya and Uganda
        - What is the trend for neonatal mortality in Angola?
        - Show me projections for 2030
        - Top 10 countries by under-five mortality rate
        - Generate a summary report for Nigeria
        """)


def render_reports_page():
    """Render the reports page"""
    st.markdown('<h2 class="section-header">Generate Reports</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning("Please initialize the system first from the sidebar.")
        return
    
    analytics = st.session_state.analytics
    pipeline = st.session_state.pipeline
    
    st.markdown("### Generate Summary Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        countries = pipeline.get_countries()
        selected_country = st.selectbox(
            "Select Country (optional - leave blank for regional report)",
            [None] + sorted(countries)
        )
    
    with col2:
        st.write("")  # Spacing
        generate_btn = st.button("📋 Generate Report", use_container_width=True)
    
    if generate_btn:
        with st.spinner("Generating report..."):
            report = analytics.generate_summary_report(selected_country)
        
        st.markdown("### Report")
        st.text_area("Report Content", report, height=400)
        
        # Download button
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"mortality_report_{selected_country or 'regional'}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )


def render_visualizer_page():
    """Render the interactive visualizer page"""
    st.markdown('<h2 class="section-header">Interactive Chart Visualizer</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning("Please initialize the system first from the sidebar.")
        return
    
    visualizer = st.session_state.visualizer
    pipeline = st.session_state.pipeline
    
    st.markdown("""
    Create customized visualizations with full control over:
    - Country selection
    - Indicator selection
    - Prediction methods
    - Chart types (Chart or Map)
    - Year ranges
    """)
    
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
            
            # Indicator selection
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
    st.markdown('<h2 class="section-header">About WHO AFRO Data Hub</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Mission
    
    The WHO AFRO Data Hub provides comprehensive analytics and insights into health data across 
    the African continent, with a focus on maternal and child mortality indicators.
    
    ### Data Sources
    
    This platform analyzes data from multiple sources including:
    - WHO Global Health Observatory
    - UNICEF Data
    - National Health Information Systems
    - Demographic and Health Surveys
    
    ### Indicators Tracked
    
    - **Neonatal Mortality Rate**: Deaths per 1,000 live births in the first 28 days
    - **Infant Mortality Rate**: Deaths per 1,000 live births in the first year
    - **Under-Five Mortality Rate**: Deaths per 1,000 live births before age 5
    - **Maternal Mortality Ratio (MMR)**: Deaths per 100,000 live births
    - **Stillbirth Rate**: Stillbirths per 1,000 total births
    
    ### 2030 Targets
    
    The platform tracks progress towards Sustainable Development Goal (SDG) targets:
    - Reduce neonatal mortality to at least 12 per 1,000 live births
    - Reduce under-five mortality to at least 25 per 1,000 live births
    - Reduce maternal mortality ratio to less than 70 per 100,000 live births
    
    ### Contact
    
    For questions or support, please contact WHO AFRO.
    
    ### Technical Information
    
    - **Platform**: Streamlit
    - **Data Processing**: Python, Pandas
    - **Analytics Engine**: Custom-built mortality analytics
    - **AI Chatbot**: Natural language processing for data queries
    """)


def main():
    """Main application"""
    
    # Render header
    render_header()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🌍 WHO AFRO")
        st.markdown("**Data Hub Analytics**")
        
        st.markdown("### Navigation")
        
        if st.button("🏠 Home", use_container_width=True, key="nav_home"):
            st.session_state.current_page = 'Home'
            st.rerun()
        
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state.current_page = 'Dashboard'
            st.rerun()
        
        if st.button("🤖 AI Chatbot", use_container_width=True, key="nav_chatbot"):
            st.session_state.current_page = 'Chatbot'
            st.rerun()
        
        if st.button("📋 Reports", use_container_width=True, key="nav_reports"):
            st.session_state.current_page = 'Reports'
            st.rerun()
        
        if st.button("📈 Interactive Charts", use_container_width=True, key="nav_visualizer"):
            st.session_state.current_page = 'Visualizer'
            st.rerun()
        
        if st.button("ℹ️ About", use_container_width=True, key="nav_about"):
            st.session_state.current_page = 'About'
            st.rerun()
        
        st.markdown("---")
        
        # System status
        st.markdown("### System Status")
        if not st.session_state.data_loaded:
            if st.button("🚀 Initialize System", use_container_width=True):
                if initialize_system():
                    st.success("System initialized!")
                    st.rerun()
        else:
            st.success("✅ System Ready")
            summary = st.session_state.pipeline.get_data_summary()
            st.caption(f"Countries: {summary['countries']}")
            st.caption(f"Indicators: {summary['indicators']}")
            st.caption(f"Records: {summary['mortality_records']:,}")
        
        st.markdown("---")
        st.markdown("### Quick Links")
        st.markdown("""
        - [WHO AFRO Website](https://www.afro.who.int/)
        - [Global Health Observatory](https://www.who.int/data/gho)
        - [SDG Targets](https://www.who.int/sdg/targets/en/)
        """)
    
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

