"""
TB Burden Analytics Module
Analyzes TB burden estimates for WHO AFRO region countries
Based on Global TB Programme burden estimates
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class TBBurdenAnalytics:
    """Analytics for TB Burden estimates focusing on AFRO countries"""
    
    def __init__(self, burden_data_path: str, country_lookup_path: str):
        """
        Initialize TB Burden Analytics
        
        Args:
            burden_data_path: Path to TB burden countries CSV
            country_lookup_path: Path to AFRO countries lookup CSV
        """
        self.burden_data_path = burden_data_path
        self.country_lookup_path = country_lookup_path
        self.burden_data = None
        self.afro_countries = None
        self.burden_afro = None
        
    def load_data(self):
        """Load and clean TB burden data for AFRO countries"""
        print("Loading TB Burden data...")
        
        # Load burden data
        self.burden_data = pd.read_csv(self.burden_data_path)
        
        # Load AFRO countries lookup
        self.afro_countries = pd.read_csv(self.country_lookup_path)
        
        # Filter for AFRO countries only
        afro_iso3_list = self.afro_countries['ISO3'].tolist()
        self.burden_afro = self.burden_data[
            self.burden_data['iso3'].isin(afro_iso3_list)
        ].copy()
        
        # Clean country names using lookup
        country_mapping = dict(zip(
            self.afro_countries['ISO3'], 
            self.afro_countries['Country']
        ))
        self.burden_afro['country_clean'] = self.burden_afro['iso3'].map(country_mapping)
        
        # Fill any missing with original country name
        self.burden_afro['country_clean'].fillna(self.burden_afro['country'], inplace=True)
        
        print(f"Loaded data for {self.burden_afro['country_clean'].nunique()} AFRO countries")
        print(f"Year range: {self.burden_afro['year'].min()} - {self.burden_afro['year'].max()}")
        
        return self
    
    def get_latest_year(self) -> int:
        """Get the most recent year in the dataset"""
        return int(self.burden_afro['year'].max())
    
    def get_burden_summary(self, year: Optional[int] = None) -> Dict:
        """
        Get summary statistics for TB burden in AFRO region
        
        Args:
            year: Specific year (default: latest year)
            
        Returns:
            Dictionary with summary statistics
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.burden_afro[self.burden_afro['year'] == year].copy()
        
        summary = {
            'year': year,
            'total_countries': len(data_year),
            'total_population': data_year['e_pop_num'].sum(),
            'total_incident_cases': data_year['e_inc_num'].sum(),
            'total_tb_hiv_cases': data_year['e_inc_tbhiv_num'].sum(),
            'total_mortality_cases': data_year['e_mort_num'].sum(),
            'regional_incidence_rate_100k': (data_year['e_inc_num'].sum() / data_year['e_pop_num'].sum()) * 100000,
            'regional_mortality_rate_100k': (data_year['e_mort_num'].sum() / data_year['e_pop_num'].sum()) * 100000,
            'regional_tbhiv_percent': (data_year['e_inc_tbhiv_num'].sum() / data_year['e_inc_num'].sum()) * 100 if data_year['e_inc_num'].sum() > 0 else 0
        }
        
        return summary
    
    def get_top_burden_countries(self, indicator: str = 'e_inc_num', 
                                 n: int = 10, year: Optional[int] = None,
                                 ascending: bool = False) -> pd.DataFrame:
        """
        Get top N countries by burden indicator
        
        Args:
            indicator: Burden indicator column name
            n: Number of countries to return
            year: Specific year (default: latest)
            ascending: If True, get lowest burden; if False, get highest burden
            
        Returns:
            DataFrame with top countries
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.burden_afro[self.burden_afro['year'] == year].copy()
        
        # Sort and get top N
        data_sorted = data_year.sort_values(by=indicator, ascending=ascending)
        top_n = data_sorted.head(n)[['country_clean', 'iso3', indicator, 'e_pop_num']]
        
        return top_n.reset_index(drop=True)
    
    def get_indicator_over_time(self, country: str, indicator: str) -> pd.DataFrame:
        """
        Get indicator trend over time for a specific country
        
        Args:
            country: Country name
            indicator: Burden indicator
            
        Returns:
            DataFrame with year and indicator values
        """
        country_data = self.burden_afro[
            self.burden_afro['country_clean'] == country
        ][['year', indicator]].sort_values('year')
        
        return country_data
    
    def get_burden_indicators(self, year: Optional[int] = None) -> pd.DataFrame:
        """
        Get all key TB burden indicators for all AFRO countries
        
        Args:
            year: Specific year (default: latest)
            
        Returns:
            DataFrame with key indicators
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.burden_afro[self.burden_afro['year'] == year].copy()
        
        # Select key burden indicators
        key_indicators = [
            'country_clean', 'iso3', 'year', 'e_pop_num',
            'e_inc_100k', 'e_inc_num',  # Incidence
            'e_inc_tbhiv_100k', 'e_inc_tbhiv_num',  # TB/HIV
            'e_mort_100k', 'e_mort_num',  # Mortality
            'e_mort_exc_tbhiv_100k', 'e_mort_exc_tbhiv_num',  # Mortality excluding TB/HIV
            'e_mort_tbhiv_100k', 'e_mort_tbhiv_num',  # TB/HIV mortality
            'e_tbhiv_prct',  # TB/HIV percentage
            'cfr_pct'  # Case fatality ratio
        ]
        
        available_cols = [col for col in key_indicators if col in data_year.columns]
        return data_year[available_cols].copy()
    
    def calculate_equity_measures(self, indicator: str = 'e_inc_100k', 
                                  year: Optional[int] = None) -> Dict:
        """
        Calculate equity measures for TB burden distribution
        
        Args:
            indicator: Burden indicator to analyze
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with equity measures
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.burden_afro[
            (self.burden_afro['year'] == year) & 
            (self.burden_afro[indicator].notna())
        ].copy()
        
        values = data_year[indicator].values
        
        # Calculate inequality measures
        equity = {
            'indicator': indicator,
            'year': year,
            'countries': len(data_year),
            'min_value': float(values.min()),
            'max_value': float(values.max()),
            'range': float(values.max() - values.min()),
            'ratio_max_to_min': float(values.max() / values.min()) if values.min() > 0 else None,
            'percentile_25': float(np.percentile(values, 25)),
            'percentile_50': float(np.percentile(values, 50)),
            'percentile_75': float(np.percentile(values, 75)),
            'interquartile_range': float(np.percentile(values, 75) - np.percentile(values, 25)),
            'coefficient_of_variation': float((np.std(values) / np.mean(values)) * 100) if np.mean(values) > 0 else None
        }
        
        return equity
    
    def get_regional_trends(self, indicator: str = 'e_inc_num') -> pd.DataFrame:
        """
        Get regional aggregate trends over time
        
        Args:
            indicator: Burden indicator
            
        Returns:
            DataFrame with yearly regional totals
        """
        regional_trends = self.burden_afro.groupby('year')[indicator].sum().reset_index()
        regional_trends.columns = ['year', 'regional_total']
        
        return regional_trends
    
    def get_country_burden_profile(self, country: str, year: Optional[int] = None) -> Dict:
        """
        Get comprehensive burden profile for a specific country
        
        Args:
            country: Country name
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with burden profile
        """
        if year is None:
            year = self.get_latest_year()
        
        country_data = self.burden_afro[
            (self.burden_afro['country_clean'] == country) & 
            (self.burden_afro['year'] == year)
        ]
        
        if len(country_data) == 0:
            return {'error': f'No data found for {country} in {year}'}
        
        row = country_data.iloc[0]
        
        profile = {
            'country': country,
            'iso3': row['iso3'],
            'year': year,
            'population': int(row['e_pop_num']),
            'incidence': {
                'cases': int(row['e_inc_num']) if pd.notna(row['e_inc_num']) else None,
                'rate_per_100k': float(row['e_inc_100k']) if pd.notna(row['e_inc_100k']) else None,
                'lo': int(row['e_inc_num_lo']) if 'e_inc_num_lo' in row and pd.notna(row['e_inc_num_lo']) else None,
                'hi': int(row['e_inc_num_hi']) if 'e_inc_num_hi' in row and pd.notna(row['e_inc_num_hi']) else None
            },
            'tb_hiv': {
                'cases': int(row['e_inc_tbhiv_num']) if pd.notna(row['e_inc_tbhiv_num']) else None,
                'rate_per_100k': float(row['e_inc_tbhiv_100k']) if pd.notna(row['e_inc_tbhiv_100k']) else None,
                'percent': float(row['e_tbhiv_prct']) if pd.notna(row['e_tbhiv_prct']) else None
            },
            'mortality': {
                'total_cases': int(row['e_mort_num']) if pd.notna(row['e_mort_num']) else None,
                'total_rate_per_100k': float(row['e_mort_100k']) if pd.notna(row['e_mort_100k']) else None,
                'excl_tbhiv_cases': int(row['e_mort_exc_tbhiv_num']) if pd.notna(row['e_mort_exc_tbhiv_num']) else None,
                'tbhiv_cases': int(row['e_mort_tbhiv_num']) if pd.notna(row['e_mort_tbhiv_num']) else None
            },
            'case_fatality_ratio_pct': float(row['cfr_pct']) if pd.notna(row['cfr_pct']) else None
        }
        
        return profile
    
    def get_data_summary(self) -> Dict:
        """Get summary of available data"""
        return {
            'total_countries': self.burden_afro['country_clean'].nunique(),
            'year_range': (int(self.burden_afro['year'].min()), int(self.burden_afro['year'].max())),
            'latest_year': self.get_latest_year(),
            'total_records': len(self.burden_afro),
            'key_indicators': [
                'Incidence (cases and rates)',
                'TB/HIV (cases and rates)',
                'Mortality (total and disaggregated)',
                'Case Fatality Ratio'
            ]
        }

