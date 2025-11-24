"""
TB Chart Generator Module
Creates visualizations for TB analytics
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Tuple
from tb_analytics import TBAnalytics


class TBChartGenerator:
    """Generate charts and visualizations for TB data"""
    
    def __init__(self, analytics: TBAnalytics):
        """
        Initialize TB chart generator
        
        Args:
            analytics: TBAnalytics instance
        """
        self.analytics = analytics
        self.pipeline = analytics.pipeline
    
    def create_trend_chart(self, country: str, indicator: str) -> go.Figure:
        """
        Create trend chart for country and indicator
        
        Args:
            country: Country name
            indicator: Indicator name
        
        Returns:
            Plotly figure
        """
        indicator_map = {
            "TB Notifications (Total New Cases)": ("c_newinc", "notifications"),
            "New Smear-Positive Cases": ("new_sp", "notifications"),
            "New Smear-Negative Cases": ("new_sn", "notifications"),
            "New Extrapulmonary Cases": ("new_ep", "notifications"),
            "Treatment Success Rate - New Cases (%)": ("c_new_sp_tsr", "outcomes"),
            "Treatment Success Rate (%)": ("c_new_tsr", "outcomes")
        }
        
        indicator_info = indicator_map.get(indicator)
        if not indicator_info:
            return None
        
        col_name, data_type = indicator_info
        
        # Select appropriate dataframe
        if data_type == "notifications":
            df = self.analytics.tb_notifications_df
        elif data_type == "outcomes":
            df = self.analytics.tb_outcomes_df
        else:
            return None
        
        country_data = self.pipeline.filter_by_country(country, df)
        
        if len(country_data) == 0 or col_name not in country_data.columns:
            return None
        
        sorted_data = country_data.sort_values('year')
        values = sorted_data[col_name].dropna()
        
        if len(values) == 0:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sorted_data['year'],
            y=sorted_data[col_name],
            mode='lines+markers',
            name=indicator,
            line=dict(color='#0066CC', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f'{indicator} Trend - {country}',
            xaxis_title='Year',
            yaxis_title='Value',
            hovermode='x unified',
            template='plotly_white',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_country_comparison_chart(self, countries: List[str], indicator: str) -> go.Figure:
        """
        Create comparison chart for multiple countries
        
        Args:
            countries: List of country names
            indicator: Indicator name
        
        Returns:
            Plotly figure
        """
        indicator_map = {
            "TB Notifications (Total New Cases)": ("c_newinc", "notifications"),
            "New Smear-Positive Cases": ("new_sp", "notifications"),
            "New Smear-Negative Cases": ("new_sn", "notifications"),
            "New Extrapulmonary Cases": ("new_ep", "notifications"),
            "Treatment Success Rate - New Cases (%)": ("c_new_sp_tsr", "outcomes"),
            "Treatment Success Rate (%)": ("c_new_tsr", "outcomes")
        }
        
        indicator_info = indicator_map.get(indicator)
        if not indicator_info:
            return None
        
        col_name, data_type = indicator_info
        
        # Select appropriate dataframe
        if data_type == "notifications":
            df = self.analytics.tb_notifications_df
        elif data_type == "outcomes":
            df = self.analytics.tb_outcomes_df
        else:
            return None
        
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        
        comparison_data = []
        for country in countries:
            country_data = self.pipeline.filter_by_country(country, latest_data)
            if len(country_data) > 0 and col_name in country_data.columns:
                value = country_data[col_name].iloc[0]
                if pd.notna(value):
                    comparison_data.append({
                        "country": country,
                        "value": float(value)
                    })
        
        if len(comparison_data) == 0:
            return None
        
        df_comp = pd.DataFrame(comparison_data)
        df_comp = df_comp.sort_values('value', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_comp['country'],
            y=df_comp['value'],
            marker_color='#0066CC',
            text=df_comp['value'].round(1),
            textposition='outside'
        ))
        
        fig.update_layout(
            title=f'{indicator} Comparison',
            xaxis_title='Country',
            yaxis_title='Value',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_map_chart(self, indicator: str, year: Optional[int] = None) -> go.Figure:
        """
        Create choropleth map for TB indicator
        
        Args:
            indicator: Indicator name
            year: Year (optional, uses latest if not specified)
        
        Returns:
            Plotly figure
        """
        indicator_map = {
            "TB Notifications (Total New Cases)": ("c_newinc", "notifications"),
            "New Smear-Positive Cases": ("new_sp", "notifications"),
            "New Smear-Negative Cases": ("new_sn", "notifications"),
            "New Extrapulmonary Cases": ("new_ep", "notifications"),
            "Treatment Success Rate - New Cases (%)": ("c_new_sp_tsr", "outcomes"),
            "Treatment Success Rate (%)": ("c_new_tsr", "outcomes")
        }
        
        indicator_info = indicator_map.get(indicator)
        if not indicator_info:
            return None
        
        col_name, data_type = indicator_info
        
        # Select appropriate dataframe
        if data_type == "notifications":
            df = self.analytics.tb_notifications_df.copy()
        elif data_type == "outcomes":
            df = self.analytics.tb_outcomes_df.copy()
        else:
            return None
        
        if year:
            df = df[df['year'] == year]
        else:
            latest_year = df['year'].max()
            df = df[df['year'] == latest_year]
        
        if col_name not in df.columns:
            return None
        
        # Prepare data for map
        map_data = df[['country', 'iso3', col_name]].copy()
        map_data = map_data.dropna(subset=[col_name])
        
        if len(map_data) == 0:
            return None
        
        # Create choropleth map
        fig = px.choropleth(
            map_data,
            locations='iso3',
            color=col_name,
            hover_name='country',
            hover_data={col_name: True, 'iso3': False},
            color_continuous_scale='Blues',
            title=f'{indicator} - AFRO Region ({df["year"].iloc[0] if len(df) > 0 else "N/A"})',
            labels={col_name: indicator}
        )
        
        fig.update_geos(
            visible=True,
            resolution=50,
            showcountries=True,
            countrycolor="lightgray",
            showcoastlines=True,
            coastlinecolor="lightgray",
            projection_type="natural earth",
            lonaxis_range=[-20, 55],  # Africa longitude range
            lataxis_range=[-35, 38]   # Africa latitude range
        )
        
        fig.update_layout(
            height=600,
            geo=dict(
                scope='africa',
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth'
            )
        )
        
        return fig

