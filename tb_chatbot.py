"""
TB Chatbot Module for Tuberculosis Analytics
Handles natural language queries and generates responses with charts
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from tb_analytics import TBAnalytics
from tb_data_pipeline import TBDataPipeline
from tb_chart_generator import TBChartGenerator


class TBChatbot:
    """Chatbot for TB data analysis"""
    
    def __init__(self, analytics: TBAnalytics, visualizer=None):
        """
        Initialize TB chatbot with analytics engine
        
        Args:
            analytics: TBAnalytics instance
            visualizer: Optional InteractiveVisualizer instance
        """
        self.analytics = analytics
        self.pipeline = analytics.pipeline
        self.chart_generator = TBChartGenerator(analytics)
        self.visualizer = visualizer
        
        # Common patterns for intent recognition
        self.patterns = {
            "country_stats": [
                r"statistics?.*\b(country|for|in)\s+([A-Za-z\s]+)",
                r"([A-Za-z\s]+).*statistics?",
                r"how.*\b([A-Za-z\s]+)\s+doing",
                r"tell me about\s+([A-Za-z\s]+)",
                r"show.*chart.*\b([A-Za-z\s]+)",
                r"visualize.*\b([A-Za-z\s]+)",
                r"chart.*\b([A-Za-z\s]+)"
            ],
            "compare": [
                r"compare\s+([A-Za-z\s,]+)",
                r"comparison.*\b(between|of)\s+([A-Za-z\s,]+)",
                r"which.*better.*\b([A-Za-z\s,]+)"
            ],
            "indicator": [
                r"(tb|tuberculosis|notifications?|treatment|outcomes?|success rate)",
                r"indicator.*\b(tb|tuberculosis|notifications?|treatment)"
            ],
            "trend": [
                r"trend.*\b([A-Za-z\s]+)",
                r"([A-Za-z\s]+).*trend",
                r"how.*changed.*\b([A-Za-z\s]+)",
                r"improving|worsening|getting better|getting worse"
            ],
            "map": [
                r"map",
                r"world map",
                r"geographic",
                r"choropleth",
                r"show.*map",
                r"visualize.*map",
                r"africa.*map"
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
                r"tell me about.*region",
                r"regional"
            ]
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process user query and generate response with charts
        
        Args:
            query: User's natural language query
        
        Returns:
            Dictionary with 'text' and 'chart' keys
        """
        query_lower = query.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        try:
            if intent == "map":
                return self._handle_map(query_lower)
            elif intent == "country_stats":
                return self._handle_country_stats(query_lower)
            elif intent == "compare":
                return self._handle_compare(query_lower)
            elif intent == "trend":
                return self._handle_trend(query_lower)
            elif intent == "top_countries":
                return self._handle_top_countries(query_lower)
            elif intent == "summary":
                return self._handle_summary(query_lower)
            else:
                return self._handle_general_query(query_lower)
        except Exception as e:
            return {
                "text": f"I encountered an error processing your query: {str(e)}\n\nPlease try rephrasing your question or ask for help.",
                "chart": None
            }
    
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
        """Extract TB indicator name from query"""
        indicators = [
            "TB Notifications (Total New Cases)",
            "New Smear-Positive Cases",
            "New Smear-Negative Cases",
            "New Extrapulmonary Cases",
            "Treatment Success Rate - New Cases (%)",
            "Treatment Success Rate (%)"
        ]
        
        query_lower = query.lower()
        
        # Map common terms to indicators
        indicator_map = {
            "notifications": "TB Notifications (Total New Cases)",
            "total.*cases": "TB Notifications (Total New Cases)",
            "smear.*positive": "New Smear-Positive Cases",
            "smear.*negative": "New Smear-Negative Cases",
            "extrapulmonary": "New Extrapulmonary Cases",
            "treatment.*success": "Treatment Success Rate - New Cases (%)",
            "success rate": "Treatment Success Rate (%)"
        }
        
        for term, indicator in indicator_map.items():
            if re.search(term, query_lower):
                return indicator
        
        # Try exact match
        for indicator in indicators:
            if any(word in query_lower for word in indicator.lower().split()):
                return indicator
        
        return None
    
    def _handle_country_stats(self, query: str) -> Dict[str, Any]:
        """Handle country statistics queries"""
        country = self._extract_country(query)
        
        if not country:
            return {
                "text": "I couldn't identify which country you're asking about. Please specify a country name, for example: 'What are the TB statistics for Nigeria?'",
                "chart": None
            }
        
        stats = self.analytics.get_country_statistics(country)
        
        if "error" in stats:
            return {
                "text": f"Sorry, I couldn't find TB data for {country}. Please check the spelling or try another AFRO country.",
                "chart": None
            }
        
        response = [f"📊 TB Statistics for {country}:\n"]
        
        # Generate charts
        charts = []
        
        if stats["indicators"]:
            response.append("TB Indicators:")
            
            # Generate chart for first available indicator
            first_indicator = list(stats["indicators"].keys())[0]
            chart = self.chart_generator.create_trend_chart(country, first_indicator)
            if chart:
                charts.append(chart)
            
            for indicator, data in list(stats["indicators"].items())[:5]:
                response.append(f"\n• {indicator}:")
                if data.get('latest_value') is not None:
                    response.append(f"  Latest Value: {data['latest_value']:.2f}")
                response.append(f"  Median: {data['median_value']:.2f}")
                response.append(f"  Range: {data['min_value']:.2f} - {data['max_value']:.2f}")
                if data.get('trend'):
                    response.append(f"  Trend: {data['trend']}")
        
        # Add link to interactive visualizer
        response.append(f"\n\n💡 For customizable charts with prediction methods and maps, visit the 📈 Interactive Charts page!")
        
        return {
            "text": "\n".join(response),
            "chart": charts[0] if charts else None,
            "charts": charts
        }
    
    def _handle_compare(self, query: str) -> Dict[str, Any]:
        """Handle comparison queries"""
        countries = self.pipeline.get_countries()
        query_lower = query.lower()
        found_countries = []
        
        # Sort countries by length (longest first) for better matching
        sorted_countries = sorted(countries, key=len, reverse=True)
        
        # Extract countries mentioned in query
        for country in sorted_countries:
            country_lower = country.lower()
            if country_lower in query_lower:
                idx = query_lower.find(country_lower)
                if idx == 0 or query_lower[idx-1] in [' ', ',', 'and', '&']:
                    if idx + len(country_lower) == len(query_lower) or query_lower[idx + len(country_lower)] in [' ', ',', '.', '?', '!', 'and', '&', 'vs']:
                        if country not in found_countries:
                            found_countries.append(country)
        
        if len(found_countries) < 2:
            return {
                "text": "Please specify at least two countries to compare, for example: 'Compare Nigeria and South Africa'",
                "chart": None
            }
        
        indicator = self._extract_indicator(query)
        if not indicator:
            indicator = "TB Notifications (Total New Cases)"  # Default
        
        comparison = self.analytics.compare_countries(found_countries[:5], indicator)
        
        if "error" in comparison:
            return {
                "text": comparison["error"],
                "chart": None
            }
        
        # Generate comparison chart
        chart = self.chart_generator.create_country_comparison_chart(found_countries[:5], indicator)
        
        response = [f"📈 Comparison of {indicator}:\n"]
        
        if comparison.get("countries"):
            response.append("Results:")
            sorted_comparison = sorted(
                comparison["countries"].items(),
                key=lambda x: x[1]["value"],
                reverse=True
            )
            for country, data in sorted_comparison:
                response.append(f"{data['rank']}. {country}: {data['value']:.2f}")
        
        return {
            "text": "\n".join(response),
            "chart": chart
        }
    
    def _handle_trend(self, query: str) -> Dict[str, Any]:
        """Handle trend analysis queries"""
        country = self._extract_country(query)
        indicator = self._extract_indicator(query) or "TB Notifications (Total New Cases)"
        
        if country:
            chart = self.chart_generator.create_trend_chart(country, indicator)
            if chart:
                stats = self.analytics.get_country_statistics(country)
                response = f"📈 Trend analysis for {indicator} in {country}:\n\n"
                if indicator in stats.get("indicators", {}):
                    data = stats["indicators"][indicator]
                    response += f"Latest Value: {data.get('latest_value', 'N/A')}\n"
                    response += f"Trend: {data.get('trend', 'N/A')}\n"
                return {
                    "text": response,
                    "chart": chart
                }
        else:
            # Regional trend
            trend_data = self.analytics.get_trend_analysis(indicator)
            if "error" not in trend_data:
                response = f"📈 Regional trend for {indicator}:\n"
                response += f"Percentage Change: {trend_data.get('percentage_change', 0):.1f}%\n"
                response += f"Trend: {trend_data.get('trend', 'N/A')}\n"
                return {
                    "text": response,
                    "chart": None  # Could add regional trend chart here
                }
        
        return {
            "text": "I can show trends for specific countries or indicators. Try: 'Show trend for TB notifications in Nigeria'",
            "chart": None
        }
    
    def _handle_map(self, query: str) -> Dict[str, Any]:
        """Handle map visualization queries"""
        indicator = self._extract_indicator(query) or "TB Notifications (Total New Cases)"
        
        chart = self.chart_generator.create_map_chart(indicator)
        
        if chart:
            return {
                "text": f"🗺️ Map visualization for {indicator} across AFRO region:\n\nThis map shows the distribution of {indicator} across all 47 AFRO countries.",
                "chart": chart
            }
        else:
            return {
                "text": f"Sorry, I couldn't generate a map for {indicator}. Please try another indicator.",
                "chart": None
            }
    
    def _handle_top_countries(self, query: str) -> Dict[str, Any]:
        """Handle top countries queries"""
        indicator = self._extract_indicator(query) or "TB Notifications (Total New Cases)"
        
        # Determine if asking for top or bottom
        ascending = any(word in query.lower() for word in ["lowest", "bottom", "worst", "least"])
        
        top_countries = self.analytics.get_top_countries(indicator, n=10, ascending=ascending)
        
        if "error" in top_countries:
            return {
                "text": top_countries["error"],
                "chart": None
            }
        
        response = [f"🏆 Top 10 Countries for {indicator}:\n"]
        
        for item in top_countries.get("countries", []):
            response.append(f"{item['rank']}. {item['country']}: {item['value']:.2f}")
        
        # Generate chart
        countries_list = [item['country'] for item in top_countries.get("countries", [])]
        chart = self.chart_generator.create_country_comparison_chart(countries_list, indicator)
        
        return {
            "text": "\n".join(response),
            "chart": chart
        }
    
    def _handle_summary(self, query: str) -> Dict[str, Any]:
        """Handle regional summary queries"""
        summary = self.analytics.get_regional_summary()
        
        response = [f"📊 Regional Summary - WHO AFRO:\n"]
        response.append(f"Total Countries: {summary.get('total_countries', 0)}\n")
        response.append(f"Latest Year: {summary.get('latest_year', 'N/A')}\n")
        
        if summary.get("indicators"):
            response.append("\nKey Indicators:")
            for indicator, data in list(summary["indicators"].items())[:5]:
                response.append(f"\n• {indicator}:")
                response.append(f"  Mean: {data.get('mean_value', 0):.2f}")
                response.append(f"  Range: {data.get('min_value', 0):.2f} - {data.get('max_value', 0):.2f}")
        
        return {
            "text": "\n".join(response),
            "chart": None
        }
    
    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Handle general queries"""
        return {
            "text": """I can help you with TB data analysis! Here's what I can do:

📊 **Country Statistics**: "What are the TB statistics for Nigeria?"
📈 **Comparisons**: "Compare Nigeria and South Africa"
📉 **Trends**: "Show trend for TB notifications in Kenya"
🗺️ **Maps**: "Show map of TB notifications"
🏆 **Top Countries**: "Top 10 countries by TB notifications"
📋 **Regional Summary**: "Show regional summary"

Try asking me a question about TB data!""",
            "chart": None
        }

