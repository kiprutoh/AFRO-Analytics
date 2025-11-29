"""
Mortality Analytics Module
Analyzes Maternal and Child Mortality for WHO AFRO region countries
Following TB Burden framework pattern
Uses UNICEF/UNIGME definitions and standard column structure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class MortalityDataPipeline:
    """Unified data pipeline for both Maternal and Child Mortality"""
    
    def __init__(self, maternal_data_path: str, child_data_path: str, country_lookup_path: str):
        """
        Initialize Mortality Data Pipeline
        
        Args:
            maternal_data_path: Path to maternal Mortality CSV
            child_data_path: Path to Child Mortality CSV (UNICEF format)
            country_lookup_path: Path to AFRO countries lookup CSV
        """
        self.maternal_data_path = maternal_data_path
        self.child_data_path = child_data_path
        self.country_lookup_path = country_lookup_path
        self.maternal_afro = None
        self.child_afro = None
        self.afro_countries = None
        
    def load_data(self):
        """Load and clean both Maternal and Child Mortality data"""
        print("Loading Mortality data...")
        
        # Load AFRO countries lookup
        self.afro_countries = pd.read_csv(self.country_lookup_path)
        afro_iso3_list = self.afro_countries['ISO3'].tolist()
        country_mapping = dict(zip(
            self.afro_countries['ISO3'], 
            self.afro_countries['Country']
        ))
        
        # Load Maternal Mortality data
        print("Loading Maternal Mortality data...")
        maternal_data = pd.read_csv(self.maternal_data_path)
        
        # Filter for AFRO countries
        maternal_filtered = maternal_data[
            maternal_data['ISO Code'].isin(afro_iso3_list)
        ].copy()
        
        # Reshape from wide to long format (years as columns)
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
        
        # Convert to numeric
        self.maternal_afro['year'] = pd.to_numeric(self.maternal_afro['year'], errors='coerce')
        self.maternal_afro['mmr'] = pd.to_numeric(self.maternal_afro['mmr'], errors='coerce')
        self.maternal_afro = self.maternal_afro.dropna(subset=['mmr', 'year'])
        
        # Clean country names
        self.maternal_afro['country_clean'] = self.maternal_afro['ISO Code'].map(country_mapping)
        self.maternal_afro['country_clean'] = self.maternal_afro['country_clean'].fillna(self.maternal_afro['country'])
        self.maternal_afro['iso3'] = self.maternal_afro['ISO Code']
        
        print(f"  Maternal: {self.maternal_afro['country_clean'].nunique()} countries, "
              f"years {int(self.maternal_afro['year'].min())}-{int(self.maternal_afro['year'].max())}")
        
        # Load Child Mortality data - handle both UNICEF format and clean format
        print("Loading Child Mortality data...")
        child_data = pd.read_csv(self.child_data_path, low_memory=False)
        
        # Check if file is in clean format (has 'iso', 'country', 'indicator' columns) or UNICEF format
        if 'iso' in child_data.columns and 'country' in child_data.columns and 'indicator' in child_data.columns:
            # Clean format - already has the columns we need
            print("  Detected clean format (iso, country, indicator columns)")
            child_data['iso3'] = child_data['iso']
            child_data['country_clean'] = child_data['country']
            # Indicators are already in readable format
            # Sex is already in readable format ('Total', 'Female', 'Male')
        elif 'REF_AREA:Geographic area' in child_data.columns:
            # UNICEF format - need to map columns
            print("  Detected UNICEF format")
            child_data = child_data.rename(columns={
                'REF_AREA:Geographic area': 'country_code',
                'INDICATOR:Indicator': 'indicator_code',
                'SEX:Sex': 'sex_code',
                'TIME_PERIOD:Time period': 'year',
                'OBS_VALUE:Observation Value': 'value',
                'LOWER_BOUND:Lower Bound': 'lower_bound',
                'UPPER_BOUND:Upper Bound': 'upper_bound',
                'AGE:Current age': 'age_group'
            })
            
            # Extract ISO3 code from country_code (format: "AFG: Afghanistan")
            child_data['iso3'] = child_data['country_code'].str.split(':').str[0].str.strip()
            
            # Map indicator codes to standard names
            indicator_mapping = {
                'CME_MRY0': 'Infant mortality rate',
                'CME_MRY0T4': 'Under-five mortality rate',
                'CME_MRY1T4': 'Child mortality rate (aged 1-4 years)',
                'CME_TMY0': 'Infant deaths',
                'CME_TMY0T4': 'Under-five deaths',
                'CME_TMY1T4': 'Child deaths (aged 1-4 years)'
            }
            child_data['indicator'] = child_data['indicator_code'].map(indicator_mapping)
            child_data['indicator'] = child_data['indicator'].fillna(child_data['indicator_code'])
            
            # Map sex codes to standard names
            sex_mapping = {
                'F': 'Female',
                'M': 'Male',
                '_T': 'Total'
            }
            child_data['sex'] = child_data['sex_code'].map(sex_mapping)
            child_data['sex'] = child_data['sex'].fillna(child_data['sex_code'])
            
            # Clean country names
            child_data['country_clean'] = child_data['iso3'].map(country_mapping)
            child_data['country_clean'] = child_data['country_clean'].fillna(
                child_data['country_code'].str.split(':').str[1].str.strip() if 'country_code' in child_data.columns else child_data['iso3']
            )
        else:
            print("ERROR: Unknown Child Mortality data format. Available columns:", list(child_data.columns))
            self.child_afro = pd.DataFrame()
            return self
        
        # Filter for AFRO countries
        self.child_afro = child_data[
            child_data['iso3'].isin(afro_iso3_list)
        ].copy()
        
        # Clean year - handle different year formats (including ranges like '2022-2023')
        if 'year' in self.child_afro.columns:
            # Convert to string first to handle ranges
            self.child_afro['year'] = self.child_afro['year'].astype(str)
            # Extract first year from ranges (e.g., '2022-2023' -> 2022)
            self.child_afro['year'] = self.child_afro['year'].str.split('-').str[0]
            # Convert to numeric
            self.child_afro['year'] = pd.to_numeric(self.child_afro['year'], errors='coerce')
        else:
            print("WARNING: 'year' column not found. Available columns:", list(self.child_afro.columns))
            self.child_afro = pd.DataFrame()
            return self
        
        # Filter years
        self.child_afro = self.child_afro[
            (self.child_afro['year'] >= 2000) & 
            (self.child_afro['year'] <= 2024) &
            (self.child_afro['year'].notna())
        ]
        
        # Clean value
        if 'value' in self.child_afro.columns:
            self.child_afro['value'] = pd.to_numeric(self.child_afro['value'], errors='coerce')
            self.child_afro = self.child_afro.dropna(subset=['value'])
        else:
            print("WARNING: 'value' column not found. Available columns:", list(self.child_afro.columns))
            self.child_afro = pd.DataFrame()
            return self
        
        # Debug: Check if we have data after filtering
        if len(self.child_afro) == 0:
            print("WARNING: No data remaining after filtering. Checking original data...")
            print(f"Original data shape: {child_data.shape}")
            print(f"After AFRO filter: {len(child_data[child_data['iso3'].isin(afro_iso3_list)])}")
            if 'iso3' in child_data.columns:
                print(f"Sample ISO3 codes in data: {child_data['iso3'].unique()[:10]}")
            print(f"AFRO ISO3 list sample: {afro_iso3_list[:10]}")
        
        if len(self.child_afro) > 0:
            print(f"  Child: {self.child_afro['country_clean'].nunique()} countries, "
                  f"years {int(self.child_afro['year'].min())}-{int(self.child_afro['year'].max())}, "
                  f"total records: {len(self.child_afro)}")
        else:
            print("  WARNING: Child Mortality data is empty after filtering!")
            print(f"  Original data shape: {child_data.shape}")
            print(f"  After AFRO filter: {len(child_data[child_data['iso3'].isin(afro_iso3_list)])}")
            if 'iso3' in child_data.columns:
                print(f"  Sample ISO3 codes in data: {child_data['iso3'].unique()[:10]}")
            print(f"  AFRO ISO3 list sample: {afro_iso3_list[:10]}")
        
        return self


class MaternalMortalityAnalytics:
    """Analytics for Maternal Mortality Ratio (MMR) - UNICEF/UNIGME definition"""
    
    def __init__(self, pipeline: MortalityDataPipeline):
        """
        Initialize Maternal Mortality Analytics
        
        Args:
            pipeline: MortalityDataPipeline instance with loaded data
        """
        self.pipeline = pipeline
        self.maternal_afro = pipeline.maternal_afro
        
    def get_latest_year(self) -> int:
        """Get the most recent year in the dataset"""
        return int(self.maternal_afro['year'].max())
    
    def get_mmr_summary(self, year: Optional[int] = None) -> Dict:
        """
        Get summary statistics for MMR in AFRO region
        MMR Definition (UNICEF/UNIGME): Deaths per 100,000 live births
        
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
            'countries_above_sdg_target': int((mmr_values >= 70).sum()),
            'indicator_definition': 'Maternal Mortality Ratio: Deaths per 100,000 live births (UNICEF/UNIGME)'
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
        data_sorted = data_year.sort_values(by='mmr', ascending=ascending)
        top_n = data_sorted.head(n)[['country_clean', 'iso3', 'mmr', 'year']]
        
        return top_n.reset_index(drop=True)
    
    def get_mmr_over_time(self, country: str) -> pd.DataFrame:
        """Get MMR trend over time for a specific country"""
        country_data = self.maternal_afro[
            self.maternal_afro['country_clean'] == country
        ][['year', 'mmr', 'country_clean']].sort_values('year')
        
        return country_data
    
    def calculate_equity_measures(self, year: Optional[int] = None) -> Dict:
        """Calculate equity measures for MMR distribution"""
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.maternal_afro[
            (self.maternal_afro['year'] == year) & 
            (self.maternal_afro['mmr'].notna())
        ].copy()
        
        values = data_year['mmr'].values
        
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
        """Get regional aggregate trends over time"""
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
            'definition_source': 'UNICEF/UNIGME',
            'sdg_target': 'Less than 70 per 100,000 by 2030'
        }


