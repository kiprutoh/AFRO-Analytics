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
        custom_requirements: Optional[str] = None,
        language: str = "English",
        selected_indicators: Optional[List[str]] = None,
        charts: Optional[Dict] = None
    ) -> str:
        """
        Generate a report using LLM based on provided statistics
        
        Args:
            statistics: Dictionary containing key statistics and data
            report_type: Type of report (comprehensive, summary, executive)
            country: Optional country name for country-specific reports
            custom_requirements: Optional custom requirements from user
            language: Language for the report (default: English)
            selected_indicators: Optional list of specific indicators to focus on
            charts: Optional dictionary of chart data to include
        
        Returns:
            Generated report text
        """
        # Build prompt with key statistics
        prompt = self._build_prompt(
            statistics, report_type, country, custom_requirements, 
            language, selected_indicators, charts
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000  # Increased for charts
            )
            
            report = response.choices[0].message.content.strip()
            
            # Add chart placeholders if charts provided
            if charts:
                report = self._integrate_charts(report, charts)
            
            # Add AI-generated content disclaimer
            disclaimer = self._get_ai_disclaimer(language)
            report = f"{report}\n\n---\n\n{disclaimer}"
            
            return report
            
        except Exception as e:
            fallback = self._generate_fallback_report(statistics, country, language)
            return f"Error generating report: {str(e)}\n\nFallback Report:\n{fallback}"
    
    def _get_system_prompt(self, language: str = "English") -> str:
        """Get system prompt for the LLM"""
        language_instruction = f"IMPORTANT: Generate the entire report in {language}. All text, headings, explanations, and content must be in {language}."
        
        # Language-specific decline messages
        decline_messages = {
            "English": "I apologize, but I can only provide information based on content available from the World Health Organization (WHO) website at https://www.who.int/. For information outside of WHO's official content, please refer to the WHO website directly or consult other authorized sources.",
            "French": "Je m'excuse, mais je ne peux fournir des informations que sur la base du contenu disponible sur le site Web de l'Organisation mondiale de la Santé (OMS) à https://www.who.int/. Pour des informations en dehors du contenu officiel de l'OMS, veuillez consulter directement le site Web de l'OMS ou d'autres sources autorisées.",
            "Portuguese": "Peço desculpas, mas só posso fornecer informações com base no conteúdo disponível no site da Organização Mundial da Saúde (OMS) em https://www.who.int/. Para informações fora do conteúdo oficial da OMS, consulte diretamente o site da OMS ou outras fontes autorizadas.",
            "Spanish": "Me disculpo, pero solo puedo proporcionar información basada en el contenido disponible del sitio web de la Organización Mundial de la Salud (OMS) en https://www.who.int/. Para información fuera del contenido oficial de la OMS, consulte directamente el sitio web de la OMS u otras fuentes autorizadas."
        }
        
        decline_message = decline_messages.get(language, decline_messages["English"])
        
        return f"""You are an expert health data analyst specializing in health analytics (maternal mortality, child mortality, and tuberculosis) for the WHO African Region (AFRO).

{language_instruction} 

CRITICAL CONTENT RESTRICTION:
- You MUST ONLY use information, data, and content that is available from the World Health Organization (WHO) official website: https://www.who.int/
- You MUST ONLY reference WHO publications, reports, guidelines, and official data
- If asked about topics, data, or information NOT available on https://www.who.int/, you MUST politely decline using this message:
  "{decline_message}"
- Do NOT use information from other sources, even if you believe it to be accurate
- Do NOT make up or infer information not explicitly available from WHO sources
- When referencing WHO content, you may mention it comes from WHO's official website

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
- Reference WHO sources when appropriate (e.g., "According to WHO data..." or "Based on WHO reports...")

Focus on:
- Maternal Mortality Ratio (MMR) trends and projections with interpretation
- Under-five mortality rates with detailed analysis
- Neonatal and infant mortality patterns
- Tuberculosis notifications and treatment outcomes (for TB reports)
- Progress toward SDG 2030 targets with clear assessment
- Regional comparisons and country-specific insights
- Statistical summaries that explain what the data means

IMPORTANT: 
- Always provide interpretation alongside statistics. Don't just list numbers - explain what they mean, why they matter, and what implications they have.
- Only use WHO-approved information and data from https://www.who.int/
- Politely decline requests for information not available on WHO's website"""
    
    def _build_prompt(
        self,
        statistics: Dict,
        report_type: str,
        country: Optional[str],
        custom_requirements: Optional[str] = None,
        language: str = "English",
        selected_indicators: Optional[List[str]] = None,
        charts: Optional[Dict] = None
    ) -> str:
        """Build the user prompt with statistics"""
        
        prompt_parts = []
        
        # Content restriction notice
        prompt_parts.append("=" * 80)
        prompt_parts.append("CRITICAL: CONTENT RESTRICTION")
        prompt_parts.append("=" * 80)
        prompt_parts.append("You MUST ONLY use information from the World Health Organization (WHO) official website: https://www.who.int/")
        prompt_parts.append("If the user requests information NOT available on WHO's website, politely decline.")
        prompt_parts.append("Do NOT use information from other sources.")
        prompt_parts.append("=" * 80)
        prompt_parts.append("")
        
        # STRICT INDICATOR CONSTRAINT
        if selected_indicators and selected_indicators != ["All available indicators"]:
            prompt_parts.append("=" * 80)
            prompt_parts.append("CRITICAL: INDICATOR CONSTRAINT")
            prompt_parts.append("=" * 80)
            prompt_parts.append("You MUST ONLY analyze and report on the following indicators:")
            for ind in selected_indicators:
                prompt_parts.append(f"  ✓ {ind}")
            prompt_parts.append("")
            prompt_parts.append("DO NOT include any other indicators in your analysis.")
            prompt_parts.append("DO NOT mention or discuss indicators not in the above list.")
            prompt_parts.append("Focus EXCLUSIVELY on these selected indicators.")
            prompt_parts.append("=" * 80)
            prompt_parts.append("")
        
        # Language instruction
        prompt_parts.append(f"LANGUAGE REQUIREMENT: Generate the entire report in {language}. All content must be in {language}.")
        prompt_parts.append("")
        
        if country:
            prompt_parts.append(f"Generate a {report_type} health analytics report for {country}.")
        else:
            prompt_parts.append(f"Generate a {report_type} regional health analytics report for the WHO African Region (AFRO).")
        
        # Add custom requirements if provided
        if custom_requirements and custom_requirements.strip():
            prompt_parts.append(f"\n## Custom Requirements:")
            prompt_parts.append(f"The user has specified the following requirements for this report:")
            prompt_parts.append(f"{custom_requirements}")
            prompt_parts.append(f"\nIMPORTANT: Only address these requirements if they can be answered using WHO content from https://www.who.int/")
            prompt_parts.append(f"If any requirement asks for information NOT available on WHO's website, politely decline that specific part.")
            prompt_parts.append(f"Please ensure the report addresses these specific requirements while maintaining comprehensive analysis using ONLY WHO sources.")
        
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
        
        # Add chart information if provided
        if charts:
            prompt_parts.append("\n## 📊 Charts to Reference in Report:")
            for chart_name, chart_info in charts.items():
                prompt_parts.append(f"\n**{chart_info.get('title', chart_name)}**")
                prompt_parts.append(f"- Description: {chart_info.get('description', 'N/A')}")
                prompt_parts.append(f"- Type: {chart_info.get('type', 'N/A')}")
                if 'key_insights' in chart_info:
                    prompt_parts.append(f"- Key Insights: {chart_info['key_insights']}")
            prompt_parts.append("\nWhen referencing these charts, use: [CHART: chart_name]")
        
        prompt_parts.append("\n\nPlease generate a well-structured, professional report based on this data. Include:")
        prompt_parts.append("1. Executive Summary - Provide a high-level overview with key takeaways FOR SELECTED INDICATORS ONLY")
        prompt_parts.append("2. Key Findings - List important statistics WITH interpretation FOR SELECTED INDICATORS ONLY")
        prompt_parts.append("3. Detailed Indicator Analysis - For EACH SELECTED INDICATOR:")
        prompt_parts.append("   - Present the key statistics")
        prompt_parts.append("   - Explain what they mean in practical terms")
        prompt_parts.append("   - Compare against WHO targets or benchmarks")
        prompt_parts.append("   - Discuss implications and trends")
        prompt_parts.append("   - Reference relevant charts using [CHART: name] notation")
        prompt_parts.append("4. Visual Analytics Section - Describe insights from charts")
        prompt_parts.append("5. Trends and Patterns - Explain what trends indicate FOR SELECTED INDICATORS ONLY")
        prompt_parts.append("6. Performance Assessment - Against WHO targets")
        prompt_parts.append("7. Recommendations - Actionable insights based on the SELECTED INDICATORS")
        prompt_parts.append("\nCRITICAL REQUIREMENTS:")
        if selected_indicators and selected_indicators != ["All available indicators"]:
            prompt_parts.append("⚠️ MOST IMPORTANT: ONLY analyze the indicators explicitly listed above. DO NOT mention other indicators.")
        prompt_parts.append("- Do not just list statistics. For every number, provide:")
        prompt_parts.append("  * Clear interpretation of what it means")
        prompt_parts.append("  * Context (is this good/bad, improving/declining)")
        prompt_parts.append("  * Comparison to WHO benchmarks or targets")
        prompt_parts.append("  * Practical implications for health outcomes")
        prompt_parts.append("- Reference charts where appropriate using [CHART: name]")
        prompt_parts.append("- Structure the report with markdown headings (##, ###)")
        prompt_parts.append("- Be specific and data-driven")
        prompt_parts.append("- ONLY use information from WHO's official website (https://www.who.int/)")
        prompt_parts.append("\nUse markdown formatting for headings and structure.")
        
        return "\n".join(prompt_parts)
    
    def _get_ai_disclaimer(self, language: str = "English") -> str:
        """
        Get AI-generated content disclaimer in the specified language
        
        Args:
            language: Language code
        
        Returns:
            Disclaimer text
        """
        disclaimers = {
            "English": """**AI-Generated Content**

This report was generated using artificial intelligence. Please review all content for accuracy and verify any critical information.""",
            "French": """**Contenu Généré par IA**

Ce rapport a été généré à l'aide de l'intelligence artificielle. Veuillez examiner tout le contenu pour vérifier son exactitude et vérifier toute information critique.""",
            "Portuguese": """**Conteúdo Gerado por IA**

Este relatório foi gerado usando inteligência artificial. Por favor, revise todo o conteúdo para verificar a precisão e verifique quaisquer informações críticas.""",
            "Spanish": """**Contenido Generado por IA**

Este informe fue generado usando inteligencia artificial. Por favor, revise todo el contenido para verificar la precisión y verifique cualquier información crítica."""
        }
        
        return disclaimers.get(language, disclaimers["English"])
    
    def _generate_fallback_report(
        self,
        statistics: Dict,
        country: Optional[str],
        language: str = "English"
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
        
        # Add AI disclaimer
        disclaimer = self._get_ai_disclaimer(language)
        report_lines.append(f"\n\n---\n\n{disclaimer}")
        
        return "\n".join(report_lines)
    
    def _integrate_charts(self, report: str, charts: Dict) -> str:
        """
        Integrate chart placeholders into report
        
        Args:
            report: Generated report text
            charts: Dictionary with chart information
            
        Returns:
            Report with chart placeholders
        """
        if not charts:
            return report
        
        # Add chart section
        chart_section = "\n\n## 📊 Visual Analytics\n\n"
        chart_section += "_[Charts will be displayed when viewing in the application]_\n\n"
        
        for chart_name, chart_info in charts.items():
            chart_section += f"### {chart_info.get('title', chart_name)}\n"
            chart_section += f"_{chart_info.get('description', 'Visualization for ' + chart_name)}_\n\n"
            chart_section += f"**[CHART: {chart_name}]**\n\n"
        
        # Insert before disclaimer
        if "---" in report and "AI-Generated Content" in report:
            parts = report.rsplit("---", 1)
            report = parts[0] + chart_section + "---" + parts[1]
        else:
            report += chart_section
        
        return report
    
    def filter_statistics_by_indicators(
        self,
        statistics: Dict,
        selected_indicators: List[str]
    ) -> Dict:
        """
        Filter statistics to only include selected indicators
        
        Args:
            statistics: Full statistics dictionary
            selected_indicators: List of indicator names to keep
            
        Returns:
            Filtered statistics dictionary
        """
        if not selected_indicators or selected_indicators == ["All available indicators"]:
            return statistics
        
        filtered = statistics.copy()
        
        # Extract indicator names from formatted strings (e.g., "e_inc_num (TB Incidence Cases)" -> "e_inc_num")
        clean_indicators = []
        for ind in selected_indicators:
            if '(' in ind:
                clean_indicators.append(ind.split('(')[0].strip())
            else:
                clean_indicators.append(ind.strip())
        
        # Filter regional summary indicators
        if "regional_summary" in filtered and "indicators" in filtered["regional_summary"]:
            original_indicators = filtered["regional_summary"]["indicators"]
            filtered_indicators = {}
            
            for key in clean_indicators:
                if key in original_indicators:
                    filtered_indicators[key] = original_indicators[key]
                # Also check if the key is in the formatted name
                for orig_key, orig_value in original_indicators.items():
                    if key in orig_key or orig_key in selected_indicators:
                        filtered_indicators[orig_key] = orig_value
            
            filtered["regional_summary"]["indicators"] = filtered_indicators
        
        # Filter country stats indicators
        if "country_stats" in filtered and "indicators" in filtered["country_stats"]:
            original_indicators = filtered["country_stats"]["indicators"]
            filtered_indicators = {}
            
            for key in clean_indicators:
                if key in original_indicators:
                    filtered_indicators[key] = original_indicators[key]
                for orig_key, orig_value in original_indicators.items():
                    if key in orig_key or orig_key in selected_indicators:
                        filtered_indicators[orig_key] = orig_value
            
            filtered["country_stats"]["indicators"] = filtered_indicators
        
        # Filter trend analyses
        if "trend_analyses" in filtered:
            original_trends = filtered["trend_analyses"]
            filtered_trends = {}
            
            for key in clean_indicators:
                if key in original_trends:
                    filtered_trends[key] = original_trends[key]
                for orig_key, orig_value in original_trends.items():
                    if key in orig_key or orig_key in selected_indicators:
                        filtered_trends[orig_key] = orig_value
            
            filtered["trend_analyses"] = filtered_trends
        
        # Filter top countries
        if "top_countries" in filtered:
            original_top = filtered["top_countries"]
            filtered_top = {}
            
            for key in clean_indicators:
                if key in original_top:
                    filtered_top[key] = original_top[key]
                for orig_key, orig_value in original_top.items():
                    if key in orig_key or orig_key in selected_indicators:
                        filtered_top[orig_key] = orig_value
            
            filtered["top_countries"] = filtered_top
        
        return filtered

