"""
TB Data Pipeline for Tuberculosis Analytics
Handles TB data loading, cleaning, and preprocessing
Based on WHO GTB Report 2025 structure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import os
import glob


class TBDataPipeline:
    """Pipeline for loading and processing TB data"""
    
    def __init__(self, data_dir: str = "tuberculosis "):
        """
        Initialize the TB data pipeline
        
        Args:
            data_dir: Directory containing the TB data files
        """
        self.data_dir = data_dir
        self.tb_burden = None
        self.tb_notifications = None
        self.tb_outcomes = None
        self.tb_burden_age_sex = None
        self.tb_mdr_rr = None
        self.tb_data_dictionary = None
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all TB CSV files into DataFrames
        
        Returns:
            Dictionary containing all loaded datasets
        """
        try:
            # Load TB burden estimates (main dataset)
            burden_path = os.path.join(self.data_dir, "tb burden", "TB_burden_countries_2025-09-23.csv")
            if os.path.exists(burden_path):
                self.tb_burden = pd.read_csv(burden_path)
            
            # Load TB notifications
            notif_path = os.path.join(self.data_dir, "case reported by countries", "TB_notifications_2025-09-23.csv")
            if os.path.exists(notif_path):
                self.tb_notifications = pd.read_csv(notif_path)
            
            # Load TB outcomes
            outcomes_path = os.path.join(self.data_dir, "case reported by countries", "TB_outcomes_2025-09-23.csv")
            if os.path.exists(outcomes_path):
                self.tb_outcomes = pd.read_csv(outcomes_path)
            
            # Load TB burden by age and sex
            age_sex_path = os.path.join(self.data_dir, "tb burden", "TB_burden_age_sex_2025-09-23.csv")
            if os.path.exists(age_sex_path):
                self.tb_burden_age_sex = pd.read_csv(age_sex_path)
            
            # Load MDR/RR-TB burden estimates
            mdr_path = os.path.join(self.data_dir, "tb burden", "MDR_RR_TB_burden_estimates_2025-09-23.csv")
            if os.path.exists(mdr_path):
                self.tb_mdr_rr = pd.read_csv(mdr_path)
            
            # Load data dictionary
            dict_path = os.path.join(self.data_dir, "TB_data_dictionary_2025-09-23.csv")
            if os.path.exists(dict_path):
                self.tb_data_dictionary = pd.read_csv(dict_path)
            
            print("✓ TB data files loaded successfully")
            
            return {
                "tb_burden": self.tb_burden,
                "tb_notifications": self.tb_notifications,
                "tb_outcomes": self.tb_outcomes,
                "tb_burden_age_sex": self.tb_burden_age_sex,
                "tb_mdr_rr": self.tb_mdr_rr,
                "tb_data_dictionary": self.tb_data_dictionary
            }
            
        except Exception as e:
            print(f"Error loading TB data: {str(e)}")
            raise
    
    def clean_tb_burden_data(self) -> pd.DataFrame:
        """
        Clean and preprocess TB burden data
        
        Returns:
            Cleaned DataFrame with standardized format
        """
        if self.tb_burden is None:
            raise ValueError("TB burden data not loaded. Call load_data() first.")
        
        df = self.tb_burden.copy()
        
        # Ensure year is numeric
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df.dropna(subset=['year'])
        
        # Standardize country names
        if 'country' in df.columns:
            df['country'] = df['country'].str.strip()
        
        # Filter for African region countries (AFRO)
        if 'g_whoregion' in df.columns:
            df = df[df['g_whoregion'] == 'AFR']
        
        return df
    
    def get_tb_indicators(self) -> List[str]:
        """Get list of key TB indicators"""
        return [
            "TB Incidence (per 100k)",
            "TB Mortality (per 100k)",
            "TB/HIV Incidence (per 100k)",
            "TB/HIV Mortality (per 100k)",
            "Case Detection Rate (%)",
            "MDR/RR-TB Incidence",
            "TB Notifications"
        ]
    
    def get_countries(self) -> List[str]:
        """Get list of all countries in TB dataset"""
        if self.tb_burden is None:
            self.load_data()
        
        if self.tb_burden is None or 'country' not in self.tb_burden.columns:
            return []
        
        countries = sorted(self.tb_burden['country'].unique().tolist())
        return countries
    
    def get_indicator_value(self, country: str, indicator: str, year: Optional[int] = None) -> Optional[float]:
        """
        Get value for a specific indicator, country, and year
        
        Args:
            country: Country name
            indicator: Indicator name
            year: Year (optional, uses latest if not specified)
        
        Returns:
            Indicator value or None
        """
        if self.tb_burden is None:
            self.load_data()
        
        df = self.clean_tb_burden_data()
        country_data = df[df['country'].str.contains(country, case=False, na=False)]
        
        if len(country_data) == 0:
            return None
        
        # Map indicator names to column names
        indicator_map = {
            "TB Incidence (per 100k)": "e_inc_100k",
            "TB Mortality (per 100k)": "e_mort_100k",
            "TB/HIV Incidence (per 100k)": "e_inc_tbhiv_100k",
            "TB/HIV Mortality (per 100k)": "e_mort_tbhiv_100k",
            "Case Detection Rate (%)": "c_cdr"
        }
        
        col_name = indicator_map.get(indicator)
        if col_name not in country_data.columns:
            return None
        
        if year:
            year_data = country_data[country_data['year'] == year]
            if len(year_data) > 0:
                return year_data[col_name].iloc[0]
        else:
            # Get latest year
            latest_year = country_data['year'].max()
            latest_data = country_data[country_data['year'] == latest_year]
            if len(latest_data) > 0:
                return latest_data[col_name].iloc[0]
        
        return None
    
    def filter_by_country(self, country: str, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Filter data by country
        
        Args:
            country: Country name
            df: DataFrame to filter (defaults to tb_burden)
        
        Returns:
            Filtered DataFrame
        """
        if df is None:
            if self.tb_burden is None:
                self.load_data()
            df = self.tb_burden
        
        if df is None or 'country' not in df.columns:
            return pd.DataFrame()
        
        return df[df['country'].str.contains(country, case=False, na=False)]
    
    def filter_by_year_range(self, start_year: int, end_year: int, 
                            df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Filter data by year range
        
        Args:
            start_year: Start year
            end_year: End year
            df: DataFrame to filter
        
        Returns:
            Filtered DataFrame
        """
        if df is None:
            if self.tb_burden is None:
                self.load_data()
            df = self.tb_burden
        
        if df is None or 'year' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
        return df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    
    def get_data_summary(self) -> Dict:
        """
        Get summary statistics of the TB datasets
        
        Returns:
            Dictionary with summary information
        """
        if self.tb_burden is None:
            self.load_data()
        
        summary = {
            "tb_burden_records": len(self.tb_burden) if self.tb_burden is not None else 0,
            "tb_notifications_records": len(self.tb_notifications) if self.tb_notifications is not None else 0,
            "tb_outcomes_records": len(self.tb_outcomes) if self.tb_outcomes is not None else 0,
            "countries": len(self.get_countries()),
            "indicators": len(self.get_tb_indicators()),
            "year_range": (
                int(self.tb_burden['year'].min()) if self.tb_burden is not None and 'year' in self.tb_burden.columns else None,
                int(self.tb_burden['year'].max()) if self.tb_burden is not None and 'year' in self.tb_burden.columns else None
            )
        }
        
        return summary