class ChildMortalityAnalytics:
    """Analytics for Child Mortality - UNICEF/UNIGME definitions"""
    
    def __init__(self, pipeline: MortalityDataPipeline):
        """
        Initialize Child Mortality Analytics
        
        Args:
            pipeline: MortalityDataPipeline instance with loaded data
        """
        self.pipeline = pipeline
        self.child_afro = pipeline.child_afro
        
        # UNICEF/UNIGME Indicator Definitions
        self.indicator_definitions = {
            'Infant mortality rate': 'Deaths per 1,000 live births in the first year of life (UNICEF/UNIGME)',
            'Under-five mortality rate': 'Deaths per 1,000 live births before age 5 (UNICEF/UNIGME)',
            'Child mortality rate (aged 1-4 years)': 'Deaths per 1,000 children aged 1-4 years (UNICEF/UNIGME)',
            'Infant deaths': 'Number of deaths in the first year of life',
            'Under-five deaths': 'Number of deaths before age 5',
            'Child deaths (aged 1-4 years)': 'Number of deaths among children aged 1-4 years'
        }
        
    def get_latest_year(self, indicator: str = 'Under-five mortality rate') -> int:
        """Get the most recent year in the dataset for a specific indicator"""
        indicator_data = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['sex'] == 'Total')
        ]
        return int(indicator_data['year'].max()) if len(indicator_data) > 0 else 2023
    
    def get_mortality_summary(self, year: Optional[int] = None) -> Dict:
        """
        Get summary statistics for Child Mortality in AFRO region
        
        Args:
            year: Specific year (default: latest year)
            
        Returns:
            Dictionary with summary statistics
        """
        # Focus on key rate indicators (not counts)
        key_indicators = [
            'Under-five mortality rate',
            'Infant mortality rate', 
            'Child mortality rate (aged 1-4 years)'
        ]
        
        if year is None:
            year = self.get_latest_year('Under-five mortality rate')
        
        summary = {
            'year': year,
            'total_countries': 0,
            'indicator_definitions': {}
        }
        
        for indicator in key_indicators:
            data_year = self.child_afro[
                (self.child_afro['indicator'] == indicator) &
                (self.child_afro['year'] == year) &
                (self.child_afro['sex'] == 'Total')
            ].copy()
            
            if len(data_year) > 0:
                values = data_year['value'].values
                # Create consistent key names
                indicator_key_map = {
                    'Under-five mortality rate': 'under_five_mortality_rate',
                    'Infant mortality rate': 'infant_mortality_rate',
                    'Child mortality rate (aged 1-4 years)': 'child_mortality_rate_aged_1_4_years'
                }
                indicator_key = indicator_key_map.get(indicator, indicator.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace(',', '').replace(' ', ''))
                
                summary[f'{indicator_key}_median'] = float(np.median(values))
                summary[f'{indicator_key}_mean'] = float(np.mean(values))
                summary[f'{indicator_key}_min'] = float(values.min())
                summary[f'{indicator_key}_max'] = float(values.max())
                summary['total_countries'] = max(summary['total_countries'], len(data_year))
                summary['indicator_definitions'][indicator] = self.indicator_definitions.get(indicator, '')
        
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
            (self.child_afro['sex'] == 'Total')
        ].copy()
        
        # Sort and get top N
        data_sorted = data_year.sort_values(by='value', ascending=ascending)
        top_n = data_sorted.head(n)[['country_clean', 'iso3', 'value', 'year', 'indicator']]
        
        return top_n.reset_index(drop=True)
    
    def get_mortality_over_time(self, country: str, indicator: str = 'Under-five mortality rate') -> pd.DataFrame:
        """Get mortality trend over time for a specific country"""
        country_data = self.child_afro[
            (self.child_afro['country_clean'] == country) &
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['sex'] == 'Total')
        ][['year', 'value', 'indicator', 'country_clean', 'lower_bound', 'upper_bound']].sort_values('year')
        
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
            (self.child_afro['sex'].isin(['Female', 'Male', 'Total']))
        ][['country_clean', 'iso3', 'sex', 'value', 'year']].copy()
        
        # Pivot to have Female, Male, Total as columns
        if len(sex_data) > 0:
            sex_pivot = sex_data.pivot_table(
                index=['country_clean', 'iso3', 'year'],
                columns='sex',
                values='value'
            ).reset_index()
            
            # Calculate sex ratio (Male/Female) and gap
            if 'Male' in sex_pivot.columns and 'Female' in sex_pivot.columns:
                sex_pivot['sex_ratio'] = sex_pivot['Male'] / sex_pivot['Female']
                sex_pivot['sex_gap'] = sex_pivot['Male'] - sex_pivot['Female']
            
            return sex_pivot
        
        return pd.DataFrame()
    
    def calculate_equity_measures(self, indicator: str = 'Under-five mortality rate',
                                  year: Optional[int] = None) -> Dict:
        """Calculate equity measures for mortality distribution"""
        if year is None:
            year = self.get_latest_year(indicator)
        
        data_year = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['year'] == year) &
            (self.child_afro['sex'] == 'Total') &
            (self.child_afro['value'].notna())
        ].copy()
        
        values = data_year['value'].values
        
        # Handle empty data case
        if len(values) == 0:
            return {
                'indicator': indicator,
                'year': year,
                'countries': 0,
                'min_value': None,
                'max_value': None,
                'range': None,
                'ratio_max_to_min': None,
                'percentile_25': None,
                'percentile_50': None,
                'percentile_75': None,
                'interquartile_range': None,
                'coefficient_of_variation': None,
                'definition': self.indicator_definitions.get(indicator, '')
            }
        
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
            'coefficient_of_variation': float((np.std(values) / np.mean(values)) * 100) if np.mean(values) > 0 else None,
            'definition': self.indicator_definitions.get(indicator, '')
        }
        
        return equity
    
    def get_regional_trends(self, indicator: str = 'Under-five mortality rate') -> pd.DataFrame:
        """Get regional aggregate trends over time"""
        regional_data = self.child_afro[
            (self.child_afro['indicator'] == indicator) &
            (self.child_afro['sex'] == 'Total')
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
        if self.child_afro is None or len(self.child_afro) == 0:
            return {
                'total_countries': 0,
                'year_range': (None, None),
                'latest_year': None,
                'total_records': 0,
                'total_indicators': 0,
                'key_indicators': [],
                'sex_categories': [],
                'indicator_definitions': {},
                'definition_source': 'UNICEF/UNIGME'
            }
        
        indicators = self.child_afro['indicator'].unique().tolist()
        
        return {
            'total_countries': self.child_afro['country_clean'].nunique(),
            'year_range': (int(self.child_afro['year'].min()), int(self.child_afro['year'].max())),
            'latest_year': self.get_latest_year('Under-five mortality rate'),
            'total_records': len(self.child_afro),
            'total_indicators': len(indicators),
            'key_indicators': [
                'Under-five mortality rate',
                'Infant mortality rate',
                'Child mortality rate (aged 1-4 years)'
            ],
            'sex_categories': sorted(self.child_afro['sex'].unique().tolist()),
            'indicator_definitions': self.indicator_definitions,
            'definition_source': 'UNICEF/UNIGME'
        }
