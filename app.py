"""
Streamlit Web Application for Mortality Analytics Chatbot
"""

import streamlit as st
import pandas as pd
from data_pipeline import MortalityDataPipeline
from analytics import MortalityAnalytics
from chatbot import MortalityChatbot
import sys


# Page configuration
st.set_page_config(
    page_title="Mortality Analytics Chatbot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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


def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.title("📊 Mortality Analytics")
        st.markdown("---")
        
        # Initialize button
        if not st.session_state.data_loaded:
            if st.button("🚀 Initialize System", use_container_width=True):
                if initialize_system():
                    st.success("System initialized successfully!")
                    st.rerun()
        else:
            st.success("✅ System Ready")
            
            st.markdown("---")
            st.subheader("Quick Actions")
            
            if st.button("📋 Generate Summary Report", use_container_width=True):
                report = st.session_state.analytics.generate_summary_report()
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "Generate summary report"
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": report
                })
                st.rerun()
            
            if st.button("🔮 View Projections", use_container_width=True):
                analysis = st.session_state.analytics.analyze_projections()
                response = st.session_state.chatbot._handle_projections("projections")
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "View projections"
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()
            
            if st.button("❓ Help", use_container_width=True):
                help_text = st.session_state.chatbot.get_help()
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": help_text
                })
                st.rerun()
            
            st.markdown("---")
            st.subheader("Data Info")
            if st.session_state.data_loaded:
                summary = st.session_state.pipeline.get_data_summary()
                st.write(f"**Countries:** {summary['countries']}")
                st.write(f"**Indicators:** {summary['indicators']}")
                st.write(f"**Mortality Records:** {summary['mortality_records']:,}")
                st.write(f"**MMR Records:** {summary['mmr_records']:,}")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This chatbot helps you analyze mortality data 
        for African countries. Ask questions in natural 
        language to get insights and reports.
        """)
    
    # Main content area
    st.title("🤖 Mortality Analytics Chatbot")
    st.markdown("Ask questions about mortality data for African countries in natural language.")
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.info("👈 Please initialize the system from the sidebar to begin.")
        st.markdown("""
        ### What you can do:
        - 📊 Get statistics for specific countries
        - 📈 Compare multiple countries
        - 📉 Analyze trends over time
        - 🔮 View projections for 2030
        - 🏆 Find top countries by indicators
        - 📋 Generate comprehensive reports
        """)
        return
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
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
            with st.spinner("Analyzing..."):
                response = st.session_state.chatbot.process_query(user_query)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            st.rerun()
    
    # Example queries section
    with st.expander("💡 Example Queries"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Country Statistics:**
            - What are the statistics for Kenya?
            - Tell me about Angola
            - How is Nigeria doing?
            
            **Comparisons:**
            - Compare Kenya and Uganda
            - Compare Kenya, Uganda, and Tanzania
            
            **Trends:**
            - What is the trend for Kenya?
            - How has neonatal mortality changed in Angola?
            """)
        
        with col2:
            st.markdown("""
            **Projections:**
            - Show me projections for 2030
            - Which countries are on track?
            
            **Top Countries:**
            - Top 10 countries by under-five mortality rate
            - Which countries have the highest MMR?
            
            **Summaries:**
            - Give me a summary
            - Regional overview
            """)


if __name__ == "__main__":
    main()


