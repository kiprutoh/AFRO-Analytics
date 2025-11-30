"""
AI Analytics Navigator - Pydantic AI-based chatbot for platform analytics
Uses Pydantic AI to provide intelligent navigation and analysis of health data
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openrouter import OpenRouterModel
import os


# Define dependencies for the agent
class AnalyticsDependencies(BaseModel):
    """Dependencies injected into the AI Analytics Navigator"""
    health_topic: str = Field(description="Current health topic (Tuberculosis or Mortality)")
    maternal_analytics: Optional[Any] = Field(default=None, description="Maternal mortality analytics")
    child_analytics: Optional[Any] = Field(default=None, description="Child mortality analytics")
    tb_analytics: Optional[Any] = Field(default=None, description="TB analytics")
    tb_burden_analytics: Optional[Any] = Field(default=None, description="TB burden analytics")
    tb_notif_analytics: Optional[Any] = Field(default=None, description="TB notifications/outcomes analytics")
    maternal_chart_gen: Optional[Any] = Field(default=None, description="Maternal chart generator")
    child_chart_gen: Optional[Any] = Field(default=None, description="Child chart generator")
    tb_chart_gen: Optional[Any] = Field(default=None, description="TB chart generator")


# Define output structure
class NavigatorResponse(BaseModel):
    """Response from AI Analytics Navigator"""
    answer: str = Field(description="Main answer to the user's question")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested next actions or queries")
    data_summary: Optional[str] = Field(default=None, description="Summary of relevant data found")
    needs_chart: bool = Field(default=False, description="Whether a chart should be generated")


def get_analytics_navigator(api_key: Optional[str] = None) -> Agent:
    """Create and configure the AI Analytics Navigator agent"""
    
    # Use OpenRouter model (supports multiple providers)
    model_name = os.getenv("OPENROUTER_MODEL", "openrouter/anthropic/claude-3.5-sonnet")
    
    # Get API key from parameter, environment, or session state
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY") or st.session_state.get("openrouter_api_key")
    
    if not api_key:
        raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or provide in session state.")
    
    # OpenRouterModel reads API key from OPENROUTER_API_KEY environment variable
    # Temporarily set it if not already set
    original_key = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = api_key
    
    try:
        # OpenRouterModel reads from environment variable, not constructor parameter
        model = OpenRouterModel(model_name)
    finally:
        # Restore original key if it existed
        if original_key:
            os.environ["OPENROUTER_API_KEY"] = original_key
        elif "OPENROUTER_API_KEY" in os.environ:
            # Only delete if we set it (not if it was already there)
            pass  # Keep it set for the model to use
    
    # Create agent with system instructions
    agent = Agent(
        model,
        deps_type=AnalyticsDependencies,
        output_type=NavigatorResponse,
        system_prompt="""You are the AI Analytics Navigator for the WHO AFRO Regional Health Data Hub.

Your role is to help users navigate and analyze health data from the platform. You have access to:
- Tuberculosis (TB) data: burden estimates, notifications, treatment outcomes
- Mortality data: maternal mortality ratio (MMR), child mortality rates (U5MR, IMR, NMR)

When users ask questions:
1. Provide clear, accurate answers based on available data
2. Suggest relevant follow-up questions or analyses
3. Identify what data is available for their query
4. Guide them to the right sections of the platform

