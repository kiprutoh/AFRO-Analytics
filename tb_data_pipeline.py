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
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the TB data pipeline
        
        Args:
            data_dir: Directory containing the TB data files (defaults to "tuberculosis " in project root)
        """
        if data_dir is None:
            # Try multiple possible paths
            possible_paths = [
                "tuberculosis ",
                os.path.join(os.path.dirname(__file__), "tuberculosis "),
                os.path.join(os.getcwd(), "tuberculosis ")
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    data_dir = path
                    break
            else:
                # Default to current directory
                data_dir = "tuberculosis "
        
        self.data_dir = data_dir
        
        # Verify directory exists
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(
                f"TB data directory not found: {os.path.abspath(self.data_dir)}\n"
                f"Current working directory: {os.getcwd()}\n"
                f"Please ensure the 'tuberculosis ' folder exists in the project root."
            )
        
        self.tb_burden = None
        self.tb_notifications = None
        self.tb_outcomes = None
        self.tb_burden_age_sex = None
        self.tb_mdr_rr = None
        self.tb_data_dictionary = None
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load TB notifications and outcomes data for AFRO countries
        
        Returns:
            Dictionary containing all loaded datasets
        """
        try:
            # Load TB notifications - REQUIRED
            notif_path = os.path.join(self.data_dir, "case reported by countries", "TB_notifications_2025-09-23.csv")
            if not os.path.exists(notif_path):
                raise FileNotFoundError(f"TB notifications file not found at: {notif_path}")
            
            self.tb_notifications = pd.read_csv(notif_path)
            if self.tb_notifications is None or len(self.tb_notifications) == 0:
                raise ValueError("TB notifications file is empty or could not be loaded")
            
            # Filter for AFRO countries only
            if 'g_whoregion' in self.tb_notifications.columns:
                self.tb_notifications = self.tb_notifications[self.tb_notifications['g_whoregion'] == 'AFR'].copy()
            
            # Load TB outcomes - REQUIRED
            outcomes_path = os.path.join(self.data_dir, "case reported by countries", "TB_outcomes_2025-09-23.csv")
            if not os.path.exists(outcomes_path):
                raise FileNotFoundError(f"TB outcomes file not found at: {outcomes_path}")
            
            self.tb_outcomes = pd.read_csv(outcomes_path)
            if self.tb_outcomes is None or len(self.tb_outcomes) == 0:
                raise ValueError("TB outcomes file is empty or could not be loaded")
            
            # Filter for AFRO countries only
            if 'g_whoregion' in self.tb_outcomes.columns:
                self.tb_outcomes = self.tb_outcomes[self.tb_outcomes['g_whoregion'] == 'AFR'].copy()
            
            # Load TB burden estimates (for reference, but focus on notifications/outcomes)
            burden_path = os.path.join(self.data_dir, "tb burden", "TB_burden_countries_2025-09-23.csv")
            if os.path.exists(burden_path):
                self.tb_burden = pd.read_csv(burden_path)
                # Filter for AFRO
                if 'g_whoregion' in self.tb_burden.columns:
                    self.tb_burden = self.tb_burden[self.tb_burden['g_whoregion'] == 'AFR'].copy()
            
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
    
    def clean_tb_notifications_data(self) -> pd.DataFrame:
        """
        Clean and preprocess TB notifications data (AFRO only)
        
        Returns:
            Cleaned DataFrame with standardized format
        """
        if self.tb_notifications is None:
            raise ValueError("TB notifications data not loaded. Call load_data() first.")
        
        df = self.tb_notifications.copy()
        
        # Ensure year is numeric
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df.dropna(subset=['year'])
        
        # Standardize country names
        if 'country' in df.columns:
            df['country'] = df['country'].str.strip()
        
        # Ensure AFRO filter (should already be filtered, but double-check)
        if 'g_whoregion' in df.columns:
            df = df[df['g_whoregion'] == 'AFR']
        
        return df
    
    def clean_tb_outcomes_data(self) -> pd.DataFrame:
        """
        Clean and preprocess TB outcomes data (AFRO only)
        
        Returns:
            Cleaned DataFrame with standardized format
        """
        if self.tb_outcomes is None:
            raise ValueError("TB outcomes data not loaded. Call load_data() first.")
        
        df = self.tb_outcomes.copy()
        
        # Ensure year is numeric
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df.dropna(subset=['year'])
        
        # Standardize country names
        if 'country' in df.columns:
            df['country'] = df['country'].str.strip()
        
        # Ensure AFRO filter (should already be filtered, but double-check)
        if 'g_whoregion' in df.columns:
            df = df[df['g_whoregion'] == 'AFR']
        
        return df
    
    def clean_tb_burden_data(self) -> pd.DataFrame:
        """
        Clean and preprocess TB burden data (for reference, AFRO only)
        
        Returns:
            Cleaned DataFrame with standardized format
        """
        if self.tb_burden is None:
            # Return empty DataFrame if burden data not available
            return pd.DataFrame()
        
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
        """Get list of key TB indicators (focusing on notifications and outcomes)"""
        return [
            "TB Notifications (Total New Cases)",
            "New Smear-Positive Cases",
            "New Smear-Negative Cases",
            "New Extrapulmonary Cases",
            "Treatment Success Rate (%)",
            "Treatment Success Rate - New Cases (%)",
            "Cured Rate (%)",
            "Treatment Completion Rate (%)",
            "Death Rate (%)",
            "Failure Rate (%)"
        ]
    
    def get_countries(self) -> List[str]:
        """Get list of all AFRO countries in TB dataset"""
        if self.tb_notifications is None:
            self.load_data()
        
        # Get countries from notifications (primary source)
        countries_set = set()
        if self.tb_notifications is not None and 'country' in self.tb_notifications.columns:
            countries_set.update(self.tb_notifications['country'].unique())
        
        # Also get from outcomes
        if self.tb_outcomes is not None and 'country' in self.tb_outcomes.columns:
            countries_set.update(self.tb_outcomes['country'].unique())
        
        countries = sorted(list(countries_set))
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
        Filter data by country (AFRO countries only)
        
        Args:
            country: Country name
            df: DataFrame to filter (defaults to tb_notifications)
        
        Returns:
            Filtered DataFrame
        """
        if df is None:
            if self.tb_notifications is None:
                self.load_data()
            df = self.tb_notifications
        
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
            df: DataFrame to filter (defaults to tb_notifications)
        
        Returns:
            Filtered DataFrame
        """
        if df is None:
            if self.tb_notifications is None:
                self.load_data()
            df = self.tb_notifications
        
        if df is None or 'year' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
        return df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    
    def get_data_summary(self) -> Dict:
        """
        Get summary statistics of the TB datasets (notifications and outcomes, AFRO only)
        
        Returns:
            Dictionary with summary information
        """
        if self.tb_notifications is None:
            self.load_data()
        
        # Get year range from notifications
        notif_year_range = (None, None)
        if self.tb_notifications is not None and 'year' in self.tb_notifications.columns:
            notif_years = pd.to_numeric(self.tb_notifications['year'], errors='coerce').dropna()
            if len(notif_years) > 0:
                notif_year_range = (int(notif_years.min()), int(notif_years.max()))
        
        summary = {
            "tb_notifications_records": len(self.tb_notifications) if self.tb_notifications is not None else 0,
            "tb_outcomes_records": len(self.tb_outcomes) if self.tb_outcomes is not None else 0,
            "tb_burden_records": len(self.tb_burden) if self.tb_burden is not None else 0,
            "countries": len(self.get_countries()),
            "indicators": len(self.get_tb_indicators()),
            "year_range": notif_year_range,
            "region": "AFRO"
        }
        
        return summary

