"""
TB Notifications and Outcomes Chart Generator
Creates visualizations for TB notifications, types, age distributions, and outcomes
Following TB Burden framework
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


class TBNotifOutcomesChartGenerator:
    """Generate charts for TB Notifications and Outcomes data"""
    
    def __init__(self, analytics):
        """
        Initialize chart generator
        
        Args:
            analytics: TBNotificationsOutcomesAnalytics instance
        """
        self.analytics = analytics
    
    def create_top_notifying_chart(self, indicator: str = 'c_newinc',
                                   indicator_name: str = 'Total Notifications',
                                   n: int = 10, year: Optional[int] = None,
                                   high: bool = True) -> go.Figure:
        """
        Create bar chart for top notifying countries (no CI)
        
        Args:
            indicator: Notification indicator
            indicator_name: Display name
            n: Number of countries
            year: Specific year (default: latest)
            high: If True, show highest; if False, show lowest
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        # Get top countries
        top_countries = self.analytics.get_top_notifying_countries(
            indicator=indicator,
            n=n,
            year=year,
            ascending=not high
        )
        
        if top_countries.empty:
            return None
        
        # Create chart
        title_prefix = f"Top {n} Highest" if high else f"Top {n} Lowest"
        color_scale = 'Reds' if high else 'Greens'
        
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
            title=f'{title_prefix} Notifying Countries - {indicator_name} ({year})',
            xaxis_title=indicator_name,
            yaxis_title='',
            height=500,
            template='plotly_white',
            showlegend=False,
            yaxis={'categoryorder': 'total ascending' if not high else 'total descending'}
        )
        
        fig.add_annotation(
            text="Point estimates shown.",
            xref="paper", yref="paper",
            x=0.5, y=-0.12,
            showarrow=False,
            font=dict(size=10, color="gray"),
            xanchor='center'
        )
        
        return fig
    
    def create_age_distribution_chart(self, year: Optional[int] = None) -> go.Figure:
        """
        Create age group distribution chart
        
        Args:
            year: Specific year (default: latest)
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        age_dist = self.analytics.get_age_distribution(year=year)
        
        if age_dist.empty:
            return None
        
        fig = go.Figure()
        
        # Male bars (negative for pyramid effect)
        fig.add_trace(go.Bar(
            y=age_dist['age_group'],
            x=-age_dist['male'],
            name='Male',
            orientation='h',
            marker=dict(color='#3498db'),
            text=age_dist['male'].apply(lambda x: f'{x:,.0f}'),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Male: %{text}<br><extra></extra>'
        ))
        
        # Female bars (positive)
        fig.add_trace(go.Bar(
            y=age_dist['age_group'],
            x=age_dist['female'],
            name='Female',
            orientation='h',
            marker=dict(color='#e74c3c'),
            text=age_dist['female'].apply(lambda x: f'{x:,.0f}'),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Female: %{text}<br><extra></extra>'
        ))
        
        fig.update_layout(
            title=f'TB Cases by Age Group and Sex - AFRO Region ({year})',
            xaxis_title='Number of Cases',
            yaxis_title='Age Group',
            barmode='overlay',
            bargap=0.1,
            height=500,
            template='plotly_white',
            xaxis=dict(
                tickvals=[-200000, -100000, 0, 100000, 200000],
                ticktext=['200k', '100k', '0', '100k', '200k']
            )
        )
        
        return fig
    
    def create_notification_types_chart(self, country: str, year: Optional[int] = None) -> go.Figure:
        """
        Create pie chart for notification types
        
        Args:
            country: Country name
            year: Specific year (default: latest)
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        types_data = self.analytics.get_notification_types_breakdown(country, year)
        
        if 'error' in types_data:
            return None
        
        # Prepare data for pie chart
        labels = []
        values = []
        
        if types_data['pulmonary_lab_confirmed'] > 0:
            labels.append('Pulmonary Lab Confirmed')
            values.append(types_data['pulmonary_lab_confirmed'])
        
        if types_data['pulmonary_clin_diagnosed'] > 0:
            labels.append('Pulmonary Clinically Diagnosed')
            values.append(types_data['pulmonary_clin_diagnosed'])
        
        if types_data['extrapulmonary'] > 0:
            labels.append('Extrapulmonary')
            values.append(types_data['extrapulmonary'])
        
        if not values:
            return None
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=['#3498db', '#2ecc71', '#f39c12'])
        )])
        
        fig.update_layout(
            title=f'TB Case Types - {country} ({year})',
            height=400,
            template='plotly_white'
        )
        
        return fig
    
    def create_regional_trend_chart(self, indicator: str = 'c_newinc',
                                   indicator_name: str = 'Total Notifications') -> go.Figure:
        """
        Create regional trend chart (line chart only - no CI in notifications data)
        
        Args:
            indicator: Notification indicator
            indicator_name: Display name
            
        Returns:
            Plotly figure
        """
        trend_data = self.analytics.get_regional_trend(indicator=indicator)
        
        if trend_data.empty:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['regional_total'],
            mode='lines+markers',
            name='AFRO Region',
            line=dict(width=3, color='#e74c3c'),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)',
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
    
    def create_equity_chart(self, indicator: str = 'c_newinc',
                           indicator_name: str = 'Total Notifications',
                           year: Optional[int] = None) -> go.Figure:
        """
        Create box plot for equity analysis
        
        Args:
            indicator: Notification indicator
            indicator_name: Display name
            year: Specific year (default: latest)
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        data_year = self.analytics.notif_afro[self.analytics.notif_afro['year'] == year].copy()
        
        if indicator not in data_year.columns:
            return None
        
        # Filter positive values
        data_filtered = data_year[data_year[indicator] > 0]
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=data_filtered[indicator],
            name=indicator_name,
            marker_color='#e74c3c',
            boxmean='sd'
        ))
        
        fig.update_layout(
            title=f'Distribution of {indicator_name} Across AFRO Countries ({year})',
            yaxis_title=indicator_name,
            height=500,
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    def create_comparison_chart(self, indicator: str = 'c_newinc',
                                indicator_name: str = 'Total Notifications',
                                year: Optional[int] = None) -> go.Figure:
        """
        Create bar chart comparing all countries
        
        Args:
            indicator: Notification indicator
            indicator_name: Display name
            year: Specific year (default: latest)
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = self.analytics.get_latest_year()
        
        data_year = self.analytics.notif_afro[self.analytics.notif_afro['year'] == year].copy()
        
        if indicator not in data_year.columns:
            return None
        
        data_sorted = data_year.sort_values(by=indicator, ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=data_sorted['country_clean'],
            y=data_sorted[indicator],
            marker=dict(
                color=data_sorted[indicator],
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title=indicator_name)
            ),
            hovertemplate='<b>%{x}</b><br>' +
                         f'{indicator_name}: %{{y:,.0f}}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'{indicator_name} Across AFRO Countries ({year})',
            xaxis_title='Country',
            yaxis_title=indicator_name,
            height=600,
            template='plotly_white',
            xaxis={'tickangle': -45}
        )
        
        return fig
    
    # ==================== TREATMENT OUTCOMES CHARTS ====================
    
    def create_outcomes_bar_chart(self, indicator: str = 'c_new_tsr',
                                  indicator_name: str = 'Treatment Success Rate',
                                  n: int = 10, year: Optional[int] = None,
                                  high: bool = True) -> go.Figure:
        """
        Create bar chart for top performing countries (treatment success rates)
        
        Args:
            indicator: TSR indicator
            indicator_name: Display name
            n: Number of countries
            year: Specific year (default: latest)
            high: If True, show highest; if False, show lowest
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = int(self.analytics.outcomes_afro['year'].max())
        
        # Get top countries
        top_countries = self.analytics.get_top_performing_countries(
            indicator=indicator,
            n=n,
            year=year,
            ascending=not high
        )
        
        if top_countries.empty:
            return None
        
        # Create chart
        title_prefix = f"Top {n} Highest" if high else f"Top {n} Lowest"
        color_scale = 'Greens' if high else 'Reds'
        
        # Color based on WHO target (85%)
        colors = []
        for val in top_countries[indicator]:
            if val >= 85:
                colors.append('#27ae60')  # Green - above target
            elif val >= 75:
                colors.append('#f39c12')  # Orange - close to target
            else:
                colors.append('#e74c3c')  # Red - below target
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_countries['country_clean'],
            x=top_countries[indicator],
            orientation='h',
            marker=dict(color=colors),
            text=top_countries[indicator].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>' +
                         f'{indicator_name}: %{{x:.1f}}%<br>' +
                         '<extra></extra>'
        ))
        
        # Add WHO target line
        fig.add_vline(x=85, line_dash="dash", line_color="gray",
                     annotation_text="WHO Target: 85%",
                     annotation_position="top")
        
        fig.update_layout(
            title=f'{title_prefix} Performing Countries - {indicator_name} ({year})',
            xaxis_title=f'{indicator_name} (%)',
            yaxis_title='',
            height=500,
            template='plotly_white',
            showlegend=False,
            yaxis={'categoryorder': 'total ascending' if not high else 'total descending'}
        )
        
        return fig
    
    def create_outcomes_breakdown_chart(self, country: str, year: Optional[int] = None,
                                       category: str = 'newrel') -> go.Figure:
        """
        Create pie chart for treatment outcomes breakdown
        
        Args:
            country: Country name
            year: Specific year (default: latest)
            category: Outcome category
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = int(self.analytics.outcomes_afro['year'].max())
        
        outcomes = self.analytics.get_outcomes_breakdown(country, year, category)
        
        if 'error' in outcomes:
            return None
        
        # Prepare data
        labels = ['Treatment Success', 'Failed', 'Died', 'Lost to Follow-up']
        values = [outcomes['success'], outcomes['failed'], outcomes['died'], outcomes['lost']]
        colors = ['#27ae60', '#e74c3c', '#34495e', '#f39c12']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Cases: %{value:,.0f}<br>Percent: %{percent}<extra></extra>'
        )])
        
        category_names = {
            'newrel': 'New and Relapse TB',
            'ret_nrel': 'Retreatment TB',
            'tbhiv': 'TB/HIV'
        }
        
        fig.update_layout(
            title=f'Treatment Outcomes - {country} ({year})<br>{category_names.get(category, category)}',
            height=450,
            template='plotly_white',
            annotations=[dict(text=f'Cohort:<br>{outcomes["cohort"]:,.0f}', x=0.5, y=0.5, font_size=14, showarrow=False)]
        )
        
        return fig
    
    def create_tsr_trend_chart(self, indicator: str = 'c_new_tsr',
                               indicator_name: str = 'Treatment Success Rate') -> go.Figure:
        """
        Create regional TSR trend chart
        
        Args:
            indicator: TSR indicator
            indicator_name: Display name
            
        Returns:
            Plotly figure
        """
        trend_data = self.analytics.get_outcomes_regional_trend(indicator=indicator)
        
        if trend_data.empty:
            return None
        
        fig = go.Figure()
        
        # Add shaded area for uncertainty
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['mean_tsr'] + trend_data['std_tsr'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['mean_tsr'] - trend_data['std_tsr'],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(46, 204, 113, 0.2)',
            name='±1 Std Dev',
            hoverinfo='skip'
        ))
        
        # Add mean line
        fig.add_trace(go.Scatter(
            x=trend_data['year'],
            y=trend_data['mean_tsr'],
            mode='lines+markers',
            name='Regional Mean',
            line=dict(width=3, color='#27ae60'),
            marker=dict(size=8),
            hovertemplate='<b>Year %{x}</b><br>Mean TSR: %{y:.1f}%<br><extra></extra>'
        ))
        
        # Add WHO target line
        fig.add_hline(y=85, line_dash="dash", line_color="gray",
                     annotation_text="WHO Target: 85%",
                     annotation_position="right")
        
        fig.update_layout(
            title=f'Regional Trend - {indicator_name} (AFRO)',
            xaxis_title='Year',
            yaxis_title=f'{indicator_name} (%)',
            height=500,
            template='plotly_white',
            hovermode='x unified',
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    def create_outcomes_equity_chart(self, indicator: str = 'c_new_tsr',
                                    indicator_name: str = 'Treatment Success Rate',
                                    year: Optional[int] = None) -> go.Figure:
        """
        Create box plot for TSR equity analysis
        
        Args:
            indicator: TSR indicator
            indicator_name: Display name
            year: Specific year (default: latest)
            
        Returns:
            Plotly figure
        """
        if year is None:
            year = int(self.analytics.outcomes_afro['year'].max())
        
        data_year = self.analytics.outcomes_afro[self.analytics.outcomes_afro['year'] == year].copy()
        
        if indicator not in data_year.columns:
            return None
        
        # Filter valid values
        data_filtered = data_year[data_year[indicator] > 0]
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=data_filtered[indicator],
            name=indicator_name,
            marker_color='#27ae60',
            boxmean='sd',
            hovertemplate='TSR: %{y:.1f}%<extra></extra>'
        ))
        
        # Add WHO target line
        fig.add_hline(y=85, line_dash="dash", line_color="gray",
                     annotation_text="WHO Target: 85%",
                     annotation_position="right")
        
        fig.update_layout(
            title=f'Distribution of {indicator_name} Across AFRO Countries ({year})',
            yaxis_title=f'{indicator_name} (%)',
            height=500,
            template='plotly_white',
            showlegend=False,
            yaxis=dict(range=[0, 100])
        )
        
        return fig

