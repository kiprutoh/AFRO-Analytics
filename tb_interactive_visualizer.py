"""
TB Interactive Visualization Module
Allows users to customize TB charts, choose prediction methods, and view maps
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Tuple
from tb_analytics import TBAnalytics
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')


class TBInteractiveVisualizer:
    """Interactive visualization for TB data with customizable charts and predictions"""
    
    def __init__(self, analytics: TBAnalytics):
        """
        Initialize TB visualizer
        
        Args:
            analytics: TBAnalytics instance
        """
        self.analytics = analytics
        self.pipeline = analytics.pipeline
        
        # Country ISO code mapping for maps (AFRO countries)
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
            log_values = np.log(values + 1e-10)
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
            window = min(3, len(values))
            avg_value = np.mean(values[-window:])
            trend = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0
            predictions = avg_value + trend * (future_years.flatten() - years[-1, 0])
        
        else:
            model = LinearRegression()
            model.fit(years, values)
            predictions = model.predict(future_years)
        
        return predictions
    
    def create_custom_trend_chart(self, country: str, indicator: str, 
                                  start_year: int = 2000, end_year: int = 2023,
                                  show_projection: bool = True,
                                  prediction_method: str = 'linear') -> go.Figure:
        """
        Create customizable trend chart with projections
        
        Args:
            country: Country name
            indicator: Indicator name
            start_year: Start year for observed data
            end_year: End year for observed data
            show_projection: Whether to show projection to 2030
            prediction_method: Method for projection
        
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
        
        country_data = self.pipeline.filter_by_country(country, df)
        
        if len(country_data) == 0 or col_name not in country_data.columns:
            return None
        
        # Filter by year range
        country_data = country_data[
            (country_data['year'] >= start_year) & 
            (country_data['year'] <= end_year)
        ].sort_values('year')
        
        if len(country_data) == 0:
            return None
        
        observed_data = country_data[col_name].dropna()
        observed_years = country_data['year'].values
        
        if len(observed_data) == 0:
            return None
        
        fig = go.Figure()
        
        # Observed data
        fig.add_trace(go.Scatter(
            x=observed_years,
            y=observed_data.values,
            mode='lines+markers',
            name='Observed Data',
            line=dict(color='#0066CC', width=3),
            marker=dict(size=8)
        ))
        
        # Projection if requested
        if show_projection and len(observed_data) >= 2:
            projection_years = np.arange(end_year + 1, 2031)
            if len(projection_years) > 0:
                predictions = self.predict_future_values(
                    observed_years.astype(float),
                    observed_data.values.astype(float),
                    projection_years.astype(float),
                    prediction_method
                )
                
                fig.add_trace(go.Scatter(
                    x=projection_years,
                    y=predictions,
                    mode='lines+markers',
                    name='Projection (2024-2030)',
                    line=dict(color='#FFA500', width=2, dash='dash'),
                    marker=dict(size=6),
                    fill='tonexty',
                    fillcolor='rgba(255, 165, 0, 0.1)'
                ))
        
        fig.update_layout(
            title=f'{indicator} - {country}',
            xaxis_title='Year',
            yaxis_title='Value',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_map(self, indicator: str, year: Optional[int] = None) -> go.Figure:
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
        map_data = df[['country', col_name]].copy()
        map_data = map_data.dropna(subset=[col_name])
        
        # Add ISO codes
        map_data['iso3'] = map_data['country'].map(self.country_iso_map)
        map_data = map_data.dropna(subset=['iso3'])
        
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
            lonaxis_range=[-20, 55],
            lataxis_range=[-35, 38]
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
    
    def create_multi_country_comparison(self, countries: List[str], indicator: str,
                                       show_projection: bool = False,
                                       prediction_method: str = 'linear') -> go.Figure:
        """
        Create comparison chart for multiple countries
        
        Args:
            countries: List of country names
            indicator: Indicator name
            show_projection: Whether to show projections
            prediction_method: Method for projection
        
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
            height=500,
            showlegend=False
        )
        
        return fig

