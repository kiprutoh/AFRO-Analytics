"""
Main Website for Mortality Analytics
Modern, professional interface with multi-language support
"""

import streamlit as st
import pandas as pd
from data_pipeline import MortalityDataPipeline
from analytics import MortalityAnalytics
from chatbot import MortalityChatbot
from interactive_visualizer import InteractiveVisualizer
import plotly.graph_objects as go

# Translations
TRANSLATIONS = {
    'ENG': {
        'title': 'African Mortality Analytics Dashboard',
        'subtitle': 'Comprehensive mortality data analysis and insights',
        'initialize': 'Initialize System',
        'home': 'Home',
        'dashboard': 'Dashboard',
        'chatbot': 'Chatbot',
        'reports': 'Reports',
        'about': 'About',
        'system_ready': 'System Ready',
        'loading': 'Loading data and initializing system...',
        'ask_question': 'Ask a question about mortality data...',
        'example_queries': 'Example Queries',
        'country_stats': 'Country Statistics',
        'comparisons': 'Comparisons',
        'trends': 'Trends',
        'projections': 'Projections',
        'top_countries': 'Top Countries',
        'data_info': 'Data Info',
        'countries': 'Countries',
        'indicators': 'Indicators',
        'mortality_records': 'Mortality Records',
        'mmr_records': 'MMR Records',
    },
    'PT': {
        'title': 'Painel de Análise de Mortalidade Africana',
        'subtitle': 'Análise abrangente de dados de mortalidade e insights',
        'initialize': 'Inicializar Sistema',
        'home': 'Início',
        'dashboard': 'Painel',
        'chatbot': 'Chatbot',
        'reports': 'Relatórios',
        'about': 'Sobre',
        'system_ready': 'Sistema Pronto',
        'loading': 'Carregando dados e inicializando sistema...',
        'ask_question': 'Faça uma pergunta sobre dados de mortalidade...',
        'example_queries': 'Consultas de Exemplo',
        'country_stats': 'Estatísticas do País',
        'comparisons': 'Comparações',
        'trends': 'Tendências',
        'projections': 'Projeções',
        'top_countries': 'Principais Países',
        'data_info': 'Informações de Dados',
        'countries': 'Países',
        'indicators': 'Indicadores',
        'mortality_records': 'Registros de Mortalidade',
        'mmr_records': 'Registros MMR',
    },
    'FR': {
        'title': 'Tableau de Bord d\'Analyse de la Mortalité Africaine',
        'subtitle': 'Analyse complète des données de mortalité et informations',
        'initialize': 'Initialiser le Système',
        'home': 'Accueil',
        'dashboard': 'Tableau de Bord',
        'chatbot': 'Chatbot',
        'reports': 'Rapports',
        'about': 'À Propos',
        'system_ready': 'Système Prêt',
        'loading': 'Chargement des données et initialisation du système...',
        'ask_question': 'Posez une question sur les données de mortalité...',
        'example_queries': 'Exemples de Requêtes',
        'country_stats': 'Statistiques des Pays',
        'comparisons': 'Comparaisons',
        'trends': 'Tendances',
        'projections': 'Projections',
        'top_countries': 'Principaux Pays',
        'data_info': 'Info de Données',
        'countries': 'Pays',
        'indicators': 'Indicateurs',
        'mortality_records': 'Enregistrements de Mortalité',
        'mmr_records': 'Enregistrements MMR',
    }
}

