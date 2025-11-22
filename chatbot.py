"""
Chatbot Module for Mortality Analytics
Handles natural language queries and generates responses
"""

import re
from typing import Dict, List, Optional, Tuple
from analytics import MortalityAnalytics
from data_pipeline import MortalityDataPipeline


class MortalityChatbot:
    """Chatbot for mortality data analysis"""
    
    def __init__(self, analytics: MortalityAnalytics):
        """
        Initialize chatbot with analytics engine
        
        Args:
            analytics: MortalityAnalytics instance
        """
        self.analytics = analytics
        self.pipeline = analytics.pipeline
        
        # Common patterns for intent recognition
        self.patterns = {
            "country_stats": [
                r"statistics?.*\b(country|for|in)\s+([A-Za-z\s]+)",
                r"([A-Za-z\s]+).*statistics?",
                r"how.*\b([A-Za-z\s]+)\s+doing",
                r"tell me about\s+([A-Za-z\s]+)"
            ],
            "compare": [
                r"compare\s+([A-Za-z\s,]+)",
                r"comparison.*\b(between|of)\s+([A-Za-z\s,]+)",
                r"which.*better.*\b([A-Za-z\s,]+)"
            ],
            "indicator": [
                r"(neonatal|infant|under.?five|maternal|mmr|mortality).*rate",
                r"indicator.*\b(neonatal|infant|under.?five|maternal|mmr)"
            ],
            "trend": [
                r"trend.*\b([A-Za-z\s]+)",
                r"([A-Za-z\s]+).*trend",
                r"how.*changed.*\b([A-Za-z\s]+)",
                r"improving|worsening|getting better|getting worse"
            ],
            "projections": [
                r"projection",
                r"2030",
                r"on track",
                r"future",
                r"forecast"
            ],
            "top_countries": [
                r"top\s+(\d+)?.*countries?",
                r"highest|lowest|best|worst.*countries?",
                r"which countries?.*highest|lowest"
            ],
            "summary": [
                r"summary",
                r"overview",
                r"general.*information",
                r"tell me about.*region"
            ]
        }
    
    def process_query(self, query: str) -> str:
        """
        Process user query and generate response
        
        Args:
            query: User's natural language query
        
        Returns:
            Response string
        """
        query_lower = query.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        try:
            if intent == "country_stats":
                return self._handle_country_stats(query_lower)
            elif intent == "compare":
                return self._handle_compare(query_lower)
            elif intent == "trend":
                return self._handle_trend(query_lower)
            elif intent == "projections":
                return self._handle_projections(query_lower)
            elif intent == "top_countries":
                return self._handle_top_countries(query_lower)
            elif intent == "summary":
                return self._handle_summary(query_lower)
            elif intent == "indicator":
                return self._handle_indicator_info(query_lower)
            else:
                return self._handle_general_query(query_lower)
        except Exception as e:
            return f"I encountered an error processing your query: {str(e)}\n\nPlease try rephrasing your question or ask for help."
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        return "general"
    
    def _extract_country(self, query: str) -> Optional[str]:
        """Extract country name from query"""
        countries = self.pipeline.get_countries()
        query_lower = query.lower()
        
        # Sort countries by length (longest first) to match multi-word countries first
        sorted_countries = sorted(countries, key=len, reverse=True)
        
        # Try to find country name (exact match first)
        for country in sorted_countries:
            country_lower = country.lower()
            # Check if country name appears as whole word/phrase
            if country_lower in query_lower:
                # Verify it's not part of another word
                idx = query_lower.find(country_lower)
                if idx == 0 or query_lower[idx-1] == ' ':
                    if idx + len(country_lower) == len(query_lower) or query_lower[idx + len(country_lower)] in [' ', ',', '.', '?', '!']:
                        return country
        
        return None
    
    def _extract_indicator(self, query: str) -> Optional[str]:
        """Extract indicator name from query"""
        indicators = self.pipeline.get_indicators()
        
        query_lower = query.lower()
        
        # Map common terms to indicators
        indicator_map = {
            "neonatal": "Neonatal mortality rate",
            "infant": "Infant mortality rate",
            "under.?five": "Under-five mortality rate",
            "under 5": "Under-five mortality rate",
            "maternal": "MMR",
            "mmr": "MMR"
        }
        
        for term, indicator in indicator_map.items():
            if re.search(term, query_lower):
                return indicator
        
        # Try exact match
        for indicator in indicators:
            if indicator.lower() in query_lower:
                return indicator
        
        return None
    
    def _handle_country_stats(self, query: str) -> str:
        """Handle country statistics queries"""
        country = self._extract_country(query)
        
        if not country:
            return "I couldn't identify which country you're asking about. Please specify a country name, for example: 'What are the statistics for Kenya?'"
        
        stats = self.analytics.get_country_statistics(country)
        
        response = [f"📊 Statistics for {country}:\n"]
        
        if stats["indicators"]:
            response.append("Mortality Indicators:")
            for indicator, data in list(stats["indicators"].items())[:5]:
                response.append(f"\n• {indicator}:")
                response.append(f"  Latest Value: {data['latest_value']:.2f}")
                response.append(f"  Average: {data['mean_value']:.2f}")
                response.append(f"  Trend: {data['trend']}")
        
        if stats["mmr_trend"]:
            response.append(f"\n• Maternal Mortality Ratio (MMR):")
            response.append(f"  Latest: {stats['mmr_trend']['latest_mmr']:.2f} per 100,000 live births")
            response.append(f"  Average: {stats['mmr_trend']['mean_mmr']:.2f}")
            response.append(f"  Trend: {stats['mmr_trend']['trend']}")
        
        return "\n".join(response)
    
    def _handle_compare(self, query: str) -> str:
        """Handle comparison queries"""
        # Try to extract countries - look for "compare X and Y" or "X vs Y" patterns
        countries = self.pipeline.get_countries()
        query_lower = query.lower()
        found_countries = []
        
        # Sort countries by length (longest first) for better matching
        sorted_countries = sorted(countries, key=len, reverse=True)
        
        # Extract countries mentioned in query
        for country in sorted_countries:
            country_lower = country.lower()
            if country_lower in query_lower:
                # Check if it's a whole word match
                idx = query_lower.find(country_lower)
                if idx == 0 or query_lower[idx-1] in [' ', ',', 'and', '&']:
                    if idx + len(country_lower) == len(query_lower) or query_lower[idx + len(country_lower)] in [' ', ',', '.', '?', '!', 'and', '&', 'vs']:
                        if country not in found_countries:
                            found_countries.append(country)
        
        if len(found_countries) < 2:
            return "Please specify at least two countries to compare, for example: 'Compare Kenya and Uganda' or 'Kenya vs Uganda'"
        
        indicator = self._extract_indicator(query)
        if not indicator:
            indicator = "Under-five mortality rate"  # Default
        
        comparison = self.analytics.compare_countries(found_countries[:5], indicator)
        
        response = [f"📈 Comparison of {indicator}:\n"]
        
        if comparison.get("ranking"):
            response.append("Ranking:")
            for i, item in enumerate(comparison["ranking"], 1):
                response.append(f"{i}. {item['country']}: {item['value']:.2f}")
            
            # Add info about countries without data
            if comparison.get("countries_without_data"):
                response.append(f"\n⚠️ Note: No data available for: {', '.join(comparison['countries_without_data'])}")
        else:
            if comparison.get("countries_without_data"):
                response.append(f"No data available for {indicator} in the requested countries: {', '.join(comparison['countries_without_data'])}")
            else:
                response.append("No comparison data available for the selected countries and indicator.")
        
        return "\n".join(response)
    
    def _handle_trend(self, query: str) -> str:
        """Handle trend analysis queries"""
        country = self._extract_country(query)
        indicator = self._extract_indicator(query)
        
        if not country:
            return "Please specify a country for trend analysis, for example: 'What is the trend for Kenya?'"
        
        if not indicator:
            # Get trend for all indicators
            stats = self.analytics.get_country_statistics(country)
            response = [f"📉 Trends for {country}:\n"]
            
            for ind, data in list(stats["indicators"].items())[:5]:
                response.append(f"• {ind}: {data['trend']}")
            
            return "\n".join(response)
        else:
            trend_analysis = self.analytics.get_trend_analysis(country, indicator)
            
            if "error" in trend_analysis:
                return f"Sorry, I couldn't find trend data for {indicator} in {country}."
            
            response = [
                f"📉 Trend Analysis: {indicator} in {country}\n",
                f"Current Value: {trend_analysis['current_value']:.2f}",
                f"Baseline Value: {trend_analysis['baseline_value']:.2f}",
                f"Change: {trend_analysis['change']:.2f} ({trend_analysis['change_pct']:.1f}%)",
                f"Trend: {trend_analysis['trend']}",
                f"Year Range: {trend_analysis['year_range'][0]} - {trend_analysis['year_range'][1]}"
            ]
            
            return "\n".join(response)
    
    def _handle_projections(self, query: str) -> str:
        """Handle projection queries"""
        country = self._extract_country(query)
        
        analysis = self.analytics.analyze_projections(country)
        
        response = ["🔮 Projections Analysis:\n"]
        
        if country:
            response.append(f"For {country}:\n")
        
        if analysis["mmr_projections"]:
            mmr_proj = analysis["mmr_projections"]
            response.append("Maternal Mortality Ratio (MMR):")
            response.append(f"  On Track: {mmr_proj['on_track_count']} indicator(s)")
            response.append(f"  Off Track: {mmr_proj['off_track_count']} indicator(s)")
            response.append(f"  Average Projected MMR 2030: {mmr_proj['avg_proj_2030']:.2f}")
            
            if mmr_proj.get("countries_on_track"):
                response.append(f"\n  Countries On Track: {', '.join(mmr_proj['countries_on_track'][:5])}")
        
        return "\n".join(response)
    
    def _handle_top_countries(self, query: str) -> str:
        """Handle top countries queries"""
        indicator = self._extract_indicator(query)
        if not indicator:
            indicator = "Under-five mortality rate"
        
        # Extract number
        num_match = re.search(r"top\s+(\d+)", query.lower())
        top_n = int(num_match.group(1)) if num_match else 10
        
        # Determine if highest or lowest
        ascending = "lowest" in query.lower() or "best" in query.lower()
        
        top_df = self.analytics.get_top_countries_by_indicator(indicator, top_n, ascending)
        
        if len(top_df) == 0:
            return f"Sorry, I couldn't find data for {indicator}."
        
        response = [f"🏆 Top {top_n} Countries by {indicator}:\n"]
        
        for i, row in top_df.iterrows():
            response.append(f"{i+1}. {row['country']}: {row['value']:.2f} (Year: {int(row['year'])})")
        
        return "\n".join(response)
    
    def _handle_summary(self, query: str) -> str:
        """Handle summary queries"""
        country = self._extract_country(query)
        
        report = self.analytics.generate_summary_report(country)
        
        return report
    
    def _handle_indicator_info(self, query: str) -> str:
        """Handle indicator information queries"""
        indicator = self._extract_indicator(query)
        
        if not indicator:
            return "Please specify an indicator, for example: 'Tell me about neonatal mortality rate'"
        
        # Get regional summary for this indicator
        summary = self.analytics.get_regional_summary()
        
        if indicator in summary["indicators"]:
            data = summary["indicators"][indicator]
            response = [
                f"📊 {indicator} - Regional Overview:\n",
                f"Mean Value: {data['mean_value']:.2f}",
                f"Median Value: {data['median_value']:.2f}",
                f"Range: {data['min_value']:.2f} - {data['max_value']:.2f}",
                f"Standard Deviation: {data['std_dev']:.2f}"
            ]
            return "\n".join(response)
        
        return f"Information about {indicator} is available. Try asking for specific country statistics."
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general queries"""
        # Try to provide helpful response
        response = [
            "I can help you analyze mortality data for African countries. Here's what I can do:\n",
            "• Provide statistics for specific countries",
            "• Compare countries",
            "• Analyze trends",
            "• Show projections for 2030",
            "• List top countries by indicators",
            "• Generate summary reports\n",
            "Try asking:",
            "- 'What are the statistics for Kenya?'",
            "- 'Compare Kenya and Uganda'",
            "- 'What is the trend for neonatal mortality in Angola?'",
            "- 'Show me projections for 2030'",
            "- 'Top 10 countries by under-five mortality rate'"
        ]
        
        return "\n".join(response)
    
    def get_help(self) -> str:
        """Get help message"""
        return """
🤖 Mortality Analytics Chatbot - Help Guide

I can help you analyze mortality data for African countries. Here are some example queries:

📊 Country Statistics:
  - "What are the statistics for Kenya?"
  - "Tell me about Angola"
  - "How is Nigeria doing?"

📈 Comparisons:
  - "Compare Kenya and Uganda"
  - "Compare Kenya, Uganda, and Tanzania"

📉 Trends:
  - "What is the trend for Kenya?"
  - "How has neonatal mortality changed in Angola?"
  - "Is infant mortality improving in Nigeria?"

🔮 Projections:
  - "Show me projections for 2030"
  - "Which countries are on track?"
  - "What are the projections for Kenya?"

🏆 Top Countries:
  - "Top 10 countries by under-five mortality rate"
  - "Which countries have the highest MMR?"
  - "Top 5 countries with lowest neonatal mortality"

📋 Summaries:
  - "Give me a summary"
  - "Regional overview"
  - "Summary for Kenya"

Available Indicators:
  - Neonatal mortality rate
  - Infant mortality rate
  - Under-five mortality rate
  - Maternal Mortality Ratio (MMR)
  - And more...
        """

