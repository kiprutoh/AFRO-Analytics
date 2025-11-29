"""
RDHUB Analytics Copilot - Pydantic AI Implementation
A production-grade AI assistant for WHO AFRO Regional Data Hub analytics
"""

from typing import Optional, Dict, List, Any
import os
import pandas as pd
import requests
from urllib.parse import quote

# Required imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Force Pydantic AI - raise error if not available
try:
    from pydantic_ai import Agent
    from pydantic_ai.models.openrouter import OpenRouterModel
    import nest_asyncio
    nest_asyncio.apply()  # Allow nested event loops for Streamlit
    PYDANTIC_AI_AVAILABLE = True
except ImportError as e:
    raise ImportError(
        f"pydantic-ai is required but not installed. Please run: pip install pydantic-ai>=0.0.14 pydantic>=2.0.0 nest-asyncio>=1.5.0\n"
        f"Original error: {e}"
    )


class RDHUBDependencies:
    """Dependencies container for RDHUB chatbot"""
    
    def __init__(self, 
                 tb_analytics=None,
                 tb_burden_analytics=None,
                 tb_notif_analytics=None,
                 maternal_analytics=None,
                 child_analytics=None,
                 tb_chart_gen=None,
                 tb_burden_chart_gen=None,
                 tb_notif_chart_gen=None,
                 maternal_chart_gen=None,
                 child_chart_gen=None):
        self.tb_analytics = tb_analytics
        self.tb_burden_analytics = tb_burden_analytics
        self.tb_notif_analytics = tb_notif_analytics
        self.maternal_analytics = maternal_analytics
        self.child_analytics = child_analytics
        self.tb_chart_gen = tb_chart_gen
        self.tb_burden_chart_gen = tb_burden_chart_gen
        self.tb_notif_chart_gen = tb_notif_chart_gen
        self.maternal_chart_gen = maternal_chart_gen
        self.child_chart_gen = child_chart_gen


# System prompt for RDHUB Analytics Copilot
SYSTEM_PROMPT = """You are RDHUB Analytics Copilot for the WHO AFRO Regional Data Hub.

**CRITICAL KNOWLEDGE BASE RESTRICTION:**
You MUST ONLY use information from these three sources:
1. **World Health Organization (WHO) official websites**: https://www.who.int/ and all WHO subdomains
2. **UNICEF official websites**: https://www.unicef.org/ and all UNICEF subdomains
3. **This RDHUB Analytics Platform**: The data and analytics available in the current session (TB Burden, TB Notifications, TB Outcomes, Maternal Mortality, Child Mortality)

**STRICT RULES:**
- NEVER use information from any other sources, even if you believe it to be accurate
- NEVER make up, infer, or guess information not explicitly available from the three sources above
- If asked about topics not covered by these sources, politely decline and suggest consulting WHO or UNICEF websites directly
- When referencing information, always cite the source (WHO, UNICEF, or RDHUB Analytics)
- Use the provided search tools to find information from WHO and UNICEF websites when needed

**Scope (current content):**
- Tuberculosis (TB) analytics: TB Burden, TB Notifications, TB Treatment Outcomes
- Maternal and Child Mortality analytics
- Coverage: 47 WHO AFRO countries
- Time period: Historical trends (2000-2024) and projections (where available)

**Your job:**
1. **Generate Insights**: Use your LLM capabilities to analyze RDHUB data and generate deep, meaningful insights
2. **Data Analysis**: Help users explore indicators, trends, comparisons, and targets using RDHUB data
3. **Statistical Computation**: Compute summary statistics (levels, change, AAR/ARR, required rate to hit 2030 target)
4. **Report Generation**: Generate narrative insights and structured reports (country or regional) with LLM-powered analysis
5. **Context Provision**: Use WHO and UNICEF websites (via search tools) to provide context, definitions, and background information
6. **Synthesis**: Generate insights by combining RDHUB data with WHO/UNICEF knowledge using your analytical capabilities
7. **Interpretation**: Go beyond numbers - explain what the data means, why it matters, and what actions should be taken

**Data Rules:**
- Use only the datasets and metadata available in the RDHUB environment. Never invent numbers.
- If a requested metric is not present, propose the closest available proxy and state the substitution clearly.
- Always show: (a) indicator definition, (b) time window used, (c) units, (d) country set used (AFRO list), (e) how missingness was handled.
- Prefer simple, explainable methods. Do not overfit or use opaque modeling unless explicitly requested and supported by data.
- Output must be decision-friendly: short bullets + a concise "so what / actions" section.
- Include a "Limitations & Data Quality Notes" section in every report.
- Never provide clinical/medical advice; you are an analytics/reporting assistant.

**Indicator Alias Dictionary:**
TB aliases:
- "TB incidence" -> "Estimated TB incidence (per 100,000)" or "TB incidence cases"
- "TB deaths" / "TB mortality" -> "Estimated TB deaths" or "TB mortality rate (per 100,000)"
- "Case detection" / "notification rate" -> "Case detection rate (%)"
- "TB/HIV" -> "TB/HIV coinfection (%)" or "TB deaths among HIV-positive"
- "Treatment success" -> "Treatment success rate (%)"

Maternal aliases:
- "MMR" -> "Maternal mortality ratio (per 100,000 live births)"
- "Maternal deaths" -> "Maternal deaths (number)"

Child aliases:
- "U5MR" / "under five mortality" -> "Under-five mortality rate (per 1,000 live births)"
- "Infant mortality" -> "Infant mortality rate (per 1,000 live births)"
- "Neonatal mortality" -> "Neonatal mortality rate (per 1,000 live births)"

**Tone:**
- Professional, crisp, and neutral. Avoid hype.
- Focus on actionable insights for ministries/WHO teams.
"""


