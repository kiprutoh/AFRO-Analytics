"""
Mortality Analytics Module
Analyzes Maternal and Child Mortality for WHO AFRO region countries
Following TB Burden framework pattern with focus on Sex and Wealth Quintile disaggregation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class MaternalMortalityAnalytics:
    """Analytics for Maternal Mortality Ratio (MMR) focusing on AFRO countries"""
    
    def __init__(self, maternal_data_path: str, country_lookup_path: str):
        """
        Initialize Maternal Mortality Analytics
        
        Args:
            maternal_data_path: Path to maternal Mortality CSV (wide format)
            country_lookup_path: Path to AFRO countries lookup CSV
        """
        self.maternal_data_path = maternal_data_path
        self.country_lookup_path = country_lookup_path
        self.maternal_data = None
        self.afro_countries = None
        self.maternal_afro = None
        
    def load_data(self):
        """Load and clean Maternal Mortality data for AFRO countries"""
        print("Loading Maternal Mortality data...")
        
        # Load maternal data (wide format with years as columns)
        self.maternal_data = pd.read_csv(self.maternal_data_path)
        
        # Load AFRO countries lookup
        self.afro_countries = pd.read_csv(self.country_lookup_path)
        
        # Filter for AFRO countries only
        afro_iso3_list = self.afro_countries['ISO3'].tolist()
        maternal_filtered = self.maternal_data[
            self.maternal_data['ISO Code'].isin(afro_iso3_list)
        ].copy()
        
        # Reshape from wide to long format
        year_cols = [str(year) for year in range(2000, 2024)]  # 2000-2023
        year_cols_available = [col for col in year_cols if col in maternal_filtered.columns]
        
        id_vars = ['ISO Code', 'country', 'UNICEF Programme Region', 
                   'UNICEF Reporting Region', 'UNICEF Sub-Reporting Region']
        
        self.maternal_afro = pd.melt(
            maternal_filtered,
            id_vars=id_vars,
            value_vars=year_cols_available,
            var_name='year',
            value_name='mmr'
        )
        
        # Convert year to integer and MMR to numeric
        self.maternal_afro['year'] = pd.to_numeric(self.maternal_afro['year'], errors='coerce')
        self.maternal_afro['mmr'] = pd.to_numeric(self.maternal_afro['mmr'], errors='coerce')
        
        # Drop rows with missing MMR values
        self.maternal_afro = self.maternal_afro.dropna(subset=['mmr', 'year'])
        
        # Clean country names using lookup
        country_mapping = dict(zip(
            self.afro_countries['ISO3'], 
            self.afro_countries['Country']
        ))
        self.maternal_afro['country_clean'] = self.maternal_afro['ISO Code'].map(country_mapping)
        
        # Fill any missing with original country name
        self.maternal_afro['country_clean'] = self.maternal_afro['country_clean'].fillna(self.maternal_afro['country'])
        
        # Add iso3 column for consistency
        self.maternal_afro['iso3'] = self.maternal_afro['ISO Code']
        
        print(f"Loaded data for {self.maternal_afro['country_clean'].nunique()} AFRO countries")
        print(f"Year range: {int(self.maternal_afro['year'].min())} - {int(self.maternal_afro['year'].max())}")
        
        return self
    
    def get_latest_year(self) -> int:
        """Get the most recent year in the dataset"""
        return int(self.maternal_afro['year'].max())
    
    def get_mmr_summary(self, year: Optional[int] = None) -> Dict:
        """
        Get summary statistics for MMR in AFRO region
        
        Args:
            year: Specific year (default: latest year)
            
        Returns:
            Dictionary with summary statistics
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.maternal_afro[self.maternal_afro['year'] == year].copy()
        
        mmr_values = data_year['mmr'].values
        
        summary = {
            'year': year,
            'total_countries': len(data_year),
            'regional_median_mmr': float(np.median(mmr_values)),
            'regional_mean_mmr': float(np.mean(mmr_values)),
            'min_mmr': float(mmr_values.min()),
            'max_mmr': float(mmr_values.max()),
            'best_performing_country': data_year.loc[data_year['mmr'].idxmin(), 'country_clean'],
            'worst_performing_country': data_year.loc[data_year['mmr'].idxmax(), 'country_clean'],
            'countries_below_sdg_target': int((mmr_values < 70).sum()),  # SDG target: <70 per 100,000
            'countries_above_sdg_target': int((mmr_values >= 70).sum())
        }
        
        return summary
    
    def get_top_mmr_countries(self, n: int = 10, year: Optional[int] = None,
                              ascending: bool = False) -> pd.DataFrame:
        """
        Get top N countries by MMR
        
        Args:
            n: Number of countries to return
            year: Specific year (default: latest)
            ascending: If True, get lowest MMR; if False, get highest MMR
            
        Returns:
            DataFrame with top countries
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.maternal_afro[self.maternal_afro['year'] == year].copy()
        
        # Sort and get top N
        data_sorted = data_year.sort_values(by='mmr', ascending=ascending)
        top_n = data_sorted.head(n)[['country_clean', 'iso3', 'mmr', 'year']]
        
        return top_n.reset_index(drop=True)
    
    def get_mmr_over_time(self, country: str) -> pd.DataFrame:
        """
        Get MMR trend over time for a specific country
        
        Args:
            country: Country name
            
        Returns:
            DataFrame with year and MMR values
        """
        country_data = self.maternal_afro[
            self.maternal_afro['country_clean'] == country
        ][['year', 'mmr', 'country_clean']].sort_values('year')
        
        return country_data
    
    def calculate_equity_measures(self, year: Optional[int] = None) -> Dict:
        """
        Calculate equity measures for MMR distribution
        
        Args:
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with equity measures
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.maternal_afro[
            (self.maternal_afro['year'] == year) & 
            (self.maternal_afro['mmr'].notna())
        ].copy()
        
        values = data_year['mmr'].values
        
        # Calculate inequality measures
        equity = {
            'indicator': 'Maternal Mortality Ratio',
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
    
    def get_regional_trends(self) -> pd.DataFrame:
        """
        Get regional aggregate trends over time
        
        Returns:
            DataFrame with yearly regional median/mean MMR
        """
        regional_trends = self.maternal_afro.groupby('year').agg({
            'mmr': ['mean', 'median', 'min', 'max', 'count']
        }).reset_index()
        
        regional_trends.columns = ['year', 'mean_mmr', 'median_mmr', 'min_mmr', 'max_mmr', 'country_count']
        
        return regional_trends
    
    def get_country_list(self) -> List[str]:
        """Get list of all countries in dataset"""
        return sorted(self.maternal_afro['country_clean'].unique().tolist())
    
    def get_data_summary(self) -> Dict:
        """Get summary of available data"""
        return {
            'total_countries': self.maternal_afro['country_clean'].nunique(),
            'year_range': (int(self.maternal_afro['year'].min()), int(self.maternal_afro['year'].max())),
            'latest_year': self.get_latest_year(),
            'total_records': len(self.maternal_afro),
            'indicator': 'Maternal Mortality Ratio (deaths per 100,000 live births)',
            'sdg_target': 'Less than 70 per 100,000 by 2030'
        }


class ChildMortalityAnalytics:
    """Analytics for Child Mortality (U5MR, IMR, NMR) focusing on AFRO countries with Sex and Wealth Quintile disaggregation"""
    
    def __init__(self, child_data_path: str, country_lookup_path: str):
        """
        Initialize Child Mortality Analytics
        
        Args:
            child_data_path: Path to Child Mortality CSV (long format)
            country_lookup_path: Path to AFRO countries lookup CSV
        """
        self.child_data_path = child_data_path
        self.country_lookup_path = country_lookup_path
        self.child_data = None
        self.afro_countries = None
        self.child_afro = None
        
    def load_data(self):
        """Load and clean Child Mortality data for AFRO countries"""
        print("Loading Child Mortality data...")
        
        # Load child data (long format)
        self.child_data = pd.read_csv(self.child_data_path, low_memory=False)
        
        # Load AFRO countries lookup
        self.afro_countries = pd.read_csv(self.country_lookup_path)
        
        # Filter for AFRO countries only
        afro_iso3_list = self.afro_countries['ISO3'].tolist()
        self.child_afro = self.child_data[
            self.child_data['iso'].isin(afro_iso3_list)
        ].copy()
        
        # Clean year column (remove invalid years)
        self.child_afro['year'] = pd.to_numeric(self.child_afro['year'], errors='coerce')
        self.child_afro = self.child_afro[
            (self.child_afro['year'] >= 1980) & 
            (self.child_afro['year'] <= 2024) &
            (self.child_afro['year'].notna())
        ]
        
        # Convert value to numeric
        self.child_afro['value'] = pd.to_numeric(self.child_afro['value'], errors='coerce')
        
        # Drop rows with missing values
        self.child_afro = self.child_afro.dropna(subset=['value'])
        
        # Clean country names using lookup
        country_mapping = dict(zip(
            self.afro_countries['ISO3'], 
            self.afro_countries['Country']
        ))
        self.child_afro['country_clean'] = self.child_afro['iso'].map(country_mapping)
        
        # Fill any missing with original country name
        self.child_afro['country_clean'] = self.child_afro['country_clean'].fillna(self.child_afro['country'])
        
        # Add iso3 column for consistency
        self.child_afro['iso3'] = self.child_afro['iso']
        
        # Clean Sex column (standardize values)
        self.child_afro['sex'] = self.child_afro['sex'].fillna('Total')
        self.child_afro['sex'] = self.child_afro['sex'].str.strip()
        
        # Clean Wealth Quintile column
        self.child_afro['Wealth Quintile'] = self.child_afro['Wealth Quintile'].fillna('Total')
        self.child_afro['Wealth Quintile'] = self.child_afro['Wealth Quintile'].str.strip()
        
        print(f"Loaded data for {self.child_afro['country_clean'].nunique()} AFRO countries")
        print(f"Year range: {int(self.child_afro['year'].min())} - {int(self.child_afro['year'].max())}")
        print(f"Indicators: {self.child_afro['indicator'].nunique()}")
        
        return self
    
    def get_latest_year(self, indicator: str = 'Under-five mortality rate') -> int:
        """Get the most recent year in the dataset for a specific indicator"""
        indicator_data = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['sex'] == 'Total') &
            (self.child_afro['Wealth Quintile'] == 'Total')
        ]
        return int(indicator_data['year'].max()) if len(indicator_data) > 0 else 2024
    
    def get_mortality_summary(self, year: Optional[int] = None) -> Dict:
        """
        Get summary statistics for Child Mortality in AFRO region
        
        Args:
            year: Specific year (default: latest year)
            
        Returns:
            Dictionary with summary statistics
        """
        # Focus on key indicators: U5MR, IMR, NMR
        key_indicators = [
            'Under-five mortality rate',
            'Infant mortality rate', 
            'Neonatal mortality rate'
        ]
        
        if year is None:
            year = self.get_latest_year('Under-five mortality rate')
        
        summary = {
            'year': year,
            'total_countries': 0
        }
        
        for indicator in key_indicators:
            data_year = self.child_afro[
                (self.child_afro['indicator'] == indicator) &
                (self.child_afro['year'] == year) &
                (self.child_afro['sex'] == 'Total') &
                (self.child_afro['Wealth Quintile'] == 'Total')
            ].copy()
            
            if len(data_year) > 0:
                values = data_year['value'].values
                indicator_key = indicator.lower().replace(' ', '_').replace('-', '_')
                
                summary[f'{indicator_key}_median'] = float(np.median(values))
                summary[f'{indicator_key}_mean'] = float(np.mean(values))
                summary[f'{indicator_key}_min'] = float(values.min())
                summary[f'{indicator_key}_max'] = float(values.max())
                summary['total_countries'] = max(summary['total_countries'], len(data_year))
        
        return summary
    
    def get_top_mortality_countries(self, indicator: str = 'Under-five mortality rate',
                                    n: int = 10, year: Optional[int] = None,
                                    ascending: bool = False) -> pd.DataFrame:
        """
        Get top N countries by mortality indicator
        
        Args:
            indicator: Mortality indicator
            n: Number of countries to return
            year: Specific year (default: latest)
            ascending: If True, get lowest; if False, get highest
            
        Returns:
            DataFrame with top countries
        """
        if year is None:
            year = self.get_latest_year(indicator)
        
        data_year = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['year'] == year) &
            (self.child_afro['sex'] == 'Total') &
            (self.child_afro['Wealth Quintile'] == 'Total')
        ].copy()
        
        # Sort and get top N
        data_sorted = data_year.sort_values(by='value', ascending=ascending)
        top_n = data_sorted.head(n)[['country_clean', 'iso3', 'value', 'year', 'indicator']]
        
        return top_n.reset_index(drop=True)
    
    def get_mortality_over_time(self, country: str, indicator: str = 'Under-five mortality rate') -> pd.DataFrame:
        """
        Get mortality trend over time for a specific country
        
        Args:
            country: Country name
            indicator: Mortality indicator
            
        Returns:
            DataFrame with year and value
        """
        country_data = self.child_afro[
            (self.child_afro['country_clean'] == country) &
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['sex'] == 'Total') &
            (self.child_afro['Wealth Quintile'] == 'Total')
        ][['year', 'value', 'indicator', 'country_clean']].sort_values('year')
        
        return country_data
    
    def get_sex_disaggregation(self, indicator: str = 'Under-five mortality rate',
                               year: Optional[int] = None) -> pd.DataFrame:
        """
        Get sex-disaggregated data for mortality indicator
        
        Args:
            indicator: Mortality indicator
            year: Specific year (default: latest)
            
        Returns:
            DataFrame with sex-disaggregated data
        """
        if year is None:
            year = self.get_latest_year(indicator)
        
        sex_data = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['year'] == year) &
            (self.child_afro['Wealth Quintile'] == 'Total') &
            (self.child_afro['sex'].isin(['Female', 'Male', 'Total']))
        ][['country_clean', 'iso3', 'sex', 'value', 'year']].copy()
        
        # Pivot to have Female, Male, Total as columns
        if len(sex_data) > 0:
            sex_pivot = sex_data.pivot_table(
                index=['country_clean', 'iso3', 'year'],
                columns='sex',
                values='value'
            ).reset_index()
            
            # Calculate sex ratio (Male/Female)
            if 'Male' in sex_pivot.columns and 'Female' in sex_pivot.columns:
                sex_pivot['sex_ratio'] = sex_pivot['Male'] / sex_pivot['Female']
                sex_pivot['sex_gap'] = sex_pivot['Male'] - sex_pivot['Female']
            
            return sex_pivot
        
        return pd.DataFrame()
    
    def get_wealth_quintile_analysis(self, indicator: str = 'Under-five mortality rate',
                                     year: Optional[int] = None) -> pd.DataFrame:
        """
        Get wealth quintile disaggregated data
        
        Args:
            indicator: Mortality indicator
            year: Specific year (default: latest)
            
        Returns:
            DataFrame with wealth quintile data
        """
        if year is None:
            year = self.get_latest_year(indicator)
        
        wealth_data = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['year'] == year) &
            (self.child_afro['sex'] == 'Total') &
            (self.child_afro['Wealth Quintile'].isin(['Lowest', 'Second', 'Middle', 'Fourth', 'Highest', 'Total']))
        ][['country_clean', 'iso3', 'Wealth Quintile', 'value', 'year']].copy()
        
        # Pivot to have quintiles as columns
        if len(wealth_data) > 0:
            wealth_pivot = wealth_data.pivot_table(
                index=['country_clean', 'iso3', 'year'],
                columns='Wealth Quintile',
                values='value'
            ).reset_index()
            
            # Calculate wealth ratio (Lowest/Highest) - equity measure
            if 'Lowest' in wealth_pivot.columns and 'Highest' in wealth_pivot.columns:
                wealth_pivot['wealth_ratio'] = wealth_pivot['Lowest'] / wealth_pivot['Highest']
                wealth_pivot['wealth_gap'] = wealth_pivot['Lowest'] - wealth_pivot['Highest']
            
            return wealth_pivot
        
        return pd.DataFrame()
    
    def calculate_equity_measures(self, indicator: str = 'Under-five mortality rate',
                                  year: Optional[int] = None) -> Dict:
        """
        Calculate equity measures for mortality distribution
        
        Args:
            indicator: Mortality indicator
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with equity measures
        """
        if year is None:
            year = self.get_latest_year(indicator)
        
        data_year = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['year'] == year) &
            (self.child_afro['sex'] == 'Total') &
            (self.child_afro['Wealth Quintile'] == 'Total') &
            (self.child_afro['value'].notna())
        ].copy()
        
        values = data_year['value'].values
        
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
    
    def get_regional_trends(self, indicator: str = 'Under-five mortality rate') -> pd.DataFrame:
        """
        Get regional aggregate trends over time
        
        Args:
            indicator: Mortality indicator
            
        Returns:
            DataFrame with yearly regional aggregates
        """
        regional_data = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['sex'] == 'Total') &
            (self.child_afro['Wealth Quintile'] == 'Total')
        ].copy()
        
        regional_trends = regional_data.groupby('year').agg({
            'value': ['mean', 'median', 'min', 'max', 'count']
        }).reset_index()
        
        regional_trends.columns = ['year', 'mean_value', 'median_value', 'min_value', 'max_value', 'country_count']
        
        return regional_trends
    
    def get_country_list(self) -> List[str]:
        """Get list of all countries in dataset"""
        return sorted(self.child_afro['country_clean'].unique().tolist())
    
    def get_data_summary(self) -> Dict:
        """Get summary of available data"""
        indicators = self.child_afro['indicator'].unique().tolist()
        
        return {
            'total_countries': self.child_afro['country_clean'].nunique(),
            'year_range': (int(self.child_afro['year'].min()), int(self.child_afro['year'].max())),
            'latest_year': self.get_latest_year(),
            'total_records': len(self.child_afro),
            'total_indicators': len(indicators),
            'key_indicators': [
                'Under-five mortality rate',
                'Infant mortality rate',
                'Neonatal mortality rate'
            ],
            'sex_categories': sorted(self.child_afro['sex'].unique().tolist()),
            'wealth_quintiles': sorted(self.child_afro['Wealth Quintile'].unique().tolist())
        }

