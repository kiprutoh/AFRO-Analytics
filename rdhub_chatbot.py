"""
RDHUB Analytics Copilot - Built with Pydantic AI
WHO AFRO Regional Data Hub Analytics Assistant
Focus: Tuberculosis (TB) and Maternal + Child Mortality analytics
"""

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime


# ============================================================================
# OUTPUT MODELS
# ============================================================================

class IndicatorSummary(BaseModel):
    """Summary of an indicator"""
    indicator_name: str = Field(description="Exact indicator name from dataset")
    latest_value: float = Field(description="Latest available value")
    latest_year: int = Field(description="Year of latest value")
    baseline_value: Optional[float] = Field(None, description="Baseline value")
    baseline_year: Optional[int] = Field(None, description="Baseline year")
    absolute_change: Optional[float] = Field(None, description="Absolute change from baseline")
    relative_change: Optional[float] = Field(None, description="Relative change (%)")
    aarr: Optional[float] = Field(None, description="Average Annual Rate of Reduction (%)")
    unit: str = Field(description="Unit of measurement")
    countries_available: int = Field(description="Number of countries with data")


class BenchmarkComparison(BaseModel):
    """Country comparison with AFRO benchmarks"""
    country: str = Field(description="Country name")
    value: float = Field(description="Country value")
    afro_median: float = Field(description="AFRO median")
    afro_mean: float = Field(description="AFRO mean")
    rank: int = Field(description="Rank among AFRO countries")
    quintile: str = Field(description="Quintile (1st, 2nd, 3rd, 4th, 5th)")
    gap_to_median: float = Field(description="Gap to AFRO median")


class TargetAssessment(BaseModel):
    """Target gap and required rate analysis"""
    current_value: float = Field(description="Current value")
    target_value: float = Field(description="Target value")
    target_year: int = Field(description="Target year (typically 2030)")
    gap: float = Field(description="Gap to target")
    required_annual_reduction: float = Field(description="Required annual reduction rate (%)")
    current_aarr: Optional[float] = Field(None, description="Current AARR if available")
    status: str = Field(description="On track / Needs acceleration / Off track")


class AnalyticsReport(BaseModel):
    """Structured analytics report"""
    executive_summary: List[str] = Field(description="5 bullets max")
    situation_overview: Dict[str, Any] = Field(description="Indicator, unit, years, country set")
    trends_pace: Dict[str, Any] = Field(description="Trends and AARR interpretation")
    benchmarking: Dict[str, Any] = Field(description="Comparison with AFRO and peers")
    target_assessment: Optional[TargetAssessment] = Field(None, description="Target gap analysis")
    implications: List[str] = Field(description="3-6 program/policy implications")
    limitations: List[str] = Field(description="Data quality and limitations")
    reproducibility: Dict[str, Any] = Field(description="Filters, formulas, parameters, exclusions")


# ============================================================================
# DEPENDENCIES
# ============================================================================

class RDHUBDependencies(BaseModel):
    """Dependencies injected into the agent"""
    tb_analytics: Optional[Any] = Field(None, description="TB analytics instance")
    tb_burden_analytics: Optional[Any] = Field(None, description="TB burden analytics instance")
    tb_notif_analytics: Optional[Any] = Field(None, description="TB notifications/outcomes analytics")
    maternal_analytics: Optional[Any] = Field(None, description="Maternal mortality analytics")
    child_analytics: Optional[Any] = Field(None, description="Child mortality analytics")
    country_lookup: Optional[pd.DataFrame] = Field(None, description="AFRO countries lookup")
    afro_iso3_list: Optional[List[str]] = Field(None, description="List of AFRO ISO3 codes")


# ============================================================================
# INDICATOR ALIAS DICTIONARY
# ============================================================================

INDICATOR_ALIASES = {
    # TB aliases
    "tb incidence": ["e_inc_100k", "e_inc_num"],
    "tb deaths": ["e_mort_num"],
    "tb mortality rate": ["e_mort_100k"],
    "tb treatment coverage": ["c_cdr"],
    "case detection": ["c_cdr"],
    "notification rate": ["c_newinc"],
    "mdr tb": ["e_rr_pct", "e_rr_num"],
    "rr tb": ["e_rr_pct", "e_rr_num"],
    "tb/hiv": ["e_tbhiv_100k", "e_tbhiv_num"],
    
    # Maternal aliases
    "mmr": ["mmr"],
    "maternal mortality ratio": ["mmr"],
    "maternal deaths": ["mmr"],
    
    # Child aliases
    "u5mr": ["Under-five mortality rate"],
    "under five mortality": ["Under-five mortality rate"],
    "infant mortality": ["Infant mortality rate"],
    "neonatal mortality": ["Neonatal mortality rate"],
    "child mortality 1-4": ["Child mortality rate (aged 1-4 years)"],
}


# ============================================================================
# SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT = """You are RDHUB Analytics Copilot for the WHO AFRO Regional Data Hub.