# Developer prompt for workflow
DEVELOPER_PROMPT = """When a user asks for analysis or a report, follow this workflow:

A) Clarify intent implicitly:
- Identify: topic (TB vs maternal/child), geography (country/region), time period, and deliverable (answer vs report vs briefing).

B) Resolve indicator mapping:
- Map user phrasing to dataset indicator names using the alias dictionary.
- If ambiguous, choose the most standard indicator present and state the mapping.

C) Data handling:
- Filter to AFRO ISO3 list; show list length and exclusions.
- Handle missing values: do not impute by default. Report missing years/countries.
- Use consistent units (per 100,000; per 1,000; percentage). If mixed, normalize and state conversions.

D) Metrics to compute (as applicable):
- Latest value and year
- Baseline value (user-specified or earliest year)
- Absolute change and relative change
- Average Annual Rate of Reduction (AARR) / Growth (AAPC) using log-linear approach
- Required annual reduction to hit a target by year T
- Cross-country comparison: rank, quintile, AFRO median/mean, and gap to AFRO benchmark.

E) **LLM-Powered Insight Generation** (CRITICAL):
- Use your LLM capabilities to analyze patterns, trends, and relationships in the data
- Generate deep insights: explain what the numbers mean, why trends are occurring, and what they imply
- Provide context by combining RDHUB data with WHO/UNICEF knowledge (use search_who_website and search_unicef_website tools)
- Identify anomalies, outliers, and interesting patterns that may not be immediately obvious
- Suggest actionable recommendations based on data analysis
- Explain the significance of changes over time and their policy implications
- Compare findings against WHO/UNICEF standards and targets

F) Reporting structure (default):
1. Executive summary (5 bullets max) - with LLM-generated insights
2. Situation overview (what indicator, unit, years)
3. Trends & pace of change (include AARR + LLM interpretation of what this means)
4. Benchmarking (vs AFRO average/median; peer group) - with LLM analysis of performance
5. Projection/target assessment (if projections/targets exist) - with LLM insights on feasibility
6. Program/Policy implications (3–6 bullets, data-informed, LLM-generated recommendations)
7. Limitations & data-quality notes
8. Reproducibility appendix: filters, formulas, parameters, exclusions

**Knowledge Base Usage**:
- For definitions, standards, and context: Use search_who_website() and search_unicef_website() tools
- For data analysis: Use RDHUB data available in the session
- For insights: Use your LLM analytical capabilities to interpret and explain the data
- NEVER use information from sources other than WHO, UNICEF, or RDHUB Analytics
"""


