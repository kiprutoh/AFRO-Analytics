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


    def create_enhanced_map(self, indicator: str, year: int = 2023) -> go.Figure:
        """
        Create enhanced choropleth map for indicator across African countries with country names
        
        Args:
            indicator: Indicator name
            year: Year to display
        
        Returns:
            Plotly figure
        """
        # Country ISO code mapping for maps
        country_iso_map = {
            'Angola': 'AGO', 'Algeria': 'DZA', 'Benin': 'BEN', 'Botswana': 'BWA',
            'Burkina Faso': 'BFA', 'Burundi': 'BDI', 'Cabo Verde': 'CPV',
            'Cameroon': 'CMR', 'Central African Republic': 'CAF', 'Chad': 'TCD',
            'Comoros': 'COM', 'Congo': 'COG', "Côte d'Ivoire": 'CIV',
            'Democratic Republic of the Congo': 'COD', 'Equatorial Guinea': 'GNQ',
            'Eritrea': 'ERI', 'Ethiopia': 'ETH', 'Gabon': 'GAB', 'Gambia': 'GMB',
            'Ghana': 'GHA', 'Guinea': 'GIN', 'Guinea-Bissau': 'GNB', 'Kenya': 'KEN',
            'Lesotho': 'LSO', 'Liberia': 'LBR', 'Madagascar': 'MDG', 'Malawi': 'MWI',
            'Mali': 'MLI', 'Mauritania': 'MRT', 'Mauritius': 'MUS', 'Mozambique': 'MOZ',
            'Namibia': 'NAM', 'Niger': 'NER', 'Nigeria': 'NGA', 'Rwanda': 'RWA',
            'Sao Tome and Principe': 'STP', 'Senegal': 'SEN', 'Seychelles': 'SYC',
            'Sierra Leone': 'SLE', 'South Africa': 'ZAF', 'South Sudan': 'SSD',
            'Eswatini': 'SWZ', 'United Republic of Tanzania': 'TZA', 'Togo': 'TGO',
            'Uganda': 'UGA', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE'
        }
        
        # Get data for all countries
        all_data = []
        
        # Handle MMR separately
        if indicator == "MMR" or "Maternal" in indicator:
            for _, row in self.analytics.mmr_df.iterrows():
                if row['year'] <= year:
                    country = row['country']
                    iso_code = country_iso_map.get(country, '')
                    if iso_code:
                        # Get latest value for this country up to the specified year
                        country_data = self.analytics.mmr_df[
                            (self.analytics.mmr_df['country'] == country) & 
                            (self.analytics.mmr_df['year'] <= year)
                        ]
                        if len(country_data) > 0:
                            latest = country_data.sort_values('year').iloc[-1]
                            all_data.append({
                                'country': country,
                                'iso': iso_code,
                                'value': latest['value'],
                                'year': latest['year']
                            })
        else:
            # Handle other indicators
            for country in self.pipeline.get_countries():
                country_data = self.pipeline.filter_by_country(country, self.analytics.mortality_df)
                ind_data = country_data[country_data['indicator'] == indicator]
                
                if len(ind_data) > 0:
                    year_data = ind_data[ind_data['year'] <= year]
                    if len(year_data) > 0:
                        latest = year_data.sort_values('year').iloc[-1]
                        iso_code = country_iso_map.get(country, '')
                        if iso_code:
                            all_data.append({
                                'country': country,
                                'iso': iso_code,
                                'value': latest['value'],
                                'year': latest['year']
                            })
        
        if len(all_data) == 0:
            return None
        
        df = pd.DataFrame(all_data)
        
        # Create enhanced map with country names
        fig = go.Figure(data=go.Choropleth(
            locations=df['iso'],
            z=df['value'],
            text=df['country'],  # Country names for hover
            customdata=df[['country', 'value', 'year']],
            colorscale='Reds',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='white',
            marker_line_width=1.5,
            colorbar_title="Rate",
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         f'{indicator}: %{{z:.2f}}<br>' +
                         'Year: %{customdata[2]}<extra></extra>'
        ))
        
        # Add country name annotations (centered on each country)
        country_centers = {
            'AGO': (-12.5, -17.5), 'DZA': (28, 3), 'BEN': (9.5, 6.5), 'BWA': (-22, -24),
            'BFA': (12, -2), 'BDI': (-3.5, 29.9), 'CPV': (16, -24), 'CMR': (7, 6),
            'CAF': (7, 21), 'TCD': (15, 19), 'COM': (-12.2, 43.9), 'COG': (-1, -1),
            'CIV': (8, -5), 'COD': (-4, 21), 'GNQ': (1.5, 10), 'ERI': (15, 15),
            'ETH': (9, 38.5), 'GAB': (-1, 12), 'GMB': (13.5, -13.5), 'GHA': (8, -2),
            'GIN': (10, -10), 'GNB': (12, -12), 'KEN': (1, 38), 'LSO': (-29.5, 28.5),
            'LBR': (6.5, -9.5), 'MDG': (-20, 47), 'MWI': (-13.5, 34), 'MLI': (17, -4),
            'MRT': (20, -10), 'MUS': (-20.3, 57.5), 'MOZ': (-18, 35), 'NAM': (-22, 17),
            'NER': (17, 8), 'NGA': (10, 8), 'RWA': (-2, 30), 'STP': (1, 7),
            'SEN': (14, -14), 'SYC': (-4.6, 55.5), 'SLE': (8.5, -11.5), 'ZAF': (-29, 24),
            'SSD': (7, 30), 'SWZ': (-26.5, 31.5), 'TZA': (-6, 35), 'TGO': (8, 1),
            'UGA': (1, 32), 'ZMB': (-15, 28), 'ZWE': (-19, 29.5)
        }
        
        # Add country name annotations
        for _, row in df.iterrows():
            iso = row['iso']
            country_name = row['country']
            if iso in country_centers:
                lat, lon = country_centers[iso]
                fig.add_trace(go.Scattergeo(
                    lon=[lon],
                    lat=[lat],
                    text=[country_name],
                    mode='text',
                    textfont=dict(size=11, color='black', family='Arial Black'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        fig.update_geos(
            visible=True,
            resolution=50,
            showcountries=True,
            countrycolor="white",
            showcoastlines=True,
            coastlinecolor="white",
            showland=True,
            landcolor="lightgray",
            showocean=True,
            oceancolor="lightblue",
            projection_type="natural earth",
            lonaxis_range=[-20, 55],
            lataxis_range=[-35, 38],
            bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_layout(
            title=dict(
                text=f'{indicator} by Country - Africa ({year})',
                font=dict(size=20, color='#0066CC')
            ),
            height=900,  # Bigger map
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='lightblue',
                showlakes=True
            ),
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        return fig