Scope (current content): Tuberculosis (TB) and Maternal + Child Mortality analytics for the 47 WHO AFRO countries, including trends (historical) and projections (to 2030 where available).

Your job:
1) Help users explore indicators, trends, comparisons, and targets.
2) Compute summary statistics (levels, change, AAR/ARR, required rate to hit 2030 target).
3) Generate narrative insights and structured reports (country or regional).
4) Provide transparent methods and assumptions and flag data limitations.

Rules:
- Use only the datasets and metadata available in the RDHUB environment. Never invent numbers.
- If a requested metric is not present, propose the closest available proxy and state the substitution clearly.
- Always show: (a) indicator definition, (b) time window used, (c) units, (d) country set used (AFRO list), (e) how missingness was handled.
- Prefer simple, explainable methods. Do not overfit or use opaque modeling unless explicitly requested and supported by data.
- Output must be decision-friendly: short bullets + a concise "so what / actions" section.
- Include a "Limitations & Data Quality Notes" section in every report.
- Never provide clinical/medical advice; you are an analytics/reporting assistant.

When analyzing data:
- Filter to AFRO ISO3 list; show list length and exclusions.
- Handle missing values: do not impute by default. Report missing years/countries.
- Use consistent units (per 100,000; per 1,000; percentage). If mixed, normalize and state conversions.

Metrics to compute (as applicable):
- Latest value and year
- Baseline value (user-specified or earliest year)
- Absolute change and relative change
- Average Annual Rate of Reduction (AARR) / Growth (AAPC) using log-linear approach:
  AARR = (1 - (V_latest / V_baseline)^(1/Δyears)) * 100
- Required annual reduction to hit a target by year T:
  Req = (1 - (Target / V_latest)^(1/(T - latest_year))) * 100
- Cross-country comparison: rank, quintile, AFRO median/mean, and gap to AFRO benchmark.

Tone: Professional, crisp, and neutral. Avoid hype. Focus on actionable insights for ministries/WHO teams.
"""


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

def create_rdhub_agent(model: str = "openai:gpt-4o-mini"):
    """Create the RDHUB Analytics Copilot agent"""
    
    agent = Agent(
        model,
        deps_type=RDHUBDependencies,
        system_prompt=SYSTEM_PROMPT,
    )
    
    return agent


# ============================================================================
# TOOLS
# ============================================================================

def register_tools(agent: Agent):
    """Register tools for the agent"""
    
    @agent.tool
    async def get_indicator_summary(
        ctx: RunContext[RDHUBDependencies],
        indicator_alias: str,
        country: Optional[str] = None,
        year: Optional[int] = None
    ) -> IndicatorSummary:
        """
        Get summary statistics for an indicator.
        
        Args:
            indicator_alias: User-friendly indicator name (will be mapped to dataset column)
            country: Optional country name or ISO3 code
            year: Optional specific year (defaults to latest available)
        """
        # Map alias to actual indicator
        indicator_key = indicator_alias.lower()
        actual_indicators = INDICATOR_ALIASES.get(indicator_key, [indicator_alias])
        
        # Try to get data from appropriate analytics
        deps = ctx.deps
        
        # This is a placeholder - actual implementation would query the analytics
        # For now, return a structured response
        return IndicatorSummary(
            indicator_name=actual_indicators[0] if actual_indicators else indicator_alias,
            latest_value=0.0,
            latest_year=2023,
            unit="per 100,000",
            countries_available=47
        )
    
    @agent.tool
    async def calculate_aarr(
        ctx: RunContext[RDHUBDependencies],
        baseline_value: float,
        latest_value: float,
        baseline_year: int,
        latest_year: int
    ) -> float:
        """
        Calculate Average Annual Rate of Reduction (AARR).
        
        Formula: AARR = (1 - (V_latest / V_baseline)^(1/Δyears)) * 100
        """
        if baseline_value <= 0 or latest_value <= 0:
            return 0.0
        
        delta_years = latest_year - baseline_year
        if delta_years <= 0:
            return 0.0
        
        ratio = latest_value / baseline_value
        aarr = (1 - (ratio ** (1 / delta_years))) * 100
        
        return round(aarr, 2)
    
    @agent.tool
    async def calculate_required_rate(
        ctx: RunContext[RDHUBDependencies],
        current_value: float,
        target_value: float,
        current_year: int,
        target_year: int = 2030
    ) -> float:
        """
        Calculate required annual reduction rate to hit target.
        
        Formula: Req = (1 - (Target / V_latest)^(1/(T - latest_year))) * 100
        """
        if current_value <= 0 or target_value <= 0:
            return 0.0
        
        years_to_target = target_year - current_year
        if years_to_target <= 0:
            return 0.0
        
        ratio = target_value / current_value
        required_rate = (1 - (ratio ** (1 / years_to_target))) * 100
        
        return round(required_rate, 2)
    
    @agent.tool
    async def get_country_ranking(
        ctx: RunContext[RDHUBDependencies],
        indicator: str,
        year: Optional[int] = None,
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get country ranking for an indicator.
        
        Returns top 10 and bottom 10 countries, plus AFRO median/mean.
        """
        # Placeholder - actual implementation would query analytics
        return []
    
    @agent.tool
    async def generate_report(
        ctx: RunContext[RDHUBDependencies],
        topic: str,
        geography: str,
        period: str,
        indicators: List[str]
    ) -> AnalyticsReport:
        """
        Generate a full analytical report.
        
        Args:
            topic: TB / Maternal / Child Mortality / Combined
            geography: Country ISO3 or "AFRO Region" or list of countries
            period: e.g., "2000-2023"
            indicators: List of indicators to analyze
        """
        # Placeholder - actual implementation would generate full report
        return AnalyticsReport(
            executive_summary=["Report generation in progress..."],
            situation_overview={},
            trends_pace={},
            benchmarking={},
            implications=[],
            limitations=[],
            reproducibility={}
        )
    
    return agent