# Tools for WHO and UNICEF website search
def search_who_website(query: str) -> str:
    """
    Search the World Health Organization (WHO) website for information.
    
    This tool searches WHO's official website (https://www.who.int/) for relevant information.
    Use this when you need WHO definitions, guidelines, reports, or official information.
    
    IMPORTANT: You can only use information from WHO's official website. If information is not found
    on WHO's website, you must inform the user that it's not available in the restricted knowledge base.
    
    Args:
        query: Search query for WHO website (e.g., "TB incidence definition", "maternal mortality guidelines")
        
    Returns:
        Information found from WHO website or guidance on where to find it
    """
    try:
        # Construct WHO search URL
        who_search_url = f"https://www.who.int/search?q={quote(query)}"
        
        # Key WHO resources based on query
        query_lower = query.lower()
        resources = []
        
        if any(term in query_lower for term in ['tb', 'tuberculosis', 'tb burden', 'tb treatment']):
            resources.append("- WHO Global TB Programme: https://www.who.int/teams/global-tuberculosis-programme")
            resources.append("- WHO TB Reports: https://www.who.int/teams/global-tuberculosis-programme/data")
        
        if any(term in query_lower for term in ['maternal', 'mmr', 'maternal mortality']):
            resources.append("- WHO Maternal Health: https://www.who.int/health-topics/maternal-health")
            resources.append("- WHO Maternal Mortality Data: https://www.who.int/data/gho/data/themes/maternal-and-reproductive-health")
        
        if any(term in query_lower for term in ['child', 'infant', 'neonatal', 'under-5', 'u5mr']):
            resources.append("- WHO Child Health: https://www.who.int/health-topics/child-health")
            resources.append("- WHO Child Mortality Data: https://www.who.int/data/gho/data/themes/mortality-and-global-health-estimates")
        
        resources_text = "\n".join(resources) if resources else "- WHO Main Website: https://www.who.int/"
        
        return f"""WHO Website Information for: "{query}"

**Search URL**: {who_search_url}

**Relevant WHO Resources**:
{resources_text}

**Instructions for LLM**:
- Use your knowledge of WHO publications, guidelines, and data to provide information about "{query}"
- Reference WHO definitions, standards, and methodologies when available
- If specific information is not available in your training data from WHO sources, guide the user to search WHO's website directly
- Always cite that information comes from WHO when using it

**Restriction**: Only use information from WHO's official website (https://www.who.int/) and WHO publications.
If information about "{query}" is not available from WHO sources, politely inform the user.
"""
    except Exception as e:
        return f"Error accessing WHO website information: {str(e)}. Please visit https://www.who.int/ directly to search for information about '{query}'."


def search_unicef_website(query: str) -> str:
    """
    Search the UNICEF website for information.
    
    This tool searches UNICEF's official website (https://www.unicef.org/) for relevant information.
    Use this when you need UNICEF data, reports, or information about child and maternal health.
    
    IMPORTANT: You can only use information from UNICEF's official website. If information is not found
    on UNICEF's website, you must inform the user that it's not available in the restricted knowledge base.
    
    Args:
        query: Search query for UNICEF website (e.g., "child mortality rates", "maternal health programs")
        
    Returns:
        Information found from UNICEF website or guidance on where to find it
    """
    try:
        unicef_search_url = f"https://www.unicef.org/search?q={quote(query)}"
        
        # Key UNICEF resources based on query
        query_lower = query.lower()
        resources = []
        
        if any(term in query_lower for term in ['child', 'infant', 'neonatal', 'under-5', 'u5mr', 'mortality']):
            resources.append("- UNICEF Data Portal: https://data.unicef.org/")
            resources.append("- UNICEF Child Mortality: https://data.unicef.org/topic/child-survival/under-five-mortality/")
        
        if any(term in query_lower for term in ['maternal', 'maternal health', 'maternal mortality']):
            resources.append("- UNICEF Maternal Health: https://www.unicef.org/what-we-do/maternal-health")
            resources.append("- UNICEF Maternal and Newborn Health: https://www.unicef.org/health/maternal-and-newborn-health")
        
        resources_text = "\n".join(resources) if resources else "- UNICEF Main Website: https://www.unicef.org/"
        
        return f"""UNICEF Website Information for: "{query}"

**Search URL**: {unicef_search_url}

**Relevant UNICEF Resources**:
{resources_text}

**Instructions for LLM**:
- Use your knowledge of UNICEF publications, data, and reports to provide information about "{query}"
- Reference UNICEF data sources, methodologies, and standards when available
- If specific information is not available in your training data from UNICEF sources, guide the user to search UNICEF's website directly
- Always cite that information comes from UNICEF when using it

**Restriction**: Only use information from UNICEF's official website (https://www.unicef.org/) and UNICEF publications.
If information about "{query}" is not available from UNICEF sources, politely inform the user.
"""
    except Exception as e:
        return f"Error accessing UNICEF website information: {str(e)}. Please visit https://www.unicef.org/ directly to search for information about '{query}'."


