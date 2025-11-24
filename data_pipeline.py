"""
Data Pipeline for Mortality Analytics
Handles data loading, cleaning, and preprocessing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import os


class MortalityDataPipeline:
    """Pipeline for loading and processing mortality data"""
    
    def __init__(self, data_dir: str = "."):
        """
        Initialize the data pipeline
        
        Args:
            data_dir: Directory containing the CSV files
        """
        self.data_dir = data_dir
        self.mortality_data = None
        self.mmr_data = None
        self.mortality_projections = None
        self.mmr_projections = None
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV files into DataFrames
        
        Returns:
            Dictionary containing all loaded datasets
        """
        try:
            # Load mortality data
            mortality_path = os.path.join(self.data_dir, "mortality_clean_afro.csv")
            self.mortality_data = pd.read_csv(mortality_path)
            
            # Load MMR data
            mmr_path = os.path.join(self.data_dir, "mmr_clean_afro.csv")
            self.mmr_data = pd.read_csv(mmr_path)
            
            # Load mortality projections
            mortality_proj_path = os.path.join(self.data_dir, "mortality_projections_afro.csv")
            self.mortality_projections = pd.read_csv(mortality_proj_path)
            
            # Load MMR projections
            mmr_proj_path = os.path.join(self.data_dir, "mmr_projections_afro.csv")
            self.mmr_projections = pd.read_csv(mmr_proj_path)
            
            print("✓ All data files loaded successfully")
            
            return {
                "mortality": self.mortality_data,
                "mmr": self.mmr_data,
                "mortality_projections": self.mortality_projections,
                "mmr_projections": self.mmr_projections
            }
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise
    
    def clean_mortality_data(self) -> pd.DataFrame:
        """
        Clean and preprocess mortality data
        
        Returns:
            Cleaned DataFrame
        """
        if self.mortality_data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        df = self.mortality_data.copy()
        
        # Convert year to numeric, handling ranges like "2015-2016"
        def parse_year(year_str):
            if pd.isna(year_str):
                return None
            year_str = str(year_str)
            if '-' in year_str:
                # Take the first year in range
                return int(year_str.split('-')[0])
            try:
                return int(float(year_str))
            except:
                return None
        
        df['year'] = df['year'].apply(parse_year)
        df = df.dropna(subset=['year', 'value'])
        
        # Ensure value is numeric
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
        
        # Standardize country names
        df['country'] = df['country'].str.strip()
        
        return df
    
    def clean_mmr_data(self) -> pd.DataFrame:
        """
        Clean and preprocess MMR data
        
        Returns:
            Cleaned DataFrame
        """
        if self.mmr_data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        df = self.mmr_data.copy()
        
        # Standardize column names
        df = df.rename(columns={'ISO Code': 'iso'})
        
        # Ensure value is numeric
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value', 'year'])
        
        # Standardize country names
        df['country'] = df['country'].str.strip()
        
        return df
    
    def get_countries(self) -> List[str]:
        """Get list of all countries in the dataset"""
        if self.mortality_data is None:
            self.load_data()
        
        mortality_countries = set(self.mortality_data['country'].unique())
        mmr_countries = set(self.mmr_data['country'].unique())
        all_countries = sorted(list(mortality_countries.union(mmr_countries)))
        
        return all_countries
    
    def get_indicators(self) -> List[str]:
        """Get list of all mortality indicators"""
        if self.mortality_data is None:
            self.load_data()
        
        indicators = sorted(self.mortality_data['indicator'].unique().tolist())
        return indicators
    
    def get_data_summary(self) -> Dict:
        """
        Get summary statistics of the datasets
        
        Returns:
            Dictionary with summary information
        """
        if self.mortality_data is None:
            self.load_data()
        
        summary = {
            "mortality_records": len(self.mortality_data),
            "mmr_records": len(self.mmr_data),
            "mortality_projections": len(self.mortality_projections),
            "mmr_projections": len(self.mmr_projections),
            "countries": len(self.get_countries()),
            "indicators": len(self.get_indicators()),
            "year_range_mortality": (
                self.mortality_data['year'].min() if 'year' in self.mortality_data.columns 
                else None,
                self.mortality_data['year'].max() if 'year' in self.mortality_data.columns 
                else None
            ),
            "year_range_mmr": (
                self.mmr_data['year'].min(),
                self.mmr_data['year'].max()
            )
        }
        
        return summary
    
    def filter_by_country(self, country: str, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Filter data by country
        
        Args:
            country: Country name
            df: DataFrame to filter (defaults to mortality_data)
        
        Returns:
            Filtered DataFrame
        """
        if df is None:
            if self.mortality_data is None:
                self.load_data()
            df = self.mortality_data
        
        return df[df['country'].str.contains(country, case=False, na=False)]
    
    def filter_by_indicator(self, indicator: str, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Filter data by indicator
        
        Args:
            indicator: Indicator name
            df: DataFrame to filter (defaults to mortality_data)
        
        Returns:
            Filtered DataFrame
        """
        if df is None:
            if self.mortality_data is None:
                self.load_data()
            df = self.mortality_data
        
        return df[df['indicator'].str.contains(indicator, case=False, na=False)]
    
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
            if self.mortality_data is None:
                self.load_data()
            df = self.mortality_data
        
        if 'year' not in df.columns:
            return df
        
        # Clean year column if needed
        df = df.copy()
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
        return df[(df['year'] >= start_year) & (df['year'] <= end_year)]