# Page configuration
st.set_page_config(
    page_title="African Mortality Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'ENG'
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if 'analytics' not in st.session_state:
    st.session_state.analytics = None
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'


def get_text(key):
    """Get translated text"""
    return TRANSLATIONS[st.session_state.language].get(key, key)


def language_selector():
    """Compact language selector in top right corner"""
    st.markdown("""
        <style>
        .language-selector {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 999999;
            background: white;
            border-radius: 8px;
            padding: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            display: flex;
            gap: 2px;
        }
        .lang-btn {
            background: #f0f2f6;
            border: none;
            padding: 6px 10px;
            cursor: pointer;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            color: #262730;
            transition: all 0.2s;
            min-width: 36px;
            text-align: center;
        }
        .lang-btn:hover {
            background: #e0e2e6;
            transform: translateY(-1px);
        }
        .lang-btn.active {
            background: #0066CC;
            color: white;
        }
        </style>
        <div class="language-selector">
            <button class="lang-btn {eng_active}" onclick="window.location.href='?lang=ENG'">ENG</button>
            <button class="lang-btn {pt_active}" onclick="window.location.href='?lang=PT'">PT</button>
            <button class="lang-btn {fr_active}" onclick="window.location.href='?lang=FR'">FR</button>
        </div>
    """.format(
        eng_active="active" if st.session_state.language == 'ENG' else "",
        pt_active="active" if st.session_state.language == 'PT' else "",
        fr_active="active" if st.session_state.language == 'FR' else ""
    ), unsafe_allow_html=True)
    
    # Handle language change via query params
    query_params = st.query_params
    if 'lang' in query_params:
        new_lang = query_params['lang']
        if new_lang in ['ENG', 'PT', 'FR'] and new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.rerun()


def initialize_system():
    """Initialize the data pipeline and analytics system"""
    try:
        with st.spinner(get_text('loading')):
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


def render_home_page():
    """Render home page"""
    st.title(get_text('title'))
    st.markdown(f"### {get_text('subtitle')}")
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👇 " + get_text('initialize'))
            if st.button("🚀 " + get_text('initialize'), use_container_width=True, type="primary"):
                if initialize_system():
                    st.success("✅ " + get_text('system_ready'))
                    st.rerun()
    else:
        # Show key statistics
        summary = st.session_state.pipeline.get_data_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=get_text('countries'),
                value=summary['countries']
            )
        
        with col2:
            st.metric(
                label=get_text('indicators'),
                value=summary['indicators']
            )
        
        with col3:
            st.metric(
                label=get_text('mortality_records'),
                value=f"{summary['mortality_records']:,}"
            )
        
        with col4:
            st.metric(
                label=get_text('mmr_records'),
                value=f"{summary['mmr_records']:,}"
            )
        
        st.markdown("---")
        
        # Feature cards
        st.markdown("### 📊 Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; height: 200px;">
                <h4>📈 Dashboard</h4>
                <p>Interactive visualizations with customizable charts, maps, and projections</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; height: 200px;">
                <h4>🤖 Chatbot</h4>
                <p>Ask questions in natural language and get instant insights</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="padding: 20px; background: #f0f2f6; border-radius: 10px; height: 200px;">
                <h4>📋 Reports</h4>
                <p>Generate comprehensive reports and summaries</p>
            </div>
            """, unsafe_allow_html=True)


def render_dashboard_page():
    """Render dashboard page"""
    st.title("📊 " + get_text('dashboard'))
    
    if not st.session_state.data_loaded:
        st.warning("Please initialize the system first from the Home page.")
        return
    
    # Dashboard controls
    col1, col2 = st.columns([1, 1])
    
    with col1:
        countries = st.session_state.pipeline.get_countries()
        selected_country = st.selectbox("Select Country", countries)
    
    with col2:
        indicators = st.session_state.analytics.mortality_df['indicator'].unique().tolist()
        selected_indicator = st.selectbox("Select Indicator", indicators)
    
    # Visualization options
    st.markdown("### Visualization Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        prediction_method = st.selectbox(
            "Prediction Method",
            ['linear', 'exponential', 'polynomial', 'moving_average']
        )
    
    with col2:
        show_projection = st.checkbox("Show Projections", value=True)
    
    with col3:
        end_year = st.slider("Projection End Year", 2024, 2035, 2030)
    
    # Create and display chart
    if selected_country and selected_indicator:
        fig = st.session_state.visualizer.create_custom_trend_chart(
            country=selected_country,
            indicator=selected_indicator,
            prediction_method=prediction_method,
            show_projection=show_projection,
            start_year=2000,
            end_year=end_year
        )
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for this selection")
    
    # Map visualization
    st.markdown("### Geographic View")
    
    if selected_indicator:
        map_year = st.slider("Select Year for Map", 2000, 2023, 2023)
        
        fig_map = st.session_state.visualizer.create_country_map(
            indicator=selected_indicator,
            year=map_year
        )
        
        if fig_map:
            st.plotly_chart(fig_map, use_container_width=True)


def render_chatbot_page():
    """Render chatbot page"""
    st.title("🤖 " + get_text('chatbot'))
    
    if not st.session_state.data_loaded:
        st.warning("Please initialize the system first from the Home page.")
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
        user_query = st.chat_input(get_text('ask_question'))
        
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
    
    # Example queries
    with st.expander("💡 " + get_text('example_queries')):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Country Statistics:**
            - What are the statistics for Kenya?
            - Tell me about Angola
            
            **Comparisons:**
            - Compare Kenya and Uganda
            - Compare Kenya, Uganda, and Tanzania
            
            **Trends:**
            - What is the trend for Kenya?
            - How has neonatal mortality changed?
            """)
        
        with col2:
            st.markdown("""
            **Projections:**
            - Show me projections for 2030
            - Which countries are on track?
            
            **Top Countries:**
            - Top 10 countries by under-five mortality
            
            **Summaries:**
            - Give me a summary
            - Regional overview
            """)


