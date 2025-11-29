"""
RDHUB Analytics Copilot - Pydantic AI Implementation
Advanced chatbot for WHO AFRO Regional Data Hub analytics
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Try to import analytics modules
try:
    from tb_burden_analytics import TBBurdenAnalytics
    from tb_notif_outcomes_analytics import TBNotificationsOutcomesAnalytics
    from mortality_analytics import MaternalMortalityAnalytics, ChildMortalityAnalytics
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False


class RDHUBDependencies(BaseModel):
    """Dependencies for RDHUB chatbot"""
    tb_burden_analytics: Optional[Any] = None
    tb_notif_analytics: Optional[Any] = None
    maternal_analytics: Optional[Any] = None
    child_analytics: Optional[Any] = None
    health_topic: str = "Tuberculosis"


# System prompt for RDHUB Analytics Copilot
SYSTEM_PROMPT = """You are RDHUB Analytics Copilot for the WHO AFRO Regional Data Hub.

**Scope (current content):**
- Tuberculosis (TB) analytics: TB Burden, TB Notifications, TB Treatment Outcomes
- Maternal + Child Mortality analytics
- Coverage: 47 WHO AFRO countries
- Time period: Historical trends (2000-2024) and projections (to 2030 where available)

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

**Indicator Aliases:**
TB: "TB incidence" → "Estimated TB incidence (per 100,000)", "TB deaths" → "Estimated TB deaths", "TB mortality rate" → "TB mortality rate (per 100,000)", "Case detection" → "TB case notification rate", "TB/HIV" → "TB/HIV coinfection (%)"
Maternal: "MMR" → "Maternal mortality ratio (per 100,000 live births)"
Child: "U5MR" → "Under-five mortality rate (per 1,000 live births)", "Infant mortality" → "Infant mortality rate (per 1,000 live births)", "Neonatal mortality" → "Neonatal mortality rate (per 1,000 live births)"

**Tone:** Professional, crisp, and neutral. Avoid hype. Focus on actionable insights for ministries/WHO teams."""


class RDHUBChatbot:
    """Pydantic AI-based chatbot for RDHUB Analytics"""
    
    def __init__(self, dependencies: RDHUBDependencies):
        """
        Initialize RDHUB chatbot with Pydantic AI
        
        Args:
            dependencies: RDHUBDependencies containing analytics instances
        """
        self.dependencies = dependencies
        
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY or OPENROUTER_API_KEY must be set")
        
        # Initialize Pydantic AI agent
        model = OpenAIModel("gpt-4o-mini", api_key=api_key)
        
        self.agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            dependencies=dependencies
        )
    
    async def process_query_async(self, query: str) -> Dict[str, Any]:
        """
        Process user query asynchronously
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with 'text' and optional 'chart' keys
        """
        try:
            result = await self.agent.run(query)
            return {
                "text": result.data,
                "chart": None  # Charts can be added later if needed
            }
        except Exception as e:
            return {
                "text": f"I encountered an error processing your query: {str(e)}\n\nPlease try rephrasing your question.",
                "chart": None
            }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process user query (synchronous wrapper)
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with 'text' and optional 'chart' keys
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.process_query_async(query))
