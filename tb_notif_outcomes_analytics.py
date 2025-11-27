"""
TB Notifications and Outcomes Analytics
Analyzes TB case notifications, notification types, age distributions, and treatment outcomes
Following WHO-defined indicators and TB Burden framework
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List


class TBNotificationsOutcomesAnalytics:
    """Analyze TB notifications and treatment outcomes for AFRO region"""
    
    def __init__(self, notifications_file: str = 'TB_notifications_2025-11-27.csv',
                 lookup_file: str = 'look up file WHO_AFRO_47_Countries_ISO3_Lookup_File.csv'):
        """
        Initialize analytics
        
        Args:
            notifications_file: Path to TB notifications CSV
            lookup_file: Path to AFRO countries lookup CSV
        """
        self.notifications_file = notifications_file
        self.lookup_file = lookup_file
        self.notif_data = None
        self.afro_countries = None
        self.notif_afro = None
        
    def load_data(self):
        """Load and clean TB notifications data for AFRO region"""
        print("Loading TB Notifications data...")
        
        # Load notifications data
        self.notif_data = pd.read_csv(self.notifications_file)
        
        # Load lookup file
        self.afro_countries = pd.read_csv(self.lookup_file)
        
        # Clean and filter for AFRO countries
        self._clean_and_filter_countries()
        
        print(f"Loaded data for {self.notif_afro['country_clean'].nunique()} AFRO countries")
        print(f"Year range: {self.notif_afro['year'].min()} - {self.notif_afro['year'].max()}")
        
    def _clean_and_filter_countries(self):
        """Clean country names and filter for AFRO region"""
        # Merge with lookup to get clean country names
        self.notif_afro = self.notif_data.merge(
            self.afro_countries[['Country', 'ISO3']], 
            left_on='iso3', 
            right_on='ISO3', 
            how='inner'  # Inner join keeps only AFRO countries
        )
        
        self.notif_afro['country_clean'] = self.notif_afro['Country']
        
        # Ensure numeric types for key indicators
        numeric_cols = [
            'c_newinc',  # Total new and relapse cases
            'new_sp', 'new_sn', 'new_su', 'new_ep', 'new_oth',  # By type
            'new_labconf', 'new_clindx',  # By diagnosis method
            # Age groups (example - males 0-14, 15-24, etc.)
            'newrel_m014', 'newrel_m1524', 'newrel_m2534', 'newrel_m3544', 
            'newrel_m4554', 'newrel_m5564', 'newrel_m65',
            # Age groups females
            'newrel_f014', 'newrel_f1524', 'newrel_f2534', 'newrel_f3544',
            'newrel_f4554', 'newrel_f5564', 'newrel_f65',
        ]
        
        for col in numeric_cols:
            if col in self.notif_afro.columns:
                self.notif_afro[col] = pd.to_numeric(self.notif_afro[col], errors='coerce').fillna(0)
    
    def get_latest_year(self) -> int:
        """Get the most recent year in dataset"""
        return int(self.notif_afro['year'].max())
    
    def get_data_summary(self) -> Dict:
        """Get overall data summary"""
        latest_year = self.get_latest_year()
        
        return {
            'total_countries': self.notif_afro['country_clean'].nunique(),
            'year_range': (int(self.notif_afro['year'].min()), latest_year),
            'latest_year': latest_year,
            'total_records': len(self.notif_afro)
        }
    
    def get_notifications_summary(self, year: Optional[int] = None) -> Dict:
        """
        Get regional TB notifications summary
        
        Args:
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with notification metrics
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.notif_afro[self.notif_afro['year'] == year].copy()
        
        # WHO-defined indicators
        summary = {
            'year': year,
            'total_countries': len(data_year),
            'total_new_relapse': data_year['c_newinc'].sum(),  # Main indicator
            'pulmonary_lab_confirmed': data_year['new_labconf'].sum() if 'new_labconf' in data_year.columns else 0,
            'pulmonary_clin_diagnosed': data_year['new_clindx'].sum() if 'new_clindx' in data_year.columns else 0,
            'extrapulmonary': data_year['new_ep'].sum() if 'new_ep' in data_year.columns else 0,
        }
        
        # Notification by type (if available)
        if 'new_sp' in data_year.columns:
            summary['smear_positive'] = data_year['new_sp'].sum()
        if 'new_sn' in data_year.columns:
            summary['smear_negative'] = data_year['new_sn'].sum()
        
        return summary
    
    def get_top_notifying_countries(self, indicator: str = 'c_newinc', 
                                   n: int = 10, year: Optional[int] = None,
                                   ascending: bool = False) -> pd.DataFrame:
        """
        Get top N countries by notification indicator
        
        Args:
            indicator: Notification indicator column
            n: Number of countries
            year: Specific year (default: latest)
            ascending: If True, get lowest; if False, get highest
            
        Returns:
            DataFrame with top countries
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.notif_afro[self.notif_afro['year'] == year].copy()
        
        if indicator not in data_year.columns:
            return pd.DataFrame()
        
        # Sort and get top N
        data_sorted = data_year.sort_values(by=indicator, ascending=ascending)
        top_n = data_sorted.head(n)[['country_clean', 'iso3', indicator]]
        
        return top_n.reset_index(drop=True)
    
    def get_age_distribution(self, year: Optional[int] = None) -> pd.DataFrame:
        """
        Get age group distribution of TB cases
        
        Args:
            year: Specific year (default: latest)
            
        Returns:
            DataFrame with age distribution
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.notif_afro[self.notif_afro['year'] == year].copy()
        
        # Age groups - WHO standard
        age_groups = {
            '0-14': ['newrel_m014', 'newrel_f014'],
            '15-24': ['newrel_m1524', 'newrel_f1524'],
            '25-34': ['newrel_m2534', 'newrel_f2534'],
            '35-44': ['newrel_m3544', 'newrel_f3544'],
            '45-54': ['newrel_m4554', 'newrel_f4554'],
            '55-64': ['newrel_m5564', 'newrel_f5564'],
            '65+': ['newrel_m65', 'newrel_f65'],
        }
        
        age_dist = []
        for age_group, cols in age_groups.items():
            male_col, female_col = cols
            male_cases = data_year[male_col].sum() if male_col in data_year.columns else 0
            female_cases = data_year[female_col].sum() if female_col in data_year.columns else 0
            total_cases = male_cases + female_cases
            
            age_dist.append({
                'age_group': age_group,
                'male': male_cases,
                'female': female_cases,
                'total': total_cases,
                'percent': 0  # Will calculate after
            })
        
        df = pd.DataFrame(age_dist)
        
        # Calculate percentages
        total_all = df['total'].sum()
        if total_all > 0:
            df['percent'] = (df['total'] / total_all * 100).round(1)
        
        return df
    
    def get_notification_types_breakdown(self, country: str, year: Optional[int] = None) -> Dict:
        """
        Get notification types breakdown for a country
        
        Args:
            country: Country name
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with notification types
        """
        if year is None:
            year = self.get_latest_year()
        
        data = self.notif_afro[
            (self.notif_afro['country_clean'] == country) & 
            (self.notif_afro['year'] == year)
        ]
        
        if data.empty:
            return {'error': 'No data available'}
        
        row = data.iloc[0]
        
        return {
            'country': country,
            'year': year,
            'total_new_relapse': row['c_newinc'],
            'pulmonary_lab_confirmed': row['new_labconf'] if 'new_labconf' in row else 0,
            'pulmonary_clin_diagnosed': row['new_clindx'] if 'new_clindx' in row else 0,
            'extrapulmonary': row['new_ep'] if 'new_ep' in row else 0,
            'smear_positive': row['new_sp'] if 'new_sp' in row else 0,
            'smear_negative': row['new_sn'] if 'new_sn' in row else 0,
        }
    
    def get_regional_trend(self, indicator: str = 'c_newinc') -> pd.DataFrame:
        """
        Get regional aggregate trend
        
        Args:
            indicator: Notification indicator
            
        Returns:
            DataFrame with yearly regional totals
        """
        if indicator not in self.notif_afro.columns:
            return pd.DataFrame()
        
        trend = self.notif_afro.groupby('year')[indicator].sum().reset_index()
        trend.columns = ['year', 'regional_total']
        
        return trend
    
    def calculate_equity_measures(self, indicator: str = 'c_newinc', 
                                  year: Optional[int] = None) -> Dict:
        """
        Calculate equity measures for notifications
        
        Args:
            indicator: Notification indicator
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with equity metrics
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.notif_afro[self.notif_afro['year'] == year].copy()
        
        if indicator not in data_year.columns:
            return {'error': f'Indicator {indicator} not found'}
        
        values = data_year[indicator].replace([np.inf, -np.inf], np.nan).dropna()
        values = values[values > 0]  # Only positive values
        
        if values.empty:
            return {'error': 'No valid data'}
        
        min_val = values.min()
        max_val = values.max()
        
        return {
            'min_value': min_val,
            'max_value': max_val,
            'range': max_val - min_val,
            'ratio_max_to_min': max_val / min_val if min_val != 0 else np.inf,
            'coefficient_of_variation': (values.std() / values.mean() * 100) if values.mean() != 0 else np.nan,
            'median': values.median(),
            'mean': values.mean()
        }
    
    def get_country_list(self) -> List[str]:
        """Get list of AFRO countries in dataset"""
        return sorted(self.notif_afro['country_clean'].unique().tolist())


# Treatment Outcomes indicators would be added when treatment outcomes data structure is identified
# The framework is ready to extend with outcomes-specific methods