def render_reports_page():
    """Render reports page"""
    st.title("📋 " + get_text('reports'))
    
    if not st.session_state.data_loaded:
        st.warning("Please initialize the system first from the Home page.")
        return
    
    st.markdown("### Generate Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Generate Summary Report", use_container_width=True):
            with st.spinner("Generating report..."):
                report = st.session_state.analytics.generate_summary_report()
                st.markdown(report)
    
    with col2:
        if st.button("🔮 Generate Projections Report", use_container_width=True):
            with st.spinner("Analyzing projections..."):
                analysis = st.session_state.analytics.analyze_projections()
                st.json(analysis)


def render_about_page():
    """Render about page"""
    st.title("ℹ️ " + get_text('about'))
    
    st.markdown("""
    ## African Mortality Analytics Dashboard
    
    This comprehensive platform provides advanced analytics and insights into mortality data 
    across African countries.
    
    ### Features:
    - 📊 Interactive visualizations with multiple chart types
    - 🤖 Natural language chatbot interface
    - 🗺️ Geographic mapping of mortality indicators
    - 🔮 Predictive analytics with multiple algorithms
    - 📋 Comprehensive reporting tools
    - 🌍 Multi-language support (English, Portuguese, French)
    
    ### Data Sources:
    - Mortality rates across African nations (2000-2023)
    - Maternal Mortality Ratio (MMR) data
    - SDG targets and projections to 2030
    
    ### Technologies:
    - Python, Streamlit, Plotly
    - Machine Learning for predictions
    - Natural Language Processing for chatbot
    
    ---
    
    **Version:** 1.0.0  
    **Last Updated:** November 2025
    """)


def main():
    """Main application"""
    
    # Language selector (always visible)
    language_selector()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        pages = {
            get_text('home'): '🏠',
            get_text('dashboard'): '📊',
            get_text('chatbot'): '🤖',
            get_text('reports'): '📋',
            get_text('about'): 'ℹ️'
        }
        
        for page_name, icon in pages.items():
            if st.button(f"{icon} {page_name}", use_container_width=True, 
                        key=page_name,
                        type="primary" if st.session_state.current_page == page_name else "secondary"):
                st.session_state.current_page = page_name
                st.rerun()
        
        st.markdown("---")
        
        # System status
        if st.session_state.data_loaded:
            st.success("✅ " + get_text('system_ready'))
            
            # Data info
            st.markdown("### " + get_text('data_info'))
            summary = st.session_state.pipeline.get_data_summary()
            st.write(f"**{get_text('countries')}:** {summary['countries']}")
            st.write(f"**{get_text('indicators')}:** {summary['indicators']}")
            st.write(f"**{get_text('mortality_records')}:** {summary['mortality_records']:,}")
            st.write(f"**{get_text('mmr_records')}:** {summary['mmr_records']:,}")
        else:
            st.info("ℹ️ System not initialized")
    
    # Render current page
    current_page_key = st.session_state.current_page
    
    # Map translated names back to English for internal routing
    page_map = {
        'Home': render_home_page,
        'Início': render_home_page,
        'Accueil': render_home_page,
        'Dashboard': render_dashboard_page,
        'Painel': render_dashboard_page,
        'Tableau de Bord': render_dashboard_page,
        'Chatbot': render_chatbot_page,
        'Reports': render_reports_page,
        'Relatórios': render_reports_page,
        'Rapports': render_reports_page,
        'About': render_about_page,
        'Sobre': render_about_page,
        'À Propos': render_about_page,
    }
    
    render_func = page_map.get(current_page_key, render_home_page)
    render_func()


if __name__ == "__main__":
    main()

