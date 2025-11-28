"""
Mortality Chart Generator
Creates visualizations for Maternal and Child Mortality data
Following TB Burden chart pattern exactly
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


class MaternalMortalityChartGenerator:
    """Generate charts for Maternal Mortality data"""
    
    def __init__(self, analytics):
        """
        Initialize chart generator
        
        Args:
            analytics: MaternalMortalityAnalytics instance
        """
        self.analytics = analytics
        
    def create_top_mmr_chart(self, n: int = 10, year: Optional[int] = None,
                             high_burden: bool = True) -> go.Figure:
        """
        Create horizontal bar chart for top MMR countries
        
        Args:
            n: Number of countries
            year: Specific year (default: latest)
            high_burden: If True, show highest MMR; if False, show lowest
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        top_countries = self.analytics.get_top_mmr_countries(n=n, year=year, ascending=not high_burden)
        
        title_prefix = "Top 10 High" if high_burden else "Top 10 Low"
        color_scale = 'Reds' if high_burden else 'Greens'
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_countries['country_clean'],
            x=top_countries['mmr'],
            orientation='h',
            marker=dict(
                color=top_countries['mmr'],
                colorscale=color_scale,
                showscale=True,
                colorbar=dict(title='MMR (per 100,000)')
            ),
            text=top_countries['mmr'].apply(lambda x: f'{x:.0f}'),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>' +
                         'MMR: %{x:.0f} per 100,000<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'{title_prefix} MMR Countries - Maternal Mortality Ratio ({year})',
            xaxis_title='Maternal Mortality Ratio (per 100,000 live births)',
            yaxis_title='',
            height=500,
            template='plotly_white',
            showlegend=False,
            yaxis={'categoryorder': 'total ascending' if not high_burden else 'total descending'}
        )
        
        return fig
    
    def create_regional_trend_chart(self) -> go.Figure:
        """Create regional aggregate trend chart"""
        regional_trends = self.analytics.get_regional_trends()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=regional_trends['year'],
            y=regional_trends['median_mmr'],
            mode='lines+markers',
            name='Median MMR',
            line=dict(width=3, color='#f5576c'),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(245, 87, 108, 0.2)',
            hovertemplate='<b>Year %{x}</b><br>' +
                         'Median MMR: %{y:.0f} per 100,000<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title='Regional Trend - Maternal Mortality Ratio (AFRO)',
            xaxis_title='Year',
            yaxis_title='Maternal Mortality Ratio (per 100,000 live births)',
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_country_trend_chart(self, country: str) -> go.Figure:
        """Create trend chart for a specific country"""
        trend_data = self.analytics.get_mmr_over_time(country)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['mmr'],
            mode='lines+markers',
            name='MMR',
            line=dict(width=3, color='#f5576c'),
            marker=dict(size=8),
            hovertemplate='<b>Year %{x}</b><br>' +
                         'MMR: %{y:.0f} per 100,000<br>' +
                         '<extra></extra>'
        ))
        
        # Add SDG target line (70 per 100,000)
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="green",
            annotation_text="SDG Target: 70 per 100,000",
            annotation_position="right"
        )
        
        fig.update_layout(
            title=f'Maternal Mortality Ratio Trend - {country}',
            xaxis_title='Year',
            yaxis_title='Maternal Mortality Ratio (per 100,000 live births)',
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_map(self, year: Optional[int] = None) -> go.Figure:
        """Create choropleth map of MMR"""
        if year is None:
            year = self.analytics.get_latest_year()
        
        data_year = self.analytics.maternal_afro[
            self.analytics.maternal_afro['year'] == year
        ][['country_clean', 'iso3', 'mmr']].copy()
        
        fig = px.choropleth(
            data_year,
            locations='iso3',
            color='mmr',
            hover_name='country_clean',
            hover_data={'mmr': ':,.0f', 'iso3': False},
            color_continuous_scale='Reds',
            scope='africa',
            title=f'Maternal Mortality Ratio Map ({year})'
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
    
    def create_equity_chart(self, year: Optional[int] = None) -> go.Figure:
        """Create box plot showing MMR distribution"""
        if year is None:
            year = self.analytics.get_latest_year()
        
        data_year = self.analytics.maternal_afro[
            (self.analytics.maternal_afro['year'] == year) &
            (self.analytics.maternal_afro['mmr'].notna())
        ].copy()
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=data_year['mmr'],
            name='AFRO Countries',
            marker=dict(color='#f5576c'),
            boxmean='sd',
            hovertext=data_year['country_clean'],
            hovertemplate='<b>%{hovertext}</b><br>' +
                         'MMR: %{y:.0f} per 100,000<br>' +
                         '<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            y=data_year['mmr'],
            mode='markers',
            name='Countries',
            marker=dict(
                size=8,
                color='rgba(245, 87, 108, 0.5)',
                line=dict(width=1, color='white')
            ),
            text=data_year['country_clean'],
            hovertemplate='<b>%{text}</b><br>' +
                         'MMR: %{y:.0f} per 100,000<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'MMR Distribution Across AFRO Countries ({year})',
            yaxis_title='Maternal Mortality Ratio (per 100,000 live births)',
            height=600,
            template='plotly_white',
            showlegend=False
        )
        
        return fig


class ChildMortalityChartGenerator:
    """Generate charts for Child Mortality data"""
    
    def __init__(self, analytics):
        """
        Initialize chart generator
        
        Args:
            analytics: ChildMortalityAnalytics instance
        """
        self.analytics = analytics
        
    def create_top_mortality_chart(self, indicator: str = 'Under-five mortality rate',
                                   indicator_name: str = 'Under-five Mortality Rate',
                                   n: int = 10, year: Optional[int] = None,
                                   high_burden: bool = True) -> go.Figure:
        """
        Create horizontal bar chart for top mortality countries
        
        Args:
            indicator: Mortality indicator
            indicator_name: Display name
            n: Number of countries
            year: Specific year (default: latest)
            high_burden: If True, show highest; if False, show lowest
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year(indicator)
        
        top_countries = self.analytics.get_top_mortality_countries(
            indicator=indicator, n=n, year=year, ascending=not high_burden
        )
        
        title_prefix = "Top 10 High" if high_burden else "Top 10 Low"
        color_scale = 'Reds' if high_burden else 'Greens'
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_countries['country_clean'],
            x=top_countries['value'],
            orientation='h',
            marker=dict(
                color=top_countries['value'],
                colorscale=color_scale,
                showscale=True,
                colorbar=dict(title=indicator_name)
            ),
            text=top_countries['value'].apply(lambda x: f'{x:.1f}'),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>' +
                         f'{indicator_name}: %{{x:.1f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'{title_prefix} Mortality Countries - {indicator_name} ({year})',
            xaxis_title=indicator_name,
            yaxis_title='',
            height=500,
            template='plotly_white',
            showlegend=False,
            yaxis={'categoryorder': 'total ascending' if not high_burden else 'total descending'}
        )
        
        return fig
    
    def create_regional_trend_chart(self, indicator: str = 'Under-five mortality rate',
                                    indicator_name: str = 'Under-five Mortality Rate') -> go.Figure:
        """Create regional aggregate trend chart"""
        regional_trends = self.analytics.get_regional_trends(indicator)
        
        fig = go.Figure()
        
        # Check if confidence intervals available
        has_ci = 'lower_bound' in self.analytics.child_afro.columns and 'upper_bound' in self.analytics.child_afro.columns
        
        if has_ci:
            # Get CI data for regional trend
            ci_data = self.analytics.child_afro[
                (self.analytics.child_afro['indicator'] == indicator) &
                (self.analytics.child_afro['sex'] == 'Total')
            ].groupby('year').agg({
                'value': 'mean',
                'upper_bound': 'mean',
                'lower_bound': 'mean'
            }).reset_index()
            
            # Add upper bound (invisible)
            fig.add_trace(go.Scatter(
                x=ci_data['year'],
                y=ci_data['upper_bound'],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Add lower bound with fill
            fig.add_trace(go.Scatter(
                x=ci_data['year'],
                y=ci_data['lower_bound'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(79, 172, 254, 0.2)',
                name='95% CI',
                showlegend=True,
                hoverinfo='skip'
            ))
        
        fig.add_trace(go.Scatter(
            x=regional_trends['year'],
            y=regional_trends['median_value'],
            mode='lines+markers',
            name='Median',
            line=dict(width=3, color='#4facfe'),
            marker=dict(size=8),
            fill='tozeroy' if not has_ci else None,
            fillcolor='rgba(79, 172, 254, 0.2)' if not has_ci else None,
            hovertemplate='<b>Year %{x}</b><br>' +
                         f'Median {indicator_name}: %{{y:.1f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Regional Trend - {indicator_name} (AFRO)' + (' [with 95% CI]' if has_ci else ''),
            xaxis_title='Year',
            yaxis_title=indicator_name,
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_country_trend_chart(self, country: str, indicator: str = 'Under-five mortality rate',
                                   indicator_name: str = 'Under-five Mortality Rate') -> go.Figure:
        """Create trend chart for a specific country"""
        trend_data = self.analytics.get_mortality_over_time(country, indicator)
        
        fig = go.Figure()
        
        has_ci = 'lower_bound' in trend_data.columns and 'upper_bound' in trend_data.columns
        
        if has_ci:
            # Add CI band
            fig.add_trace(go.Scatter(
                x=trend_data['year'],
                y=trend_data['upper_bound'],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig.add_trace(go.Scatter(
                x=trend_data['year'],
                y=trend_data['lower_bound'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(79, 172, 254, 0.2)',
                name='95% CI',
                showlegend=True,
                hoverinfo='skip'
            ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['value'],
            mode='lines+markers',
            name=indicator_name,
            line=dict(width=3, color='#4facfe'),
            marker=dict(size=8),
            hovertemplate='<b>Year %{x}</b><br>' +
                         f'{indicator_name}: %{{y:.1f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'{indicator_name} Trend - {country}' + (' [with 95% CI]' if has_ci else ''),
            xaxis_title='Year',
            yaxis_title=indicator_name,
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def create_sex_comparison_chart(self, indicator: str = 'Under-five mortality rate',
                                   indicator_name: str = 'Under-five Mortality Rate',
                                   year: Optional[int] = None) -> go.Figure:
        """
        Create sex comparison chart (Female vs Male)
        
        Args:
            indicator: Mortality indicator
            indicator_name: Display name
            year: Specific year
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year(indicator)
        
        sex_data = self.analytics.get_sex_disaggregation(indicator, year)
        
        if len(sex_data) == 0:
            return None
        
        # Get top 10 countries by Total for comparison
        top_countries = sex_data.nlargest(10, 'Total')['country_clean'].tolist()
        sex_filtered = sex_data[sex_data['country_clean'].isin(top_countries)].copy()
        
        fig = go.Figure()
        
        if 'Female' in sex_filtered.columns and 'Male' in sex_filtered.columns:
            fig.add_trace(go.Bar(
                name='Female',
                x=sex_filtered['country_clean'],
                y=sex_filtered['Female'],
                marker_color='#ff69b4',
                hovertemplate='<b>%{x}</b><br>Female: %{y:.1f}<br><extra></extra>'
            ))
            
            fig.add_trace(go.Bar(
                name='Male',
                x=sex_filtered['country_clean'],
                y=sex_filtered['Male'],
                marker_color='#1e90ff',
                hovertemplate='<b>%{x}</b><br>Male: %{y:.1f}<br><extra></extra>'
            ))
        
        fig.update_layout(
            title=f'Sex Disaggregation - {indicator_name} ({year})',
            xaxis_title='Country',
            yaxis_title=indicator_name,
            barmode='group',
            height=500,
            template='plotly_white',
            xaxis={'tickangle': -45}
        )
        
        return fig
    
    def create_map(self, indicator: str = 'Under-five mortality rate',
                   indicator_name: str = 'Under-five Mortality Rate',
                   year: Optional[int] = None) -> go.Figure:
        """Create choropleth map of mortality"""
        if year is None:
            year = self.analytics.get_latest_year(indicator)
        
        data_year = self.analytics.child_afro[
            (self.analytics.child_afro['indicator'] == indicator) &
            (self.analytics.child_afro['year'] == year) &
            (self.analytics.child_afro['sex'] == 'Total')
        ][['country_clean', 'iso3', 'value']].copy()
        
        fig = px.choropleth(
            data_year,
            locations='iso3',
            color='value',
            hover_name='country_clean',
            hover_data={'value': ':,.1f', 'iso3': False},
            color_continuous_scale='Blues',
            scope='africa',
            title=f'{indicator_name} Map ({year})'
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
    
    def create_equity_chart(self, indicator: str = 'Under-five mortality rate',
                           indicator_name: str = 'Under-five Mortality Rate',
                           year: Optional[int] = None) -> go.Figure:
        """Create box plot showing mortality distribution"""
        if year is None:
            year = self.analytics.get_latest_year(indicator)
        
        data_year = self.analytics.child_afro[
            (self.analytics.child_afro['indicator'] == indicator) &
            (self.analytics.child_afro['year'] == year) &
            (self.analytics.child_afro['sex'] == 'Total') &
            (self.analytics.child_afro['value'].notna())
        ].copy()
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=data_year['value'],
            name='AFRO Countries',
            marker=dict(color='#4facfe'),
            boxmean='sd',
            hovertext=data_year['country_clean'],
            hovertemplate='<b>%{hovertext}</b><br>' +
                         f'{indicator_name}: %{{y:.1f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            y=data_year['value'],
            mode='markers',
            name='Countries',
            marker=dict(
                size=8,
                color='rgba(79, 172, 254, 0.5)',
                line=dict(width=1, color='white')
            ),
            text=data_year['country_clean'],
            hovertemplate='<b>%{text}</b><br>' +
                         f'{indicator_name}: %{{y:.1f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'{indicator_name} Distribution Across AFRO Countries ({year})',
            yaxis_title=indicator_name,
            height=600,
            template='plotly_white',
            showlegend=False
        )
        
        return fig