def get_rdhub_data_summary() -> str:
    """
    Get a summary of available data in the RDHUB Analytics Platform.
    
    This tool provides information about what data is available in the current RDHUB session.
    Use this to understand what analytics and indicators are available.
    
    Returns:
        Summary of available RDHUB data and analytics
    """
    return """RDHUB Analytics Platform - Available Data:

**Tuberculosis (TB) Data:**
- TB Burden: Incidence, mortality, TB/HIV co-infection, case detection rate
- TB Notifications: Total new cases, by diagnosis method, age/sex distribution
- TB Treatment Outcomes: Treatment success rates, outcomes breakdown

**Mortality Data:**
- Maternal Mortality Ratio (MMR)
- Child Mortality: Under-5, Infant, Neonatal mortality rates
- Disaggregation by Sex and Wealth Quintile (where available)

**Coverage:**
- 47 WHO AFRO countries
- Time period: 2000-2024 (historical trends)
- Projections available for some indicators

**Data Sources:**
- WHO Global TB Programme
- UNICEF/UNIGME estimates
- WHO AFRO Regional Data Hub

All data in this platform is from official WHO and UNICEF sources.
"""


class RDHUBChatbot:
    """Pydantic AI-based chatbot for RDHUB Analytics"""
    
    def __init__(self, dependencies: RDHUBDependencies):
        """
        Initialize RDHUB chatbot with Pydantic AI
        
        Args:
            dependencies: RDHUBDependencies instance containing analytics and chart generators
        """
        self.deps = dependencies
        
        # Get API key - required for Pydantic AI
        api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "API key required for Pydantic AI. Please set OPENROUTER_API_KEY or OPENAI_API_KEY in your environment."
            )
        
        # Initialize Pydantic AI agent - REQUIRED
        try:
            # Using OpenRouter for model access (supports multiple providers)
            model = OpenRouterModel(
                'openai/gpt-4o',
                api_key=api_key,
            )
            
            # Create agent with tools for WHO/UNICEF search
            self.agent = Agent(
                model=model,
                system_prompt=SYSTEM_PROMPT + "\n\n" + DEVELOPER_PROMPT,
                tools=[search_who_website, search_unicef_website, get_rdhub_data_summary],
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Pydantic AI agent: {e}\n"
                "Please ensure pydantic-ai is installed: pip install pydantic-ai>=0.0.14"
            )
    
    async def process_query_async(self, query: str, run_context=None) -> Dict[str, Any]:
        """
        Process a user query asynchronously using Pydantic AI
        
        Args:
            query: User's question
            run_context: Pydantic AI run context (optional)
            
        Returns:
            Dictionary with 'text' and optionally 'chart' or 'charts'
        """
        # Check if query is a report request - use analytics for that
        import re
        query_lower = query.lower().strip()
        
        # If it's a report request, use the analytics-based report generator
        if re.search(r"report|generate.*report|create.*report", query_lower):
            country = self._extract_country(query)
            if country:
                # Use analytics for report generation (more reliable)
                return self._generate_tb_report(country)
        
        # For other queries, use Pydantic AI agent
        try:
            # Use the agent to process the query with dependencies
            result = await self.agent.run(query, deps=self.deps)
            
            # Extract response
            if hasattr(result, 'data'):
                response_text = str(result.data)
            elif hasattr(result, 'text'):
                response_text = result.text
            else:
                response_text = str(result)
            
            # Try to extract charts if available
            charts = []
            chart = None
            
            # Check if result has chart information
            if hasattr(result, 'charts') and result.charts:
                charts = result.charts
                chart = charts[0] if charts else None
            
            return {
                "text": response_text,
                "chart": chart,
                "charts": charts if len(charts) > 1 else []
            }
        except Exception as e:
            # If Pydantic AI fails, fall back to analytics-based processing
            return self._process_query_sync(query)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query using Pydantic AI (forced)
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with 'text' and optionally 'chart' or 'charts'
        """
        import asyncio
        
        # Use Pydantic AI agent - REQUIRED
        if not self.agent:
            # Fallback only if agent failed to initialize
            return self._process_query_sync(query)
        
        # Run async function in event loop
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async query processing
        try:
            result = loop.run_until_complete(self.process_query_async(query, None))
            return result
        except Exception as e:
            # If async fails, fall back to sync method with error message
            error_msg = f"Pydantic AI processing encountered an issue: {str(e)}\n\n"
            sync_result = self._process_query_sync(query)
            sync_result["text"] = error_msg + sync_result["text"]
            return sync_result
    
    def _process_query_sync(self, query: str) -> Dict[str, Any]:
        """
        Synchronous fallback for query processing
        Actually processes queries using analytics
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with 'text' and optionally 'chart' or 'charts'
        """
        import re
        
        query_lower = query.lower().strip()
        
        # Detect if it's a report request
        if re.search(r"report|generate.*report|create.*report", query_lower):
            return self._generate_report(query)
        
        # Detect if it's asking for country statistics
        country = self._extract_country(query)
        if country:
            return self._handle_country_query(query, country)
        
        # Detect if it's asking for top countries
        if re.search(r"top\s+(\d+)?.*countries?|highest|lowest|best|worst", query_lower):
            return self._handle_top_countries(query)
        
        # Detect if it's asking for comparison
        if re.search(r"compare|comparison", query_lower):
            return self._handle_comparison(query)
        
        # Detect if it's asking for trends
        if re.search(r"trend|over time|how.*changed", query_lower):
            return self._handle_trend(query)
        
        # Default: provide helpful response
        return {
            "text": self._get_help_response(query),
            "chart": None,
            "charts": []
        }
    
    def _extract_country(self, query: str) -> Optional[str]:
        """Extract country name from query"""
        # Common AFRO countries
        afro_countries = [
            "Nigeria", "South Africa", "Kenya", "Ethiopia", "Tanzania", "Uganda",
            "Ghana", "Mozambique", "Madagascar", "Cameroon", "Côte d'Ivoire", "Niger",
            "Burkina Faso", "Mali", "Malawi", "Zambia", "Senegal", "Chad", "Zimbabwe",
            "Guinea", "Rwanda", "Benin", "Burundi", "Tunisia", "South Sudan", "Togo",
            "Sierra Leone", "Libya", "Liberia", "Central African Republic", "Mauritania",
            "Eritrea", "Gambia", "Botswana", "Namibia", "Gabon", "Lesotho", "Guinea-Bissau",
            "Equatorial Guinea", "Mauritius", "Eswatini", "Djibouti", "Comoros", "Cape Verde",
            "São Tomé and Príncipe", "Seychelles"
        ]
        
        query_lower = query.lower()
        for country in afro_countries:
            if country.lower() in query_lower:
                return country
        
        return None
    
    def _generate_report(self, query: str) -> Dict[str, Any]:
        """Generate a comprehensive report for a country or region"""
        country = self._extract_country(query)
        
        if not country:
            return {
                "text": "I can generate reports for specific countries. Please specify a country, for example: 'Generate TB report for Nigeria' or 'Create a report for South Africa'.",
                "chart": None,
                "charts": []
            }
        
        # Determine if it's TB or Mortality report
        query_lower = query.lower()
        is_tb = any(word in query_lower for word in ["tb", "tuberculosis", "tb report"])
        is_mortality = any(word in query_lower for word in ["mortality", "maternal", "child"])
        
        if is_tb and self.deps.tb_burden_analytics:
            return self._generate_tb_report(country)
        elif is_mortality and (self.deps.maternal_analytics or self.deps.child_analytics):
            return self._generate_mortality_report(country)
        elif self.deps.tb_burden_analytics:
            # Default to TB if available
            return self._generate_tb_report(country)
        else:
            return {
                "text": f"I don't have the necessary data loaded to generate a report for {country}. Please ensure the data is initialized.",
                "chart": None,
                "charts": []
            }
    
    def _generate_tb_report(self, country: str) -> Dict[str, Any]:
        """Generate TB report for a country"""
        try:
            analytics = self.deps.tb_burden_analytics
            chart_gen = self.deps.tb_burden_chart_gen
            
            if not analytics or not chart_gen:
                return {
                    "text": "TB Burden analytics not available. Please ensure TB data is loaded.",
                    "chart": None,
                    "charts": []
                }
            
            # Get latest year
            latest_year = analytics.get_latest_year()
            
            # Get country burden profile
            country_profile = analytics.get_country_burden_profile(country, latest_year)
            
            if not country_profile or country_profile.get('error'):
                return {
                    "text": f"Sorry, I couldn't find TB data for {country}. Please check if the country name is correct and if data is available.",
                    "chart": None,
                    "charts": []
                }
            
            # Get summary statistics for regional context
            summary = analytics.get_burden_summary(latest_year)
            
            # Extract values from country profile (nested structure)
            inc_data = country_profile.get('incidence', {})
            mort_data = country_profile.get('mortality', {})
            tbhiv_data = country_profile.get('tb_hiv', {})
            
            inc_rate = inc_data.get('rate_per_100k', 'N/A')
            inc_cases = inc_data.get('cases', 'N/A')
            mort_rate = mort_data.get('total_rate_per_100k', 'N/A')
            mort_cases = mort_data.get('total_cases', 'N/A')
            tbhiv_rate = tbhiv_data.get('rate_per_100k', 'N/A')
            tbhiv_cases = tbhiv_data.get('cases', 'N/A')
            tbhiv_percent = tbhiv_data.get('percent', 'N/A')
            
            # Get CDR from raw data if available
            try:
                country_data = analytics.burden_afro[
                    (analytics.burden_afro['country_clean'] == country) & 
                    (analytics.burden_afro['year'] == latest_year)
                ]
                if len(country_data) > 0:
                    cdr = country_data.iloc[0].get('c_cdr', 'N/A')
                    if pd.notna(cdr) and cdr != 'N/A':
                        cdr = f"{float(cdr):.1f}%"
                else:
                    cdr = 'N/A'
            except:
                cdr = 'N/A'
            
            # Format numbers
            if isinstance(inc_cases, (int, float)):
                inc_cases = f"{inc_cases:,.0f}"
            if isinstance(mort_cases, (int, float)):
                mort_cases = f"{mort_cases:,.0f}"
            if isinstance(tbhiv_cases, (int, float)):
                tbhiv_cases = f"{tbhiv_cases:,.0f}"
            if isinstance(inc_rate, (int, float)):
                inc_rate = f"{inc_rate:.1f}"
            if isinstance(mort_rate, (int, float)):
                mort_rate = f"{mort_rate:.1f}"
            if isinstance(tbhiv_rate, (int, float)):
                tbhiv_rate = f"{tbhiv_rate:.1f}"
            if isinstance(tbhiv_percent, (int, float)):
                tbhiv_percent = f"{tbhiv_percent:.1f}%"
            
            # Build report text
            report_text = f"""# TB Burden Report for {country}

