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

# Botpress chatbot integration
BOTPRESS_CHATBOT_URL = "https://cdn.botpress.cloud/webchat/v3.3/shareable.html?configUrl=https://files.bpcontent.cloud/2025/11/09/06/20251109063717-AGMWRARO.json"
from tb_interactive_visualizer import TBInteractiveVisualizer
from tb_burden_analytics import TBBurdenAnalytics
from tb_burden_chart_generator import TBBurdenChartGenerator
from translations import get_translation, TRANSLATIONS
from datetime import datetime
import sys
import os
from dotenv import load_dotenv


# Health Topic Content Configuration
def get_topic_content(topic: str, content_key: str, language: str = "English") -> str:
    """
    Get content specific to the health topic
    
    Args:
        topic: Health topic (Tuberculosis, Maternal Mortality, Child Mortality)
        content_key: Type of content needed
        language: Selected language
    
    Returns:
        Topic-specific content string
    """
    
    content_map = {
        "Tuberculosis": {
            "page_focus": {
                "English": "Focus: TB Case Notifications and Treatment Outcomes for WHO AFRO Region",
                "French": "Focus : Notifications de cas de TB et résultats du traitement pour la région AFRO de l'OMS",
                "Portuguese": "Foco: Notificações de casos de TB e resultados do tratamento para a Região AFRO da OMS",
                "Spanish": "Enfoque: Notificaciones de casos de TB y resultados del tratamiento para la Región AFRO de la OMS"
            },
            "chatbot_help": {
                "English": "Ask questions about TB data in natural language. The chatbot can help you:\n- Get TB statistics for specific countries (with charts)\n- Compare TB indicators across countries (with charts)\n- Analyze TB trends (with charts)\n- View TB notifications and outcomes\n- Generate TB reports",
                "French": "Posez des questions sur les données TB en langage naturel. Le chatbot peut vous aider à :\n- Obtenir des statistiques TB pour des pays spécifiques (avec graphiques)\n- Comparer les indicateurs TB entre les pays (avec graphiques)\n- Analyser les tendances TB (avec graphiques)\n- Voir les notifications et résultats TB\n- Générer des rapports TB",
                "Portuguese": "Faça perguntas sobre dados de TB em linguagem natural. O chatbot pode ajudá-lo a:\n- Obter estatísticas de TB para países específicos (com gráficos)\n- Comparar indicadores de TB entre países (com gráficos)\n- Analisar tendências de TB (com gráficos)\n- Ver notificações e resultados de TB\n- Gerar relatórios de TB",
                "Spanish": "Haga preguntas sobre datos de TB en lenguaje natural. El chatbot puede ayudarle a:\n- Obtener estadísticas de TB para países específicos (con gráficos)\n- Comparar indicadores de TB entre países (con gráficos)\n- Analizar tendencias de TB (con gráficos)\n- Ver notificaciones y resultados de TB\n- Generar informes de TB"
            },
            "example_queries": {
                "English": """**Country Statistics (with charts):**
- What are the TB statistics for Kenya?
- Show me TB notification charts for Angola
- Visualize TB treatment outcomes for Nigeria

**Comparisons (with charts):**
- Compare TB notification rates between Kenya and Uganda
- Compare TB treatment success rates across Kenya, Uganda, and Tanzania

**Trends (with charts):**
- What is the trend for TB notifications in Angola?
- Show TB treatment success trend chart for Kenya

**Reports:**
- Generate a TB summary report for Nigeria
- Create a comprehensive TB analysis for the AFRO region""",
                "French": """**Statistiques des Pays (avec graphiques) :**
- Quelles sont les statistiques TB pour le Kenya ?
- Montrez-moi les graphiques de notifications TB pour l'Angola
- Visualisez les résultats du traitement TB pour le Nigeria

**Comparaisons (avec graphiques) :**
- Comparez les taux de notification TB entre le Kenya et l'Ouganda
- Comparez les taux de réussite du traitement TB au Kenya, en Ouganda et en Tanzanie

**Tendances (avec graphiques) :**
- Quelle est la tendance des notifications TB en Angola ?
- Montrez le graphique de tendance de réussite du traitement TB pour le Kenya

**Rapports :**
- Générez un rapport récapitulatif TB pour le Nigeria
- Créez une analyse TB complète pour la région AFRO""",
                "Portuguese": """**Estatísticas do País (com gráficos):**
- Quais são as estatísticas de TB para o Quênia?
- Mostre-me os gráficos de notificações de TB para Angola
- Visualize os resultados do tratamento de TB para a Nigéria

**Comparações (com gráficos):**
- Compare as taxas de notificação de TB entre Quênia e Uganda
- Compare as taxas de sucesso do tratamento de TB no Quênia, Uganda e Tanzânia

**Tendências (com gráficos):**
- Qual é a tendência das notificações de TB em Angola?
- Mostre o gráfico de tendência de sucesso do tratamento de TB para o Quênia

**Relatórios:**
- Gere um relatório resumido de TB para a Nigéria
- Crie uma análise abrangente de TB para a região AFRO""",
                "Spanish": """**Estadísticas del País (con gráficos):**
- ¿Cuáles son las estadísticas de TB para Kenia?
- Muéstrame los gráficos de notificaciones de TB para Angola
- Visualiza los resultados del tratamiento de TB para Nigeria

**Comparaciones (con gráficos):**
- Compara las tasas de notificación de TB entre Kenia y Uganda
- Compara las tasas de éxito del tratamiento de TB en Kenia, Uganda y Tanzania

**Tendencias (con gráficos):**
- ¿Cuál es la tendencia de las notificaciones de TB en Angola?
- Muestra el gráfico de tendencia de éxito del tratamiento de TB para Kenia

**Informes:**
- Genera un informe resumido de TB para Nigeria
- Crea un análisis integral de TB para la región AFRO"""
            },
            "visualizer_desc": {
                "English": "Create customized TB visualizations with full control over:\n- Country selection (47 AFRO countries)\n- TB indicator selection (Notifications, Outcomes)\n- Prediction methods\n- Chart types (Chart or Map)\n- Year ranges",
                "French": "Créez des visualisations TB personnalisées avec un contrôle total sur :\n- Sélection de pays (47 pays AFRO)\n- Sélection d'indicateurs TB (Notifications, Résultats)\n- Méthodes de prédiction\n- Types de graphiques (Graphique ou Carte)\n- Plages d'années",
                "Portuguese": "Crie visualizações de TB personalizadas com controle total sobre:\n- Seleção de país (47 países AFRO)\n- Seleção de indicadores de TB (Notificações, Resultados)\n- Métodos de previsão\n- Tipos de gráfico (Gráfico ou Mapa)\n- Intervalos de anos",
                "Spanish": "Cree visualizaciones de TB personalizadas con control total sobre:\n- Selección de país (47 países AFRO)\n- Selección de indicadores de TB (Notificaciones, Resultados)\n- Métodos de predicción\n- Tipos de gráfico (Gráfico o Mapa)\n- Rangos de años"
            }
        },
        "Mortality": {
            "page_focus": {
                "English": "Focus: Maternal and Child Mortality Data for WHO AFRO Region",
                "French": "Focus : Données de mortalité maternelle et infantile pour la région AFRO de l'OMS",
                "Portuguese": "Foco: Dados de mortalidade materna e infantil para a Região AFRO da OMS",
                "Spanish": "Enfoque: Datos de mortalidad materna e infantil para la Región AFRO de la OMS"
            },
            "chatbot_help": {
                "English": "Ask questions about mortality data in natural language. The chatbot can help you:\n- Get statistics for specific countries (with charts)\n- Compare countries (with charts)\n- Analyze trends (with charts)\n- View projections (with charts)\n- Generate reports",
                "French": "Posez des questions sur les données de mortalité en langage naturel. Le chatbot peut vous aider à :\n- Obtenir des statistiques pour des pays spécifiques (avec graphiques)\n- Comparer les pays (avec graphiques)\n- Analyser les tendances (avec graphiques)\n- Voir les projections (avec graphiques)\n- Générer des rapports",
                "Portuguese": "Faça perguntas sobre dados de mortalidade em linguagem natural. O chatbot pode ajudá-lo a:\n- Obter estatísticas para países específicos (com gráficos)\n- Comparar países (com gráficos)\n- Analisar tendências (com gráficos)\n- Ver projeções (com gráficos)\n- Gerar relatórios",
                "Spanish": "Haga preguntas sobre datos de mortalidad en lenguaje natural. El chatbot puede ayudarle a:\n- Obtener estadísticas para países específicos (con gráficos)\n- Comparar países (con gráficos)\n- Analizar tendencias (con gráficos)\n- Ver proyecciones (con gráficos)\n- Generar informes"
            },
            "example_queries": {
                "English": """**Country Statistics (with charts):**
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
- Generate a summary report for Nigeria""",
                "French": """**Statistiques des Pays (avec graphiques) :**
- Quelles sont les statistiques pour le Kenya ?
- Montrez-moi les graphiques pour l'Angola
- Visualisez les données pour le Nigeria

**Comparaisons (avec graphiques) :**
- Comparez le Kenya et l'Ouganda
- Comparez le Kenya, l'Ouganda et la Tanzanie

**Tendances (avec graphiques) :**
- Quelle est la tendance de la mortalité néonatale en Angola ?
- Montrez le graphique de tendance pour le Kenya

**Projections (avec graphiques) :**
- Montrez-moi les projections pour 2030
- Projections pour le Kenya

**Meilleurs Pays (avec graphiques) :**
- Top 10 des pays par taux de mortalité des moins de cinq ans

**Rapports :**
- Générez un rapport récapitulatif pour le Nigeria""",
                "Portuguese": """**Estatísticas do País (com gráficos):**
- Quais são as estatísticas para o Quênia?
- Mostre-me os gráficos para Angola
- Visualize os dados para a Nigéria

**Comparações (com gráficos):**
- Compare Quênia e Uganda
- Compare Quênia, Uganda e Tanzânia

**Tendências (com gráficos):**
- Qual é a tendência da mortalidade neonatal em Angola?
- Mostre o gráfico de tendência para o Quênia

**Projeções (com gráficos):**
- Mostre-me as projeções para 2030
- Projeções para o Quênia

**Principais Países (com gráficos):**
- Top 10 países por taxa de mortalidade de menores de cinco anos

**Relatórios:**
- Gere um relatório resumido para a Nigéria""",
                "Spanish": """**Estadísticas del País (con gráficos):**
- ¿Cuáles son las estadísticas para Kenia?
- Muéstrame los gráficos para Angola
- Visualiza los datos para Nigeria

**Comparaciones (con gráficos):**
- Compara Kenia y Uganda
- Compara Kenia, Uganda y Tanzania

**Tendencias (con gráficos):**
- ¿Cuál es la tendencia de la mortalidad neonatal en Angola?
- Muestra el gráfico de tendencia para Kenia

**Proyecciones (con gráficos):**
- Muéstrame las proyecciones para 2030
- Proyecciones para Kenia

**Países Principales (con gráficos):**
- Top 10 países por tasa de mortalidad de menores de cinco años

**Informes:**
- Genera un informe resumido para Nigeria"""
            },
            "visualizer_desc": {
                "English": "Create customized visualizations with full control over:\n- Country selection\n- Indicator selection\n- Prediction methods\n- Chart types (Chart or Map)\n- Year ranges",
                "French": "Créez des visualisations personnalisées avec un contrôle total sur :\n- Sélection de pays\n- Sélection d'indicateurs\n- Méthodes de prédiction\n- Types de graphiques (Graphique ou Carte)\n- Plages d'années",
                "Portuguese": "Crie visualizações personalizadas com controle total sobre:\n- Seleção de país\n- Seleção de indicador\n- Métodos de previsão\n- Tipos de gráfico (Gráfico ou Mapa)\n- Intervalos de anos",
                "Spanish": "Cree visualizaciones personalizadas con control total sobre:\n- Selección de país\n- Selección de indicador\n- Métodos de predicción\n- Tipos de gráfico (Gráfico o Mapa)\n- Rangos de años"
            }
        },
        "Child Mortality": {
            "page_focus": {
                "English": "Focus: Child Mortality Data for WHO AFRO Region",
                "French": "Focus : Données de mortalité infantile pour la région AFRO de l'OMS",
                "Portuguese": "Foco: Dados de mortalidade infantil para a Região AFRO da OMS",
                "Spanish": "Enfoque: Datos de mortalidad infantil para la Región AFRO de la OMS"
            },
            "chatbot_help": {
                "English": "Ask questions about child mortality data in natural language. The chatbot can help you:\n- Get statistics for specific countries (with charts)\n- Compare countries (with charts)\n- Analyze trends (with charts)\n- View projections (with charts)\n- Generate reports",
                "French": "Posez des questions sur les données de mortalité infantile en langage naturel. Le chatbot peut vous aider à :\n- Obtenir des statistiques pour des pays spécifiques (avec graphiques)\n- Comparer les pays (avec graphiques)\n- Analyser les tendances (avec graphiques)\n- Voir les projections (avec graphiques)\n- Générer des rapports",
                "Portuguese": "Faça perguntas sobre dados de mortalidade infantil em linguagem natural. O chatbot pode ajudá-lo a:\n- Obter estatísticas para países específicos (com gráficos)\n- Comparar países (com gráficos)\n- Analisar tendências (com gráficos)\n- Ver projeções (com gráficos)\n- Gerar relatórios",
                "Spanish": "Haga preguntas sobre datos de mortalidad infantil en lenguaje natural. El chatbot puede ayudarle a:\n- Obtener estadísticas para países específicos (con gráficos)\n- Comparar países (con gráficos)\n- Analizar tendencias (con gráficos)\n- Ver proyecciones (con gráficos)\n- Generar informes"
            },
            "example_queries": {
                "English": """**Country Statistics (with charts):**
- What are the child mortality statistics for Kenya?
- Show me child mortality charts for Angola
- Visualize child mortality data for Nigeria

**Comparisons (with charts):**
- Compare child mortality between Kenya and Uganda
- Compare under-five mortality across Kenya, Uganda, and Tanzania

**Trends (with charts):**
- What is the trend for infant mortality in Angola?
- Show child mortality trend chart for Kenya

**Projections (with charts):**
- Show me child mortality projections for 2030
- Under-five mortality projections for Kenya

**Top Countries (with charts):**
- Top 10 countries by infant mortality rate

**Reports:**
- Generate a child mortality summary report for Nigeria""",
                "French": """**Statistiques des Pays (avec graphiques) :**
- Quelles sont les statistiques de mortalité infantile pour le Kenya ?
- Montrez-moi les graphiques de mortalité infantile pour l'Angola
- Visualisez les données de mortalité infantile pour le Nigeria

**Comparaisons (avec graphiques) :**
- Comparez la mortalité infantile entre le Kenya et l'Ouganda
- Comparez la mortalité des moins de cinq ans au Kenya, en Ouganda et en Tanzanie

**Tendances (avec graphiques) :**
- Quelle est la tendance de la mortalité infantile en Angola ?
- Montrez le graphique de tendance de mortalité infantile pour le Kenya

**Projections (avec graphiques) :**
- Montrez-moi les projections de mortalité infantile pour 2030
- Projections de mortalité des moins de cinq ans pour le Kenya

**Meilleurs Pays (avec graphiques) :**
- Top 10 des pays par taux de mortalité infantile

**Rapports :**
- Générez un rapport récapitulatif de mortalité infantile pour le Nigeria""",
                "Portuguese": """**Estatísticas do País (com gráficos):**
- Quais são as estatísticas de mortalidade infantil para o Quênia?
- Mostre-me os gráficos de mortalidade infantil para Angola
- Visualize os dados de mortalidade infantil para a Nigéria

**Comparações (com gráficos):**
- Compare a mortalidade infantil entre Quênia e Uganda
- Compare a mortalidade de menores de cinco anos no Quênia, Uganda e Tanzânia

**Tendências (com gráficos):**
- Qual é a tendência da mortalidade infantil em Angola?
- Mostre o gráfico de tendência de mortalidade infantil para o Quênia

**Projeções (com gráficos):**
- Mostre-me as projeções de mortalidade infantil para 2030
- Projeções de mortalidade de menores de cinco anos para o Quênia

**Principais Países (com gráficos):**
- Top 10 países por taxa de mortalidade infantil

**Relatórios:**
- Gere um relatório resumido de mortalidade infantil para a Nigéria""",
                "Spanish": """**Estadísticas del País (con gráficos):**
- ¿Cuáles son las estadísticas de mortalidad infantil para Kenia?
- Muéstrame los gráficos de mortalidad infantil para Angola
- Visualiza los datos de mortalidad infantil para Nigeria

**Comparaciones (con gráficos):**
- Compara la mortalidad infantil entre Kenia y Uganda
- Compara la mortalidad de menores de cinco años en Kenia, Uganda y Tanzania

**Tendencias (con gráficos):**
- ¿Cuál es la tendencia de la mortalidad infantil en Angola?
- Muestra el gráfico de tendencia de mortalidad infantil para Kenia

**Proyecciones (con gráficos):**
- Muéstrame las proyecciones de mortalidad infantil para 2030
- Proyecciones de mortalidad de menores de cinco años para Kenia

**Países Principales (con gráficos):**
- Top 10 países por tasa de mortalidad infantil

**Informes:**
- Genera un informe resumido de mortalidad infantil para Nigeria"""
            },
            "visualizer_desc": {
                "English": "Create customized child mortality visualizations with full control over:\n- Country selection\n- Indicator selection (infant, neonatal, under-five mortality)\n- Prediction methods\n- Chart types (Chart or Map)\n- Year ranges",
                "French": "Créez des visualisations de mortalité infantile personnalisées avec un contrôle total sur :\n- Sélection de pays\n- Sélection d'indicateurs (mortalité infantile, néonatale, des moins de cinq ans)\n- Méthodes de prédiction\n- Types de graphiques (Graphique ou Carte)\n- Plages d'années",
                "Portuguese": "Crie visualizações de mortalidade infantil personalizadas com controle total sobre:\n- Seleção de país\n- Seleção de indicador (mortalidade infantil, neonatal, de menores de cinco anos)\n- Métodos de previsão\n- Tipos de gráfico (Gráfico ou Mapa)\n- Intervalos de anos",
                "Spanish": "Cree visualizaciones de mortalidad infantil personalizadas con control total sobre:\n- Selección de país\n- Selección de indicador (mortalidad infantil, neonatal, de menores de cinco años)\n- Métodos de predicción\n- Tipos de gráfico (Gráfico o Mapa)\n- Rangos de años"
            }
        }
    }
    
    # Get content for the specified topic and key
    if topic in content_map and content_key in content_map[topic]:
        return content_map[topic][content_key].get(language, content_map[topic][content_key]["English"])
    
    # Default to Maternal Mortality if topic not found
    if content_key in content_map["Maternal Mortality"]:
        return content_map["Maternal Mortality"][content_key].get(language, content_map["Maternal Mortality"][content_key]["English"])
    
    return ""

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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: none;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    .stat-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    .stat-card:hover::before {
        opacity: 1;
    }
    .stat-value {
        font-size: 2.2rem;
        font-weight: 900;
        text-align: center;
        color: #ffffff;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        margin: 0.5rem 0;
        letter-spacing: -1px;
    }
    .stat-label {
        color: rgba(255, 255, 255, 0.95);
        font-size: 0.85rem;
        margin-top: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        text-align: center;
        letter-spacing: 1.2px;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    /* Card Color Variations */
    .stColumn:nth-child(1) .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stColumn:nth-child(2) .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .stColumn:nth-child(3) .stat-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .stColumn:nth-child(4) .stat-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
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


def initialize_system(indicator_type: str = "Mortality"):
    """Initialize the data pipeline and analytics system
    
    Args:
        indicator_type: Type of indicator ("Tuberculosis", "Mortality")
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
                
                # Initialize TB Burden analytics
                burden_path = "TB_burden_countries_2025-11-27.csv"
                lookup_path = "look up file WHO_AFRO_47_Countries_ISO3_Lookup_File.csv"
                
                try:
                    import os
                    if os.path.exists(burden_path) and os.path.exists(lookup_path):
                        tb_burden_analytics = TBBurdenAnalytics(burden_path, lookup_path)
                        tb_burden_analytics.load_data()
                        tb_burden_chart_gen = TBBurdenChartGenerator(tb_burden_analytics)
                        
                        st.session_state.tb_burden_analytics = tb_burden_analytics
                        st.session_state.tb_burden_chart_gen = tb_burden_chart_gen
                        st.success("✓ TB Burden data loaded successfully!")
                    else:
                        st.warning(f"TB Burden data files not found: {burden_path} or {lookup_path}")
                        st.session_state.tb_burden_analytics = None
                        st.session_state.tb_burden_chart_gen = None
                except Exception as e:
                    st.error(f"TB Burden initialization failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.session_state.tb_burden_analytics = None
                    st.session_state.tb_burden_chart_gen = None
                
                # Initialize TB Notifications/Outcomes analytics
                notif_path = "TB_notifications_2025-11-27.csv"
                outcomes_path = "TB_outcomes_2025-11-27.csv"
                
                try:
                    if os.path.exists(notif_path) and os.path.exists(outcomes_path) and os.path.exists(lookup_path):
                        from tb_notif_outcomes_analytics import TBNotificationsOutcomesAnalytics
                        from tb_notif_outcomes_charts import TBNotifOutcomesChartGenerator
                        
                        tb_notif_analytics = TBNotificationsOutcomesAnalytics(notif_path, outcomes_path, lookup_path)
                        tb_notif_analytics.load_data()
                        tb_notif_chart_gen = TBNotifOutcomesChartGenerator(tb_notif_analytics)
                        
                        st.session_state.tb_notif_analytics = tb_notif_analytics
                        st.session_state.tb_notif_chart_gen = tb_notif_chart_gen
                        st.success("✓ TB Notifications/Outcomes data loaded successfully!")
                    else:
                        missing = []
                        if not os.path.exists(notif_path): missing.append(notif_path)
                        if not os.path.exists(outcomes_path): missing.append(outcomes_path)
                        if not os.path.exists(lookup_path): missing.append(lookup_path)
                        st.warning(f"TB data files not found: {', '.join(missing)}")
                        st.session_state.tb_notif_analytics = None
                        st.session_state.tb_notif_chart_gen = None
                except Exception as e:
                    st.error(f"TB Notifications/Outcomes initialization failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.session_state.tb_notif_analytics = None
                    st.session_state.tb_notif_chart_gen = None
                
                # Store TB components
                st.session_state.tb_pipeline = pipeline
                st.session_state.tb_analytics = analytics
                st.session_state.tb_visualizer = visualizer
                st.session_state.tb_chatbot = chatbot
                
                # Initialize RDHUB chatbot with Pydantic AI if available
                # Botpress chatbot - no initialization needed (embedded via iframe)
                st.session_state.rdhub_chatbot = None
                st.session_state.tb_chatbot = None
                st.session_state.pipeline = None
                st.session_state.analytics = None
                st.session_state.visualizer = None
                st.session_state.chatbot = None
                st.session_state.data_loaded = True
                st.session_state.indicator_type = "Tuberculosis"
            elif indicator_type == "Mortality":
                # Initialize Mortality data pipeline (unified for Maternal and Child)
                from mortality_analytics import MortalityDataPipeline, MaternalMortalityAnalytics, ChildMortalityAnalytics
                from mortality_charts import MaternalMortalityChartGenerator, ChildMortalityChartGenerator
                
                maternal_path = "maternal Mortality.csv"
                child_path = "Child Mortality.csv"
                lookup_path = "look up file WHO_AFRO_47_Countries_ISO3_Lookup_File.csv"
                
                try:
                    import os
                    if os.path.exists(maternal_path) and os.path.exists(child_path) and os.path.exists(lookup_path):
                        # Initialize unified pipeline
                        pipeline = MortalityDataPipeline(maternal_path, child_path, lookup_path)
                        pipeline.load_data()
                        
                        # Initialize separate analytics
                        maternal_analytics = MaternalMortalityAnalytics(pipeline)
                        child_analytics = ChildMortalityAnalytics(pipeline)
                        
                        # Initialize chart generators
                        maternal_chart_gen = MaternalMortalityChartGenerator(maternal_analytics)
                        child_chart_gen = ChildMortalityChartGenerator(child_analytics)
                        
                        # Store in session state
                        st.session_state.mortality_pipeline = pipeline
                        st.session_state.maternal_analytics = maternal_analytics
                        st.session_state.child_analytics = child_analytics
                        st.session_state.maternal_chart_gen = maternal_chart_gen
                        st.session_state.child_chart_gen = child_chart_gen
                        
                        # Botpress chatbot - no initialization needed (embedded via iframe)
                        st.session_state.rdhub_chatbot = None
                        st.session_state.chatbot = None
                        
                        st.success("✓ Mortality data loaded successfully!")
                        st.session_state.data_loaded = True
                        st.session_state.indicator_type = "Mortality"
                    else:
                        missing = []
                        if not os.path.exists(maternal_path): missing.append(maternal_path)
                        if not os.path.exists(child_path): missing.append(child_path)
                        if not os.path.exists(lookup_path): missing.append(lookup_path)
                        st.error(f"Mortality data files not found: {', '.join(missing)}")
                        st.session_state.data_loaded = False
                        return False
                except Exception as e:
                    st.error(f"Mortality initialization failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.session_state.data_loaded = False
                    return False
            
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
    indicator_type = st.session_state.get("indicator_type", "Mortality")
    
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
                # Auto-detect from data, default to 1980-2024 if not available
                if year_range[0] and year_range[1]:
                    year_text = f"{year_range[0]}-{year_range[1]}"
                else:
                    year_text = "1980-2024"
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{year_text}</div>
                    <div class="stat-label">Year Range</div>
                </div>
                """, unsafe_allow_html=True)
        elif indicator_type == "Mortality" and hasattr(st.session_state, 'maternal_analytics') and st.session_state.maternal_analytics is not None:
            maternal_summary = st.session_state.maternal_analytics.get_data_summary()
            child_summary = st.session_state.child_analytics.get_data_summary()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{maternal_summary['total_countries']}</div>
                    <div class="stat-label">{get_translation("afro_countries", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{len(child_summary['key_indicators'])}</div>
                    <div class="stat-label">{get_translation("indicators", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_records = maternal_summary['total_records'] + child_summary['total_records']
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_records:,}</div>
                    <div class="stat-label">{get_translation("mortality_records", current_lang)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                year_range = maternal_summary['year_range']
                year_text = f"{year_range[0]}-{year_range[1]}"
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
    """Render specialized TB dashboard with sub-category selection"""
    try:
        import plotly.graph_objects as go
        import plotly.express as px
    except ImportError:
        st.error("Plotly is required for TB dashboard. Please install: pip install plotly")
        return
    
    # Get current language for translations
    current_lang = st.session_state.get("selected_language", "English")
    
    # Main header
    st.markdown(f'<h2 class="section-header">Tuberculosis Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    # Sub-category selector at the top
    st.markdown("""
    <div class="info-box" style="margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>Select TB Data Category:</strong> Choose which aspect of TB data you want to analyze
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for TB subcategory if not exists
    if 'tb_subcategory' not in st.session_state:
        st.session_state.tb_subcategory = 'TB Burden'
    
    # Sub-category selection buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📉 TB Burden Estimates", 
                     use_container_width=True, 
                     type="primary" if st.session_state.tb_subcategory == 'TB Burden' else "secondary",
                     key="tb_burden_btn"):
            st.session_state.tb_subcategory = 'TB Burden'
            st.rerun()
    
    with col2:
        if st.button("📊 TB Notifications", 
                     use_container_width=True, 
                     type="primary" if st.session_state.tb_subcategory == 'TB Notifications' else "secondary",
                     key="tb_notif_btn"):
            st.session_state.tb_subcategory = 'TB Notifications'
            st.rerun()
    
    with col3:
        if st.button("🏥 TB Outcomes", 
                     use_container_width=True, 
                     type="primary" if st.session_state.tb_subcategory == 'TB Outcomes' else "secondary",
                     key="tb_outcomes_btn"):
            st.session_state.tb_subcategory = 'TB Outcomes'
            st.rerun()
    
    st.markdown("---")
    
    # Render the selected sub-category
    selected_subcategory = st.session_state.tb_subcategory
    
    # ==================================================================================
    # TB BURDEN SECTION (DEFAULT/FIRST)
    # ==================================================================================
    if selected_subcategory == 'TB Burden':
        render_tb_burden_section(current_lang)
        return
    
    # ==================================================================================
    # TB NOTIFICATIONS SECTION
    # ==================================================================================
    elif selected_subcategory == 'TB Notifications':
        st.markdown(f'<h3 class="section-header">{get_translation("tb_notifications", current_lang)} Analytics</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box" style="margin-bottom: 2rem;">
            <p style="margin: 0; font-size: 0.95rem;">
                    <strong>Focus:</strong> TB Case Notifications for WHO AFRO Region (47 countries)
                <br>Data based on Global Tuberculosis Report 2024 indicators
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        render_tb_notifications_section(analytics, pipeline, current_lang)
        return
    
    # ==================================================================================
    # TB OUTCOMES SECTION
    # ==================================================================================
    elif selected_subcategory == 'TB Outcomes':
        render_tb_outcomes_section(analytics, pipeline, current_lang)
        return


def render_tb_notifications_section(analytics, pipeline, current_lang):
    """Render TB Notifications section with WHO-compliant indicators"""
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Check if we have the new TB notifications analytics
    if not hasattr(st.session_state, 'tb_notif_analytics') or st.session_state.tb_notif_analytics is None:
        st.warning("TB Notifications analytics not loaded. Please re-initialize the system.")
        return
    
    notif_analytics = st.session_state.tb_notif_analytics
    chart_gen = st.session_state.tb_notif_chart_gen
    
    # Get notifications summary
    notif_summary = notif_analytics.get_notifications_summary()
    
    # Header
    st.markdown("""
    <div class="info-box" style="margin-bottom: 2rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>WHO Post-2012 Definitions:</strong> Lab confirmed, Clinically diagnosed, Extrapulmonary
            <br><strong>Note:</strong> Smear positive/negative classifications discontinued after 2012
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Regional Overview Cards - WHO Compliant
    st.markdown(f"""
    <div class="dashboard-card">
        <h3 style="color: #e74c3c; margin-bottom: 1.5rem; font-size: 1.5rem;">TB Notifications Overview - {notif_summary['year']}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = notif_summary['total_new_relapse']
        range_text = ""
        if f'total_new_relapse_min' in notif_summary and f'total_new_relapse_max' in notif_summary:
            range_text = f"<p style='margin: 0.25rem 0; font-size: 0.9rem; color: #666;'>Range: {notif_summary['total_new_relapse_min']:,.0f} - {notif_summary['total_new_relapse_max']:,.0f}</p>"
        
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">
            <div class="stat-value" style="color: white;">{total:,.0f}</div>
            <div class="stat-label" style="color: #ecf0f1;">Total New & Relapse TB</div>
            {range_text}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        lab_conf = notif_summary['pulmonary_lab_confirmed']
        range_text = ""
        if f'pulmonary_lab_confirmed_min' in notif_summary and f'pulmonary_lab_confirmed_max' in notif_summary:
            range_text = f"<p style='margin: 0.25rem 0; font-size: 0.9rem; color: #666;'>Range: {notif_summary['pulmonary_lab_confirmed_min']:,.0f} - {notif_summary['pulmonary_lab_confirmed_max']:,.0f}</p>"
        
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);">
            <div class="stat-value" style="color: white;">{lab_conf:,.0f}</div>
            <div class="stat-label" style="color: #ecf0f1;">Pulmonary Lab Confirmed</div>
            {range_text}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        clin_diag = notif_summary['pulmonary_clin_diagnosed']
        range_text = ""
        if f'pulmonary_clin_diagnosed_min' in notif_summary and f'pulmonary_clin_diagnosed_max' in notif_summary:
            range_text = f"<p style='margin: 0.25rem 0; font-size: 0.9rem; color: #666;'>Range: {notif_summary['pulmonary_clin_diagnosed_min']:,.0f} - {notif_summary['pulmonary_clin_diagnosed_max']:,.0f}</p>"
        
            st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);">
            <div class="stat-value" style="color: white;">{clin_diag:,.0f}</div>
            <div class="stat-label" style="color: #ecf0f1;">Pulmonary Clinically Diagnosed</div>
            {range_text}
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        ep = notif_summary['extrapulmonary']
        range_text = ""
        if f'extrapulmonary_min' in notif_summary and f'extrapulmonary_max' in notif_summary:
            range_text = f"<p style='margin: 0.25rem 0; font-size: 0.9rem; color: #666;'>Range: {notif_summary['extrapulmonary_min']:,.0f} - {notif_summary['extrapulmonary_max']:,.0f}</p>"
        
            st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);">
            <div class="stat-value" style="color: white;">{ep:,.0f}</div>
            <div class="stat-label" style="color: #ecf0f1;">Extrapulmonary TB</div>
            {range_text}
            </div>
            """, unsafe_allow_html=True)
    
    st.info("💡 **WHO Definitions:** All indicators follow WHO post-2012 case definitions for TB")
    
    # Tabs for comprehensive notifications analysis
    notif_tab1, notif_tab2, notif_tab3, notif_tab4, notif_tab5 = st.tabs([
        "🔴 High/Low Notifying Countries",
        "👥 Age & Sex Distribution",
        "📋 Notification Types",
        "📈 Regional Trends",
        "⚖️ Equity Analysis"
    ])
    
    with notif_tab1:
        st.markdown("### Top Notifying Countries")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Highest Notifying Countries")
            high_chart = chart_gen.create_top_notifying_chart(
                indicator='c_newinc',
                indicator_name='Total New & Relapse TB Cases',
                n=10,
                year=notif_summary['year'],
                high=True
            )
            if high_chart:
                st.plotly_chart(high_chart, use_container_width=True)
        
        with col2:
            st.markdown("#### Lowest Notifying Countries")
            low_chart = chart_gen.create_top_notifying_chart(
                indicator='c_newinc',
                indicator_name='Total New & Relapse TB Cases',
                n=10,
                year=notif_summary['year'],
                high=False
            )
            if low_chart:
                st.plotly_chart(low_chart, use_container_width=True)
    
    with notif_tab2:
        st.markdown("### Age and Sex Distribution of TB Cases")
        
        age_chart = chart_gen.create_age_distribution_chart(year=notif_summary['year'])
        if age_chart:
            st.plotly_chart(age_chart, use_container_width=True)
            
            # Show age distribution table
            age_dist = notif_analytics.get_age_distribution(year=notif_summary['year'])
            
            st.markdown("#### Age Distribution Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(
                    age_dist[['age_group', 'male', 'female', 'total', 'percent']].style.format({
                        'male': '{:,.0f}',
                        'female': '{:,.0f}',
                        'total': '{:,.0f}',
                        'percent': '{:.1f}%'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            
            with col2:
                # Key insights
                if not age_dist.empty:
                    most_affected = age_dist.loc[age_dist['total'].idxmax()]
                    st.info(f"""
                    **Key Insights:**
                    - Most affected age group: **{most_affected['age_group']}** ({most_affected['percent']:.1f}%)
                    - Total cases: {most_affected['total']:,.0f}
                    - Male cases: {most_affected['male']:,.0f}
                    - Female cases: {most_affected['female']:,.0f}
                    """)
        else:
            st.warning("Age distribution data not available for selected year")
    
    with notif_tab3:
        st.markdown("### Notification Types by Country")
        
        countries = notif_analytics.get_country_list()
        
        selected_country = st.selectbox(
            "Select Country for Notification Types",
            countries,
            key="notif_types_country"
        )
        
        if selected_country:
            types_chart = chart_gen.create_notification_types_chart(
                country=selected_country,
                year=notif_summary['year']
            )
            
            if types_chart:
                st.plotly_chart(types_chart, use_container_width=True)
                
                # Show breakdown
                types_data = notif_analytics.get_notification_types_breakdown(selected_country, notif_summary['year'])
                
                if 'error' not in types_data:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Lab Confirmed", f"{types_data['pulmonary_lab_confirmed']:,.0f}")
                    with col2:
                        st.metric("Clinically Diagnosed", f"{types_data['pulmonary_clin_diagnosed']:,.0f}")
                    with col3:
                        st.metric("Extrapulmonary", f"{types_data['extrapulmonary']:,.0f}")
                    
                    st.info("""
                    **WHO Case Definitions (Post-2012):**
                    - **Lab Confirmed:** Bacteriologically confirmed pulmonary TB
                    - **Clinically Diagnosed:** Pulmonary TB diagnosed by clinical criteria
                    - **Extrapulmonary:** TB in organs other than lungs
                    """)
            else:
                st.warning(f"Notification types data not available for {selected_country}")
    
    with notif_tab4:
        st.markdown("### Regional Notification Trends")
        
        trend_indicator = st.selectbox(
            "Select Indicator",
            ["c_newinc", "new_labconf", "new_clindx", "new_ep"],
            format_func=lambda x: {
                "c_newinc": "Total New & Relapse TB",
                "new_labconf": "Pulmonary Lab Confirmed",
                "new_clindx": "Pulmonary Clinically Diagnosed",
                "new_ep": "Extrapulmonary TB"
            }[x],
            key="notif_trend_indicator"
        )
        
        indicator_names = {
            "c_newinc": "Total New & Relapse TB Cases",
            "new_labconf": "Pulmonary Lab Confirmed Cases",
            "new_clindx": "Pulmonary Clinically Diagnosed Cases",
            "new_ep": "Extrapulmonary TB Cases"
        }
        
        trend_chart = chart_gen.create_regional_trend_chart(
            indicator=trend_indicator,
            indicator_name=indicator_names[trend_indicator]
        )
        
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
    
    with notif_tab5:
        st.markdown("### Equity Analysis")
        
        equity_indicator = st.selectbox(
            "Select Indicator for Equity Analysis",
            ["c_newinc", "new_labconf", "new_clindx", "new_ep"],
            format_func=lambda x: {
                "c_newinc": "Total New & Relapse TB",
                "new_labconf": "Pulmonary Lab Confirmed",
                "new_clindx": "Pulmonary Clinically Diagnosed",
                "new_ep": "Extrapulmonary TB"
            }[x],
            key="notif_equity_indicator"
        )
        
        indicator_names_equity = {
            "c_newinc": "Total New & Relapse TB Cases",
            "new_labconf": "Pulmonary Lab Confirmed Cases",
            "new_clindx": "Pulmonary Clinically Diagnosed Cases",
            "new_ep": "Extrapulmonary TB Cases"
        }
        
        # Show equity chart
        equity_chart = chart_gen.create_equity_chart(
            indicator=equity_indicator,
            indicator_name=indicator_names_equity[equity_indicator],
            year=notif_summary['year']
        )
        
        if equity_chart:
            st.plotly_chart(equity_chart, use_container_width=True)
            
            # Show equity measures
            equity_measures = notif_analytics.calculate_equity_measures(
                indicator=equity_indicator,
                year=notif_summary['year']
            )
            
            if 'error' not in equity_measures:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Min Value", f"{equity_measures['min_value']:,.0f}")
                with col2:
                    st.metric("Max Value", f"{equity_measures['max_value']:,.0f}")
                with col3:
                    st.metric("Ratio (Max/Min)", f"{equity_measures['ratio_max_to_min']:.1f}x")
                with col4:
                    st.metric("Coeff. of Variation", f"{equity_measures['coefficient_of_variation']:.1f}%")
                
                st.info("""
                **Equity Measures Interpretation:**
                - **Ratio (Max/Min):** Higher values indicate greater inequality
                - **Coefficient of Variation:** >50% indicates high dispersion
                - Box plot shows distribution with outliers
                """)


def render_tb_outcomes_section(analytics, pipeline, current_lang):
    """Render TB Treatment Outcomes section following TB Burden framework"""
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Check if we have the TB outcomes analytics
    if not hasattr(st.session_state, 'tb_notif_analytics') or st.session_state.tb_notif_analytics is None:
        st.warning("TB Outcomes analytics not loaded. Please re-initialize the system.")
        return
    
    outcomes_analytics = st.session_state.tb_notif_analytics
    chart_gen = st.session_state.tb_notif_chart_gen
    
    # Category selector
    st.markdown("""
    <div class="info-box" style="margin-bottom: 2rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>Focus:</strong> TB Treatment Outcomes and Success Rates for WHO AFRO Region (47 countries)
            <br><strong>Data includes:</strong> Treatment success, failure, death, and lost to follow-up rates
            <br><strong>WHO Target:</strong> ≥85% treatment success rate
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Outcome category selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        outcome_category = st.selectbox(
            "Select Patient Category",
            ["newrel", "ret_nrel", "tbhiv"],
            format_func=lambda x: {
                "newrel": "New and Relapse TB Cases",
                "ret_nrel": "Retreatment TB Cases",
                "tbhiv": "TB/HIV Co-infected Cases"
            }[x],
            key="outcomes_category"
        )
    
    # Get outcomes summary for selected category
    outcomes_summary = outcomes_analytics.get_outcomes_summary(category=outcome_category)
    
    # Regional Overview Cards
    st.markdown(f"""
    <div class="dashboard-card">
        <h3 style="color: #27ae60; margin-bottom: 1.5rem; font-size: 1.5rem;">Treatment Outcomes Overview - {outcomes_summary['category']} ({outcomes_summary['year']})</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cohort = outcomes_summary['cohort']
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">
            <div class="stat-value" style="color: white;">{cohort:,.0f}</div>
            <div class="stat-label" style="color: #ecf0f1;">Total Cohort</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        success = outcomes_summary['success']
        success_pct = outcomes_summary['success_pct']
        color = '#27ae60' if success_pct >= 85 else ('#f39c12' if success_pct >= 75 else '#e74c3c')
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);">
            <div class="stat-value" style="color: white;">{success_pct:.1f}%</div>
            <div class="stat-label" style="color: #ecf0f1;">Treatment Success</div>
            <p style="margin: 0.25rem 0; font-size: 0.9rem; color: #ecf0f1;">({success:,.0f} cases)</p>
        </div>
                """, unsafe_allow_html=True)
    
    with col3:
        died = outcomes_summary['died']
        died_pct = outcomes_summary['died_pct']
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);">
            <div class="stat-value" style="color: white;">{died_pct:.1f}%</div>
            <div class="stat-label" style="color: #ecf0f1;">Died</div>
            <p style="margin: 0.25rem 0; font-size: 0.9rem; color: #ecf0f1;">({died:,.0f} cases)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        lost = outcomes_summary['lost']
        lost_pct = outcomes_summary['lost_pct']
    st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);">
            <div class="stat-value" style="color: white;">{lost_pct:.1f}%</div>
            <div class="stat-label" style="color: #ecf0f1;">Lost to Follow-up</div>
            <p style="margin: 0.25rem 0; font-size: 0.9rem; color: #ecf0f1;">({lost:,.0f} cases)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        failed = outcomes_summary['failed']
        failed_pct = outcomes_summary['failed_pct']
        st.metric("Treatment Failed", f"{failed_pct:.1f}% ({failed:,.0f} cases)")
    
    with col2:
        if 'tsr_mean' in outcomes_summary:
            st.metric("Mean TSR Across Countries", f"{outcomes_summary['tsr_mean']:.1f}%",
                     delta=f"{outcomes_summary['tsr_mean'] - 85:.1f}% vs WHO target")
    
    with col3:
        if 'countries_above_85' in outcomes_summary:
            st.metric("Countries Above WHO Target (≥85%)", 
                     f"{outcomes_summary['countries_above_85']}/{outcomes_summary['total_countries']}")
    
    # Tabs for comprehensive outcomes analysis
    out_tab1, out_tab2, out_tab3, out_tab4, out_tab5 = st.tabs([
        "🎯 High/Low Performing Countries",
        "📊 Country Outcomes Breakdown",
        "📈 Regional TSR Trends",
        "⚖️ Equity Analysis",
        "📋 WHO Performance Summary"
    ])
    
    # Map category to TSR indicator
    tsr_indicators = {
        'newrel': 'c_new_tsr',
        'ret_nrel': 'c_ret_tsr',
        'tbhiv': 'c_tbhiv_tsr'
    }
    tsr_indicator = tsr_indicators.get(outcome_category, 'c_new_tsr')
    
    with out_tab1:
        st.markdown("### Treatment Success Rate by Country")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Highest Performing Countries")
            high_chart = chart_gen.create_outcomes_bar_chart(
                indicator=tsr_indicator,
                indicator_name='Treatment Success Rate',
                n=10,
                year=outcomes_summary['year'],
                high=True
            )
            if high_chart:
                st.plotly_chart(high_chart, use_container_width=True)
    
    with col2:
            st.markdown("#### Lowest Performing Countries")
            low_chart = chart_gen.create_outcomes_bar_chart(
                indicator=tsr_indicator,
                indicator_name='Treatment Success Rate',
                n=10,
                year=outcomes_summary['year'],
                high=False
            )
            if low_chart:
                st.plotly_chart(low_chart, use_container_width=True)
    
    with out_tab2:
        st.markdown("### Detailed Outcomes Breakdown by Country")
        
        countries = outcomes_analytics.get_country_list()
        
        selected_country = st.selectbox(
            "Select Country",
            countries,
            key="outcomes_country"
        )
        
        if selected_country:
            breakdown_chart = chart_gen.create_outcomes_breakdown_chart(
                country=selected_country,
                year=outcomes_summary['year'],
                category=outcome_category
            )
            
            if breakdown_chart:
                st.plotly_chart(breakdown_chart, use_container_width=True)
                
                # Show detailed numbers
                breakdown_data = outcomes_analytics.get_outcomes_breakdown(
                    selected_country, outcomes_summary['year'], outcome_category
                )
                
                if 'error' not in breakdown_data:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric("Cohort", f"{breakdown_data['cohort']:,.0f}")
                    with col2:
                        st.metric("Success", f"{breakdown_data['success']:,.0f}")
                    with col3:
                        st.metric("Failed", f"{breakdown_data['failed']:,.0f}")
                    with col4:
                        st.metric("Died", f"{breakdown_data['died']:,.0f}")
                    with col5:
                        st.metric("Lost", f"{breakdown_data['lost']:,.0f}")
                    
                    if breakdown_data['tsr'] > 0:
                        tsr_val = breakdown_data['tsr']
                        st.info(f"""
                        **Treatment Success Rate:** {tsr_val:.1f}%
                        {"✅ Above WHO target (≥85%)" if tsr_val >= 85 else "⚠️ Below WHO target (≥85%)"}
                        """)
            else:
                st.warning(f"Outcomes data not available for {selected_country}")
    
    with out_tab3:
        st.markdown("### Regional Treatment Success Rate Trends")
        
        trend_chart = chart_gen.create_tsr_trend_chart(
            indicator=tsr_indicator,
            indicator_name='Treatment Success Rate'
        )
        
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)
            
            # Show trend statistics
            trend_data = outcomes_analytics.get_outcomes_regional_trend(tsr_indicator)
            if not trend_data.empty:
                latest = trend_data.iloc[-1]
                earliest = trend_data.iloc[0]
                
            col1, col2, col3 = st.columns(3)
                
            with col1:
                    st.metric("Latest Year TSR", f"{latest['mean_tsr']:.1f}%")
            with col2:
                    change = latest['mean_tsr'] - earliest['mean_tsr']
                    st.metric("Change Since First Year", f"{change:+.1f}%")
            with col3:
                    st.metric("Standard Deviation", f"{latest['std_tsr']:.1f}%")
    
    with out_tab4:
        st.markdown("### Equity in Treatment Success Rates")
        
        equity_chart = chart_gen.create_outcomes_equity_chart(
            indicator=tsr_indicator,
            indicator_name='Treatment Success Rate',
            year=outcomes_summary['year']
        )
        
        if equity_chart:
            st.plotly_chart(equity_chart, use_container_width=True)
            
            # Show equity measures
            equity_measures = outcomes_analytics.calculate_outcomes_equity(
                indicator=tsr_indicator,
                year=outcomes_summary['year']
            )
            
            if 'error' not in equity_measures:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Min TSR", f"{equity_measures['min_value']:.1f}%")
                with col2:
                    st.metric("Max TSR", f"{equity_measures['max_value']:.1f}%")
                with col3:
                    st.metric("Range", f"{equity_measures['range']:.1f}%")
                with col4:
                    st.metric("Coeff. of Variation", f"{equity_measures['coefficient_of_variation']:.1f}%")
                
                st.info(f"""
                **WHO Target Performance:**
                - Countries at or above target (≥85%): **{equity_measures['countries_above_target']}** ({equity_measures['percent_above_target']:.1f}%)
                - Countries below target (<85%): **{equity_measures['countries_below_target']}**
                - Mean TSR: **{equity_measures['mean']:.1f}%**
                - Median TSR: **{equity_measures['median']:.1f}%**
                """)
    
    with out_tab5:
        st.markdown("### WHO Treatment Success Rate Benchmarking")
        
        st.info("""
        **WHO Global TB Programme Targets:**
        - Treatment Success Rate: **≥85%** for all patient categories
        - Death Rate: **<5%**
        - Lost to Follow-up Rate: **<5%**
        """)
        
        # Performance summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Regional Performance")
            perf_data = {
                'Metric': ['Treatment Success', 'Died', 'Lost to Follow-up', 'Failed'],
                'Regional %': [
                    f"{outcomes_summary['success_pct']:.1f}%",
                    f"{outcomes_summary['died_pct']:.1f}%",
                    f"{outcomes_summary['lost_pct']:.1f}%",
                    f"{outcomes_summary['failed_pct']:.1f}%"
                ],
                'WHO Target': ['≥85%', '<5%', '<5%', 'N/A']
            }
            st.dataframe(pd.DataFrame(perf_data), hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("#### Key Insights")
            success_above = outcomes_summary['success_pct'] >= 85
            died_below = outcomes_summary['died_pct'] < 5
            lost_below = outcomes_summary['lost_pct'] < 5
            
            st.markdown(f"""
            {'✅' if success_above else '⚠️'} Treatment success rate {'meets' if success_above else 'does not meet'} WHO target
            
            {'✅' if died_below else '⚠️'} Death rate {'meets' if died_below else 'does not meet'} WHO target
            
            {'✅' if lost_below else '⚠️'} Lost to follow-up rate {'meets' if lost_below else 'does not meet'} WHO target
            
            **Overall Assessment:** {
                'EXCELLENT - All targets met!' if (success_above and died_below and lost_below)
                else 'GOOD - Most targets met' if sum([success_above, died_below, lost_below]) >= 2
                else 'NEEDS IMPROVEMENT - Targets not met'
            }
            """)


def render_tb_burden_section(current_lang):
    """Render TB Burden Estimates section"""
    st.markdown(f'<h3 class="section-header">📉 TB Burden Estimates</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="margin-bottom: 2rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>Focus:</strong> TB Burden Estimates including incidence, TB/HIV, mortality with confidence intervals
            <br><strong>Data Source:</strong> WHO Global TB Programme | <strong>Coverage:</strong> 47 AFRO countries | <strong>Years:</strong> 2000-2024
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if TB Burden data is loaded
    if hasattr(st.session_state, 'tb_burden_analytics') and st.session_state.tb_burden_analytics is not None:
        burden_analytics = st.session_state.tb_burden_analytics
        burden_chart_gen = st.session_state.tb_burden_chart_gen
        
        # Get latest year and summary
        latest_year = burden_analytics.get_latest_year()
        burden_summary = burden_analytics.get_burden_summary(year=latest_year)
        
        # Regional Burden Overview Cards
        st.markdown(f"""
        <div class="dashboard-card">
            <h3 style="color: #8B4513; margin-bottom: 1.5rem; font-size: 1.5rem;">Regional Burden Overview - {latest_year}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{burden_summary['total_incident_cases']:,.0f}</div>
                <div class="stat-label">TB Incident Cases</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{burden_summary['regional_incidence_rate_100k']:.1f}</div>
                <div class="stat-label">Incidence Rate<br>(per 100,000)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{burden_summary['total_tb_hiv_cases']:,.0f}</div>
                <div class="stat-label">TB/HIV Cases</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{burden_summary['total_mortality_cases']:,.0f}</div>
                <div class="stat-label">TB Deaths</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Case Detection Rate Card (single card - CI shown only on line charts)
        st.markdown(f"""
        <div class="dashboard-card" style="margin-top: 1rem; margin-bottom: 1rem;">
            <h4 style="color: #8B4513; margin-bottom: 0.5rem;">Case Detection Rate (Treatment Coverage)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20873a 100%);">
                <div class="stat-value" style="color: white; font-size: 3rem;">{burden_summary['case_detection_rate']:.1f}%</div>
                <div class="stat-label" style="color: #e8f5e9; font-size: 1.2rem;">Regional Case Detection Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.info("💡 **Case Detection Rate (CDR)** = Percentage of estimated incident TB cases that are detected and notified. Higher rates indicate better case finding. Confidence intervals are shown in trend charts.")
        
        # Tabs for different burden visualizations
        burden_tab1, burden_tab2, burden_tab3, burden_tab4 = st.tabs([
            "🔴 High Burden Countries", 
            "🟢 Low Burden Countries", 
            "🗺️ Burden Maps",
            "⚖️ Equity Analysis"
        ])
        
        with burden_tab1:
            st.markdown("### Top 10 High Burden Countries")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### TB Incidence (Cases)")
                high_inc_chart = burden_chart_gen.create_top_burden_chart(
                    indicator='e_inc_num',
                    indicator_name='TB Incidence Cases',
                    n=10,
                    year=latest_year,
                    high_burden=True
                )
                st.plotly_chart(high_inc_chart, use_container_width=True)
            
            with col2:
                st.markdown("#### TB Mortality (Cases)")
                high_mort_chart = burden_chart_gen.create_top_burden_chart(
                    indicator='e_mort_num',
                    indicator_name='TB Mortality Cases',
                    n=10,
                    year=latest_year,
                    high_burden=True
                )
                st.plotly_chart(high_mort_chart, use_container_width=True)
        
        with burden_tab2:
            st.markdown("### Top 10 Low Burden Countries")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### TB Incidence (Cases)")
                low_inc_chart = burden_chart_gen.create_top_burden_chart(
                    indicator='e_inc_num',
                    indicator_name='TB Incidence Cases',
                    n=10,
                    year=latest_year,
                    high_burden=False
                )
                st.plotly_chart(low_inc_chart, use_container_width=True)
            
            with col2:
                st.markdown("#### TB Mortality (Cases)")
                low_mort_chart = burden_chart_gen.create_top_burden_chart(
                    indicator='e_mort_num',
                    indicator_name='TB Mortality Cases',
                    n=10,
                    year=latest_year,
                    high_burden=False
                )
                st.plotly_chart(low_mort_chart, use_container_width=True)
        
        with burden_tab3:
            st.markdown("### TB Burden Maps")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                map_indicator = st.selectbox(
                    "Select Indicator for Map",
                    ["e_inc_100k", "e_mort_100k", "e_inc_tbhiv_100k", "cfr_pct"],
                    format_func=lambda x: {
                        "e_inc_100k": "TB Incidence Rate (per 100k)",
                        "e_mort_100k": "TB Mortality Rate (per 100k)",
                        "e_inc_tbhiv_100k": "TB/HIV Rate (per 100k)",
                        "cfr_pct": "Case Fatality Ratio (%)"
                    }[x],
                    key="burden_map_indicator"
                )
            
            indicator_names = {
                "e_inc_100k": "TB Incidence Rate (per 100,000)",
                "e_mort_100k": "TB Mortality Rate (per 100,000)",
                "e_inc_tbhiv_100k": "TB/HIV Incidence Rate (per 100,000)",
                "cfr_pct": "Case Fatality Ratio (%)"
            }
            
            map_chart = burden_chart_gen.create_burden_map(
                indicator=map_indicator,
                indicator_name=indicator_names[map_indicator],
                year=latest_year
            )
            st.plotly_chart(map_chart, use_container_width=True)
            
            # Regional trend for selected indicator
            st.markdown("### Regional Trend Over Time")
            
            # Map indicator to count version for trends
            trend_indicators = {
                "e_inc_100k": ("e_inc_num", "TB Incidence Cases"),
                "e_mort_100k": ("e_mort_num", "TB Mortality Cases"),
                "e_inc_tbhiv_100k": ("e_inc_tbhiv_num", "TB/HIV Cases"),
                "cfr_pct": ("e_inc_num", "TB Incidence Cases")
            }
            
            trend_ind, trend_name = trend_indicators.get(map_indicator, ("e_inc_num", "TB Cases"))
            trend_chart = burden_chart_gen.create_regional_trend_chart(
                indicator=trend_ind,
                indicator_name=trend_name
            )
            st.plotly_chart(trend_chart, use_container_width=True)
        
        with burden_tab4:
            st.markdown("### Equity Analysis - TB Burden Distribution")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                equity_indicator = st.selectbox(
                    "Select Indicator",
                    ["e_inc_100k", "e_mort_100k", "e_inc_tbhiv_100k"],
                    format_func=lambda x: {
                        "e_inc_100k": "Incidence Rate (per 100k)",
                        "e_mort_100k": "Mortality Rate (per 100k)",
                        "e_inc_tbhiv_100k": "TB/HIV Rate (per 100k)"
                    }[x],
                    key="burden_equity_indicator"
                )
            
            equity_names = {
                "e_inc_100k": "TB Incidence Rate (per 100,000)",
                "e_mort_100k": "TB Mortality Rate (per 100,000)",
                "e_inc_tbhiv_100k": "TB/HIV Incidence Rate (per 100,000)"
            }
            
            # Show equity chart
            equity_chart = burden_chart_gen.create_equity_chart(
                indicator=equity_indicator,
                indicator_name=equity_names[equity_indicator],
                year=latest_year
            )
            st.plotly_chart(equity_chart, use_container_width=True)
            
            # Show equity measures
            equity_measures = burden_analytics.calculate_equity_measures(
                indicator=equity_indicator,
                year=latest_year
            )
            
            st.markdown(f"""
            <div class="dashboard-card" style="margin-top: 1rem;">
                <h4 style="color: #8B4513; margin-bottom: 1rem;">Equity Measures</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Min Value", f"{equity_measures['min_value']:.1f}")
            with col2:
                st.metric("Max Value", f"{equity_measures['max_value']:.1f}")
            with col3:
                st.metric("Ratio (Max/Min)", f"{equity_measures['ratio_max_to_min']:.1f}x")
            with col4:
                st.metric("Coeff. of Variation", f"{equity_measures['coefficient_of_variation']:.1f}%")
            
            st.info("""
            **Equity Measures Interpretation:**
            - **Ratio (Max/Min)**: Higher values indicate greater inequality. A ratio of 1 means perfect equality.
            - **Coefficient of Variation**: Measures relative variability. Values >50% indicate high dispersion.
            - The box plot shows the distribution across countries, with outliers indicating exceptional burden levels.
            """)
    else:
        st.warning("""
        **TB Burden data not loaded.** 
        
        This may have occurred during initialization. The system will continue to work with TB Notifications and Outcomes data.
        
        To load TB Burden data, you can re-initialize the system from the sidebar.
        """)


# OLD render_tb_outcomes_section REMOVED - Using new version at line 1695


def render_mortality_dashboard():
    """Render Mortality dashboard with Maternal and Child tabs - Mimics TB dashboard format exactly"""
    try:
        import plotly.graph_objects as go
        import plotly.express as px
    except ImportError:
        st.error("Plotly is required for Mortality dashboard. Please install: pip install plotly")
        return
    
    # Get current language for translations
    current_lang = st.session_state.get("selected_language", "English")
    
    # Check if data is loaded
    if not hasattr(st.session_state, 'maternal_analytics') or st.session_state.maternal_analytics is None:
        st.error("Mortality data not initialized. Please initialize the system from the sidebar.")
        return
    
    # Main header - matching TB format
    st.markdown(f'<h2 class="section-header">Mortality Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    # Category selector - matching TB format exactly
    st.markdown("""
    <div class="info-box" style="margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>Select Mortality Data Category:</strong> Choose which aspect of mortality data you want to analyze
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for mortality subcategory if not exists
    if 'mortality_subcategory' not in st.session_state:
        st.session_state.mortality_subcategory = 'Maternal Mortality'
    
    # Sub-category selection buttons - matching TB format
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Maternal Mortality", 
                     use_container_width=True, 
                     type="primary" if st.session_state.mortality_subcategory == 'Maternal Mortality' else "secondary",
                     key="maternal_mortality_btn"):
            st.session_state.mortality_subcategory = 'Maternal Mortality'
            st.rerun()
    
    with col2:
        if st.button("👶 Child Mortality", 
                     use_container_width=True, 
                     type="primary" if st.session_state.mortality_subcategory == 'Child Mortality' else "secondary",
                     key="child_mortality_btn"):
            st.session_state.mortality_subcategory = 'Child Mortality'
            st.rerun()
    
    # Route to appropriate section
    if st.session_state.mortality_subcategory == 'Maternal Mortality':
        render_maternal_mortality_section()
    else:
        render_child_mortality_section()


def render_maternal_mortality_section():
    """Render Maternal Mortality section - Mimics TB Burden format exactly"""
    current_lang = st.session_state.get("selected_language", "English")
    maternal_analytics = st.session_state.maternal_analytics
    maternal_chart_gen = st.session_state.maternal_chart_gen
    
    st.markdown(f'<h3 class="section-header">📊 Maternal Mortality</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="margin-bottom: 2rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>Focus:</strong> Maternal Mortality Ratio (MMR) - Deaths per 100,000 live births
            <br><strong>Data Source:</strong> UNICEF/UNIGME | <strong>Coverage:</strong> 47 AFRO countries | <strong>Years:</strong> 2000-2024
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get latest year and summary
    latest_year = maternal_analytics.get_latest_year()
    summary = maternal_analytics.get_mmr_summary(latest_year)
    
    # Regional Burden Overview Cards - Matching TB Burden format exactly
    st.markdown(f"""
    <div class="dashboard-card">
        <h3 style="color: #f5576c; margin-bottom: 1.5rem; font-size: 1.5rem;">Regional Burden Overview - {latest_year}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{summary['regional_median_mmr']:,.0f}</div>
            <div class="stat-label">Regional Median MMR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{summary['min_mmr']:,.0f}</div>
            <div class="stat-label">Best MMR<br>(per 100,000)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{summary['max_mmr']:,.0f}</div>
            <div class="stat-label">Worst MMR<br>(per 100,000)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        year_range = maternal_analytics.get_data_summary()['year_range']
        year_text = f"{year_range[0]}-{year_range[1]}"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{year_text}</div>
            <div class="stat-label">Year Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    # SDG Target Card (matching CDR card format from TB Burden)
    st.markdown(f"""
    <div class="dashboard-card" style="margin-top: 1rem; margin-bottom: 1rem;">
        <h4 style="color: #f5576c; margin-bottom: 0.5rem;">SDG 2030 Target Progress</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        progress_pct = (summary['countries_below_sdg_target'] / summary['total_countries']) * 100 if summary['total_countries'] > 0 else 0
    st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20873a 100%);">
            <div class="stat-value" style="color: white; font-size: 3rem;">{progress_pct:.1f}%</div>
            <div class="stat-label" style="color: #e8f5e9; font-size: 1.2rem;">Countries Below SDG Target</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **SDG Target:** Less than 70 maternal deaths per 100,000 live births by 2030. Progress shown as percentage of countries meeting the target.")
    
    # Tabs matching TB Burden format exactly
    burden_tab1, burden_tab2, burden_tab3, burden_tab4 = st.tabs([
        "🔴 High Burden Countries", 
        "🟢 Low Burden Countries", 
        "🗺️ Burden Maps",
        "⚖️ Equity Analysis"
    ])
    
    with burden_tab1:
        st.markdown("### Top 10 High MMR Countries")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Maternal Mortality Ratio")
            high_mmr_chart = maternal_chart_gen.create_top_mmr_chart(
                n=10,
                year=latest_year,
                high_burden=True
            )
            st.plotly_chart(high_mmr_chart, use_container_width=True)
        
        with col2:
            st.markdown("#### Top 10 High MMR Countries")
            high_mmr = maternal_analytics.get_top_mmr_countries(n=10, year=latest_year, ascending=False)
            st.dataframe(
                high_mmr[['country_clean', 'mmr']].rename(columns={'country_clean': 'Country', 'mmr': 'MMR (per 100,000)'}),
                use_container_width=True,
                hide_index=True
            )
    
    with burden_tab2:
        st.markdown("### Top 10 Low MMR Countries")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Maternal Mortality Ratio")
            low_mmr_chart = maternal_chart_gen.create_top_mmr_chart(
                n=10,
                year=latest_year,
                high_burden=False
            )
            st.plotly_chart(low_mmr_chart, use_container_width=True)
        
        with col2:
            st.markdown("#### Top 10 Low MMR Countries")
            low_mmr = maternal_analytics.get_top_mmr_countries(n=10, year=latest_year, ascending=True)
            st.dataframe(
                low_mmr[['country_clean', 'mmr']].rename(columns={'country_clean': 'Country', 'mmr': 'MMR (per 100,000)'}),
                use_container_width=True,
                hide_index=True
            )
    
    with burden_tab3:
        st.markdown("### MMR Maps")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            map_year = st.selectbox(
                "Select Year for Map",
                options=range(2000, 2024),
                index=len(range(2000, 2024))-1,
                key="maternal_map_year"
            )
        
        with col2:
            map_chart = maternal_chart_gen.create_map(year=map_year)
            st.plotly_chart(map_chart, use_container_width=True)
    
    with burden_tab4:
        st.markdown("### Equity Analysis")
        equity_measures = maternal_analytics.calculate_equity_measures(year=latest_year)
        equity_chart = maternal_chart_gen.create_equity_chart(year=latest_year)
        st.plotly_chart(equity_chart, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Min MMR", f"{equity_measures['min_value']:.0f}")
        with col2:
            st.metric("Max MMR", f"{equity_measures['max_value']:.0f}")
        with col3:
            st.metric("Ratio (Max/Min)", f"{equity_measures['ratio_max_to_min']:.1f}x" if equity_measures['ratio_max_to_min'] else "N/A")
        with col4:
            st.metric("Coeff. of Variation", f"{equity_measures['coefficient_of_variation']:.1f}%" if equity_measures['coefficient_of_variation'] else "N/A")


def render_child_mortality_section():
    """Render Child Mortality section - Mimics TB Notifications format exactly"""
    current_lang = st.session_state.get("selected_language", "English")
    
    # Check if analytics are available
    if not hasattr(st.session_state, 'child_analytics') or st.session_state.child_analytics is None:
        st.error("Child Mortality analytics not loaded. Please re-initialize the system.")
        return
    
    child_analytics = st.session_state.child_analytics
    child_chart_gen = st.session_state.child_chart_gen
    
    # Check if data is loaded
    if child_analytics.child_afro is None or len(child_analytics.child_afro) == 0:
        st.error("Child Mortality data is empty. Please check the data file and re-initialize.")
        return
    
    st.markdown(f'<h3 class="section-header">👶 Child Mortality</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box" style="margin-bottom: 2rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>Focus:</strong> Child Mortality Indicators - Under-five, Infant, and Neonatal Mortality Rates
            <br><strong>Data Source:</strong> UNICEF/UNIGME | <strong>Coverage:</strong> 47 AFRO countries | <strong>Years:</strong> 2000-2024
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get latest year and summary with error handling
    try:
        # Check if child_afro has data
        if child_analytics.child_afro is None or len(child_analytics.child_afro) == 0:
            st.error("Child Mortality data is empty. Please check the data file and re-initialize the system.")
            st.info("**Troubleshooting:**\n"
                   "- Ensure 'Child Mortality.csv' file exists\n"
                   "- Check that the file has the correct format (UNICEF format)\n"
                   "- Verify the file contains data for AFRO countries\n"
                   "- Re-initialize the system from the sidebar")
            return
        
        latest_year = child_analytics.get_latest_year('Under-five mortality rate')
        summary = child_analytics.get_mortality_summary(latest_year)
        
        # Check if summary has data
        if summary.get('total_countries', 0) == 0:
            # Try to get data summary to show what's available
            data_summary = child_analytics.get_data_summary()
            
            # Debug: Show what data we have
            st.warning(f"No Child Mortality data found for year {latest_year}.")
            st.info(f"**Data Summary:**\n"
                   f"- Total records in dataset: {len(child_analytics.child_afro)}\n"
                   f"- Countries: {data_summary.get('total_countries', 0)}\n"
                   f"- Year range: {data_summary.get('year_range', 'N/A')}\n"
                   f"- Available indicators: {data_summary.get('key_indicators', [])}")
            
            # Show sample data
            with st.expander("View Sample Data"):
                st.dataframe(child_analytics.child_afro.head(20))
                st.write(f"Unique indicators: {child_analytics.child_afro['indicator'].unique()}")
                st.write(f"Unique years: {sorted(child_analytics.child_afro['year'].unique())}")
                st.write(f"Unique countries: {sorted(child_analytics.child_afro['country_clean'].unique())[:10]}")
            return
    except Exception as e:
        st.error(f"Error loading Child Mortality data: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())
        return
    
    # Regional Overview Cards
    st.markdown(f"""
    <div class="dashboard-card" style="margin-top: 1rem;">
        <h3 style="color: #4facfe; margin-bottom: 1.5rem; font-size: 1.5rem;">Regional Burden Overview - {latest_year}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        u5mr_median = summary.get('under_five_mortality_rate_median', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{u5mr_median:.1f}</div>
            <div class="stat-label">Under-Five Mortality Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        imr_median = summary.get('infant_mortality_rate_median', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{imr_median:.1f}</div>
            <div class="stat-label">Infant Mortality Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        nmr_median = summary.get('child_mortality_rate_aged_1_4_years_median', 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{nmr_median:.1f}</div>
            <div class="stat-label">Child Mortality (1-4 years)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        year_range = child_analytics.get_data_summary()['year_range']
        year_text = f"{year_range[0]}-{year_range[1]}"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{year_text}</div>
            <div class="stat-label">Year Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Indicator selection - show all available indicators
    st.markdown("---")
    
    # Get all available indicators from the data
    if child_analytics.child_afro is not None and len(child_analytics.child_afro) > 0:
        # Get all unique indicators, prioritizing rate indicators
        all_indicators = sorted(child_analytics.child_afro['indicator'].unique().tolist())
        rate_indicators = [ind for ind in all_indicators if 'rate' in ind.lower()]
        count_indicators = [ind for ind in all_indicators if 'rate' not in ind.lower()]
        available_indicators = rate_indicators + count_indicators
        
        # Create display names (capitalize first letter of each word)
        indicator_display = {ind: ' '.join(word.capitalize() for word in ind.split()) for ind in available_indicators}
        
        # Default to Under-five mortality rate if available
        default_indicator = 'Under-five mortality rate' if 'Under-five mortality rate' in available_indicators else available_indicators[0] if available_indicators else None
        
        selected_indicator = st.selectbox(
            "Select Indicator",
            options=available_indicators,
            format_func=lambda x: indicator_display.get(x, x),
            index=available_indicators.index(default_indicator) if default_indicator and default_indicator in available_indicators else 0,
            key="child_mortality_indicator"
        )
    else:
        # Fallback to key indicators if data not loaded
        indicator_options = {
            'Under-five mortality rate': 'Under-five Mortality Rate',
            'Infant mortality rate': 'Infant Mortality Rate',
            'Child mortality rate (aged 1-4 years)': 'Child Mortality Rate (1-4 years)'
        }
        selected_indicator = st.selectbox(
            "Select Indicator",
            options=list(indicator_options.keys()),
            format_func=lambda x: indicator_options[x],
            key="child_mortality_indicator"
        )
    
    # Tabs matching TB Notifications format
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔴 High Burden Countries",
        "🟢 Low Burden Countries",
        "📈 Temporal Trends",
        "👥 Sex Disaggregation",
        "⚖️ Equity Analysis"
    ])
    
    with tab1:
        st.markdown(f"### Top 10 High {indicator_options[selected_indicator]} Countries")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### {indicator_options[selected_indicator]}")
            high_chart = child_chart_gen.create_top_mortality_chart(
                indicator=selected_indicator,
                indicator_name=indicator_options[selected_indicator],
                n=10,
                year=latest_year,
                high_burden=True
            )
            st.plotly_chart(high_chart, use_container_width=True)
    
    with col2:
            st.markdown(f"#### Top 10 High {indicator_options[selected_indicator]} Countries")
            high_countries = child_analytics.get_top_mortality_countries(
                indicator=selected_indicator, n=10, year=latest_year, ascending=False
            )
            st.dataframe(
                high_countries[['country_clean', 'value']].rename(columns={'country_clean': 'Country', 'value': indicator_options[selected_indicator]}),
                use_container_width=True,
                hide_index=True
            )
    
    with tab2:
        st.markdown(f"### Top 10 Low {indicator_options[selected_indicator]} Countries")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### {indicator_options[selected_indicator]}")
            low_chart = child_chart_gen.create_top_mortality_chart(
                indicator=selected_indicator,
                indicator_name=indicator_options[selected_indicator],
                n=10,
                year=latest_year,
                high_burden=False
            )
            st.plotly_chart(low_chart, use_container_width=True)
        
        with col2:
            st.markdown(f"#### Top 10 Low {indicator_options[selected_indicator]} Countries")
            low_countries = child_analytics.get_top_mortality_countries(
                indicator=selected_indicator, n=10, year=latest_year, ascending=True
            )
            st.dataframe(
                low_countries[['country_clean', 'value']].rename(columns={'country_clean': 'Country', 'value': indicator_options[selected_indicator]}),
                use_container_width=True,
                hide_index=True
            )
    
    with tab3:
        st.markdown("### Regional and Country Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Regional Trend")
            regional_chart = child_chart_gen.create_regional_trend_chart(indicator=selected_indicator)
            st.plotly_chart(regional_chart, use_container_width=True)
        
        with col2:
            st.markdown("#### Country Trend")
            countries = child_analytics.get_country_list()
            selected_country = st.selectbox("Select Country", countries, key="child_trend_country")
            if selected_country:
                country_chart = child_chart_gen.create_country_trend_chart(selected_country, indicator=selected_indicator)
                st.plotly_chart(country_chart, use_container_width=True)
    
    with tab4:
        st.markdown("### Sex Disaggregation Analysis")
        sex_data = child_analytics.get_sex_disaggregation(indicator=selected_indicator, year=latest_year)
        
        if len(sex_data) > 0 and 'Female' in sex_data.columns and 'Male' in sex_data.columns:
            sex_chart = child_chart_gen.create_sex_comparison_chart(indicator=selected_indicator, year=latest_year)
            if sex_chart:
                st.plotly_chart(sex_chart, use_container_width=True)
            
            # Show sex ratio statistics
            st.markdown("#### Sex Ratio Analysis")
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_ratio = sex_data['sex_ratio'].mean() if 'sex_ratio' in sex_data.columns else None
                st.metric("Average Sex Ratio (M/F)", f"{avg_ratio:.2f}" if avg_ratio else "N/A")
            with col2:
                avg_gap = sex_data['sex_gap'].mean() if 'sex_gap' in sex_data.columns else None
                st.metric("Average Sex Gap (M-F)", f"{avg_gap:.1f}" if avg_gap else "N/A")
            with col3:
                st.metric("Countries with Data", len(sex_data))
        else:
            st.info("Sex disaggregated data not available for this indicator/year combination.")
    
    with tab5:
        st.markdown("### Equity Analysis")
        equity_measures = child_analytics.calculate_equity_measures(indicator=selected_indicator, year=latest_year)
        
        # Check if we have data before displaying
        if equity_measures['countries'] == 0:
            st.warning(f"No data available for {indicator_options[selected_indicator]} in {latest_year}.")
        else:
            equity_chart = child_chart_gen.create_equity_chart(indicator=selected_indicator, year=latest_year)
            if equity_chart:
                st.plotly_chart(equity_chart, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Min Value", f"{equity_measures['min_value']:.1f}" if equity_measures['min_value'] is not None else "N/A")
            with col2:
                st.metric("Max Value", f"{equity_measures['max_value']:.1f}" if equity_measures['max_value'] is not None else "N/A")
            with col3:
                st.metric("Ratio (Max/Min)", f"{equity_measures['ratio_max_to_min']:.1f}x" if equity_measures['ratio_max_to_min'] else "N/A")
            with col4:
                st.metric("Coeff. of Variation", f"{equity_measures['coefficient_of_variation']:.1f}%" if equity_measures['coefficient_of_variation'] else "N/A")


def render_dashboard_page():
    """Render the modern analytics dashboard"""
    current_lang = st.session_state.get("selected_language", "English")
    st.markdown(f'<h2 class="section-header">{get_translation("analytics_dashboard", current_lang)}</h2>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning(get_translation("please_initialize", current_lang))
        return
    
    # Get analytics and pipeline based on indicator type
    indicator_type = st.session_state.get("indicator_type", "Mortality")
    
    if indicator_type == "Tuberculosis" and hasattr(st.session_state, 'tb_analytics') and st.session_state.tb_analytics is not None:
        analytics = st.session_state.tb_analytics
        pipeline = st.session_state.tb_pipeline
        # Render specialized TB dashboard
        render_tb_dashboard(analytics, pipeline)
        return
    
    elif indicator_type == "Mortality" and hasattr(st.session_state, 'maternal_analytics') and st.session_state.maternal_analytics is not None:
        # Render Mortality dashboard
        render_mortality_dashboard()
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
    health_topic = st.session_state.get("indicator_type", "Mortality")
    selected_language = st.session_state.get("selected_language", "English")
    
    # Display current settings with topic-specific styling
    topic_colors = {
        "Tuberculosis": "#8B4513",
        "Mortality": "#f5576c"
    }
    topic_color = topic_colors.get(health_topic, "#0066CC")
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem; padding: 1rem; background: linear-gradient(135deg, {topic_color} 0%, #004499 100%); border-radius: 10px; color: white;">
        <strong>Health Topic:</strong> {health_topic} | <strong>Language:</strong> {selected_language}
    </div>
    """, unsafe_allow_html=True)
    
    # Use translations
    current_lang = st.session_state.get("selected_language", "English")
    
    st.markdown(f'<h2 class="section-header">{get_translation("chatbot", current_lang)}</h2>', unsafe_allow_html=True)
    
    # Beautiful chatbot introduction
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 15px; 
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <div style="text-align: center; color: white;">
            <h2 style="color: white; margin-bottom: 1rem; font-size: 2rem;">
                🤖 Regional Health Data Hub Assistant
            </h2>
            <p style="font-size: 1.1rem; margin-bottom: 0.5rem; opacity: 0.95;">
                Your intelligent companion for exploring health data
            </p>
            <p style="font-size: 0.95rem; opacity: 0.85; margin: 0;">
                Ask questions about trends, comparisons, statistics, and get instant insights with visualizations
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display topic-specific help text
    st.markdown(get_topic_content(health_topic, "chatbot_help", current_lang))
    
    # Botpress Chatbot Integration
    st.markdown("""
    <div style="margin-top: 2rem; margin-bottom: 2rem;">
        <h3 style="color: #0066CC; margin-bottom: 1rem;">💬 Chat with Regional Health Data Hub Assistant</h3>
        <p style="color: #666; margin-bottom: 1rem;">
            Use the chat widget below to ask questions about health data, get insights, and explore analytics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Embed Botpress webchat
    botpress_url = BOTPRESS_CHATBOT_URL
    
    st.markdown(f"""
    <div style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <iframe 
            src="{botpress_url}"
            style="width: 100%; height: 100%; border: none;"
            allow="microphone; camera"
            title="Regional Health Data Hub Assistant">
        </iframe>
    </div>
    """, unsafe_allow_html=True)
    


def _collect_statistics_for_llm(analytics, pipeline, country: str = None, indicator_type: str = "Mortality") -> Dict:
    """Collect key statistics for LLM report generation
    
    Args:
        analytics: Analytics instance (MortalityAnalytics or TBAnalytics)
        pipeline: Pipeline instance (MortalityDataPipeline or TBDataPipeline)
        country: Optional country name
        indicator_type: Type of indicator ("Tuberculosis", "Mortality")
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
                # Get indicators from pipeline if available, otherwise use default key indicators
                if hasattr(pipeline, 'get_indicators'):
                    indicators = pipeline.get_indicators()
                else:
                    # Default key indicators for mortality
                    indicators = ['Under-five mortality rate', 'Infant mortality rate', 'Neonatal mortality rate']
                
                for indicator in indicators[:3]:  # Top 3 indicators
                    try:
                        if hasattr(analytics, 'get_trend_analysis'):
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
                # Get indicators from pipeline if available, otherwise use default key indicators
                if hasattr(pipeline, 'get_indicators'):
                    indicators = pipeline.get_indicators()
                else:
                    # Default key indicators for mortality
                    indicators = ['Under-five mortality rate', 'Infant mortality rate', 'Neonatal mortality rate', 'Maternal mortality ratio']
                
                for indicator in indicators[:5]:  # Top 5 indicators
                    try:
                        if hasattr(analytics, 'get_top_countries_by_indicator'):
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
    health_topic = st.session_state.get("indicator_type", "Mortality")
    selected_language = st.session_state.get("selected_language", "English")
    
    # Display current settings with topic-specific styling
    topic_colors = {
        "Tuberculosis": "#8B4513",
        "Mortality": "#f5576c"
    }
    topic_color = topic_colors.get(health_topic, "#0066CC")
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem; padding: 1rem; background: linear-gradient(135deg, {topic_color} 0%, #004499 100%); border-radius: 10px; color: white;">
        <strong>Health Topic:</strong> {health_topic} | <strong>Language:</strong> {selected_language}
        <br><small style="opacity: 0.9;">{get_topic_content(health_topic, "page_focus", selected_language)}</small>
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
    
    # ==================================================================================
    # TB SUBCATEGORY AND INDICATOR SELECTION (for Tuberculosis reports)
    # ==================================================================================
    
    tb_subcategory = None
    selected_indicators_list = []
    
    if health_topic == "Tuberculosis":
        st.markdown("---")
        st.markdown("### 📊 Select TB Data Category and Indicators")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            tb_subcategory = st.selectbox(
                "Select TB Data Category",
                ["All TB Data", "TB Burden", "TB Notifications", "TB Outcomes"],
                index=0,
                key="report_tb_subcategory",
                help="Choose which aspect of TB data to include in the report"
            )
        
        with col2:
            # Get available indicators based on subcategory
            if tb_subcategory == "TB Burden" and hasattr(st.session_state, 'tb_burden_analytics'):
                available_indicators_tb = [
                    "e_inc_num (TB Incidence Cases)",
                    "e_inc_100k (TB Incidence Rate per 100k)",
                    "e_mort_num (TB Mortality Cases)",
                    "e_mort_100k (TB Mortality Rate per 100k)",
                    "e_inc_tbhiv_num (TB/HIV Cases)",
                    "e_mort_tbhiv_num (TB/HIV Mortality)"
                ]
            elif tb_subcategory == "TB Notifications":
                summary = analytics.get_regional_summary()
                indicators = summary.get('indicators', {})
                notif_indicators = [ind for ind in indicators.keys() if 'outcome' not in ind.lower() and 'success' not in ind.lower()]
                available_indicators_tb = notif_indicators[:10]  # Limit to 10
            elif tb_subcategory == "TB Outcomes":
                summary = analytics.get_regional_summary()
                indicators = summary.get('indicators', {})
                outcome_indicators = [ind for ind in indicators.keys() if 'outcome' in ind.lower() or 'success' in ind.lower() or 'cured' in ind.lower()]
                available_indicators_tb = outcome_indicators
            else:  # All TB Data
                available_indicators_tb = ["All available indicators"]
            
            if available_indicators_tb:
                indicator_selection_mode = st.radio(
                    "Indicator Selection",
                    ["All Indicators", "Select Specific Indicators"],
                    key="indicator_mode",
                    horizontal=True
                )
                
                if indicator_selection_mode == "Select Specific Indicators" and available_indicators_tb != ["All available indicators"]:
                    selected_indicators_list = st.multiselect(
                        "Choose Indicators",
                        available_indicators_tb,
                        default=available_indicators_tb[:3] if len(available_indicators_tb) >= 3 else available_indicators_tb,
                        key="selected_indicators_report",
                        help="Select which indicators to include in the report"
                    )
                else:
                    selected_indicators_list = available_indicators_tb
        
        # Show selection summary
        if tb_subcategory and selected_indicators_list:
            st.info(f"""
            **Report Configuration:**
            - Category: {tb_subcategory}
            - Indicators: {len(selected_indicators_list)} selected
            - The report will focus on {tb_subcategory} data for the selected country/region
            """)
        
        # ==================================================================================
        # AUTO-GENERATE CHARTS (based on category and indicators)
        # ==================================================================================
        
        # Automatically determine which charts to generate based on category
        selected_chart_types = []
        
        if tb_subcategory == "TB Burden" and hasattr(st.session_state, 'tb_burden_analytics'):
            selected_chart_types = ["Regional Trend", "Top 10 High Burden"]
            
        elif tb_subcategory == "TB Notifications" and hasattr(st.session_state, 'tb_notif_analytics'):
            selected_chart_types = ["Top Notifying Countries", "Regional Trend"]
            
        elif tb_subcategory == "TB Outcomes" and hasattr(st.session_state, 'tb_notif_analytics'):
            selected_chart_types = ["Treatment Success Rates", "TSR Trends"]
        
        st.markdown("---")
    
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
            
            # FILTER STATISTICS BASED ON SELECTED INDICATORS
            if selected_indicators_list and selected_indicators_list != ["All available indicators"]:
                statistics = llm_generator.filter_statistics_by_indicators(statistics, selected_indicators_list)
            
            # GENERATE CHARTS USING DASHBOARD/INTERACTIVE CHART SYSTEM
            report_charts = {}
            report_charts_metadata = {}
            
            with st.spinner("🎨 Generating charts using dashboard data..."):
                # TB BURDEN CHARTS
                if tb_subcategory == "TB Burden" and hasattr(st.session_state, 'tb_burden_analytics'):
                    burden_analytics = st.session_state.tb_burden_analytics
                    burden_chart_gen = st.session_state.tb_burden_chart_gen
                    
                    for chart_type in selected_chart_types:
                        try:
                            if chart_type == "Regional Trend" and selected_indicators_list:
                                # Generate trend chart for each selected indicator
                                for indicator in selected_indicators_list[:3]:  # Limit
                                    ind_code = indicator.split('(')[0].strip() if '(' in indicator else indicator
                                    fig = burden_chart_gen.create_regional_trend_chart(
                                        indicator=ind_code,
                                        indicator_name=indicator
                                    )
                                    if fig:
                                        chart_key = f"Regional Trend - {indicator}"
                                        report_charts[chart_key] = fig
                                        report_charts_metadata[chart_key] = {
                                            'title': f'Regional Trend: {indicator}',
                                            'type': 'line_chart',
                                            'description': f'AFRO regional trend with 95% confidence intervals from dashboard data',
                                            'key_insights': f'Shows temporal pattern and uncertainty ranges for {indicator}'
                                        }
                            
                            elif chart_type == "Top 10 High Burden" and selected_indicators_list:
                                for indicator in selected_indicators_list[:2]:
                                    ind_code = indicator.split('(')[0].strip() if '(' in indicator else indicator
                                    fig = burden_chart_gen.create_top_burden_chart(
                                        indicator=ind_code,
                                        indicator_name=indicator,
                                        n=10,
                                        high=True
                                    )
                                    if fig:
                                        chart_key = f"Top 10 High - {indicator}"
                                        report_charts[chart_key] = fig
                                        report_charts_metadata[chart_key] = {
                                            'title': f'Top 10 High Burden: {indicator}',
                                            'type': 'bar_chart',
                                            'description': f'Countries with highest {indicator} (same as dashboard)',
                                            'key_insights': f'Identifies priority countries for intervention'
                                        }
                            
                            elif chart_type == "Top 10 Low Burden" and selected_indicators_list:
                                ind_code = selected_indicators_list[0].split('(')[0].strip() if '(' in selected_indicators_list[0] else selected_indicators_list[0]
                                fig = burden_chart_gen.create_top_burden_chart(
                                    indicator=ind_code,
                                    indicator_name=selected_indicators_list[0],
                                    n=10,
                                    high=False
                                )
                                if fig:
                                    chart_key = "Top 10 Low Burden"
                                    report_charts[chart_key] = fig
                                    report_charts_metadata[chart_key] = {
                                        'title': 'Top 10 Low Burden Countries',
                                        'type': 'bar_chart',
                                        'description': 'Countries with lowest burden (dashboard data)',
                                        'key_insights': 'Shows countries with best performance'
                                    }
                            
                            elif chart_type == "Geographic Map" and selected_indicators_list:
                                ind_code = selected_indicators_list[0].split('(')[0].strip() if '(' in selected_indicators_list[0] else selected_indicators_list[0]
                                fig = burden_chart_gen.create_map(
                                    indicator=ind_code,
                                    indicator_name=selected_indicators_list[0]
                                )
                                if fig:
                                    chart_key = "Geographic Distribution"
                                    report_charts[chart_key] = fig
                                    report_charts_metadata[chart_key] = {
                                        'title': 'Geographic Distribution Map',
                                        'type': 'map',
                                        'description': 'Spatial distribution across AFRO region (interactive map from dashboard)',
                                        'key_insights': 'Visualizes geographic patterns'
                                    }
                        except Exception as e:
                            st.warning(f"Could not generate {chart_type}: {e}")
                
                # TB NOTIFICATIONS CHARTS
                elif tb_subcategory == "TB Notifications" and hasattr(st.session_state, 'tb_notif_analytics'):
                    notif_analytics = st.session_state.tb_notif_analytics
                    notif_chart_gen = st.session_state.tb_notif_chart_gen
                    
                    for chart_type in selected_chart_types:
                        try:
                            if chart_type == "Top Notifying Countries" and selected_indicators_list:
                                for indicator in selected_indicators_list[:2]:
                                    ind_code = indicator.split('(')[0].strip() if '(' in indicator else indicator
                                    # Use correct method name
                                    fig = notif_chart_gen.create_top_notifying_chart(
                                        indicator=ind_code,
                                        indicator_name=indicator,
                                        n=10
                                    )
                                    if fig:
                                        chart_key = f"Top Countries - {indicator}"
                                        report_charts[chart_key] = fig
                                        report_charts_metadata[chart_key] = {
                                            'title': f'Top 10 Countries: {indicator}',
                                            'type': 'bar_chart',
                                            'description': f'Countries with highest {indicator} (dashboard data)',
                                            'key_insights': f'Identifies countries with highest case notifications'
                                        }
                            
                            elif chart_type == "Regional Trend" and selected_indicators_list:
                                for indicator in selected_indicators_list[:3]:
                                    ind_code = indicator.split('(')[0].strip() if '(' in indicator else indicator
                                    fig = notif_chart_gen.create_regional_trend_chart(
                                        indicator=ind_code,
                                        indicator_name=indicator
                                    )
                                    if fig:
                                        chart_key = f"Regional Trend - {indicator}"
                                        report_charts[chart_key] = fig
                                        report_charts_metadata[chart_key] = {
                                            'title': f'Regional Trend: {indicator}',
                                            'type': 'line_chart',
                                            'description': f'AFRO regional notification trend (from interactive charts)',
                                            'key_insights': f'Shows temporal patterns for {indicator}'
                                        }
                            
                            elif chart_type == "Age & Sex Distribution":
                                # Use correct method name
                                fig = notif_chart_gen.create_age_distribution_chart()
                                if fig:
                                    chart_key = "Age Sex Distribution"
                                    report_charts[chart_key] = fig
                                    report_charts_metadata[chart_key] = {
                                        'title': 'Age and Sex Distribution',
                                        'type': 'population_pyramid',
                                        'description': 'Demographics of TB notifications (dashboard visualization)',
                                        'key_insights': 'Shows age and sex patterns'
                                    }
                            
                            elif chart_type == "Notification Types":
                                # Skip if no country selected (this chart requires a country)
                                if selected_country:
                                    fig = notif_chart_gen.create_notification_types_chart(country=selected_country)
                                    if fig:
                                        chart_key = "Notification Types"
                                        report_charts[chart_key] = fig
                                        report_charts_metadata[chart_key] = {
                                            'title': f'TB Notification Types - {selected_country}',
                                            'type': 'pie_chart',
                                            'description': 'Breakdown by diagnosis method (dashboard chart)',
                                            'key_insights': 'Distribution of diagnostic methods'
                                        }
                                else:
                                    # For regional reports, use regional trend instead
                                    st.info("ℹ️ Notification Types chart requires country selection. Skipping for regional report.")
                        except Exception as e:
                            st.warning(f"Could not generate {chart_type}: {e}")
                
                # TB OUTCOMES CHARTS
                elif tb_subcategory == "TB Outcomes" and hasattr(st.session_state, 'tb_notif_analytics'):
                    notif_analytics = st.session_state.tb_notif_analytics
                    notif_chart_gen = st.session_state.tb_notif_chart_gen
                    
                    for chart_type in selected_chart_types:
                        try:
                            if chart_type == "Treatment Success Rates":
                                # Use correct method name: create_outcomes_bar_chart
                                fig = notif_chart_gen.create_outcomes_bar_chart(
                                    indicator='c_new_tsr',
                                    indicator_name='Treatment Success Rate (New/Relapse)',
                                    n=10
                                )
                                if fig:
                                    chart_key = "Treatment Success Rates"
                                    report_charts[chart_key] = fig
                                    report_charts_metadata[chart_key] = {
                                        'title': 'Treatment Success Rates by Country',
                                        'type': 'bar_chart',
                                        'description': 'TSR with WHO target line (dashboard visualization)',
                                        'key_insights': 'Performance against WHO 85% target'
                                    }
                            
                            elif chart_type == "Outcomes Breakdown":
                                # This chart requires a country parameter
                                if selected_country:
                                    fig = notif_chart_gen.create_outcomes_breakdown_chart(country=selected_country)
                                    if fig:
                                        chart_key = "Outcomes Breakdown"
                                        report_charts[chart_key] = fig
                                        report_charts_metadata[chart_key] = {
                                            'title': f'Treatment Outcomes Distribution - {selected_country}',
                                            'type': 'pie_chart',
                                            'description': 'Distribution of treatment results (dashboard chart)',
                                            'key_insights': 'Breakdown: Cured, Completed, Failed, Died, Lost'
                                        }
                                else:
                                    st.info("ℹ️ Outcomes Breakdown chart requires country selection. Skipping for regional report.")
                            
                            elif chart_type == "TSR Trends":
                                # Use correct method name: create_tsr_trend_chart
                                fig = notif_chart_gen.create_tsr_trend_chart(
                                    indicator='c_new_tsr',
                                    indicator_name='New/Relapse TSR'
                                )
                                if fig:
                                    chart_key = "TSR Trends"
                                    report_charts[chart_key] = fig
                                    report_charts_metadata[chart_key] = {
                                        'title': 'Treatment Success Rate Trends',
                                        'type': 'line_chart',
                                        'description': 'Regional TSR trends with WHO target (from interactive charts)',
                                        'key_insights': 'Shows progress toward WHO benchmarks over time'
                                    }
                        except Exception as e:
                            st.warning(f"Could not generate {chart_type}: {e}")
            
            # Generate report using LLM with selected indicators and dashboard charts
            with st.spinner(f"🤖 Generating AI-powered report in {selected_language}... This may take a moment."):
                report = llm_generator.generate_report(
                    statistics=statistics,
                    report_type=report_type,
                    country=selected_country,
                    custom_requirements=custom_prompt if custom_prompt else None,
                    language=selected_language,
                    selected_indicators=selected_indicators_list,
                    charts=report_charts_metadata
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
            
            # Display report with markdown rendering and embedded charts
            report_lines = report.split('\n')
            current_section = []
            
            for line in report_lines:
                # Check for chart placeholder
                if '[CHART:' in line and ']' in line:
                    # Display accumulated text
                    if current_section:
                        st.markdown('\n'.join(current_section))
                        current_section = []
                    
                    # Extract and display chart
                    chart_name = line[line.find('[CHART:')+7:line.find(']')].strip()
                    if chart_name in report_charts:
                        st.plotly_chart(report_charts[chart_name], use_container_width=True)
                else:
                    current_section.append(line)
            
            # Display remaining text
            if current_section:
                st.markdown('\n'.join(current_section))
            
            # Download buttons - Word and PDF
            st.markdown("---")
            st.markdown("### 📥 Download Report")
            
            col1, col2, col3 = st.columns(3)
            
            # Prepare report for export
            from report_exporter import ReportExporter
            exporter = ReportExporter()
            
            with col1:
                # Text download
                st.download_button(
                    label="📄 Download as Text",
                    data=report,
                    file_name=f"report_{selected_country or 'regional'}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                # Word download with charts
                try:
                    word_bytes = exporter.export_to_word(report, report_charts)
                    st.download_button(
                        label="📘 Download as Word",
                        data=word_bytes,
                        file_name=f"report_{selected_country or 'regional'}_{datetime.now().strftime('%Y%m%d')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                except Exception as e:
                    st.button("📘 Word (Install python-docx)", disabled=True, use_container_width=True,
                             help=f"Error: {str(e)}")
            
            with col3:
                # PDF download with charts
                try:
                    pdf_bytes = exporter.export_to_pdf(report, report_charts)
                    st.download_button(
                        label="📕 Download as PDF",
                        data=pdf_bytes,
                        file_name=f"report_{selected_country or 'regional'}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.button("📕 PDF (Install pdfkit)", disabled=True, use_container_width=True,
                             help=f"Error: {str(e)}")
            
            st.success(f"✅ Report generated successfully! {len(report_charts)} chart(s) from dashboard data included.")
            
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


def render_tb_burden_explorer(burden_visualizer, burden_analytics, current_lang):
    """Render TB Burden indicator explorer with tabs"""
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.markdown("### 📊 TB Burden Indicator Explorer")
    st.info("Explore TB burden indicators across countries and over time. Confidence intervals are shown on trend charts.")
    
    # Indicator categories in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Incidence",
        "💀 Mortality", 
        "🩺 TB/HIV",
        "🔍 Case Detection"
    ])
    
    with tab1:
        st.markdown("#### TB Incidence Indicators")
        
        inc_indicator = st.selectbox(
            "Select Incidence Indicator",
            ["e_inc_num", "e_inc_100k"],
            format_func=lambda x: {
                "e_inc_num": "TB Incidence (Total Cases)",
                "e_inc_100k": "TB Incidence Rate (per 100,000)"
            }[x],
            key="inc_indicator"
        )
        
        viz_type_inc = st.radio("Visualization Type", ["Country Comparison", "Regional Trend", "Country Trend"], horizontal=True, key="viz_inc")
        
        if viz_type_inc == "Country Comparison":
            year = st.slider("Select Year", 2000, 2024, 2024, key="inc_year")
            chart = burden_visualizer.create_burden_comparison_chart(
                indicator=inc_indicator,
                indicator_name="TB Incidence (Total Cases)" if inc_indicator == "e_inc_num" else "TB Incidence Rate (per 100,000)",
                year=year
            )
            st.plotly_chart(chart, use_container_width=True)
            
        elif viz_type_inc == "Regional Trend":
            chart = burden_visualizer.create_regional_trend_chart(
                indicator=inc_indicator,
                indicator_name="TB Incidence (Total Cases)" if inc_indicator == "e_inc_num" else "TB Incidence Rate (per 100,000)"
            )
            st.plotly_chart(chart, use_container_width=True)
            st.info("✓ Confidence intervals shown as shaded band")
            
        else:  # Country Trend
            countries = burden_analytics.burden_afro['country_clean'].unique()
            country = st.selectbox("Select Country", sorted(countries), key="inc_country")
            chart = burden_visualizer.create_trend_chart(
                country=country,
                indicator=inc_indicator,
                indicator_name="TB Incidence"
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.info("✓ Confidence intervals shown as shaded band")
    
    with tab2:
        st.markdown("#### TB Mortality Indicators")
        
        mort_indicator = st.selectbox(
            "Select Mortality Indicator",
            ["e_mort_num", "e_mort_100k"],
            format_func=lambda x: {
                "e_mort_num": "TB Mortality (Total Deaths)",
                "e_mort_100k": "TB Mortality Rate (per 100,000)"
            }[x],
            key="mort_indicator"
        )
        
        viz_type_mort = st.radio("Visualization Type", ["Country Comparison", "Regional Trend", "Country Trend"], horizontal=True, key="viz_mort")
        
        if viz_type_mort == "Country Comparison":
            year = st.slider("Select Year", 2000, 2024, 2024, key="mort_year")
            chart = burden_visualizer.create_burden_comparison_chart(
                indicator=mort_indicator,
                indicator_name="TB Mortality (Total Deaths)" if mort_indicator == "e_mort_num" else "TB Mortality Rate (per 100,000)",
                year=year
            )
            st.plotly_chart(chart, use_container_width=True)
            
        elif viz_type_mort == "Regional Trend":
            chart = burden_visualizer.create_regional_trend_chart(
                indicator=mort_indicator,
                indicator_name="TB Mortality (Total Deaths)" if mort_indicator == "e_mort_num" else "TB Mortality Rate (per 100,000)"
            )
            st.plotly_chart(chart, use_container_width=True)
            st.info("✓ Confidence intervals shown as shaded band")
            
        else:  # Country Trend
            countries = burden_analytics.burden_afro['country_clean'].unique()
            country = st.selectbox("Select Country", sorted(countries), key="mort_country")
            chart = burden_visualizer.create_trend_chart(
                country=country,
                indicator=mort_indicator,
                indicator_name="TB Mortality"
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.info("✓ Confidence intervals shown as shaded band")
    
    with tab3:
        st.markdown("#### TB/HIV Indicators")
        
        tbhiv_indicator = st.selectbox(
            "Select TB/HIV Indicator",
            ["e_inc_tbhiv_num", "e_mort_tbhiv_num"],
            format_func=lambda x: {
                "e_inc_tbhiv_num": "TB/HIV Incidence (Total Cases)",
                "e_mort_tbhiv_num": "TB/HIV Mortality (Total Deaths)"
            }[x],
            key="tbhiv_indicator"
        )
        
        viz_type_tbhiv = st.radio("Visualization Type", ["Country Comparison", "Regional Trend", "Country Trend"], horizontal=True, key="viz_tbhiv")
        
        if viz_type_tbhiv == "Country Comparison":
            year = st.slider("Select Year", 2000, 2024, 2024, key="tbhiv_year")
            chart = burden_visualizer.create_burden_comparison_chart(
                indicator=tbhiv_indicator,
                indicator_name="TB/HIV Incidence" if tbhiv_indicator == "e_inc_tbhiv_num" else "TB/HIV Mortality",
                year=year
            )
            st.plotly_chart(chart, use_container_width=True)
            
        elif viz_type_tbhiv == "Regional Trend":
            chart = burden_visualizer.create_regional_trend_chart(
                indicator=tbhiv_indicator,
                indicator_name="TB/HIV Incidence" if tbhiv_indicator == "e_inc_tbhiv_num" else "TB/HIV Mortality"
            )
            st.plotly_chart(chart, use_container_width=True)
            st.info("✓ Confidence intervals shown as shaded band")
            
        else:  # Country Trend
            countries = burden_analytics.burden_afro['country_clean'].unique()
            country = st.selectbox("Select Country", sorted(countries), key="tbhiv_country")
            chart = burden_visualizer.create_trend_chart(
                country=country,
                indicator=tbhiv_indicator,
                indicator_name="TB/HIV"
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.info("✓ Confidence intervals shown as shaded band")
    
    with tab4:
        st.markdown("#### Case Detection Rate")
        st.info("📊 Case Detection Rate = Percentage of estimated incident TB cases that are detected and notified")
        
        viz_type_cdr = st.radio("Visualization Type", ["Country Comparison", "Regional Trend"], horizontal=True, key="viz_cdr")
        
        if viz_type_cdr == "Country Comparison":
            year = st.slider("Select Year", 2000, 2024, 2024, key="cdr_year")
            
            # Get CDR data for all countries for selected year
            data_year = burden_analytics.burden_afro[burden_analytics.burden_afro['year'] == year].copy()
            data_year = data_year.sort_values('c_cdr', ascending=False)
            
            fig = px.bar(
                data_year,
                x='c_cdr',
                y='country_clean',
                orientation='h',
                title=f'Case Detection Rate by Country ({year})',
                labels={'c_cdr': 'Case Detection Rate (%)', 'country_clean': 'Country'},
                color='c_cdr',
                color_continuous_scale='RdYlGn',
                height=800
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
        else:  # Regional Trend
            # Calculate regional average CDR over time
            cdr_trend = burden_analytics.burden_afro.groupby('year').agg({
                'c_cdr': 'mean',
                'c_cdr_hi': 'mean',
                'c_cdr_lo': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            
            # Add upper bound (invisible line)
            fig.add_trace(go.Scatter(
                x=cdr_trend['year'],
                y=cdr_trend['c_cdr_hi'],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                name='Upper Bound',
                hoverinfo='skip'
            ))
            
            # Add lower bound with fill to upper bound (creates CI band)
            fig.add_trace(go.Scatter(
                x=cdr_trend['year'],
                y=cdr_trend['c_cdr_lo'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',  # Fill to previous trace (upper bound)
                fillcolor='rgba(40, 167, 69, 0.2)',
                name='95% CI',
                showlegend=True,
                hoverinfo='skip'
            ))
            
            # Add main estimate line on top
            fig.add_trace(go.Scatter(
                x=cdr_trend['year'],
                y=cdr_trend['c_cdr'],
                mode='lines+markers',
                name='CDR Estimate',
                line=dict(width=3, color='#28a745'),
                marker=dict(size=8),
                hovertemplate='<b>Year %{x}</b><br>' +
                             'CDR: %{y:.1f}%<br>' +
                             'High Bound: %{customdata[0]:.1f}%<br>' +
                             'Low Bound: %{customdata[1]:.1f}%<br>' +
                             '<extra></extra>',
                customdata=cdr_trend[['c_cdr_hi', 'c_cdr_lo']].values
            ))
            
            fig.update_layout(
                title='Regional Case Detection Rate Trend (AFRO) [with 95% CI]',
                xaxis_title='Year',
                yaxis_title='Case Detection Rate (%)',
                height=500,
                template='plotly_white',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.info("✓ Confidence intervals shown as shaded band")


def render_tb_notifications_explorer(notif_analytics, chart_gen, current_lang):
    """Render TB Notifications indicator explorer with tabs"""
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.markdown("### 📊 TB Notifications Indicator Explorer")
    st.info("Explore TB notification indicators from dashboard across countries and over time.")
    
    # Indicator categories in tabs - matching dashboard indicators
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Total Notifications",
        "🔬 By Diagnosis Method",
        "👥 Age & Sex Distribution",
        "📋 Notification Types"
    ])
    
    latest_year = notif_analytics.get_latest_year()
    countries = notif_analytics.get_country_list()
    
    # TAB 1: Total Notifications (c_newinc)
    with tab1:
        st.markdown("#### Total New & Relapse TB Cases")
        
        viz_type = st.radio(
            "Visualization Type",
            ["Country Comparison", "Regional Trend", "Country Trend"],
            horizontal=True,
            key="notif_total_viz"
        )
        
        if viz_type == "Country Comparison":
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Top 10 Highest")
                chart = chart_gen.create_top_notifying_chart(
                    indicator='c_newinc',
                    indicator_name='Total New & Relapse TB',
                    n=10,
                    year=latest_year,
                    high=True
                )
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
            
            with col2:
                st.markdown("##### Top 10 Lowest")
                chart = chart_gen.create_top_notifying_chart(
                    indicator='c_newinc',
                    indicator_name='Total New & Relapse TB',
                    n=10,
                    year=latest_year,
                    high=False
                )
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
        
        elif viz_type == "Regional Trend":
            chart = chart_gen.create_regional_trend_chart(
                indicator='c_newinc',
                indicator_name='Total New & Relapse TB Cases'
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        elif viz_type == "Country Trend":
            selected_country = st.selectbox(
                "Select Country",
                countries,
                key="notif_total_country"
            )
            
            # Create simple country trend
            country_data = notif_analytics.notif_afro[
                notif_analytics.notif_afro['country_clean'] == selected_country
            ][['year', 'c_newinc']].sort_values('year')
            
            if not country_data.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=country_data['year'],
                    y=country_data['c_newinc'],
                    mode='lines+markers',
                    name=selected_country,
                    line=dict(width=3, color='#3498db'),
                    marker=dict(size=8)
                ))
                fig.update_layout(
                    title=f'Total Notifications Trend - {selected_country}',
                    xaxis_title='Year',
                    yaxis_title='Total Cases',
                    height=500,
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # TAB 2: By Diagnosis Method
    with tab2:
        st.markdown("#### Notifications by Diagnosis Method")
        
        viz_type = st.radio(
            "Visualization Type",
            ["Country Comparison", "Regional Trend"],
            horizontal=True,
            key="notif_diagnosis_viz"
        )
        
        indicator_select = st.selectbox(
            "Select Indicator",
            ["new_labconf", "new_clindx", "new_ep"],
            format_func=lambda x: {
                "new_labconf": "Pulmonary Lab Confirmed",
                "new_clindx": "Pulmonary Clinically Diagnosed",
                "new_ep": "Extrapulmonary TB"
            }[x],
            key="notif_diagnosis_indicator"
        )
        
        indicator_names = {
            "new_labconf": "Pulmonary Lab Confirmed Cases",
            "new_clindx": "Pulmonary Clinically Diagnosed Cases",
            "new_ep": "Extrapulmonary TB Cases"
        }
        
        if viz_type == "Country Comparison":
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Top 10 Countries")
                chart = chart_gen.create_top_notifying_chart(
                    indicator=indicator_select,
                    indicator_name=indicator_names[indicator_select],
                    n=10,
                    year=latest_year,
                    high=True
                )
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
            
            with col2:
                st.markdown("##### Bottom 10 Countries")
                chart = chart_gen.create_top_notifying_chart(
                    indicator=indicator_select,
                    indicator_name=indicator_names[indicator_select],
                    n=10,
                    year=latest_year,
                    high=False
                )
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
        
        elif viz_type == "Regional Trend":
            chart = chart_gen.create_regional_trend_chart(
                indicator=indicator_select,
                indicator_name=indicator_names[indicator_select]
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)
    
    # TAB 3: Age & Sex Distribution
    with tab3:
        st.markdown("#### TB Cases by Age Group and Sex")
        
        year_select = st.slider(
            "Select Year",
            min_value=int(notif_analytics.notif_afro['year'].min()),
            max_value=latest_year,
            value=latest_year,
            key="notif_age_year"
        )
        
        age_chart = chart_gen.create_age_distribution_chart(year=year_select)
        if age_chart:
            st.plotly_chart(age_chart, use_container_width=True)
            
            # Show data table
            age_dist = notif_analytics.get_age_distribution(year=year_select)
            if not age_dist.empty:
                st.markdown("##### Age Distribution Summary")
                st.dataframe(
                    age_dist[['age_group', 'male', 'female', 'total', 'percent']].style.format({
                        'male': '{:,.0f}',
                        'female': '{:,.0f}',
                        'total': '{:,.0f}',
                        'percent': '{:.1f}%'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("Age distribution data not available for selected year")
    
    # TAB 4: Notification Types
    with tab4:
        st.markdown("#### Notification Types Breakdown by Country")
        
        selected_country = st.selectbox(
            "Select Country",
            countries,
            key="notif_types_country"
        )
        
        year_select = st.slider(
            "Select Year",
            min_value=int(notif_analytics.notif_afro['year'].min()),
            max_value=latest_year,
            value=latest_year,
            key="notif_types_year"
        )
        
        types_chart = chart_gen.create_notification_types_chart(
            country=selected_country,
            year=year_select
        )
        
        if types_chart:
            st.plotly_chart(types_chart, use_container_width=True)
            
            # Show breakdown metrics
            types_data = notif_analytics.get_notification_types_breakdown(selected_country, year_select)
            
            if 'error' not in types_data:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Lab Confirmed", f"{types_data['pulmonary_lab_confirmed']:,.0f}")
                with col2:
                    st.metric("Clinically Diagnosed", f"{types_data['pulmonary_clin_diagnosed']:,.0f}")
                with col3:
                    st.metric("Extrapulmonary", f"{types_data['extrapulmonary']:,.0f}")
        else:
            st.warning(f"Notification types data not available for {selected_country}")


def render_tb_outcomes_explorer(outcomes_analytics, chart_gen, current_lang):
    """Render TB Outcomes indicator explorer with tabs"""
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.markdown("### 🏥 TB Treatment Outcomes Indicator Explorer")
    st.info("Explore TB treatment outcomes from dashboard with WHO targets.")
    
    # Category selector
    outcome_category = st.selectbox(
        "Patient Category",
        ["newrel", "ret_nrel", "tbhiv"],
        format_func=lambda x: {
            "newrel": "New and Relapse TB Cases",
            "ret_nrel": "Retreatment TB Cases",
            "tbhiv": "TB/HIV Co-infected Cases"
        }[x],
        key="outcomes_explorer_category"
    )
    
    # Indicator categories in tabs - matching dashboard
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Treatment Success Rate",
        "📊 Outcomes Breakdown",
        "📈 TSR Trends",
        "⚖️ WHO Performance"
    ])
    
    latest_year = int(outcomes_analytics.outcomes_afro['year'].max())
    countries = outcomes_analytics.get_country_list()
    
    # Map category to TSR indicator
    tsr_indicators = {
        'newrel': 'c_new_tsr',
        'ret_nrel': 'c_ret_tsr',
        'tbhiv': 'c_tbhiv_tsr'
    }
    tsr_indicator = tsr_indicators.get(outcome_category, 'c_new_tsr')
    
    # TAB 1: Treatment Success Rate
    with tab1:
        st.markdown("#### Treatment Success Rate by Country")
        
        viz_type = st.radio(
            "Visualization Type",
            ["Top Performers", "Bottom Performers", "All Countries Distribution"],
            horizontal=True,
            key="outcomes_tsr_viz"
        )
        
        if viz_type == "Top Performers":
            chart = chart_gen.create_outcomes_bar_chart(
                indicator=tsr_indicator,
                indicator_name='Treatment Success Rate',
                n=15,
                year=latest_year,
                high=True
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        elif viz_type == "Bottom Performers":
            chart = chart_gen.create_outcomes_bar_chart(
                indicator=tsr_indicator,
                indicator_name='Treatment Success Rate',
                n=15,
                year=latest_year,
                high=False
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        elif viz_type == "All Countries Distribution":
            chart = chart_gen.create_outcomes_equity_chart(
                indicator=tsr_indicator,
                indicator_name='Treatment Success Rate',
                year=latest_year
            )
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                
                # Show equity measures
                equity = outcomes_analytics.calculate_outcomes_equity(tsr_indicator, latest_year)
                if 'error' not in equity:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Min TSR", f"{equity['min_value']:.1f}%")
                    with col2:
                        st.metric("Max TSR", f"{equity['max_value']:.1f}%")
                    with col3:
                        st.metric("Range", f"{equity['range']:.1f}%")
                    with col4:
                        st.metric("Above WHO Target", f"{equity['countries_above_target']}")
    
    # TAB 2: Outcomes Breakdown
    with tab2:
        st.markdown("#### Treatment Outcomes by Country")
        
        selected_country = st.selectbox(
            "Select Country",
            countries,
            key="outcomes_breakdown_country"
        )
        
        year_select = st.slider(
            "Select Year",
            min_value=int(outcomes_analytics.outcomes_afro['year'].min()),
            max_value=latest_year,
            value=latest_year,
            key="outcomes_breakdown_year"
        )
        
        breakdown_chart = chart_gen.create_outcomes_breakdown_chart(
            country=selected_country,
            year=year_select,
            category=outcome_category
        )
        
        if breakdown_chart:
            st.plotly_chart(breakdown_chart, use_container_width=True)
            
            # Show detailed metrics
            breakdown_data = outcomes_analytics.get_outcomes_breakdown(
                selected_country, year_select, outcome_category
            )
            
            if 'error' not in breakdown_data:
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Cohort", f"{breakdown_data['cohort']:,.0f}")
                with col2:
                    st.metric("Success", f"{breakdown_data['success']:,.0f}")
                with col3:
                    st.metric("Failed", f"{breakdown_data['failed']:,.0f}")
                with col4:
                    st.metric("Died", f"{breakdown_data['died']:,.0f}")
                with col5:
                    st.metric("Lost", f"{breakdown_data['lost']:,.0f}")
                
                if breakdown_data['tsr'] > 0:
                    tsr_val = breakdown_data['tsr']
                    st.info(f"""
                    **Treatment Success Rate:** {tsr_val:.1f}%
                    {"✅ Above WHO target (≥85%)" if tsr_val >= 85 else "⚠️ Below WHO target (≥85%)"}
                    """)
        else:
            st.warning(f"Outcomes data not available for {selected_country}")
    
    # TAB 3: TSR Trends
    with tab3:
        st.markdown("#### Treatment Success Rate Trends")
        
        viz_type = st.radio(
            "Visualization Type",
            ["Regional Trend", "Country Trend"],
            horizontal=True,
            key="outcomes_trend_viz"
        )
        
        if viz_type == "Regional Trend":
            trend_chart = chart_gen.create_tsr_trend_chart(
                indicator=tsr_indicator,
                indicator_name='Treatment Success Rate'
            )
            if trend_chart:
                st.plotly_chart(trend_chart, use_container_width=True)
                
                # Show trend statistics
                trend_data = outcomes_analytics.get_outcomes_regional_trend(tsr_indicator)
                if not trend_data.empty:
                    latest = trend_data.iloc[-1]
                    earliest = trend_data.iloc[0]
                    change = latest['mean_tsr'] - earliest['mean_tsr']
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Latest Year TSR", f"{latest['mean_tsr']:.1f}%")
                    with col2:
                        st.metric("Change Since First Year", f"{change:+.1f}%")
                    with col3:
                        st.metric("Standard Deviation", f"{latest['std_tsr']:.1f}%")
        
        elif viz_type == "Country Trend":
            selected_country = st.selectbox(
                "Select Country",
                countries,
                key="outcomes_trend_country"
            )
            
            # Get country-specific trend
            country_data = outcomes_analytics.outcomes_afro[
                outcomes_analytics.outcomes_afro['country_clean'] == selected_country
            ][['year', tsr_indicator]].sort_values('year')
            
            if not country_data.empty and country_data[tsr_indicator].sum() > 0:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=country_data['year'],
                    y=country_data[tsr_indicator],
                    mode='lines+markers',
                    name=selected_country,
                    line=dict(width=3, color='#27ae60'),
                    marker=dict(size=8)
                ))
                
                # Add WHO target line
                fig.add_hline(y=85, line_dash="dash", line_color="gray",
                             annotation_text="WHO Target: 85%",
                             annotation_position="right")
                
                fig.update_layout(
                    title=f'Treatment Success Rate Trend - {selected_country}',
                    xaxis_title='Year',
                    yaxis_title='TSR (%)',
                    height=500,
                    template='plotly_white',
                    yaxis=dict(range=[0, 100])
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"TSR trend data not available for {selected_country}")
    
    # TAB 4: WHO Performance
    with tab4:
        st.markdown("#### WHO Target Performance Summary")
        
        # Get outcomes summary
        outcomes_summary = outcomes_analytics.get_outcomes_summary(category=outcome_category)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Regional Performance")
            perf_data = {
                'Metric': ['Treatment Success', 'Died', 'Lost to Follow-up', 'Failed'],
                'Regional %': [
                    f"{outcomes_summary['success_pct']:.1f}%",
                    f"{outcomes_summary['died_pct']:.1f}%",
                    f"{outcomes_summary['lost_pct']:.1f}%",
                    f"{outcomes_summary['failed_pct']:.1f}%"
                ],
                'WHO Target': ['≥85%', '<5%', '<5%', 'N/A'],
                'Status': [
                    '✅' if outcomes_summary['success_pct'] >= 85 else '⚠️',
                    '✅' if outcomes_summary['died_pct'] < 5 else '⚠️',
                    '✅' if outcomes_summary['lost_pct'] < 5 else '⚠️',
                    'N/A'
                ]
            }
            st.dataframe(pd.DataFrame(perf_data), hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("##### Key Statistics")
            col2_1, col2_2 = st.columns(2)
            
            with col2_1:
                st.metric("Total Cohort", f"{outcomes_summary['cohort']:,.0f}")
                st.metric("Success Cases", f"{outcomes_summary['success']:,.0f}")
            
            with col2_2:
                if 'countries_above_85' in outcomes_summary:
                    st.metric("Countries ≥85%", 
                             f"{outcomes_summary['countries_above_85']}/{outcomes_summary['total_countries']}")
                if 'tsr_mean' in outcomes_summary:
                    st.metric("Mean TSR", f"{outcomes_summary['tsr_mean']:.1f}%")
        
        # Overall assessment
        success_above = outcomes_summary['success_pct'] >= 85
        died_below = outcomes_summary['died_pct'] < 5
        lost_below = outcomes_summary['lost_pct'] < 5
        
        st.markdown("---")
        st.markdown("##### Overall Assessment")
        assessment = (
            'EXCELLENT - All targets met!' if (success_above and died_below and lost_below)
            else 'GOOD - Most targets met' if sum([success_above, died_below, lost_below]) >= 2
            else 'NEEDS IMPROVEMENT - Targets not met'
        )
        
        color = '#27ae60' if assessment.startswith('EXCELLENT') else '#f39c12' if assessment.startswith('GOOD') else '#e74c3c'
        st.markdown(f"<div style='padding: 1rem; background: {color}; color: white; border-radius: 5px; text-align: center; font-weight: bold;'>{assessment}</div>", unsafe_allow_html=True)


def render_mortality_visualizer():
    """Render Mortality interactive visualizer - similar to TB visualizer"""
    current_lang = st.session_state.get("selected_language", "English")
    
    # Check if data is loaded - both maternal and child analytics must be available
    if (not hasattr(st.session_state, 'maternal_analytics') or st.session_state.maternal_analytics is None or
        not hasattr(st.session_state, 'child_analytics') or st.session_state.child_analytics is None):
        st.error("Mortality data not fully initialized. Please initialize the system from the sidebar.")
        return
    
    # Category selector
    st.markdown("""
    <div class="info-box" style="margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.95rem;">
            <strong>Select Mortality Data Category:</strong> Choose which aspect of mortality data you want to visualize
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for mortality subcategory if not exists
    if 'mortality_viz_subcategory' not in st.session_state:
        st.session_state.mortality_viz_subcategory = 'Maternal Mortality'
    
    # Sub-category selection buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Maternal Mortality", 
                     use_container_width=True, 
                     type="primary" if st.session_state.mortality_viz_subcategory == 'Maternal Mortality' else "secondary",
                     key="maternal_mortality_viz_btn"):
            st.session_state.mortality_viz_subcategory = 'Maternal Mortality'
            st.rerun()
    
    with col2:
        if st.button("👶 Child Mortality", 
                     use_container_width=True, 
                     type="primary" if st.session_state.mortality_viz_subcategory == 'Child Mortality' else "secondary",
                     key="child_mortality_viz_btn"):
            st.session_state.mortality_viz_subcategory = 'Child Mortality'
            st.rerun()
    
    # Route to appropriate visualizer
    if st.session_state.mortality_viz_subcategory == 'Maternal Mortality':
        render_maternal_mortality_visualizer()
    else:
        render_child_mortality_visualizer()


def render_maternal_mortality_visualizer():
    """Render Maternal Mortality interactive charts"""
    current_lang = st.session_state.get("selected_language", "English")
    maternal_analytics = st.session_state.maternal_analytics
    maternal_chart_gen = st.session_state.maternal_chart_gen
    
    st.markdown("### 📊 Maternal Mortality Interactive Charts")
    
    # Country selection
    countries = maternal_analytics.get_country_list()
    selected_country = st.selectbox("Select Country (optional)", [None] + countries, key="maternal_viz_country")
    
    # Year selection
    latest_year = maternal_analytics.get_latest_year()
    selected_year = st.selectbox("Select Year", 
                                options=range(2000, latest_year + 1),
                                index=len(range(2000, latest_year + 1)) - 1,
                                key="maternal_viz_year")
    
    # Chart type selection
    chart_type = st.radio("Select Chart Type",
                         ["Top Countries", "Trend Analysis", "Geographic Map", "Equity Analysis"],
                         key="maternal_viz_chart_type")
    
    if chart_type == "Top Countries":
        col1, col2 = st.columns(2)
        with col1:
            n_countries = st.slider("Number of Countries", 5, 20, 10, key="maternal_top_n")
        with col2:
            high_low = st.radio("Show", ["High MMR", "Low MMR"], key="maternal_high_low")
        
        chart = maternal_chart_gen.create_top_mmr_chart(
            n=n_countries,
            year=selected_year,
            high_burden=(high_low == "High MMR")
        )
        st.plotly_chart(chart, use_container_width=True)
    
    elif chart_type == "Trend Analysis":
        if selected_country:
            chart = maternal_chart_gen.create_country_trend_chart(selected_country)
        else:
            chart = maternal_chart_gen.create_regional_trend_chart()
        st.plotly_chart(chart, use_container_width=True)
    
    elif chart_type == "Geographic Map":
        chart = maternal_chart_gen.create_map(year=selected_year)
        st.plotly_chart(chart, use_container_width=True)
    
    elif chart_type == "Equity Analysis":
        chart = maternal_chart_gen.create_equity_chart(year=selected_year)
        st.plotly_chart(chart, use_container_width=True)


def render_child_mortality_visualizer():
    """Render Child Mortality interactive charts"""
    current_lang = st.session_state.get("selected_language", "English")
    child_analytics = st.session_state.child_analytics
    child_chart_gen = st.session_state.child_chart_gen
    
    st.markdown("### 👶 Child Mortality Interactive Charts")
    
    # Indicator selection
    indicator_options = {
        'Under-five mortality rate': 'Under-five Mortality Rate',
        'Infant mortality rate': 'Infant Mortality Rate',
        'Child mortality rate (aged 1-4 years)': 'Child Mortality Rate (1-4 years)'
    }
    
    selected_indicator = st.selectbox(
        "Select Indicator",
        options=list(indicator_options.keys()),
        format_func=lambda x: indicator_options[x],
        key="child_viz_indicator"
    )
    
    # Country selection
    countries = child_analytics.get_country_list()
    selected_country = st.selectbox("Select Country (optional)", [None] + countries, key="child_viz_country")
    
    # Year selection
    latest_year = child_analytics.get_latest_year(selected_indicator)
    selected_year = st.selectbox("Select Year",
                                options=range(2000, latest_year + 1),
                                index=len(range(2000, latest_year + 1)) - 1,
                                key="child_viz_year")
    
    # Chart type selection
    chart_type = st.radio("Select Chart Type",
                         ["Top Countries", "Trend Analysis", "Sex Disaggregation", "Geographic Map", "Equity Analysis"],
                         key="child_viz_chart_type")
    
    if chart_type == "Top Countries":
        col1, col2 = st.columns(2)
        with col1:
            n_countries = st.slider("Number of Countries", 5, 20, 10, key="child_top_n")
        with col2:
            high_low = st.radio("Show", ["High Mortality", "Low Mortality"], key="child_high_low")
        
        chart = child_chart_gen.create_top_mortality_chart(
            indicator=selected_indicator,
            indicator_name=indicator_options[selected_indicator],
            n=n_countries,
            year=selected_year,
            high_burden=(high_low == "High Mortality")
        )
        st.plotly_chart(chart, use_container_width=True)
    
    elif chart_type == "Trend Analysis":
        if selected_country:
            chart = child_chart_gen.create_country_trend_chart(
                selected_country,
                indicator=selected_indicator,
                indicator_name=indicator_options[selected_indicator]
            )
        else:
            chart = child_chart_gen.create_regional_trend_chart(
                indicator=selected_indicator,
                indicator_name=indicator_options[selected_indicator]
            )
        st.plotly_chart(chart, use_container_width=True)
    
    elif chart_type == "Sex Disaggregation":
        chart = child_chart_gen.create_sex_comparison_chart(
            indicator=selected_indicator,
            indicator_name=indicator_options[selected_indicator],
            year=selected_year
        )
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Sex disaggregated data not available for this indicator/year.")
    
    elif chart_type == "Geographic Map":
        chart = child_chart_gen.create_map(
            indicator=selected_indicator,
            indicator_name=indicator_options[selected_indicator],
            year=selected_year
        )
        st.plotly_chart(chart, use_container_width=True)
    
    elif chart_type == "Equity Analysis":
        chart = child_chart_gen.create_equity_chart(
            indicator=selected_indicator,
            indicator_name=indicator_options[selected_indicator],
            year=selected_year
        )
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No data available for equity analysis.")


def render_visualizer_page():
    """Render the interactive visualizer page"""
    # Get current health topic and language
    health_topic = st.session_state.get("indicator_type", "Mortality")
    selected_language = st.session_state.get("selected_language", "English")
    
    # Display current settings with topic-specific styling
    topic_colors = {
        "Tuberculosis": "#8B4513",
        "Mortality": "#f5576c"
    }
    topic_color = topic_colors.get(health_topic, "#0066CC")
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem; padding: 1rem; background: linear-gradient(135deg, {topic_color} 0%, #004499 100%); border-radius: 10px; color: white;">
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
    elif health_topic == "Mortality":
        # For Mortality, check that both maternal and child analytics are available
        if (hasattr(st.session_state, 'maternal_analytics') and st.session_state.maternal_analytics is not None and
            hasattr(st.session_state, 'child_analytics') and st.session_state.child_analytics is not None):
            # Render Mortality visualizer directly (no separate visualizer class needed)
            render_mortality_visualizer()
            return
        else:
            st.error(f"Mortality data not fully initialized. Please initialize the system from the sidebar.")
            return
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
    
    # Display topic-specific description
    st.markdown(get_topic_content(health_topic, "visualizer_desc", current_lang))
    
    # ==================================================================================
    # TB SUBCATEGORY SELECTION (for Tuberculosis visualizations)
    # ==================================================================================
    
    if health_topic == "Tuberculosis":
        st.markdown("---")
        st.markdown("### 📊 Select TB Data Category")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📉 TB Burden", 
                         use_container_width=True,
                         type="primary" if st.session_state.get('viz_tb_subcategory') == 'TB Burden' else "secondary",
                         key="viz_tb_burden"):
                st.session_state.viz_tb_subcategory = 'TB Burden'
                st.rerun()
        
        with col2:
            if st.button("📊 TB Notifications", 
                         use_container_width=True,
                         type="primary" if st.session_state.get('viz_tb_subcategory') == 'TB Notifications' else "secondary",
                         key="viz_tb_notif"):
                st.session_state.viz_tb_subcategory = 'TB Notifications'
                st.rerun()
        
        with col3:
            if st.button("🏥 TB Outcomes", 
                         use_container_width=True,
                         type="primary" if st.session_state.get('viz_tb_subcategory') == 'TB Outcomes' else "secondary",
                         key="viz_tb_outcomes"):
                st.session_state.viz_tb_subcategory = 'TB Outcomes'
                st.rerun()
        
        # Initialize if not set
        if 'viz_tb_subcategory' not in st.session_state:
            st.session_state.viz_tb_subcategory = 'TB Burden'
        
        # Show selected category info
        viz_category = st.session_state.viz_tb_subcategory
        category_descriptions = {
            'TB Burden': 'WHO burden estimates including incidence, mortality, and TB/HIV data',
            'TB Notifications': 'Reported TB cases by country, type, and demographics',
            'TB Outcomes': 'Treatment success rates, outcomes, and performance metrics'
        }
        
        st.info(f"**{viz_category}**: {category_descriptions[viz_category]}")
        st.markdown("---")
        
        # Filter visualizer options based on selected subcategory
        if viz_category == 'TB Burden' and hasattr(st.session_state, 'tb_burden_analytics'):
            # Use TB Burden visualizer - special handling
            from tb_burden_chart_generator import TBBurdenChartGenerator
            burden_visualizer = TBBurdenChartGenerator(st.session_state.tb_burden_analytics)
            burden_analytics = st.session_state.tb_burden_analytics
            
            # Special TB Burden exploration interface
            render_tb_burden_explorer(burden_visualizer, burden_analytics, current_lang)
            return  # Exit early for TB Burden
        
        elif viz_category == 'TB Notifications' and hasattr(st.session_state, 'tb_notif_analytics'):
            # Use TB Notifications visualizer
            render_tb_notifications_explorer(st.session_state.tb_notif_analytics, st.session_state.tb_notif_chart_gen, current_lang)
            return  # Exit early for TB Notifications
        
        elif viz_category == 'TB Outcomes' and hasattr(st.session_state, 'tb_notif_analytics'):
            # Use TB Outcomes visualizer
            render_tb_outcomes_explorer(st.session_state.tb_notif_analytics, st.session_state.tb_notif_chart_gen, current_lang)
            return  # Exit early for TB Outcomes
    
    # Control Panel (for non-TB Burden visualizations)
    with st.expander("⚙️ Chart Controls", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Country selection
            if hasattr(pipeline, 'get_countries'):
                countries = pipeline.get_countries()
            else:
                # Fallback: try to get countries from analytics
                if hasattr(analytics, 'get_country_list'):
                    countries = analytics.get_country_list()
                else:
                    countries = []
            
            if countries:
                selected_country = st.selectbox(
                    "Select Country",
                    countries,
                    index=0
                )
            else:
                st.warning("No countries available")
                selected_country = None
            
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
                # Get indicators from pipeline if available
                if hasattr(pipeline, 'get_indicators'):
                    indicators = pipeline.get_indicators()
                else:
                    # Fallback to default mortality indicators
                    indicators = [
                        'Under-five mortality rate',
                        'Infant mortality rate',
                        'Neonatal mortality rate',
                        'Maternal mortality ratio'
                    ]
            
            if indicators:
                selected_indicator = st.selectbox(
                    "Select Indicator",
                    indicators,
                    index=0
                )
            else:
                st.warning("No indicators available")
                selected_indicator = None
        
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
            ["Tuberculosis", "Mortality"],
            index=0,  # Default to Tuberculosis
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
        
        if st.button(f"📈 {get_translation('visualizer', current_lang)}", use_container_width=True, key="nav_visualizer"):
            st.session_state.current_page = 'Visualizer'
            st.rerun()
        
        if st.button(f"📋 {get_translation('reports', current_lang)}", use_container_width=True, key="nav_reports"):
            st.session_state.current_page = 'Reports'
            st.rerun()
        
        if st.button(f"🤖 {get_translation('chatbot', current_lang)}", use_container_width=True, key="nav_chatbot"):
            st.session_state.current_page = 'Chatbot'
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
                
                # TB Burden status
                if hasattr(st.session_state, 'tb_burden_analytics') and st.session_state.tb_burden_analytics is not None:
                    burden_summary = st.session_state.tb_burden_analytics.get_data_summary()
                    st.caption(f"✓ TB Burden Records: {burden_summary['total_records']:,}")
                    st.caption(f"  Year Range: {burden_summary['year_range'][0]}-{burden_summary['year_range'][1]}")
                else:
                    st.caption("⚠️ TB Burden data: Not loaded")
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

