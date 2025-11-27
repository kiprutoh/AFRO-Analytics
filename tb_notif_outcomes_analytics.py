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
                 outcomes_file: str = 'TB_outcomes_2025-11-27.csv',
                 lookup_file: str = 'look up file WHO_AFRO_47_Countries_ISO3_Lookup_File.csv'):
        """
        Initialize analytics
        
        Args:
            notifications_file: Path to TB notifications CSV
            outcomes_file: Path to TB outcomes CSV
            lookup_file: Path to AFRO countries lookup CSV
        """
        self.notifications_file = notifications_file
        self.outcomes_file = outcomes_file
        self.lookup_file = lookup_file
        self.notif_data = None
        self.outcomes_data = None
        self.afro_countries = None
        self.notif_afro = None
        self.outcomes_afro = None
        
    def load_data(self):
        """Load and clean TB notifications and outcomes data for AFRO region"""
        print("Loading TB Notifications and Outcomes data...")
        
        # Load notifications data
        self.notif_data = pd.read_csv(self.notifications_file)
        
        # Load outcomes data
        self.outcomes_data = pd.read_csv(self.outcomes_file)
        
        # Load lookup file
        self.afro_countries = pd.read_csv(self.lookup_file)
        
        # Clean and filter for AFRO countries
        self._clean_and_filter_countries()
        self._clean_and_filter_outcomes()
        
        print(f"Loaded notifications for {self.notif_afro['country_clean'].nunique()} AFRO countries")
        print(f"Notifications year range: {self.notif_afro['year'].min()} - {self.notif_afro['year'].max()}")
        print(f"Loaded outcomes for {self.outcomes_afro['country_clean'].nunique()} AFRO countries")
        print(f"Outcomes year range: {self.outcomes_afro['year'].min()} - {self.outcomes_afro['year'].max()}")
        
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
        Get regional TB notifications summary following WHO definitions
        
        NOTE: After 2012, WHO changed case definitions:
        - Smear positive/negative no longer used
        - Use: Lab confirmed, Clinically diagnosed, Extrapulmonary
        
        Args:
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with notification metrics
        """
        if year is None:
            year = self.get_latest_year()
        
        data_year = self.notif_afro[self.notif_afro['year'] == year].copy()
        
        # WHO-defined indicators (post-2012 definitions)
        summary = {
            'year': year,
            'total_countries': len(data_year),
            # Main indicator: Total new and relapse TB cases
            'total_new_relapse': data_year['c_newinc'].sum(),
            # Pulmonary cases (bacteriologically confirmed)
            'pulmonary_lab_confirmed': data_year['new_labconf'].sum() if 'new_labconf' in data_year.columns else 0,
            # Pulmonary cases (clinically diagnosed)
            'pulmonary_clin_diagnosed': data_year['new_clindx'].sum() if 'new_clindx' in data_year.columns else 0,
            # Extrapulmonary TB
            'extrapulmonary': data_year['new_ep'].sum() if 'new_ep' in data_year.columns else 0,
        }
        
        # Calculate ranges for each indicator
        for key in ['total_new_relapse', 'pulmonary_lab_confirmed', 'pulmonary_clin_diagnosed', 'extrapulmonary']:
            if key == 'total_new_relapse':
                col = 'c_newinc'
            elif key == 'pulmonary_lab_confirmed':
                col = 'new_labconf'
            elif key == 'pulmonary_clin_diagnosed':
                col = 'new_clindx'
            else:
                col = 'new_ep'
            
            if col in data_year.columns:
                values = data_year[col].replace([np.inf, -np.inf], np.nan).dropna()
                values = values[values > 0]
                if len(values) > 0:
                    summary[f'{key}_min'] = values.min()
                    summary[f'{key}_max'] = values.max()
                    summary[f'{key}_median'] = values.median()
        
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
        Get notification types breakdown for a country (WHO post-2012 definitions)
        
        NOTE: Smear positive/negative not used after 2012
        
        Args:
            country: Country name
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with notification types (WHO-compliant)
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
    
    def _clean_and_filter_outcomes(self):
        """Clean country names and filter outcomes data for AFRO region"""
        # Merge with lookup to get clean country names
        self.outcomes_afro = self.outcomes_data.merge(
            self.afro_countries[['Country', 'ISO3']], 
            left_on='iso3', 
            right_on='ISO3', 
            how='inner'
        )
        
        self.outcomes_afro['country_clean'] = self.outcomes_afro['Country']
        
        # Ensure numeric types for key outcomes indicators
        numeric_cols = [
            # New and relapse outcomes (WHO 2021+ definitions)
            'newrel_coh', 'newrel_succ', 'newrel_fail', 'newrel_died', 'newrel_lost',
            'c_new_tsr',  # Treatment success rate
            # Retreatment outcomes
            'ret_nrel_coh', 'ret_nrel_succ', 'ret_nrel_fail', 'ret_nrel_died', 'ret_nrel_lost',
            'c_ret_tsr',
            # TB/HIV outcomes
            'tbhiv_coh', 'tbhiv_succ', 'tbhiv_fail', 'tbhiv_died', 'tbhiv_lost',
            'c_tbhiv_tsr',
            # MDR/XDR outcomes
            'mdr_coh', 'mdr_succ', 'mdr_fail', 'mdr_died', 'mdr_lost',
            'xdr_coh', 'xdr_succ', 'xdr_fail', 'xdr_died', 'xdr_lost',
        ]
        
        for col in numeric_cols:
            if col in self.outcomes_afro.columns:
                self.outcomes_afro[col] = pd.to_numeric(self.outcomes_afro[col], errors='coerce').fillna(0)
    
    def get_outcomes_summary(self, year: Optional[int] = None, category: str = 'newrel') -> Dict:
        """
        Get regional TB treatment outcomes summary
        
        WHO Definitions:
        - Success = Cured + Completed
        - Failure = Treatment failed
        - Died = Died during treatment
        - Lost = Lost to follow-up
        
        Args:
            year: Specific year (default: latest)
            category: Outcome category ('newrel', 'ret_nrel', 'tbhiv', 'mdr', 'xdr')
            
        Returns:
            Dictionary with outcomes metrics
        """
        if year is None:
            year = int(self.outcomes_afro['year'].max())
        
        data_year = self.outcomes_afro[self.outcomes_afro['year'] == year].copy()
        
        # Map category to column prefixes
        if category == 'newrel':
            prefix = 'newrel'
            tsr_col = 'c_new_tsr'
            name = 'New and Relapse TB'
        elif category == 'ret_nrel':
            prefix = 'ret_nrel'
            tsr_col = 'c_ret_tsr'
            name = 'Retreatment TB'
        elif category == 'tbhiv':
            prefix = 'tbhiv'
            tsr_col = 'c_tbhiv_tsr'
            name = 'TB/HIV'
        elif category in ['mdr', 'xdr']:
            prefix = category
            tsr_col = None  # No standard TSR for MDR/XDR in this format
            name = category.upper() + ' TB'
        else:
            prefix = 'newrel'
            tsr_col = 'c_new_tsr'
            name = 'New and Relapse TB'
        
        # Calculate summary
        summary = {
            'year': year,
            'category': name,
            'total_countries': len(data_year),
            'cohort': data_year[f'{prefix}_coh'].sum(),
            'success': data_year[f'{prefix}_succ'].sum() if f'{prefix}_succ' in data_year.columns else 0,
            'failed': data_year[f'{prefix}_fail'].sum(),
            'died': data_year[f'{prefix}_died'].sum(),
            'lost': data_year[f'{prefix}_lost'].sum(),
        }
        
        # Calculate percentages
        if summary['cohort'] > 0:
            summary['success_pct'] = (summary['success'] / summary['cohort']) * 100
            summary['failed_pct'] = (summary['failed'] / summary['cohort']) * 100
            summary['died_pct'] = (summary['died'] / summary['cohort']) * 100
            summary['lost_pct'] = (summary['lost'] / summary['cohort']) * 100
        else:
            summary['success_pct'] = 0
            summary['failed_pct'] = 0
            summary['died_pct'] = 0
            summary['lost_pct'] = 0
        
        # Get TSR statistics
        if tsr_col and tsr_col in data_year.columns:
            tsr_values = data_year[tsr_col].replace([np.inf, -np.inf], np.nan).dropna()
            tsr_values = tsr_values[tsr_values > 0]
            if len(tsr_values) > 0:
                summary['tsr_mean'] = tsr_values.mean()
                summary['tsr_median'] = tsr_values.median()
                summary['tsr_min'] = tsr_values.min()
                summary['tsr_max'] = tsr_values.max()
                summary['countries_above_85'] = (tsr_values >= 85).sum()  # WHO target
        
        return summary
    
    def get_top_performing_countries(self, indicator: str = 'c_new_tsr', 
                                     n: int = 10, year: Optional[int] = None,
                                     ascending: bool = False) -> pd.DataFrame:
        """
        Get top N countries by treatment success rate
        
        Args:
            indicator: TSR indicator column
            n: Number of countries
            year: Specific year (default: latest)
            ascending: If True, get lowest; if False, get highest
            
        Returns:
            DataFrame with top countries
        """
        if year is None:
            year = int(self.outcomes_afro['year'].max())
        
        data_year = self.outcomes_afro[self.outcomes_afro['year'] == year].copy()
        
        if indicator not in data_year.columns:
            return pd.DataFrame()
        
        # Filter valid values
        data_valid = data_year[data_year[indicator] > 0].copy()
        
        # Sort and get top N
        data_sorted = data_valid.sort_values(by=indicator, ascending=ascending)
        top_n = data_sorted.head(n)[['country_clean', 'iso3', indicator]]
        
        return top_n.reset_index(drop=True)
    
    def get_outcomes_breakdown(self, country: str, year: Optional[int] = None,
                               category: str = 'newrel') -> Dict:
        """
        Get treatment outcomes breakdown for a specific country
        
        Args:
            country: Country name
            year: Specific year (default: latest)
            category: Outcome category
            
        Returns:
            Dictionary with outcomes breakdown
        """
        if year is None:
            year = int(self.outcomes_afro['year'].max())
        
        data = self.outcomes_afro[
            (self.outcomes_afro['country_clean'] == country) & 
            (self.outcomes_afro['year'] == year)
        ]
        
        if data.empty:
            return {'error': 'No data available'}
        
        row = data.iloc[0]
        
        # Map category
        if category == 'newrel':
            prefix = 'newrel'
            tsr_col = 'c_new_tsr'
        elif category == 'ret_nrel':
            prefix = 'ret_nrel'
            tsr_col = 'c_ret_tsr'
        elif category == 'tbhiv':
            prefix = 'tbhiv'
            tsr_col = 'c_tbhiv_tsr'
        else:
            prefix = category
            tsr_col = None
        
        cohort = row.get(f'{prefix}_coh', 0)
        
        return {
            'country': country,
            'year': year,
            'category': category,
            'cohort': cohort,
            'success': row.get(f'{prefix}_succ', 0),
            'failed': row.get(f'{prefix}_fail', 0),
            'died': row.get(f'{prefix}_died', 0),
            'lost': row.get(f'{prefix}_lost', 0),
            'tsr': row.get(tsr_col, 0) if tsr_col else 0
        }
    
    def get_outcomes_regional_trend(self, indicator: str = 'c_new_tsr') -> pd.DataFrame:
        """
        Get regional treatment success rate trend
        
        Args:
            indicator: TSR indicator
            
        Returns:
            DataFrame with yearly regional values
        """
        if indicator not in self.outcomes_afro.columns:
            return pd.DataFrame()
        
        # Calculate mean TSR per year
        trend = self.outcomes_afro.groupby('year')[indicator].agg(['mean', 'median', 'std']).reset_index()
        trend.columns = ['year', 'mean_tsr', 'median_tsr', 'std_tsr']
        
        # Filter out years with no data
        trend = trend[trend['mean_tsr'] > 0]
        
        return trend
    
    def calculate_outcomes_equity(self, indicator: str = 'c_new_tsr', 
                                  year: Optional[int] = None) -> Dict:
        """
        Calculate equity measures for treatment success rates
        
        Args:
            indicator: TSR indicator
            year: Specific year (default: latest)
            
        Returns:
            Dictionary with equity metrics
        """
        if year is None:
            year = int(self.outcomes_afro['year'].max())
        
        data_year = self.outcomes_afro[self.outcomes_afro['year'] == year].copy()
        
        if indicator not in data_year.columns:
            return {'error': f'Indicator {indicator} not found'}
        
        values = data_year[indicator].replace([np.inf, -np.inf], np.nan).dropna()
        values = values[values > 0]
        
        if values.empty:
            return {'error': 'No valid data'}
        
        min_val = values.min()
        max_val = values.max()
        
        # WHO target is 85%
        who_target = 85
        above_target = (values >= who_target).sum()
        below_target = (values < who_target).sum()
        
        return {
            'min_value': min_val,
            'max_value': max_val,
            'range': max_val - min_val,
            'ratio_max_to_min': max_val / min_val if min_val != 0 else np.inf,
            'coefficient_of_variation': (values.std() / values.mean() * 100) if values.mean() != 0 else np.nan,
            'median': values.median(),
            'mean': values.mean(),
            'who_target': who_target,
            'countries_above_target': above_target,
            'countries_below_target': below_target,
            'percent_above_target': (above_target / len(values)) * 100
        }