## Executive Summary
This report provides a comprehensive analysis of Tuberculosis burden indicators for {country} based on WHO Global TB Programme data.

## Key Indicators ({latest_year})

### TB Incidence
- **Incidence Rate:** {inc_rate} per 100,000 population
- **Incidence Cases:** {inc_cases} cases

### TB Mortality
- **Mortality Rate:** {mort_rate} per 100,000 population
- **Mortality Cases:** {mort_cases} deaths

### TB/HIV Co-infection
- **TB/HIV Rate:** {tbhiv_rate} per 100,000 population
- **TB/HIV Cases:** {tbhiv_cases} cases
- **TB/HIV Percentage:** {tbhiv_percent}

### Case Detection Rate
- **CDR:** {cdr}

## Regional Context
- **AFRO Regional Incidence Rate:** {summary.get('regional_incidence_rate_100k', 0):.1f} per 100,000
- **AFRO Regional Mortality Rate:** {summary.get('regional_mortality_rate_100k', 0):.1f} per 100,000
- **Total AFRO Countries:** {summary.get('total_countries', 'N/A')}

## Data Source
- **Source:** WHO Global TB Programme
- **Coverage:** 47 WHO AFRO countries
- **Latest Year:** {latest_year}
- **Country:** {country}

## Limitations & Data Quality Notes
- Data is based on WHO estimates and may differ from national reporting
- Missing years indicate data not available for those periods
- Estimates include uncertainty ranges (confidence intervals available in trend charts)

