"""
RDHUB Analytics Copilot - Pydantic AI Implementation
A production-grade AI assistant for WHO AFRO Regional Data Hub analytics
"""

from typing import Optional, Dict, List, Any
from pydantic_ai import Agent
from pydantic_ai.models import OpenRouterModel
import os
from dotenv import load_dotenv

load_dotenv()


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

**Scope (current content):**
- Tuberculosis (TB) analytics: TB Burden, TB Notifications, TB Treatment Outcomes
- Maternal and Child Mortality analytics
- Coverage: 47 WHO AFRO countries
- Time period: Historical trends (2000-2024) and projections (where available)

**Your job:**
1. Help users explore indicators, trends, comparisons, and targets
2. Compute summary statistics (levels, change, AAR/ARR, required rate to hit 2030 target)
3. Generate narrative insights and structured reports (country or regional)
4. Provide transparent methods and assumptions and flag data limitations

**Rules:**
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

E) Reporting structure (default):
1. Executive summary (5 bullets max)
2. Situation overview (what indicator, unit, years)
3. Trends & pace of change (include AARR + interpretation)
4. Benchmarking (vs AFRO average/median; peer group)
5. Projection/target assessment (if projections/targets exist)
6. Program/Policy implications (3–6 bullets, data-informed)
7. Limitations & data-quality notes
8. Reproducibility appendix: filters, formulas, parameters, exclusions
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
        
        # Get API key
        api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY must be set in environment")
        
        # Initialize Pydantic AI agent
        # Using OpenRouter for model access
        model = OpenRouterModel(
            'openai/gpt-4o',
            api_key=api_key,
        )
        
        self.agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT + "\n\n" + DEVELOPER_PROMPT,
        )
    
    async def process_query_async(self, query: str, run_context) -> Dict[str, Any]:
        """
        Process a user query asynchronously using Pydantic AI
        
        Args:
            query: User's question
            run_context: Pydantic AI run context
            
        Returns:
            Dictionary with 'text' and optionally 'chart' or 'charts'
        """
        # Use the agent to process the query
        result = await self.agent.run(query, deps=self.deps)
        
        # Extract response
        response_text = result.data if hasattr(result, 'data') else str(result)
        
        # For now, return text response
        # Chart generation can be added as tools/functions in the agent
        return {
            "text": response_text,
            "chart": None,
            "charts": []
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query synchronously (wrapper for async)
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with 'text' and optionally 'chart' or 'charts'
        """
        import asyncio
        
        # Try to get existing event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run async function
        if loop.is_running():
            # If loop is already running, we need to use a different approach
            # For Streamlit, we'll use a simpler synchronous approach
            return self._process_query_sync(query)
        else:
            return loop.run_until_complete(self.process_query_async(query, None))
    
    def _process_query_sync(self, query: str) -> Dict[str, Any]:
        """
        Synchronous fallback for query processing
        Uses a simpler approach when async is not available
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with 'text' and optionally 'chart' or 'charts'
        """
        # For now, provide a helpful response indicating the chatbot is available
        # Full Pydantic AI integration will be enhanced with proper async handling
        response = f"""I'm your RDHUB Analytics Copilot. I can help you explore:

📊 **Tuberculosis Data:**
- TB Burden (incidence, mortality, TB/HIV, case detection rate)
- TB Notifications (by type, age/sex distribution)
- TB Treatment Outcomes (success rates, outcomes breakdown)

📈 **Mortality Data:**
- Maternal Mortality Ratio (MMR)
- Child Mortality (Under-5, Infant, Neonatal)

**Your question:** {query}

I'm processing your request. Please try asking specific questions like:
- "What are the top 10 countries with highest TB incidence?"
- "Show me TB treatment success rates for 2023"
- "What is the maternal mortality ratio for Nigeria?"
- "Compare child mortality rates across AFRO countries"

*Note: Full Pydantic AI integration is being enhanced for advanced analytics.*
"""
        
        return {
            "text": response,
            "chart": None,
            "charts": []
        }
