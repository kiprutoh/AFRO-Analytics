"""
TB Burden Chart Generator
Creates visualizations for TB burden estimates
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


class TBBurdenChartGenerator:
    """Generate charts and maps for TB Burden data"""
    
    def __init__(self, analytics):
        """
        Initialize chart generator
        
        Args:
            analytics: TBBurdenAnalytics instance
        """
        self.analytics = analytics
        
    def create_top_burden_chart(self, indicator: str = 'e_inc_num',
                                indicator_name: str = 'TB Incidence (Cases)',
                                n: int = 10, year: Optional[int] = None,
                                high_burden: bool = True) -> go.Figure:
        """
        Create horizontal bar chart for top burden countries
        
        Args:
            indicator: Burden indicator column
            indicator_name: Display name for indicator
            n: Number of countries
            year: Specific year (default: latest)
            high_burden: If True, show highest burden; if False, show lowest
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        # Get top countries
        top_countries = self.analytics.get_top_burden_countries(
            indicator=indicator,
            n=n,
            year=year,
            ascending=not high_burden
        )
        
        # Create chart
        title_prefix = "Top 10 High" if high_burden else "Top 10 Low"
        color_scale = 'Reds' if high_burden else 'Greens'
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_countries['country_clean'],
            x=top_countries[indicator],
            orientation='h',
            marker=dict(
                color=top_countries[indicator],
                colorscale=color_scale,
                showscale=True,
                colorbar=dict(title=indicator_name)
            ),
            text=top_countries[indicator].apply(lambda x: f'{x:,.0f}'),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>' +
                         f'{indicator_name}: %{{x:,.0f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'{title_prefix} Burden Countries - {indicator_name} ({year})',
            xaxis_title=indicator_name,
            yaxis_title='',
            height=500,
            template='plotly_white',
            showlegend=False,
            yaxis={'categoryorder': 'total ascending' if not high_burden else 'total descending'}
        )
        
        return fig
    
    def create_burden_comparison_chart(self, indicator: str = 'e_inc_100k',
                                      indicator_name: str = 'TB Incidence Rate (per 100,000)',
                                      year: Optional[int] = None) -> go.Figure:
        """
        Create chart comparing all AFRO countries
        
        Args:
            indicator: Burden indicator
            indicator_name: Display name
            year: Specific year
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        data = self.analytics.get_burden_indicators(year=year).sort_values(
            by=indicator, ascending=False
        )
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=data['country_clean'],
            y=data[indicator],
            marker=dict(
                color=data[indicator],
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title=indicator_name)
            ),
            hovertemplate='<b>%{x}</b><br>' +
                         f'{indicator_name}: %{{y:,.1f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'TB Burden Across AFRO Countries - {indicator_name} ({year})',
            xaxis_title='Country',
            yaxis_title=indicator_name,
            height=600,
            template='plotly_white',
            xaxis={'tickangle': -45}
        )
        
        return fig
    
    def create_burden_map(self, indicator: str = 'e_inc_100k',
                         indicator_name: str = 'TB Incidence Rate (per 100,000)',
                         year: Optional[int] = None) -> go.Figure:
        """
        Create choropleth map of TB burden
        
        Args:
            indicator: Burden indicator
            indicator_name: Display name
            year: Specific year
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        data = self.analytics.get_burden_indicators(year=year)
        
        fig = px.choropleth(
            data,
            locations='iso3',
            color=indicator,
            hover_name='country_clean',
            hover_data={
                indicator: ':,.1f',
                'iso3': False
            },
            color_continuous_scale='Reds',
            scope='africa',
            title=f'TB Burden Map - {indicator_name} ({year})'
        )
        
        fig.update_geos(
            showcoastlines=True,
            coastlinecolor="Gray",
            showland=True,
            landcolor="lightgray",
            showcountries=True,
            countrycolor="white",
            projection_type="natural earth"
        )
        
        fig.update_layout(
            height=700,
            geo=dict(
                center=dict(lon=20, lat=0),
                projection_scale=3
            )
        )
        
        return fig
    
    def create_trend_chart(self, country: str, indicator: str = 'e_inc_num',
                          indicator_name: str = 'TB Incidence (Cases)') -> go.Figure:
        """
        Create trend chart for a specific country
        
        Args:
            country: Country name
            indicator: Burden indicator
            indicator_name: Display name
            
        Returns:
            Plotly figure
        """
        trend_data = self.analytics.get_indicator_over_time(country, indicator)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data[indicator],
            mode='lines+markers',
            name=indicator_name,
            line=dict(width=3, color='#0066CC'),
            marker=dict(size=8),
            hovertemplate='<b>Year %{x}</b><br>' +
                         f'{indicator_name}: %{{y:,.0f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'{indicator_name} Trend - {country}',
            xaxis_title='Year',
            yaxis_title=indicator_name,
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_regional_trend_chart(self, indicator: str = 'e_inc_num',
                                   indicator_name: str = 'TB Incidence (Cases)') -> go.Figure:
        """
        Create regional aggregate trend chart
        
        Args:
            indicator: Burden indicator
            indicator_name: Display name
            
        Returns:
            Plotly figure
        """
        trend_data = self.analytics.get_regional_trends(indicator=indicator)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['regional_total'],
            mode='lines+markers',
            fill='tozeroy',
            name='AFRO Region',
            line=dict(width=3, color='#FF6600'),
            marker=dict(size=8),
            fillcolor='rgba(255, 102, 0, 0.2)',
            hovertemplate='<b>Year %{x}</b><br>' +
                         f'Regional Total: %{{y:,.0f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Regional Trend - {indicator_name} (AFRO)',
            xaxis_title='Year',
            yaxis_title=indicator_name,
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_multi_indicator_chart(self, country: str, year: Optional[int] = None) -> go.Figure:
        """
        Create chart showing multiple burden indicators for a country
        
        Args:
            country: Country name
            year: Specific year
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        profile = self.analytics.get_country_burden_profile(country, year)
        
        if 'error' in profile:
            return None
        
        # Prepare data
        indicators = []
        values = []
        
        if profile['incidence']['cases']:
            indicators.append('Incidence\nCases')
            values.append(profile['incidence']['cases'])
        
        if profile['tb_hiv']['cases']:
            indicators.append('TB/HIV\nCases')
            values.append(profile['tb_hiv']['cases'])
        
        if profile['mortality']['total_cases']:
            indicators.append('Mortality\nCases')
            values.append(profile['mortality']['total_cases'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=indicators,
            y=values,
            marker=dict(
                color=['#0066CC', '#CC0066', '#CC6600'],
            ),
            text=[f'{v:,.0f}' for v in values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f'TB Burden Indicators - {country} ({year})',
            xaxis_title='',
            yaxis_title='Number of Cases',
            height=400,
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    def create_equity_chart(self, indicator: str = 'e_inc_100k',
                           indicator_name: str = 'TB Incidence Rate (per 100,000)',
                           year: Optional[int] = None) -> go.Figure:
        """
        Create box plot showing distribution and inequity
        
        Args:
            indicator: Burden indicator
            indicator_name: Display name
            year: Specific year
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        data = self.analytics.get_burden_indicators(year=year)
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=data[indicator],
            name='AFRO Countries',
            marker=dict(color='#0066CC'),
            boxmean='sd',  # Show mean and standard deviation
            hovertext=data['country_clean'],
            hovertemplate='<b>%{hovertext}</b><br>' +
                         f'{indicator_name}: %{{y:,.1f}}<br>' +
                         '<extra></extra>'
        ))
        
        # Add individual points
        fig.add_trace(go.Scatter(
            y=data[indicator],
            mode='markers',
            name='Countries',
            marker=dict(
                size=8,
                color='rgba(0, 102, 204, 0.5)',
                line=dict(width=1, color='white')
            ),
            text=data['country_clean'],
            hovertemplate='<b>%{text}</b><br>' +
                         f'{indicator_name}: %{{y:,.1f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'TB Burden Distribution Across AFRO Countries - {indicator_name} ({year})',
            yaxis_title=indicator_name,
            height=600,
            template='plotly_white',
            showlegend=False
        )
        
        return fig