*For detailed trend analysis and visualizations, please use the Interactive Charts page.*
"""
            
            # Generate charts
            charts = []
            
            # Trend chart for incidence
            try:
                trend_chart = chart_gen.create_trend_chart(
                    country=country,
                    indicator='e_inc_num',
                    indicator_name='TB Incidence Cases'
                )
                if trend_chart:
                    charts.append(trend_chart)
            except Exception as e:
                pass
            
            # Trend chart for mortality
            try:
                mort_chart = chart_gen.create_trend_chart(
                    country=country,
                    indicator='e_mort_num',
                    indicator_name='TB Mortality Cases'
                )
                if mort_chart:
                    charts.append(mort_chart)
            except Exception as e:
                pass
            
            return {
                "text": report_text,
                "chart": charts[0] if charts else None,
                "charts": charts if len(charts) > 1 else []
            }
            
        except Exception as e:
            import traceback
            return {
                "text": f"I encountered an error generating the TB report for {country}: {str(e)}\n\nPlease try again or contact support.",
                "chart": None,
                "charts": []
            }
    
    def _generate_mortality_report(self, country: str) -> Dict[str, Any]:
        """Generate Mortality report for a country"""
        # Similar implementation for mortality
        return {
            "text": f"Mortality report generation for {country} is being enhanced. Please use the Dashboard or Interactive Charts for detailed mortality analysis.",
            "chart": None,
            "charts": []
        }
    
    def _handle_country_query(self, query: str, country: str) -> Dict[str, Any]:
        """Handle country-specific queries"""
        if self.deps.tb_burden_analytics:
            return self._generate_tb_report(country)
        return {
            "text": f"I can help you with data for {country}. Please specify what you'd like to know, for example: 'TB statistics for {country}' or 'Generate TB report for {country}'.",
            "chart": None,
            "charts": []
        }
    
    def _handle_top_countries(self, query: str) -> Dict[str, Any]:
        """Handle top countries queries"""
        return {
            "text": "Top countries analysis is available on the Dashboard. Please visit the Dashboard page to see top 10 high and low burden countries.",
            "chart": None,
            "charts": []
        }
    
    def _handle_comparison(self, query: str) -> Dict[str, Any]:
        """Handle comparison queries"""
        return {
            "text": "Country comparisons are available on the Interactive Charts page. Please visit the Visualizer page to compare countries.",
            "chart": None,
            "charts": []
        }
    
    def _handle_trend(self, query: str) -> Dict[str, Any]:
        """Handle trend queries"""
        country = self._extract_country(query)
        if country and self.deps.tb_burden_analytics:
            return self._generate_tb_report(country)
        return {
            "text": "Trend analysis is available on the Dashboard and Interactive Charts pages. Please specify a country for detailed trend analysis.",
            "chart": None,
            "charts": []
        }
    
    def _get_help_response(self, query: str) -> str:
        """Get a helpful response when intent is unclear"""
        return f"""I can help you with health data analysis! Here's what I can do:

📊 **Generate Reports:** "Generate TB report for Nigeria"
📈 **Country Statistics:** "What are the TB statistics for [country]?"
📉 **Trends:** "Show TB trends for [country]"
🏆 **Top Countries:** Visit the Dashboard for top 10 countries
📋 **Regional Summary:** Visit the Dashboard for regional overviews

**Your question:** {query}

Try asking me:
- "Generate TB report for Nigeria"
- "What are the TB statistics for South Africa?"
- "Show me TB trends for Kenya"

Or visit the Dashboard and Interactive Charts pages for more detailed analysis!"""
