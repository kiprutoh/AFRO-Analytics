"""
Chart Generator Module
Creates visualizations for mortality analytics
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Tuple
from analytics import MortalityAnalytics


class ChartGenerator:
    """Generate charts and visualizations for mortality data"""
    
    def __init__(self, analytics: MortalityAnalytics):
        """
        Initialize chart generator
        
        Args:
            analytics: MortalityAnalytics instance
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
        country_data = self.pipeline.filter_by_country(country, self.analytics.mortality_df)
        ind_data = country_data[country_data['indicator'] == indicator]
        
        if len(ind_data) == 0:
            return None
        
        sorted_data = ind_data.sort_values('year')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sorted_data['year'],
            y=sorted_data['value'],
            mode='lines+markers',
            name=indicator,
            line=dict(color='#0066CC', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f'{indicator} Trend - {country}',
            xaxis_title='Year',
            yaxis_title='Rate',
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
        comparison_data = []
        
        for country in countries:
            country_data = self.pipeline.filter_by_country(country, self.analytics.mortality_df)
            ind_data = country_data[country_data['indicator'] == indicator]
            
            if len(ind_data) > 0:
                latest = ind_data.sort_values('year').iloc[-1]
                comparison_data.append({
                    'country': country,
                    'value': latest['value'],
                    'year': latest['year']
                })
        
        if len(comparison_data) == 0:
            return None
        
        df = pd.DataFrame(comparison_data)
        df = df.sort_values('value', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['country'],
            y=df['value'],
            marker_color='#0066CC',
            text=df['value'].round(2),
            textposition='outside',
            name=indicator
        ))
        
        fig.update_layout(
            title=f'{indicator} Comparison',
            xaxis_title='Country',
            yaxis_title='Rate',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_projection_chart(self, country: Optional[str] = None, indicator: str = "MMR") -> go.Figure:
        """
        Create projection chart showing current, projected 2030, and targets
        
        Args:
            country: Optional country filter
            indicator: Indicator name (default: MMR)
        
        Returns:
            Plotly figure
        """
        if indicator == "MMR":
            proj_df = self.analytics.mmr_proj.copy()
        else:
            proj_df = self.analytics.mortality_proj.copy()
            proj_df = proj_df[proj_df['indicator'] == indicator]
        
        if country:
            proj_df = proj_df[proj_df['country'].str.contains(country, case=False, na=False)]
        
        if len(proj_df) == 0:
            return None
        
        # Prepare data for visualization
        chart_data = []
        
        for _, row in proj_df.iterrows():
            # SDG Target for MMR: <70 per 100,000
            # For other indicators, calculate based on SDG targets
            if indicator == "MMR":
                target_2030 = 70
            elif "Under-five" in indicator:
                target_2030 = 25  # SDG target: <25 per 1,000
            elif "Neonatal" in indicator:
                target_2030 = 12  # SDG target: <12 per 1,000
            elif "Infant" in indicator:
                target_2030 = 12  # Approximate target
            else:
                target_2030 = None
            
            chart_data.append({
                'country': row['country'],
                'current': row['xT'],
                'projected_2030': row['proj_2030'],
                'target_2030': target_2030,
                'on_track': row['on_track']
            })
        
        df = pd.DataFrame(chart_data)
        df = df.head(20)  # Limit to top 20 for readability
        
        fig = go.Figure()
        
        # Current values
        fig.add_trace(go.Bar(
            name='Current (2023)',
            x=df['country'],
            y=df['current'],
            marker_color='#0066CC',
            text=df['current'].round(1),
            textposition='outside'
        ))
        
        # Projected 2030 values
        fig.add_trace(go.Bar(
            name='Projected 2030',
            x=df['country'],
            y=df['projected_2030'],
            marker_color='#FFA500',
            text=df['projected_2030'].round(1),
            textposition='outside'
        ))
        
        # Target line if available
        if df['target_2030'].notna().any():
            target_value = df['target_2030'].iloc[0]
            fig.add_hline(
                y=target_value,
                line_dash="dash",
                line_color="red",
                annotation_text=f"SDG Target 2030: {target_value}",
                annotation_position="right"
            )
        
        fig.update_layout(
            title=f'{indicator} - Current vs Projected 2030 vs Target',
            xaxis_title='Country',
            yaxis_title='Rate',
            barmode='group',
            template='plotly_white',
            height=500,
            showlegend=True,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_projection_timeline(self, country: str, indicator: str = "MMR") -> go.Figure:
        """
        Create timeline chart showing historical, current, and projected values
        
        Args:
            country: Country name
            indicator: Indicator name
        
        Returns:
            Plotly figure
        """
        # Get historical data
        country_data = self.pipeline.filter_by_country(country, self.analytics.mortality_df)
        ind_data = country_data[country_data['indicator'] == indicator]
        
        # Get projection data
        if indicator == "MMR":
            proj_data = self.analytics.mmr_proj[
                self.analytics.mmr_proj['country'].str.contains(country, case=False, na=False)
            ]
        else:
            proj_data = self.analytics.mortality_proj[
                (self.analytics.mortality_proj['country'].str.contains(country, case=False, na=False)) &
                (self.analytics.mortality_proj['indicator'] == indicator)
            ]
        
        fig = go.Figure()
        
        # Historical data
        if len(ind_data) > 0:
            sorted_hist = ind_data.sort_values('year')
            fig.add_trace(go.Scatter(
                x=sorted_hist['year'],
                y=sorted_hist['value'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='#0066CC', width=2),
                marker=dict(size=6)
            ))
        
        # Projection line
        if len(proj_data) > 0:
            row = proj_data.iloc[0]
            current_year = row['current_year']
            current_value = row['xT']
            projected_2030 = row['proj_2030']
            
            # Add current point
            fig.add_trace(go.Scatter(
                x=[current_year],
                y=[current_value],
                mode='markers',
                name='Current (2023)',
                marker=dict(size=12, color='green', symbol='circle')
            ))
            
            # Add projection line
            fig.add_trace(go.Scatter(
                x=[current_year, 2030],
                y=[current_value, projected_2030],
                mode='lines+markers',
                name='Projection to 2030',
                line=dict(color='orange', width=2, dash='dash'),
                marker=dict(size=8, color='orange')
            ))
            
            # Add target line
            if indicator == "MMR":
                target = 70
            elif "Under-five" in indicator:
                target = 25
            elif "Neonatal" in indicator:
                target = 12
            else:
                target = None
            
            if target:
                fig.add_hline(
                    y=target,
                    line_dash="dot",
                    line_color="red",
                    annotation_text=f"SDG Target: {target}",
                    annotation_position="right"
                )
        
        fig.update_layout(
            title=f'{indicator} - Historical Trend & 2030 Projection: {country}',
            xaxis_title='Year',
            yaxis_title='Rate',
            hovermode='x unified',
            template='plotly_white',
            height=450,
            showlegend=True
        )
        
        return fig
    
    def create_on_track_chart(self) -> go.Figure:
        """
        Create chart showing countries on track vs off track for 2030 targets
        
        Returns:
            Plotly figure
        """
        mmr_proj = self.analytics.mmr_proj.copy()
        
        on_track = mmr_proj[mmr_proj['on_track'] == True]
        off_track = mmr_proj[mmr_proj['on_track'] == False]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='On Track',
            x=['MMR'],
            y=[len(on_track)],
            marker_color='green',
            text=[len(on_track)],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Off Track',
            x=['MMR'],
            y=[len(off_track)],
            marker_color='red',
            text=[len(off_track)],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Countries On Track vs Off Track for 2030 MMR Target',
            xaxis_title='Indicator',
            yaxis_title='Number of Countries',
            barmode='stack',
            template='plotly_white',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_top_countries_chart(self, indicator: str, top_n: int = 10, ascending: bool = False) -> go.Figure:
        """
        Create bar chart for top countries by indicator
        
        Args:
            indicator: Indicator name
            top_n: Number of countries
            ascending: Sort order
        
        Returns:
            Plotly figure
        """
        top_df = self.analytics.get_top_countries_by_indicator(indicator, top_n, ascending)
        
        if len(top_df) == 0:
            return None
        
        fig = go.Figure()
        
        color = '#00CC66' if ascending else '#CC0000'
        
        fig.add_trace(go.Bar(
            x=top_df['country'],
            y=top_df['value'],
            marker_color=color,
            text=top_df['value'].round(2),
            textposition='outside',
            name=indicator
        ))
        
        title = f"Top {top_n} Countries - {indicator}"
        if ascending:
            title = f"Top {top_n} Countries (Lowest) - {indicator}"
        
        fig.update_layout(
            title=title,
            xaxis_title='Country',
            yaxis_title='Rate',
            template='plotly_white',
            height=400,
            showlegend=False,
            xaxis_tickangle=-45
        )
        
        return fig

