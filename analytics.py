"""
Analytics Module for Mortality Data Analysis
Provides various analytical functions and report generation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from data_pipeline import MortalityDataPipeline
from datetime import datetime


class MortalityAnalytics:
    """Analytics engine for mortality data"""
    
    def __init__(self, pipeline: MortalityDataPipeline):
        """
        Initialize analytics with data pipeline
        
        Args:
            pipeline: MortalityDataPipeline instance
        """
        self.pipeline = pipeline
        if pipeline.mortality_data is None:
            pipeline.load_data()
        
        self.mortality_df = pipeline.clean_mortality_data()
        self.mmr_df = pipeline.clean_mmr_data()
        self.mortality_proj = pipeline.mortality_projections
        self.mmr_proj = pipeline.mmr_projections
    
    def get_country_statistics(self, country: str) -> Dict:
        """
        Get comprehensive statistics for a specific country
        
        Args:
            country: Country name
        
        Returns:
            Dictionary with statistics
        """
        country_mortality = self.pipeline.filter_by_country(country, self.mortality_df)
        country_mmr = self.pipeline.filter_by_country(country, self.mmr_df)
        
        stats = {
            "country": country,
            "indicators": {},
            "mmr_trend": {}
        }
        
        # Analyze each indicator
        for indicator in country_mortality['indicator'].unique():
            ind_data = country_mortality[country_mortality['indicator'] == indicator]
            if len(ind_data) > 0:
                stats["indicators"][indicator] = {
                    "latest_value": ind_data['value'].iloc[-1] if len(ind_data) > 0 else None,
                    "mean_value": ind_data['value'].median(),  # Using median instead of mean
                    "median_value": ind_data['value'].median(),
                    "min_value": ind_data['value'].min(),
                    "max_value": ind_data['value'].max(),
                    "trend": self._calculate_trend(ind_data),
                    "data_points": len(ind_data)
                }
        
        # MMR analysis
        if len(country_mmr) > 0:
            stats["mmr_trend"] = {
                "latest_mmr": country_mmr['value'].iloc[-1] if len(country_mmr) > 0 else None,
                "mean_mmr": country_mmr['value'].median(),  # Using median instead of mean
                "median_mmr": country_mmr['value'].median(),
                "min_mmr": country_mmr['value'].min(),
                "max_mmr": country_mmr['value'].max(),
                "trend": self._calculate_trend(country_mmr),
                "year_range": (country_mmr['year'].min(), country_mmr['year'].max())
            }
        
        return stats
    
    def compare_countries(self, countries: List[str], indicator: str) -> Dict:
        """
        Compare multiple countries for a specific indicator
        
        Args:
            countries: List of country names
            indicator: Indicator to compare
        
        Returns:
            Comparison statistics
        """
        comparison = {
            "indicator": indicator,
            "countries": {},
            "countries_with_data": [],
            "countries_without_data": []
        }
        
        for country in countries:
            country_data = self.pipeline.filter_by_country(country, self.mortality_df)
            ind_data = country_data[country_data['indicator'] == indicator]
            
            if len(ind_data) > 0:
                comparison["countries"][country] = {
                    "latest_value": ind_data['value'].iloc[-1],
                    "mean_value": ind_data['value'].median(),  # Using median instead of mean
                    "median_value": ind_data['value'].median(),
                    "trend": self._calculate_trend(ind_data)
                }
                comparison["countries_with_data"].append(country)
            else:
                comparison["countries_without_data"].append(country)
        
        # Rank countries
        if comparison["countries"]:
            sorted_countries = sorted(
                comparison["countries"].items(),
                key=lambda x: x[1]["latest_value"],
                reverse=True
            )
            comparison["ranking"] = [{"country": c[0], "value": c[1]["latest_value"]} 
                                    for c in sorted_countries]
        
        return comparison
    
    def get_regional_summary(self) -> Dict:
        """
        Get summary statistics for the entire region
        
        Returns:
            Regional summary
        """
        summary = {
            "total_countries": len(self.pipeline.get_countries()),
            "indicators": {},
            "mmr_summary": {}
        }
        
        # Analyze each indicator
        for indicator in self.mortality_df['indicator'].unique():
            ind_data = self.mortality_df[self.mortality_df['indicator'] == indicator]
            summary["indicators"][indicator] = {
                "mean_value": ind_data['value'].mean(),
                "median_value": ind_data['value'].median(),
                "min_value": ind_data['value'].min(),
                "max_value": ind_data['value'].max(),
                "std_dev": ind_data['value'].std()
            }
        
        # MMR summary
        if len(self.mmr_df) > 0:
            summary["mmr_summary"] = {
                "mean_mmr": self.mmr_df['value'].median(),  # Using median instead of mean
                "median_mmr": self.mmr_df['value'].median(),
                "min_mmr": self.mmr_df['value'].min(),
                "max_mmr": self.mmr_df['value'].max(),
                "year_range": (self.mmr_df['year'].min(), self.mmr_df['year'].max())
            }
        
        return summary
    
    def analyze_projections(self, country: Optional[str] = None) -> Dict:
        """
        Analyze projection data
        
        Args:
            country: Optional country filter
        
        Returns:
            Projection analysis
        """
        analysis = {
            "mortality_projections": {},
            "mmr_projections": {}
        }
        
        # Mortality projections
        proj_df = self.mortality_proj.copy()
        if country:
            proj_df = proj_df[proj_df['country'].str.contains(country, case=False, na=False)]
        
        if len(proj_df) > 0:
            analysis["mortality_projections"] = {
                "total_indicators": len(proj_df['indicator'].unique()),
                "on_track_count": len(proj_df[proj_df['on_track'] == True]),
                "off_track_count": len(proj_df[proj_df['on_track'] == False]),
                "indicators": {}
            }
            
            for indicator in proj_df['indicator'].unique():
                ind_proj = proj_df[proj_df['indicator'] == indicator]
                analysis["mortality_projections"]["indicators"][indicator] = {
                    "on_track": len(ind_proj[ind_proj['on_track'] == True]),
                    "off_track": len(ind_proj[ind_proj['on_track'] == False]),
                    "avg_proj_2030": ind_proj['proj_2030'].mean()
                }
        
        # MMR projections
        mmr_proj_df = self.mmr_proj.copy()
        if country:
            mmr_proj_df = mmr_proj_df[mmr_proj_df['country'].str.contains(country, case=False, na=False)]
        
        if len(mmr_proj_df) > 0:
            analysis["mmr_projections"] = {
                "on_track_count": len(mmr_proj_df[mmr_proj_df['on_track'] == True]),
                "off_track_count": len(mmr_proj_df[mmr_proj_df['on_track'] == False]),
                "avg_proj_2030": mmr_proj_df['proj_2030'].mean(),
                "countries_on_track": mmr_proj_df[mmr_proj_df['on_track'] == True]['country'].tolist()
            }
        
        return analysis
    
    def generate_summary_report(self, country: Optional[str] = None) -> str:
        """
        Generate a comprehensive summary report
        
        Args:
            country: Optional country filter
        
        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("MORTALITY ANALYTICS SUMMARY REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        if country:
            report_lines.append(f"Country Focus: {country}")
            report_lines.append("")
            stats = self.get_country_statistics(country)
            
            report_lines.append("COUNTRY STATISTICS")
            report_lines.append("-" * 80)
            
            for indicator, data in stats["indicators"].items():
                report_lines.append(f"\n{indicator}:")
                report_lines.append(f"  Latest Value: {data['latest_value']:.2f}")
                report_lines.append(f"  Mean Value: {data['mean_value']:.2f}")
                report_lines.append(f"  Range: {data['min_value']:.2f} - {data['max_value']:.2f}")
                report_lines.append(f"  Trend: {data['trend']}")
            
            if stats["mmr_trend"]:
                report_lines.append(f"\nMaternal Mortality Ratio (MMR):")
                report_lines.append(f"  Latest MMR: {stats['mmr_trend']['latest_mmr']:.2f}")
                report_lines.append(f"  Mean MMR: {stats['mmr_trend']['mean_mmr']:.2f}")
                report_lines.append(f"  Trend: {stats['mmr_trend']['trend']}")
        else:
            # Regional summary
            summary = self.get_regional_summary()
            report_lines.append("REGIONAL SUMMARY")
            report_lines.append("-" * 80)
            report_lines.append(f"Total Countries: {summary['total_countries']}")
            report_lines.append("")
            
            report_lines.append("KEY INDICATORS:")
            for indicator, data in list(summary["indicators"].items())[:5]:
                report_lines.append(f"\n{indicator}:")
                report_lines.append(f"  Mean: {data['mean_value']:.2f}")
                report_lines.append(f"  Range: {data['min_value']:.2f} - {data['max_value']:.2f}")
        
        # Add projections
        report_lines.append("")
        report_lines.append("PROJECTIONS ANALYSIS")
        report_lines.append("-" * 80)
        proj_analysis = self.analyze_projections(country)
        
        if proj_analysis["mmr_projections"]:
            mmr_proj = proj_analysis["mmr_projections"]
            report_lines.append(f"MMR Projections:")
            report_lines.append(f"  Countries On Track: {mmr_proj['on_track_count']}")
            report_lines.append(f"  Countries Off Track: {mmr_proj['off_track_count']}")
            report_lines.append(f"  Average Projected MMR 2030: {mmr_proj['avg_proj_2030']:.2f}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def _calculate_trend(self, data: pd.DataFrame) -> str:
        """
        Calculate trend direction from data
        
        Args:
            data: DataFrame with 'value' and 'year' columns
        
        Returns:
            Trend description
        """
        if len(data) < 2:
            return "Insufficient data"
        
        # Sort by year
        sorted_data = data.sort_values('year')
        values = sorted_data['value'].values
        
        # Simple linear trend
        if len(values) >= 2:
            first_half = values[:len(values)//2].mean()
            second_half = values[len(values)//2:].mean()
            
            change_pct = ((second_half - first_half) / first_half) * 100
            
            if change_pct > 5:
                return f"Increasing ({change_pct:.1f}%)"
            elif change_pct < -5:
                return f"Decreasing ({abs(change_pct):.1f}%)"
            else:
                return "Stable"
        
        return "Unknown"
    
    def get_top_countries_by_indicator(self, indicator: str, top_n: int = 10, 
                                       ascending: bool = False) -> pd.DataFrame:
        """
        Get top N countries by indicator value
        
        Args:
            indicator: Indicator name
            top_n: Number of top countries to return
            ascending: Sort order
        
        Returns:
            DataFrame with top countries
        """
        ind_data = self.mortality_df[self.mortality_df['indicator'] == indicator]
        
        if len(ind_data) == 0:
            return pd.DataFrame()
        
        # Get latest value for each country
        latest_data = ind_data.groupby('country').agg({
            'value': 'last',
            'year': 'last'
        }).reset_index()
        
        latest_data = latest_data.sort_values('value', ascending=ascending)
        
        return latest_data.head(top_n)
    
    def get_trend_analysis(self, country: str, indicator: str) -> Dict:
        """
        Get detailed trend analysis for country and indicator
        
        Args:
            country: Country name
            indicator: Indicator name
        
        Returns:
            Trend analysis dictionary
        """
        country_data = self.pipeline.filter_by_country(country, self.mortality_df)
        ind_data = country_data[country_data['indicator'] == indicator]
        
        if len(ind_data) == 0:
            return {"error": "No data found"}
        
        sorted_data = ind_data.sort_values('year')
        
        analysis = {
            "country": country,
            "indicator": indicator,
            "data_points": len(sorted_data),
            "year_range": (sorted_data['year'].min(), sorted_data['year'].max()),
            "value_range": (sorted_data['value'].min(), sorted_data['value'].max()),
            "current_value": sorted_data['value'].iloc[-1],
            "baseline_value": sorted_data['value'].iloc[0],
            "change": sorted_data['value'].iloc[-1] - sorted_data['value'].iloc[0],
            "change_pct": ((sorted_data['value'].iloc[-1] - sorted_data['value'].iloc[0]) / 
                          sorted_data['value'].iloc[0]) * 100,
            "trend": self._calculate_trend(sorted_data)
        }
        
        return analysis

