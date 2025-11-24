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
        Based on key indicators from TB Report 2024
        
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
        
        # Calculate regional totals
        total_notifications = latest_notif['c_newinc'].sum() if 'c_newinc' in latest_notif.columns else 0
        total_smear_positive = latest_notif['new_sp'].sum() if 'new_sp' in latest_notif.columns else 0
        total_smear_negative = latest_notif['new_sn'].sum() if 'new_sn' in latest_notif.columns else 0
        total_extrapulmonary = latest_notif['new_ep'].sum() if 'new_ep' in latest_notif.columns else 0
        
        summary = {
            "region": "AFRO",
            "latest_year": int(latest_year),
            "total_countries": len(df_notif['country'].unique()),
            "regional_totals": {
                "total_notifications": float(total_notifications),
                "total_smear_positive": float(total_smear_positive),
                "total_smear_negative": float(total_smear_negative),
                "total_extrapulmonary": float(total_extrapulmonary)
            },
            "indicators": {}
        }
        
        # Key indicators from TB Report 2024 - Notifications
        notif_indicators = {
            "TB Notifications (Total New Cases)": "c_newinc",
            "New Smear-Positive Cases": "new_sp",
            "New Smear-Negative Cases": "new_sn",
            "New Extrapulmonary Cases": "new_ep",
            "New and Relapse Cases": "newrel"
        }
        
        for indicator_name, col_name in notif_indicators.items():
            if col_name in latest_notif.columns:
                values = latest_notif[col_name].dropna()
                if len(values) > 0:
                    summary["indicators"][indicator_name] = {
                        "median_value": float(values.median()),
                        "min_value": float(values.min()),
                        "max_value": float(values.max()),
                        "mean_value": float(values.mean()),
                        "total_regional": float(values.sum()),
                        "countries_with_data": int(values.count())
                    }
        
        # Treatment outcomes indicators - Show percentages only (not totals)
        if len(latest_outcomes) > 0:
            # Direct percentage indicators (already computed)
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
                            "mean_value": float(values.mean()),
                            "countries_with_data": int(values.count())
                        }
            
            # Calculate percentage rates from cohort data
            if 'new_sp_coh' in latest_outcomes.columns:
                # Cured Rate (%)
                if 'new_sp_cur' in latest_outcomes.columns:
                    latest_outcomes_copy = latest_outcomes.copy()
                    latest_outcomes_copy['cured_rate'] = (latest_outcomes_copy['new_sp_cur'] / latest_outcomes_copy['new_sp_coh']) * 100
                    values = latest_outcomes_copy['cured_rate'].dropna()
                    if len(values) > 0:
                        summary["indicators"]["Cured Rate (%)"] = {
                            "median_value": float(values.median()),
                            "min_value": float(values.min()),
                            "max_value": float(values.max()),
                            "mean_value": float(values.mean()),
                            "countries_with_data": int(values.count())
                        }
                
                # Treatment Completion Rate (%)
                if 'new_sp_cmplt' in latest_outcomes.columns:
                    latest_outcomes_copy = latest_outcomes.copy()
                    latest_outcomes_copy['completion_rate'] = (latest_outcomes_copy['new_sp_cmplt'] / latest_outcomes_copy['new_sp_coh']) * 100
                    values = latest_outcomes_copy['completion_rate'].dropna()
                    if len(values) > 0:
                        summary["indicators"]["Treatment Completion Rate (%)"] = {
                            "median_value": float(values.median()),
                            "min_value": float(values.min()),
                            "max_value": float(values.max()),
                            "mean_value": float(values.mean()),
                            "countries_with_data": int(values.count())
                        }
                
                # Death Rate (%)
                if 'new_sp_died' in latest_outcomes.columns:
                    latest_outcomes_copy = latest_outcomes.copy()
                    latest_outcomes_copy['death_rate'] = (latest_outcomes_copy['new_sp_died'] / latest_outcomes_copy['new_sp_coh']) * 100
                    values = latest_outcomes_copy['death_rate'].dropna()
                    if len(values) > 0:
                        summary["indicators"]["Death Rate (%)"] = {
                            "median_value": float(values.median()),
                            "min_value": float(values.min()),
                            "max_value": float(values.max()),
                            "mean_value": float(values.mean()),
                            "countries_with_data": int(values.count())
                        }
                
                # Failure Rate (%)
                if 'new_sp_fail' in latest_outcomes.columns:
                    latest_outcomes_copy = latest_outcomes.copy()
                    latest_outcomes_copy['failure_rate'] = (latest_outcomes_copy['new_sp_fail'] / latest_outcomes_copy['new_sp_coh']) * 100
                    values = latest_outcomes_copy['failure_rate'].dropna()
                    if len(values) > 0:
                        summary["indicators"]["Failure Rate (%)"] = {
                            "median_value": float(values.median()),
                            "min_value": float(values.min()),
                            "max_value": float(values.max()),
                            "mean_value": float(values.mean()),
                            "countries_with_data": int(values.count())
                        }
        
        return summary
    
    def get_trend_analysis(self, indicator: str, start_year: Optional[int] = None, end_year: Optional[int] = None) -> Dict:
        """
        Get trend analysis for a specific indicator across AFRO region
        
        Args:
            indicator: Indicator name
            start_year: Start year (optional)
            end_year: End year (optional)
        
        Returns:
            Dictionary with trend analysis
        """
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
            df = self.tb_notifications_df.copy()
        elif data_type == "outcomes":
            df = self.tb_outcomes_df.copy()
        else:
            return {"error": f"Unknown data type for indicator {indicator}"}
        
        # Filter by year range if provided
        if start_year:
            df = df[df['year'] >= start_year]
        if end_year:
            df = df[df['year'] <= end_year]
        
        if col_name not in df.columns:
            return {"error": f"Column {col_name} not found in {data_type} data"}
        
        # Calculate regional totals by year
        yearly_totals = df.groupby('year')[col_name].sum().reset_index()
        yearly_totals.columns = ['year', 'total_value']
        
        # Calculate regional averages by year
        yearly_averages = df.groupby('year')[col_name].mean().reset_index()
        yearly_averages.columns = ['year', 'average_value']
        
        # Calculate percentage change
        if len(yearly_totals) >= 2:
            first_value = yearly_totals['total_value'].iloc[0]
            last_value = yearly_totals['total_value'].iloc[-1]
            if first_value > 0:
                pct_change = ((last_value - first_value) / first_value) * 100
            else:
                pct_change = 0
        else:
            pct_change = 0
        
        return {
            "indicator": indicator,
            "yearly_totals": yearly_totals.to_dict('records'),
            "yearly_averages": yearly_averages.to_dict('records'),
            "percentage_change": float(pct_change),
            "trend": "Increasing" if pct_change > 0 else "Decreasing" if pct_change < 0 else "Stable",
            "start_year": int(yearly_totals['year'].min()) if len(yearly_totals) > 0 else None,
            "end_year": int(yearly_totals['year'].max()) if len(yearly_totals) > 0 else None
        }
    
    def get_top_countries(self, indicator: str, n: int = 10, ascending: bool = False) -> Dict:
        """
        Get top N countries for a specific indicator
        
        Args:
            indicator: Indicator name
            n: Number of countries to return
            ascending: If True, return bottom N countries
        
        Returns:
            Dictionary with top countries
        """
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
            df = self.tb_notifications_df.copy()
        elif data_type == "outcomes":
            df = self.tb_outcomes_df.copy()
        else:
            return {"error": f"Unknown data type for indicator {indicator}"}
        
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        
        if col_name not in latest_data.columns:
            return {"error": f"Column {col_name} not found"}
        
        # Get top countries
        top_countries = latest_data.nlargest(n, col_name) if not ascending else latest_data.nsmallest(n, col_name)
        
        result = {
            "indicator": indicator,
            "year": int(latest_year),
            "countries": []
        }
        
        for idx, row in top_countries.iterrows():
            if pd.notna(row[col_name]):
                result["countries"].append({
                    "country": row['country'],
                    "value": float(row[col_name]),
                    "rank": len(result["countries"]) + 1
                })
        
        return result
    
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
    
    def get_regional_outlook(self) -> Dict:
        """
        Generate comprehensive regional outlook for AFRO
        Based on TB Report 2024 structure
        
        Returns:
            Dictionary with regional outlook analysis
        """
        df_notif = self.tb_notifications_df.copy()
        df_outcomes = self.tb_outcomes_df.copy()
        
        if len(df_notif) == 0:
            return {
                "region": "AFRO",
                "error": "No notifications data available"
            }
        
        latest_year = df_notif['year'].max()
        latest_notif = df_notif[df_notif['year'] == latest_year]
        latest_outcomes = df_outcomes[df_outcomes['year'] == latest_year] if len(df_outcomes) > 0 else pd.DataFrame()
        
        # Calculate regional statistics
        outlook = {
            "region": "AFRO",
            "latest_year": int(latest_year),
            "total_countries": len(df_notif['country'].unique()),
            "countries_with_data": {},
            "regional_totals": {},
            "trends": {},
            "performance_summary": {}
        }
        
        # Regional totals for latest year
        if 'c_newinc' in latest_notif.columns:
            outlook["regional_totals"]["total_notifications"] = float(latest_notif['c_newinc'].sum())
            outlook["countries_with_data"]["notifications"] = int(latest_notif['c_newinc'].notna().sum())
        
        if 'new_sp' in latest_notif.columns:
            outlook["regional_totals"]["smear_positive"] = float(latest_notif['new_sp'].sum())
        
        if 'new_sn' in latest_notif.columns:
            outlook["regional_totals"]["smear_negative"] = float(latest_notif['new_sn'].sum())
        
        if 'new_ep' in latest_notif.columns:
            outlook["regional_totals"]["extrapulmonary"] = float(latest_notif['new_ep'].sum())
        
        # Treatment outcomes totals
        if len(latest_outcomes) > 0:
            if 'new_sp_coh' in latest_outcomes.columns:
                outlook["regional_totals"]["cohort_size"] = float(latest_outcomes['new_sp_coh'].sum())
                outlook["countries_with_data"]["outcomes"] = int(latest_outcomes['new_sp_coh'].notna().sum())
            
            if 'c_new_sp_tsr' in latest_outcomes.columns:
                tsr_values = latest_outcomes['c_new_sp_tsr'].dropna()
                if len(tsr_values) > 0:
                    outlook["performance_summary"]["treatment_success_rate"] = {
                        "mean": float(tsr_values.mean()),
                        "median": float(tsr_values.median()),
                        "min": float(tsr_values.min()),
                        "max": float(tsr_values.max()),
                        "countries_above_85": int((tsr_values >= 85).sum()),  # WHO target
                        "countries_below_85": int((tsr_values < 85).sum())
                    }
        
        # Calculate trends (comparing latest year with 5 years ago)
        if latest_year >= 2018:
            five_years_ago = latest_year - 5
            notif_5y_ago = df_notif[df_notif['year'] == five_years_ago]
            
            if len(notif_5y_ago) > 0 and 'c_newinc' in notif_5y_ago.columns:
                total_5y_ago = notif_5y_ago['c_newinc'].sum()
                total_latest = latest_notif['c_newinc'].sum()
                
                if total_5y_ago > 0:
                    pct_change = ((total_latest - total_5y_ago) / total_5y_ago) * 100
                    outlook["trends"]["notifications_5year"] = {
                        "percentage_change": float(pct_change),
                        "direction": "Increasing" if pct_change > 0 else "Decreasing" if pct_change < 0 else "Stable",
                        "value_5y_ago": float(total_5y_ago),
                        "value_latest": float(total_latest)
                    }
        
        # Country performance distribution
        if 'c_newinc' in latest_notif.columns:
            notif_values = latest_notif['c_newinc'].dropna()
            if len(notif_values) > 0:
                # Categorize countries by notification levels
                q1 = notif_values.quantile(0.25)
                q2 = notif_values.quantile(0.50)
                q3 = notif_values.quantile(0.75)
                
                outlook["performance_summary"]["notification_distribution"] = {
                    "low": int((notif_values < q1).sum()),
                    "medium_low": int(((notif_values >= q1) & (notif_values < q2)).sum()),
                    "medium_high": int(((notif_values >= q2) & (notif_values < q3)).sum()),
                    "high": int((notif_values >= q3).sum())
                }
        
        return outlook

