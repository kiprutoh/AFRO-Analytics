"""
TB Analytics Module for Tuberculosis Data Analysis
Provides analytical functions for TB data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from tb_data_pipeline import TBDataPipeline
from datetime import datetime


class TBAnalytics:
    """Analytics engine for TB data"""
    
    def __init__(self, pipeline: TBDataPipeline):
        """
        Initialize TB analytics with data pipeline
        
        Args:
            pipeline: TBDataPipeline instance
        """
        self.pipeline = pipeline
        if pipeline.tb_burden is None:
            pipeline.load_data()
        
        self.tb_burden_df = pipeline.clean_tb_burden_data()
    
    def get_country_statistics(self, country: str) -> Dict:
        """
        Get comprehensive TB statistics for a specific country
        
        Args:
            country: Country name
        
        Returns:
            Dictionary with TB statistics
        """
        country_data = self.pipeline.filter_by_country(country, self.tb_burden_df)
        
        if len(country_data) == 0:
            return {
                "country": country,
                "error": "No data found for this country"
            }
        
        # Get latest year data
        latest_year = country_data['year'].max()
        latest_data = country_data[country_data['year'] == latest_year].iloc[0]
        
        stats = {
            "country": country,
            "latest_year": int(latest_year),
            "indicators": {}
        }
        
        # Key TB indicators
        indicators = {
            "TB Incidence (per 100k)": "e_inc_100k",
            "TB Mortality (per 100k)": "e_mort_100k",
            "TB/HIV Incidence (per 100k)": "e_inc_tbhiv_100k",
            "TB/HIV Mortality (per 100k)": "e_mort_tbhiv_100k",
            "Case Detection Rate (%)": "c_cdr"
        }
        
        for indicator_name, col_name in indicators.items():
            if col_name in country_data.columns:
                values = country_data[col_name].dropna()
                if len(values) > 0:
                    stats["indicators"][indicator_name] = {
                        "latest_value": float(latest_data[col_name]) if pd.notna(latest_data[col_name]) else None,
                        "median_value": float(values.median()),
                        "min_value": float(values.min()),
                        "max_value": float(values.max()),
                        "trend": self._calculate_trend(country_data, col_name),
                        "data_points": len(values),
                        "year_range": (int(country_data['year'].min()), int(country_data['year'].max()))
                    }
        
        return stats
    
    def get_regional_summary(self) -> Dict:
        """
        Get regional summary statistics for AFRO
        
        Returns:
            Dictionary with regional summary
        """
        df = self.tb_burden_df.copy()
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        
        summary = {
            "region": "AFRO",
            "latest_year": int(latest_year),
            "total_countries": len(df['country'].unique()),
            "indicators": {}
        }
        
        indicators = {
            "TB Incidence (per 100k)": "e_inc_100k",
            "TB Mortality (per 100k)": "e_mort_100k",
            "TB/HIV Incidence (per 100k)": "e_inc_tbhiv_100k",
            "Case Detection Rate (%)": "c_cdr"
        }
        
        for indicator_name, col_name in indicators.items():
            if col_name in latest_data.columns:
                values = latest_data[col_name].dropna()
                if len(values) > 0:
                    summary["indicators"][indicator_name] = {
                        "median_value": float(values.median()),
                        "min_value": float(values.min()),
                        "max_value": float(values.max()),
                        "mean_value": float(values.mean())
                    }
        
        return summary
    
    def _calculate_trend(self, df: pd.DataFrame, column: str) -> str:
        """
        Calculate trend direction for a column
        
        Args:
            df: DataFrame with time series data
            column: Column name to analyze
        
        Returns:
            Trend description (increasing, decreasing, stable)
        """
        if column not in df.columns:
            return "No data"
        
        df_sorted = df.sort_values('year')
        values = df_sorted[column].dropna()
        
        if len(values) < 2:
            return "Insufficient data"
        
        # Simple linear trend
        recent_values = values.tail(5)  # Last 5 years
        if len(recent_values) < 2:
            recent_values = values
        
        first_val = recent_values.iloc[0]
        last_val = recent_values.iloc[-1]
        
        if pd.isna(first_val) or pd.isna(last_val):
            return "Insufficient data"
        
        change_pct = ((last_val - first_val) / first_val) * 100
        
        if change_pct > 5:
            return "Increasing"
        elif change_pct < -5:
            return "Decreasing"
        else:
            return "Stable"
    
    def compare_countries(self, countries: List[str], indicator: str) -> Dict:
        """
        Compare multiple countries for a specific TB indicator
        
        Args:
            countries: List of country names
            indicator: Indicator to compare
        
        Returns:
            Comparison statistics
        """
        indicator_map = {
            "TB Incidence (per 100k)": "e_inc_100k",
            "TB Mortality (per 100k)": "e_mort_100k",
            "TB/HIV Incidence (per 100k)": "e_inc_tbhiv_100k",
            "Case Detection Rate (%)": "c_cdr"
        }
        
        col_name = indicator_map.get(indicator)
        if not col_name:
            return {"error": f"Indicator {indicator} not found"}
        
        comparison = {
            "indicator": indicator,
            "countries": {},
            "latest_year": int(self.tb_burden_df['year'].max())
        }
        
        latest_year = self.tb_burden_df['year'].max()
        
        for country in countries:
            country_data = self.pipeline.filter_by_country(country, self.tb_burden_df)
            if len(country_data) > 0 and col_name in country_data.columns:
                latest_data = country_data[country_data['year'] == latest_year]
                if len(latest_data) > 0:
                    value = latest_data[col_name].iloc[0]
                    if pd.notna(value):
                        comparison["countries"][country] = {
                            "value": float(value),
                            "rank": None  # Will be calculated after all countries
                        }
        
        # Calculate ranks
        sorted_countries = sorted(
            comparison["countries"].items(),
            key=lambda x: x[1]["value"],
            reverse=True
        )
        
        for rank, (country, data) in enumerate(sorted_countries, 1):
            comparison["countries"][country]["rank"] = rank
        
        return comparison

