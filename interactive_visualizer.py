"""
Interactive Visualization Module
Allows users to customize charts, choose prediction methods, and view maps
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Tuple
from analytics import MortalityAnalytics
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')


class InteractiveVisualizer:
    """Interactive visualization with customizable charts and predictions"""
    
    def __init__(self, analytics: MortalityAnalytics):
        """
        Initialize visualizer
        
        Args:
            analytics: MortalityAnalytics instance
        """
        self.analytics = analytics
        self.pipeline = analytics.pipeline
        
        # Country ISO code mapping for maps
        self.country_iso_map = {
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
    
    def predict_future_values(self, years: np.ndarray, values: np.ndarray, 
                             future_years: np.ndarray, method: str = 'linear') -> np.ndarray:
        """
        Predict future values using different methods
        
        Args:
            years: Historical years
            values: Historical values
            future_years: Years to predict
            method: Prediction method ('linear', 'exponential', 'polynomial', 'moving_average')
        
        Returns:
            Predicted values
        """
        if len(years) < 2:
            return np.full(len(future_years), values[-1] if len(values) > 0 else 0)
        
        years = years.reshape(-1, 1)
        future_years = future_years.reshape(-1, 1)
        
        if method == 'linear':
            model = LinearRegression()
            model.fit(years, values)
            predictions = model.predict(future_years)
        
        elif method == 'exponential':
            # Log transform for exponential fit
            log_values = np.log(values + 1e-10)  # Add small value to avoid log(0)
            model = LinearRegression()
            model.fit(years, log_values)
            predictions = np.exp(model.predict(future_years)) - 1e-10
        
        elif method == 'polynomial':
            poly_features = PolynomialFeatures(degree=2)
            years_poly = poly_features.fit_transform(years)
            future_years_poly = poly_features.transform(future_years)
            model = LinearRegression()
            model.fit(years_poly, values)
            predictions = model.predict(future_years_poly)
        
        elif method == 'moving_average':
            # Use average of last few years
            window = min(3, len(values))
            avg_value = np.mean(values[-window:])
            trend = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0
            predictions = avg_value + trend * (future_years.flatten() - years[-1, 0])
        
        else:  # Default to linear
            model = LinearRegression()
            model.fit(years, values)
            predictions = model.predict(future_years)
        
        # Ensure predictions are non-negative
        predictions = np.maximum(predictions, 0)
        
        return predictions
    
    def create_custom_trend_chart(self, country: str, indicator: str,
                                  prediction_method: str = 'linear',
                                  show_projection: bool = True,
                                  start_year: int = 2000,
                                  end_year: int = 2030) -> go.Figure:
        """
        Create customizable trend chart with observed and projected data
        
        Args:
            country: Country name
            indicator: Indicator name
            prediction_method: Method for prediction ('linear', 'exponential', 'polynomial', 'moving_average')
            show_projection: Whether to show projections
            start_year: Start year for observed data
            end_year: End year for projections
        
        Returns:
            Plotly figure
        """
        # Try mortality data first
        country_data = self.pipeline.filter_by_country(country, self.analytics.mortality_df)
        ind_data = country_data[country_data['indicator'] == indicator]
        
        # If no data found and indicator is MMR, try MMR data
        if len(ind_data) == 0 and (indicator == "MMR" or "Maternal" in indicator):
            # Try MMR data
            mmr_data = self.analytics.mmr_df[self.analytics.mmr_df['country'] == country]
            if len(mmr_data) > 0:
                # Convert MMR data to match expected format
                ind_data = mmr_data.copy()
                ind_data['indicator'] = indicator
                ind_data['value'] = mmr_data['value']
        
        if len(ind_data) == 0:
            return None
        
        # Filter by year range
        ind_data = ind_data[(ind_data['year'] >= start_year) & (ind_data['year'] <= 2023)]
        ind_data = ind_data.sort_values('year')
        
        if len(ind_data) == 0:
            return None
        
        fig = go.Figure()
        
        # Observed data (2000-2023)
        observed_years = ind_data['year'].values
        observed_values = ind_data['value'].values
        
        # Get average value per year (in case of multiple values per year)
        df_grouped = ind_data.groupby('year')['value'].mean().reset_index()
        observed_years = df_grouped['year'].values
        observed_values = df_grouped['value'].values
        
        # Add observed data trace
        fig.add_trace(go.Scatter(
            x=observed_years,
            y=observed_values,
            mode='lines+markers',
            name='Observed (2000-2023)',
            line=dict(color='#0066CC', width=3),
            marker=dict(size=8, color='#0066CC'),
            hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Value: %{y:.2f}<extra></extra>'
        ))
        
        # Projections (2024-2030)
        if show_projection and len(observed_years) >= 2:
            projection_years = np.arange(2024, end_year + 1)
            
            # Predict future values
            predicted_values = self.predict_future_values(
                observed_years, observed_values, projection_years, prediction_method
            )
            
            # Add projection trace
            fig.add_trace(go.Scatter(
                x=projection_years,
                y=predicted_values,
                mode='lines+markers',
                name=f'Projected (2024-{end_year})',
                line=dict(color='#FFA500', width=2, dash='dash'),
                marker=dict(size=6, color='#FFA500'),
                hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Predicted: %{y:.2f}<extra></extra>'
            ))
            
            # Add shaded area for projections
            fig.add_trace(go.Scatter(
                x=np.concatenate([projection_years, projection_years[::-1]]),
                y=np.concatenate([predicted_values, np.zeros(len(predicted_values))]),
                fill='toself',
                fillcolor='rgba(255, 165, 0, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False,
                name='Projection Area'
            ))
            
            # Connect observed to projected
            if len(observed_years) > 0:
                last_observed_year = observed_years[-1]
                last_observed_value = observed_values[-1]
                first_projection_year = projection_years[0]
                first_projection_value = predicted_values[0]
                
                fig.add_trace(go.Scatter(
                    x=[last_observed_year, first_projection_year],
                    y=[last_observed_value, first_projection_value],
                    mode='lines',
                    line=dict(color='#FFA500', width=2, dash='dash'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Add SDG target line if applicable
        target_value = None
        if indicator == "MMR" or "Maternal" in indicator:
            target_value = 70
            fig.add_hline(
                y=target_value,
                line_dash="dot",
                line_color="red",
                annotation_text=f"SDG Target 2030: {target_value}",
                annotation_position="right"
            )
        elif "Under-five" in indicator:
            target_value = 25
            fig.add_hline(
                y=target_value,
                line_dash="dot",
                line_color="red",
                annotation_text=f"SDG Target 2030: {target_value}",
                annotation_position="right"
            )
        elif "Neonatal" in indicator:
            target_value = 12
            fig.add_hline(
                y=target_value,
                line_dash="dot",
                line_color="red",
                annotation_text=f"SDG Target 2030: {target_value}",
                annotation_position="right"
            )
        
        # Add curly bracket showing gap to target if projection is shown
        shapes = []
        annotations = []
        if show_projection and target_value is not None and len(projection_years) > 0:
            projected_2030 = predicted_values[-1]  # Last projected value (2030)
            gap = abs(projected_2030 - target_value)
            
            if gap > 0.1:  # Only show if significant gap
                # Determine bracket position
                if projected_2030 > target_value:
                    y_start = target_value
                    y_end = projected_2030
                else:
                    y_start = projected_2030
                    y_end = target_value
                
                bracket_y = (y_start + y_end) / 2
                bracket_x = end_year
                
                # Add curly bracket shape
                shapes = [{
                    'type': 'path',
                    'path': f'M {bracket_x+0.3},{y_start} Q {bracket_x+0.5},{bracket_y} {bracket_x+0.3},{y_end}',
                    'line': {'color': 'rgba(255,0,0,0.6)', 'width': 2},
                    'xref': 'x',
                    'yref': 'y'
                }]
                
                # Add annotation for gap value
                annotations = [{
                    'x': bracket_x + 0.5,
                    'y': bracket_y,
                    'text': f'Gap to Target: {gap:.1f}',
                    'showarrow': False,
                    'xref': 'x',
                    'yref': 'y',
                    'bgcolor': 'rgba(255,255,255,0.9)',
                    'bordercolor': 'rgba(255,0,0,0.6)',
                    'borderwidth': 1,
                    'font': {'size': 10}
                }]
        
        # Add vertical line separating observed and projected
        if show_projection:
            fig.add_vline(
                x=2023.5,
                line_dash="dot",
                line_color="gray",
                annotation_text="Observed → Projected",
                annotation_position="top"
            )
        
        layout_dict = {
            'title': f'{indicator} - {country}<br><sub>Observed (2000-2023) & Projected (2024-{end_year})</sub>',
            'xaxis_title': 'Year',
            'yaxis_title': 'Rate',
            'hovermode': 'x unified',
            'template': 'plotly_white',
            'height': 500,
            'showlegend': True,
            'legend': dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        }
        
        if shapes:
            layout_dict['shapes'] = shapes
        if annotations:
            layout_dict['annotations'] = annotations
        
        fig.update_layout(**layout_dict)
        
        return fig
    
    def create_country_map(self, indicator: str, year: int = 2023) -> go.Figure:
        """
        Create choropleth map for indicator across countries
        
        Args:
            indicator: Indicator name
            year: Year to display
        
        Returns:
            Plotly figure
        """
        # Get data for all countries
        all_data = []
        
        # Handle MMR separately
        if indicator == "MMR" or "Maternal" in indicator:
            for country in self.pipeline.get_countries():
                mmr_data = self.analytics.mmr_df[
                    (self.analytics.mmr_df['country'] == country) & 
                    (self.analytics.mmr_df['year'] <= year)
                ]
                if len(mmr_data) > 0:
                    latest = mmr_data.sort_values('year').iloc[-1]
                    iso_code = self.country_iso_map.get(country, '')
                    if iso_code:
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
                    # Get data for specified year or closest year
                    year_data = ind_data[ind_data['year'] <= year]
                    if len(year_data) > 0:
                        latest = year_data.sort_values('year').iloc[-1]
                        iso_code = self.country_iso_map.get(country, '')
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
        
        # Create map
        fig = px.choropleth(
            df,
            locations='iso',
            color='value',
            hover_name='country',
            hover_data={'value': ':.2f', 'year': True, 'iso': False},
            color_continuous_scale='Reds',
            title=f'{indicator} by Country ({year})',
            labels={'value': 'Rate'},
            scope='africa'
        )
        
        fig.update_layout(
            height=600,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth'
            )
        )
        
        return fig
    
    def create_multi_country_comparison(self, countries: List[str], indicator: str,
                                       show_projection: bool = True,
                                       prediction_method: str = 'linear') -> go.Figure:
        """
        Create comparison chart for multiple countries with projections
        
        Args:
            countries: List of country names
            indicator: Indicator name
            show_projection: Whether to show projections
            prediction_method: Prediction method
        
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        colors = ['#0066CC', '#00CC66', '#CC0066', '#FF6600', '#6600CC', '#00CCCC']
        
        for idx, country in enumerate(countries):
            country_data = self.pipeline.filter_by_country(country, self.analytics.mortality_df)
            ind_data = country_data[country_data['indicator'] == indicator]
            
            if len(ind_data) == 0:
                continue
            
            ind_data = ind_data[(ind_data['year'] >= 2000) & (ind_data['year'] <= 2023)]
            ind_data = ind_data.sort_values('year')
            
            if len(ind_data) == 0:
                continue
            
            df_grouped = ind_data.groupby('year')['value'].mean().reset_index()
            observed_years = df_grouped['year'].values
            observed_values = df_grouped['value'].values
            
            color = colors[idx % len(colors)]
            
            # Observed data
            fig.add_trace(go.Scatter(
                x=observed_years,
                y=observed_values,
                mode='lines+markers',
                name=f'{country} (Observed)',
                line=dict(color=color, width=2),
                marker=dict(size=6, color=color)
            ))
            
            # Projections
            if show_projection and len(observed_years) >= 2:
                projection_years = np.arange(2024, 2031)
                predicted_values = self.predict_future_values(
                    observed_years, observed_values, projection_years, prediction_method
                )
                
                fig.add_trace(go.Scatter(
                    x=projection_years,
                    y=predicted_values,
                    mode='lines',
                    name=f'{country} (Projected)',
                    line=dict(color=color, width=2, dash='dash'),
                    marker=dict(size=4, color=color)
                ))
        
        fig.update_layout(
            title=f'{indicator} - Multi-Country Comparison',
            xaxis_title='Year',
            yaxis_title='Rate',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig

