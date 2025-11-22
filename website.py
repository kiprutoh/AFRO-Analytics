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
from datetime import datetime
import sys


# Page configuration
st.set_page_config(
    page_title="WHO AFRO Data Hub - Mortality Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for WHO AFRO branding
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0066CC 0%, #004499 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .who-logo {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #0066CC;
        margin: 1rem 0;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #0066CC;
    }
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .section-header {
        color: #0066CC;
        border-bottom: 2px solid #0066CC;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .info-box {
        background: #E8F4F8;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #0066CC;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #0066CC;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 2rem;
    }
    .stButton>button:hover {
        background-color: #004499;
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


def initialize_system():
    """Initialize the data pipeline and analytics system"""
    try:
        with st.spinner("Loading data and initializing system..."):
            pipeline = MortalityDataPipeline()
            pipeline.load_data()
            
            analytics = MortalityAnalytics(pipeline)
            chatbot = MortalityChatbot(analytics)
            
            st.session_state.pipeline = pipeline
            st.session_state.analytics = analytics
            st.session_state.chatbot = chatbot
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
    """Render the analytics dashboard"""
    st.markdown('<h2 class="section-header">Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning("Please initialize the system first from the sidebar.")
        return
    
    analytics = st.session_state.analytics
    pipeline = st.session_state.pipeline
    
    # Regional Summary
    st.markdown("### Regional Overview")
    summary = analytics.get_regional_summary()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Key Indicators Summary")
        for indicator, data in list(summary["indicators"].items())[:5]:
            st.markdown(f"""
            **{indicator}**
            - Mean: {data['mean_value']:.2f}
            - Range: {data['min_value']:.2f} - {data['max_value']:.2f}
            """)
    
    with col2:
        st.markdown("#### MMR Summary")
        if summary.get("mmr_summary"):
            mmr = summary["mmr_summary"]
            st.metric("Mean MMR", f"{mmr['mean_mmr']:.2f}")
            st.metric("Median MMR", f"{mmr['median_mmr']:.2f}")
            st.metric("Range", f"{mmr['min_mmr']:.2f} - {mmr['max_mmr']:.2f}")
    
    # Top Countries with Visualization
    st.markdown("### Top Countries Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Highest Under-Five Mortality")
        top_high = analytics.get_top_countries_by_indicator("Under-five mortality rate", 10, ascending=False)
        if len(top_high) > 0:
            # Display chart
            st.bar_chart(top_high.set_index('country')['value'])
            st.dataframe(top_high[['country', 'value']].rename(columns={'value': 'Rate'}), use_container_width=True)
    
    with col2:
        st.markdown("#### Lowest Under-Five Mortality")
        top_low = analytics.get_top_countries_by_indicator("Under-five mortality rate", 10, ascending=True)
        if len(top_low) > 0:
            # Display chart
            st.bar_chart(top_low.set_index('country')['value'])
            st.dataframe(top_low[['country', 'value']].rename(columns={'value': 'Rate'}), use_container_width=True)
    
    # Country Comparison Chart
    st.markdown("### Country Comparison")
    selected_countries = st.multiselect(
        "Select countries to compare",
        pipeline.get_countries(),
        default=pipeline.get_countries()[:5] if len(pipeline.get_countries()) >= 5 else pipeline.get_countries()
    )
    
    if selected_countries:
        indicator_select = st.selectbox(
            "Select indicator",
            ["Under-five mortality rate", "Infant mortality rate", "Neonatal mortality rate"]
        )
        
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
            st.bar_chart(comp_df.set_index('country')['value'])
    
    # Projections Analysis
    st.markdown("### 2030 Projections Analysis")
    proj_analysis = analytics.analyze_projections()
    
    if proj_analysis.get("mmr_projections"):
        mmr_proj = proj_analysis["mmr_projections"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("On Track", mmr_proj['on_track_count'])
        with col2:
            st.metric("Off Track", mmr_proj['off_track_count'])
        with col3:
            st.metric("Avg Projected MMR 2030", f"{mmr_proj['avg_proj_2030']:.2f}")
        
        if mmr_proj.get("countries_on_track"):
            st.markdown("**Countries On Track:**")
            st.write(", ".join(mmr_proj['countries_on_track']))


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
    elif st.session_state.current_page == 'About':
        render_about_page()


if __name__ == "__main__":
    main()