# ============================================================================
# MAIN AGENT CREATION
# ============================================================================

def get_rdhub_agent(model: str = "openai:gpt-4o-mini"):
    """Get the configured RDHUB agent with all tools"""
    agent = create_rdhub_agent(model)
    agent = register_tools(agent)
    return agent


# ============================================================================
# STREAMLIT WRAPPER
# ============================================================================

class RDHUBChatbot:
    """Streamlit-compatible wrapper for RDHUB Analytics Copilot"""
    
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        """Initialize the chatbot"""
        self.agent = get_rdhub_agent(model)
        self.model = model
    
    def process_query(
        self,
        query: str,
        tb_analytics=None,
        tb_burden_analytics=None,
        tb_notif_analytics=None,
        maternal_analytics=None,
        child_analytics=None,
        country_lookup=None,
        afro_iso3_list=None
    ) -> Dict[str, Any]:
        """
        Process a user query and return response.
        
        Returns:
            dict with 'text' and optionally 'chart' keys
        """
        import asyncio
        
        # Create dependencies
        deps = RDHUBDependencies(
            tb_analytics=tb_analytics,
            tb_burden_analytics=tb_burden_analytics,
            tb_notif_analytics=tb_notif_analytics,
            maternal_analytics=maternal_analytics,
            child_analytics=child_analytics,
            country_lookup=country_lookup,
            afro_iso3_list=afro_iso3_list
        )
        
        # Run the agent
        try:
            # Handle async execution
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.agent.run(query, deps=deps)
            )
            
            # Extract response text
            response_text = str(result.data) if hasattr(result, 'data') else str(result)
            
            return {
                "text": response_text,
                "chart": None  # Charts can be added later if needed
            }
            
        except Exception as e:
            return {
                "text": f"Error processing query: {str(e)}\n\nPlease try rephrasing your question or check that the system is properly initialized.",
                "chart": None
            }
    
    def get_quick_analysis(self, analysis_type: str, country: str = None) -> str:
        """
        Get quick analysis using predefined prompts.
        
        Args:
            analysis_type: One of:
                - "tb_country_snapshot"
                - "maternal_mmr_trajectory"
                - "child_mortality_analysis"
                - "regional_ranking"
                - "progress_scorecard"
            country: Optional country name or ISO3
        """
        prompts = {
            "tb_country_snapshot": f"For {country or 'selected country'}, summarize TB performance using the latest available year: incidence rate, mortality rate, treatment coverage, and TB/HIV indicator if available. Include: latest value/year, trend since 2015, and comparison vs AFRO median.",
            
            "maternal_mmr_trajectory": f"For {country or 'selected country'}, analyze Maternal Mortality Ratio (MMR) from 2000 to latest year: compute AARR, identify inflection periods, and estimate required annual reduction to reach the 2030 target (if target exists; otherwise use SDG-style target provided in dataset metadata). Generate 6–8 bullet interpretation + limitations.",
            
            "child_mortality_analysis": f"For {country or 'selected country'}, analyze: Under-five mortality rate, Neonatal mortality rate, Infant mortality rate, and Stillbirth rate. Show latest values, pace of change since 2010, and which indicator is improving slowest. End with 3 data/prioritization implications.",
            
            "regional_ranking": f"Rank AFRO countries for selected indicator in the latest year available. Return top 10, bottom 10, AFRO median, and where {country or 'selected country'} sits (if provided). Flag missing countries and explain exclusions.",
            
            "progress_scorecard": f"Build a progress scorecard for {country or 'selected country'} for key indicators. Define thresholds: On track (required rate <= achieved rate + small margin), Needs acceleration (required rate > achieved rate but gap <= 2 percentage points), Off track (gap > 2 percentage points or trend worsening). Return a small table + interpretation."
        }
        
        if analysis_type not in prompts:
            return f"Unknown analysis type: {analysis_type}"
        
        return prompts[analysis_type]