Always be helpful, accurate, and focus on data-driven insights. If you don't have access to specific data, guide users on how to find it or what they can explore."""
    )
    
    # Register tools for data access
    @agent.tool
    async def get_country_list(ctx: RunContext[AnalyticsDependencies]) -> List[str]:
        """Get list of available countries in the dataset"""
        deps = ctx.deps
        countries = []
        
        if deps.health_topic == "Mortality":
            if deps.child_analytics and hasattr(deps.child_analytics, 'get_country_list'):
                try:
                    countries = deps.child_analytics.get_country_list()
                except:
                    pass
        elif deps.health_topic == "Tuberculosis":
            if deps.tb_analytics and hasattr(deps.tb_analytics, 'get_country_list'):
                try:
                    countries = deps.tb_analytics.get_country_list()
                except:
                    pass
        
        return countries if countries else ["No countries available"]
    
    @agent.tool
    async def get_available_indicators(ctx: RunContext[AnalyticsDependencies]) -> Dict[str, List[str]]:
        """Get list of available indicators by topic"""
        deps = ctx.deps
        indicators = {}
        
        if deps.health_topic == "Mortality":
            if deps.child_analytics and hasattr(deps.child_analytics, 'get_indicators'):
                try:
                    indicators["child_mortality"] = deps.child_analytics.get_indicators()
                except:
                    pass
            if deps.maternal_analytics:
                indicators["maternal_mortality"] = ["Maternal Mortality Ratio (MMR)"]
        elif deps.health_topic == "Tuberculosis":
            indicators["tb"] = [
                "TB Incidence Rate",
                "TB Mortality Rate",
                "TB/HIV Co-infection Rate",
                "Case Detection Rate",
                "Treatment Success Rate"
            ]
        
        return indicators
    
    @agent.tool
    async def get_country_statistics(ctx: RunContext[AnalyticsDependencies], country: str) -> Dict[str, Any]:
        """Get statistics for a specific country"""
        deps = ctx.deps
        stats = {}
        
        if deps.health_topic == "Mortality":
            # Child mortality stats
            if deps.child_analytics:
                try:
                    latest_year = deps.child_analytics.get_latest_year('Under-five mortality rate')
                    top_data = deps.child_analytics.get_top_mortality_countries(
                        indicator='Under-five mortality rate', n=100, year=latest_year, ascending=False
                    )
                    country_data = top_data[top_data['country_clean'] == country]
                    if len(country_data) > 0:
                        stats['under_five_mortality_rate'] = {
                            'value': float(country_data.iloc[0]['value']),
                            'year': int(latest_year)
                        }
                except Exception as e:
                    stats['error'] = str(e)
            
            # Maternal mortality stats
            if deps.maternal_analytics:
                try:
                    latest_year = deps.maternal_analytics.get_latest_year()
                    mmr_data = deps.maternal_analytics.get_top_mmr_countries(n=100, year=latest_year, ascending=False)
                    country_mmr = mmr_data[mmr_data['country_clean'] == country]
                    if len(country_mmr) > 0:
                        stats['maternal_mortality_ratio'] = {
                            'value': float(country_mmr.iloc[0]['mmr']),
                            'year': int(latest_year)
                        }
                except Exception as e:
                    pass
        
        return stats if stats else {"message": f"No statistics found for {country}"}
    
    @agent.tool
    async def get_regional_summary(ctx: RunContext[AnalyticsDependencies]) -> Dict[str, Any]:
        """Get regional summary statistics"""
        deps = ctx.deps
        summary = {}
        
        if deps.health_topic == "Mortality":
            if deps.child_analytics:
                try:
                    latest_year = deps.child_analytics.get_latest_year('Under-five mortality rate')
                    summary_data = deps.child_analytics.get_mortality_summary(latest_year)
                    summary['child_mortality'] = summary_data
                except:
                    pass
            
            if deps.maternal_analytics:
                try:
                    latest_year = deps.maternal_analytics.get_latest_year()
                    summary_data = deps.maternal_analytics.get_mmr_summary(latest_year)
                    summary['maternal_mortality'] = summary_data
                except:
                    pass
        
        return summary if summary else {"message": "No regional summary available"}
    
    @agent.tool
    async def get_top_countries(ctx: RunContext[AnalyticsDependencies], 
                                indicator: str = "Under-five mortality rate",
                                n: int = 10,
                                ascending: bool = False) -> Dict[str, Any]:
        """Get top N countries by indicator"""
        deps = ctx.deps
        result = {}
        
        if deps.health_topic == "Mortality" and deps.child_analytics:
            try:
                latest_year = deps.child_analytics.get_latest_year(indicator)
                top_data = deps.child_analytics.get_top_mortality_countries(
                    indicator=indicator, n=n, year=latest_year, ascending=ascending
                )
                if len(top_data) > 0:
                    result = {
                        'indicator': indicator,
                        'year': int(latest_year),
                        'countries': top_data[['country_clean', 'value']].to_dict('records')
                    }
            except Exception as e:
                result = {'error': str(e)}
        
        return result if result else {"message": f"No data available for {indicator}"}
    
    return agent


def create_navigator_dependencies() -> AnalyticsDependencies:
    """Create dependencies from session state"""
    return AnalyticsDependencies(
        health_topic=st.session_state.get("indicator_type", "Mortality"),
        maternal_analytics=st.session_state.get("maternal_analytics"),
        child_analytics=st.session_state.get("child_analytics"),
        tb_analytics=st.session_state.get("analytics"),
        tb_burden_analytics=st.session_state.get("tb_burden_analytics"),
        tb_notif_analytics=st.session_state.get("tb_notif_analytics"),
        maternal_chart_gen=st.session_state.get("maternal_chart_gen"),
        child_chart_gen=st.session_state.get("child_chart_gen"),
        tb_chart_gen=st.session_state.get("tb_chart_gen")
    )

