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
        country: Optional[str] = None,
        custom_requirements: Optional[str] = None
    ) -> str:
        """
        Generate a report using LLM based on provided statistics
        
        Args:
            statistics: Dictionary containing key statistics and data
            report_type: Type of report (comprehensive, summary, executive)
            country: Optional country name for country-specific reports
            custom_requirements: Optional custom requirements from user
        
        Returns:
            Generated report text
        """
        # Build prompt with key statistics
        prompt = self._build_prompt(statistics, report_type, country, custom_requirements)
        
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
                max_tokens=3000
            )
            
            report = response.choices[0].message.content.strip()
            return report
            
        except Exception as e:
            return f"Error generating report: {str(e)}\n\nFallback Report:\n{self._generate_fallback_report(statistics, country)}"
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the LLM"""
        return """You are an expert health data analyst specializing in maternal and child mortality analytics for the WHO African Region (AFRO). 

Your role is to analyze health data and generate comprehensive, insightful reports that:
- Present key findings clearly and concisely with detailed interpretation
- Provide summaries and interpretations of statistics and data patterns
- Explain what the numbers mean in practical terms
- Highlight trends and patterns in the data with clear explanations
- Identify countries that are on-track or off-track for SDG 2030 targets
- Provide actionable insights and recommendations for policymakers
- Use professional, data-driven language
- Structure reports with clear sections and headings
- Include specific numbers and statistics from the data provided
- Interpret statistical trends and explain their implications
- Compare values against benchmarks and targets
- Explain the significance of changes over time

Focus on:
- Maternal Mortality Ratio (MMR) trends and projections with interpretation
- Under-five mortality rates with detailed analysis
- Neonatal and infant mortality patterns
- Progress toward SDG 2030 targets with clear assessment
- Regional comparisons and country-specific insights
- Statistical summaries that explain what the data means

IMPORTANT: Always provide interpretation alongside statistics. Don't just list numbers - explain what they mean, why they matter, and what implications they have."""
    
    def _build_prompt(
        self,
        statistics: Dict,
        report_type: str,
        country: Optional[str],
        custom_requirements: Optional[str] = None
    ) -> str:
        """Build the user prompt with statistics"""
        
        prompt_parts = []
        
        if country:
            prompt_parts.append(f"Generate a {report_type} health analytics report for {country}.")
        else:
            prompt_parts.append(f"Generate a {report_type} regional health analytics report for the WHO African Region (AFRO).")
        
        # Add custom requirements if provided
        if custom_requirements and custom_requirements.strip():
            prompt_parts.append(f"\n## Custom Requirements:")
            prompt_parts.append(f"The user has specified the following requirements for this report:")
            prompt_parts.append(f"{custom_requirements}")
            prompt_parts.append(f"\nPlease ensure the report addresses these specific requirements while maintaining comprehensive analysis.")
        
        prompt_parts.append("\n## Key Statistics and Data:\n")
        prompt_parts.append("IMPORTANT: For each statistic provided below, provide interpretation explaining:")
        prompt_parts.append("- What the number means in practical terms")
        prompt_parts.append("- How it compares to targets or benchmarks")
        prompt_parts.append("- What trends indicate about progress")
        prompt_parts.append("- What implications this has for health outcomes")
        prompt_parts.append("")
        
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
                if "top" in countries and "countries" in countries["top"]:
                    top_list = list(zip(countries["top"]["countries"], countries["top"]["values"]))
                    prompt_parts.append(f"- Highest (with values): {', '.join([f'{c} ({v:.2f})' for c, v in top_list[:5]])}")
                if "bottom" in countries and "countries" in countries["bottom"]:
                    bottom_list = list(zip(countries["bottom"]["countries"], countries["bottom"]["values"]))
                    prompt_parts.append(f"- Lowest (with values): {', '.join([f'{c} ({v:.2f})' for c, v in bottom_list[:5]])}")
        
        # Add trend analyses if available
        if "trend_analyses" in statistics:
            prompt_parts.append("\n### Detailed Trend Analyses:")
            for indicator, trend_data in statistics["trend_analyses"].items():
                prompt_parts.append(f"\n**{indicator}:**")
                prompt_parts.append(f"- Current Value: {trend_data.get('current_value', 'N/A')}")
                prompt_parts.append(f"- Baseline Value: {trend_data.get('baseline_value', 'N/A')}")
                prompt_parts.append(f"- Change: {trend_data.get('change', 'N/A')} ({trend_data.get('change_pct', 'N/A'):.2f}%)")
                prompt_parts.append(f"- Trend: {trend_data.get('trend', 'N/A')}")
                prompt_parts.append(f"- Year Range: {trend_data.get('year_range', 'N/A')}")
        
        # Add SDG targets context
        if "sdg_targets" in statistics:
            prompt_parts.append("\n### SDG 2030 Targets (for reference):")
            for indicator, target_info in statistics["sdg_targets"].items():
                prompt_parts.append(f"- {indicator}: {target_info['target']} {target_info['unit']} - {target_info['description']}")
        
        prompt_parts.append("\n\nPlease generate a well-structured, professional report based on this data. Include:")
        prompt_parts.append("1. Executive Summary - Provide a high-level overview with key takeaways")
        prompt_parts.append("2. Key Findings - List important statistics WITH interpretation explaining what they mean")
        prompt_parts.append("3. Statistical Summary and Interpretation - For each key statistic:")
        prompt_parts.append("   - Present the number")
        prompt_parts.append("   - Explain what it means in practical terms")
        prompt_parts.append("   - Compare against targets or benchmarks")
        prompt_parts.append("   - Discuss implications")
        prompt_parts.append("4. Trends and Patterns Analysis - Explain what trends indicate and their significance")
        prompt_parts.append("5. SDG 2030 Progress Assessment - Detailed analysis of progress toward targets")
        prompt_parts.append("6. Recommendations (if applicable) - Actionable insights based on the data")
        prompt_parts.append("\nCRITICAL: Do not just list statistics. For every number, provide:")
        prompt_parts.append("- Clear interpretation of what it means")
        prompt_parts.append("- Context (is this good/bad, improving/declining)")
        prompt_parts.append("- Comparison to relevant benchmarks or targets")
        prompt_parts.append("- Practical implications")
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

