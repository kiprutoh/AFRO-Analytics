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
        
        # Ensure data is loaded
        if pipeline.tb_notifications is None:
            try:
                pipeline.load_data()
            except Exception as e:
                raise ValueError(f"Failed to load TB data: {str(e)}")
        
        # Verify data was loaded successfully
        if pipeline.tb_notifications is None:
            raise ValueError("TB notifications data is None after loading. Check data files.")
        
        if pipeline.tb_outcomes is None:
            raise ValueError("TB outcomes data is None after loading. Check data files.")
        
        # Clean the data (focus on notifications and outcomes)
        try:
            self.tb_notifications_df = pipeline.clean_tb_notifications_data()
            self.tb_outcomes_df = pipeline.clean_tb_outcomes_data()
            # Burden data is optional (for reference)
            try:
                self.tb_burden_df = pipeline.clean_tb_burden_data()
            except:
                self.tb_burden_df = pd.DataFrame()
        except Exception as e:
            raise ValueError(f"Failed to clean TB data: {str(e)}")
    
    def get_country_statistics(self, country: str) -> Dict:
        """
        Get comprehensive TB statistics for a specific AFRO country
        Focus on notifications and treatment outcomes
        
        Args:
            country: Country name
        
        Returns:
            Dictionary with TB statistics
        """
        # Get notifications data
        country_notif = self.pipeline.filter_by_country(country, self.tb_notifications_df)
        country_outcomes = self.pipeline.filter_by_country(country, self.tb_outcomes_df)
        
        if len(country_notif) == 0 and len(country_outcomes) == 0:
            return {
                "country": country,
                "error": "No data found for this country in AFRO region"
            }
        
        stats = {
            "country": country,
            "region": "AFRO",
            "indicators": {}
        }
        
        # Get latest year from notifications
        if len(country_notif) > 0:
            latest_year = country_notif['year'].max()
            latest_notif = country_notif[country_notif['year'] == latest_year].iloc[0] if len(country_notif[country_notif['year'] == latest_year]) > 0 else None
            stats["latest_year"] = int(latest_year)
            
            # TB Notifications indicators
            notif_indicators = {
                "TB Notifications (Total New Cases)": "c_newinc",
                "New Smear-Positive Cases": "new_sp",
                "New Smear-Negative Cases": "new_sn",
                "New Extrapulmonary Cases": "new_ep"
            }
            
            for indicator_name, col_name in notif_indicators.items():
                if col_name in country_notif.columns:
                    values = country_notif[col_name].dropna()
                    if len(values) > 0:
                        latest_val = float(latest_notif[col_name]) if latest_notif is not None and pd.notna(latest_notif[col_name]) else None
                        stats["indicators"][indicator_name] = {
                            "latest_value": latest_val,
                            "median_value": float(values.median()),
                            "min_value": float(values.min()),
                            "max_value": float(values.max()),
                            "trend": self._calculate_trend(country_notif, col_name),
                            "data_points": len(values),
                            "year_range": (int(country_notif['year'].min()), int(country_notif['year'].max()))
                        }
        
        # Get outcomes data
        if len(country_outcomes) > 0:
            latest_outcome_year = country_outcomes['year'].max()
            latest_outcome = country_outcomes[country_outcomes['year'] == latest_outcome_year].iloc[0] if len(country_outcomes[country_outcomes['year'] == latest_outcome_year]) > 0 else None
            
            # Treatment outcomes indicators
            outcome_indicators = {
                "Treatment Success Rate - New Cases (%)": "c_new_sp_tsr",
                "Treatment Success Rate (%)": "c_new_tsr",
                "Cured Rate (%)": None,  # Calculated from new_sp_cur / new_sp_coh
                "Treatment Completion Rate (%)": None,  # Calculated from new_sp_cmplt / new_sp_coh
                "Death Rate (%)": None,  # Calculated from new_sp_died / new_sp_coh
                "Failure Rate (%)": None  # Calculated from new_sp_fail / new_sp_coh
            }
            
            for indicator_name, col_name in outcome_indicators.items():
                if col_name and col_name in country_outcomes.columns:
                    values = country_outcomes[col_name].dropna()
                    if len(values) > 0:
                        latest_val = float(latest_outcome[col_name]) if latest_outcome is not None and pd.notna(latest_outcome[col_name]) else None
                        stats["indicators"][indicator_name] = {
                            "latest_value": latest_val,
                            "median_value": float(values.median()),
                            "min_value": float(values.min()),
                            "max_value": float(values.max()),
                            "trend": self._calculate_trend(country_outcomes, col_name),
                            "data_points": len(values),
                            "year_range": (int(country_outcomes['year'].min()), int(country_outcomes['year'].max()))
                        }
                elif col_name is None:
                    # Calculate derived indicators
                    if indicator_name == "Cured Rate (%)" and 'new_sp_cur' in country_outcomes.columns and 'new_sp_coh' in country_outcomes.columns:
                        country_outcomes_copy = country_outcomes.copy()
                        country_outcomes_copy['cured_rate'] = (country_outcomes_copy['new_sp_cur'] / country_outcomes_copy['new_sp_coh']) * 100
                        values = country_outcomes_copy['cured_rate'].dropna()
                        if len(values) > 0:
                            latest_val = float(latest_outcome['cured_rate']) if latest_outcome is not None and pd.notna(latest_outcome.get('cured_rate')) else None
                            stats["indicators"][indicator_name] = {
                                "latest_value": latest_val,
                                "median_value": float(values.median()),
                                "min_value": float(values.min()),
                                "max_value": float(values.max()),
                                "trend": self._calculate_trend(country_outcomes_copy, 'cured_rate'),
                                "data_points": len(values)
                            }
        
        return stats
    
    def get_regional_summary(self) -> Dict:
        """
        Get regional summary statistics for AFRO
        Focus on notifications and treatment outcomes
        
        Returns:
            Dictionary with regional summary
        """
        # Use notifications data for regional summary
        df_notif = self.tb_notifications_df.copy()
        df_outcomes = self.tb_outcomes_df.copy()
        
        if len(df_notif) == 0:
            return {
                "region": "AFRO",
                "total_countries": 0,
                "indicators": {},
                "error": "No notifications data available"
            }
        
        latest_year = df_notif['year'].max()
        latest_notif = df_notif[df_notif['year'] == latest_year]
        latest_outcomes = df_outcomes[df_outcomes['year'] == latest_year] if len(df_outcomes) > 0 else pd.DataFrame()
        
        summary = {
            "region": "AFRO",
            "latest_year": int(latest_year),
            "total_countries": len(df_notif['country'].unique()),
            "indicators": {}
        }
        
        # Notifications indicators
        notif_indicators = {
            "TB Notifications (Total New Cases)": "c_newinc",
            "New Smear-Positive Cases": "new_sp",
            "New Smear-Negative Cases": "new_sn"
        }
        
        for indicator_name, col_name in notif_indicators.items():
            if col_name in latest_notif.columns:
                values = latest_notif[col_name].dropna()
                if len(values) > 0:
                    summary["indicators"][indicator_name] = {
                        "median_value": float(values.median()),
                        "min_value": float(values.min()),
                        "max_value": float(values.max()),
                        "mean_value": float(values.mean())
                    }
        
        # Treatment outcomes indicators
        if len(latest_outcomes) > 0:
            outcome_indicators = {
                "Treatment Success Rate - New Cases (%)": "c_new_sp_tsr",
                "Treatment Success Rate (%)": "c_new_tsr"
            }
            
            for indicator_name, col_name in outcome_indicators.items():
                if col_name in latest_outcomes.columns:
                    values = latest_outcomes[col_name].dropna()
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
        Compare multiple AFRO countries for a specific TB indicator
        Focus on notifications and outcomes
        
        Args:
            countries: List of country names
            indicator: Indicator to compare
        
        Returns:
            Comparison statistics
        """
        # Map indicator names to column names
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
            return {"error": f"Indicator {indicator} not found"}
        
        col_name, data_type = indicator_info
        
        # Select appropriate dataframe
        if data_type == "notifications":
            df = self.tb_notifications_df
        elif data_type == "outcomes":
            df = self.tb_outcomes_df
        else:
            return {"error": f"Unknown data type for indicator {indicator}"}
        
        if len(df) == 0:
            return {"error": f"No {data_type} data available"}
        
        latest_year = df['year'].max()
        
        comparison = {
            "indicator": indicator,
            "countries": {},
            "latest_year": int(latest_year),
            "region": "AFRO"
        }
        
        for country in countries:
            country_data = self.pipeline.filter_by_country(country, df)
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

