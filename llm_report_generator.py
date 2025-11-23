"""
LLM-Powered Report Generator
Uses Gemini 2.5 Flash via OpenRouter to generate comprehensive reports
"""

import os
from typing import Dict, Optional, List
from openai import OpenAI
from datetime import datetime


class LLMReportGenerator:
    """Generate reports using LLM (Gemini 2.5 Flash via OpenRouter)"""
    
    def __init__(self, api_key: str):
        """
        Initialize LLM report generator
        
        Args:
            api_key: OpenRouter API key
        """
        self.api_key = api_key
        # OpenRouter uses OpenAI-compatible API
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "google/gemini-2.5-flash"
    
    def generate_report(
        self,
        statistics: Dict,
        report_type: str = "comprehensive",
        country: Optional[str] = None
    ) -> str:
        """
        Generate a report using LLM based on provided statistics
        
        Args:
            statistics: Dictionary containing key statistics and data
            report_type: Type of report (comprehensive, summary, executive)
            country: Optional country name for country-specific reports
        
        Returns:
            Generated report text
        """
        # Build prompt with key statistics
        prompt = self._build_prompt(statistics, report_type, country)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            report = response.choices[0].message.content.strip()
            return report
            
        except Exception as e:
            return f"Error generating report: {str(e)}\n\nFallback Report:\n{self._generate_fallback_report(statistics, country)}"
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the LLM"""
        return """You are an expert health data analyst specializing in maternal and child mortality analytics for the WHO African Region (AFRO). 

Your role is to analyze health data and generate comprehensive, insightful reports that:
- Present key findings clearly and concisely
- Highlight trends and patterns in the data
- Identify countries that are on-track or off-track for SDG 2030 targets
- Provide actionable insights for policymakers
- Use professional, data-driven language
- Structure reports with clear sections and headings
- Include specific numbers and statistics from the data provided

Focus on:
- Maternal Mortality Ratio (MMR) trends and projections
- Under-five mortality rates
- Neonatal and infant mortality
- Progress toward SDG 2030 targets
- Regional comparisons and country-specific insights"""
    
    def _build_prompt(
        self,
        statistics: Dict,
        report_type: str,
        country: Optional[str]
    ) -> str:
        """Build the user prompt with statistics"""
        
        prompt_parts = []
        
        if country:
            prompt_parts.append(f"Generate a {report_type} health analytics report for {country}.")
        else:
            prompt_parts.append(f"Generate a {report_type} regional health analytics report for the WHO African Region (AFRO).")
        
        prompt_parts.append("\n## Key Statistics and Data:\n")
        
        # Add country statistics if available
        if "country_stats" in statistics:
            stats = statistics["country_stats"]
            prompt_parts.append(f"\n### Country: {stats.get('country', 'N/A')}")
            
            if "indicators" in stats:
                prompt_parts.append("\n**Mortality Indicators:**")
                for indicator, data in stats["indicators"].items():
                    prompt_parts.append(f"- {indicator}:")
                    prompt_parts.append(f"  - Latest Value: {data.get('latest_value', 'N/A')}")
                    prompt_parts.append(f"  - Median Value: {data.get('median_value', 'N/A')}")
                    prompt_parts.append(f"  - Range: {data.get('min_value', 'N/A')} - {data.get('max_value', 'N/A')}")
                    prompt_parts.append(f"  - Trend: {data.get('trend', 'N/A')}")
            
            if "mmr_trend" in stats and stats["mmr_trend"]:
                mmr = stats["mmr_trend"]
                prompt_parts.append("\n**Maternal Mortality Ratio (MMR):**")
                prompt_parts.append(f"- Latest MMR: {mmr.get('latest_mmr', 'N/A')}")
                prompt_parts.append(f"- Median MMR: {mmr.get('median_mmr', 'N/A')}")
                prompt_parts.append(f"- Range: {mmr.get('min_mmr', 'N/A')} - {mmr.get('max_mmr', 'N/A')}")
                prompt_parts.append(f"- Trend: {mmr.get('trend', 'N/A')}")
        
        # Add regional summary if available
        if "regional_summary" in statistics:
            summary = statistics["regional_summary"]
            prompt_parts.append("\n### Regional Overview:")
            prompt_parts.append(f"- Total Countries: {summary.get('total_countries', 'N/A')}")
            
            if "indicators" in summary:
                prompt_parts.append("\n**Regional Indicators:**")
                for indicator, data in list(summary["indicators"].items())[:10]:
                    prompt_parts.append(f"- {indicator}:")
                    prompt_parts.append(f"  - Median: {data.get('median_value', 'N/A')}")
                    prompt_parts.append(f"  - Range: {data.get('min_value', 'N/A')} - {data.get('max_value', 'N/A')}")
        
        # Add projections if available
        if "projections" in statistics:
            proj = statistics["projections"]
            prompt_parts.append("\n### Projections Analysis:")
            
            if "mmr_projections" in proj:
                mmr_proj = proj["mmr_projections"]
                prompt_parts.append("\n**MMR Projections (2030):**")
                prompt_parts.append(f"- Countries On Track: {mmr_proj.get('on_track_count', 0)}")
                prompt_parts.append(f"- Countries Off Track: {mmr_proj.get('off_track_count', 0)}")
                prompt_parts.append(f"- Average Projected MMR 2030: {mmr_proj.get('avg_proj_2030', 'N/A')}")
                
                if "countries_on_track" in mmr_proj:
                    prompt_parts.append(f"- Countries On Track: {', '.join(mmr_proj['countries_on_track'][:10])}")
        
        # Add top countries if available
        if "top_countries" in statistics:
            prompt_parts.append("\n### Top/Bottom Countries:")
            for indicator, countries in statistics["top_countries"].items():
                prompt_parts.append(f"\n**{indicator}:**")
                if "top" in countries:
                    prompt_parts.append(f"- Highest: {', '.join(countries['top'][:5])}")
                if "bottom" in countries:
                    prompt_parts.append(f"- Lowest: {', '.join(countries['bottom'][:5])}")
        
        prompt_parts.append("\n\nPlease generate a well-structured, professional report based on this data. Include:")
        prompt_parts.append("1. Executive Summary")
        prompt_parts.append("2. Key Findings")
        prompt_parts.append("3. Trends and Patterns")
        prompt_parts.append("4. SDG 2030 Progress Assessment")
        prompt_parts.append("5. Recommendations (if applicable)")
        prompt_parts.append("\nUse markdown formatting for headings and structure.")
        
        return "\n".join(prompt_parts)
    
    def _generate_fallback_report(
        self,
        statistics: Dict,
        country: Optional[str]
    ) -> str:
        """Generate a basic fallback report if LLM fails"""
        report_lines = []
        report_lines.append("# Health Analytics Report")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        if country:
            report_lines.append(f"## Country: {country}")
        else:
            report_lines.append("## Regional Report: WHO African Region")
        
        report_lines.append("\nNote: LLM report generation unavailable. Please check API configuration.")
        
        return "\n".join(report_lines)

