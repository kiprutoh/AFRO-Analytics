"""
Chatbot Module for Mortality Analytics
Handles natural language queries and generates responses with charts
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from analytics import MortalityAnalytics
from data_pipeline import MortalityDataPipeline
from chart_generator import ChartGenerator


class MortalityChatbot:
    """Chatbot for mortality data analysis"""
    
    def __init__(self, analytics: MortalityAnalytics, visualizer=None):
        """
        Initialize chatbot with analytics engine
        
        Args:
            analytics: MortalityAnalytics instance
            visualizer: Optional InteractiveVisualizer instance
        """
        self.analytics = analytics
        self.pipeline = analytics.pipeline
        self.chart_generator = ChartGenerator(analytics)
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
                r"forecast",
                r"2000.*2023.*projection",
                r"projection.*2023.*2030"
            ],
            "map": [
                r"map",
                r"world map",
                r"geographic",
                r"choropleth",
                r"show.*map",
                r"visualize.*map"
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
    
    def _handle_country_stats(self, query: str) -> Dict[str, Any]:
        """Handle country statistics queries"""
        country = self._extract_country(query)
        
        if not country:
            return {
                "text": "I couldn't identify which country you're asking about. Please specify a country name, for example: 'What are the statistics for Kenya?'",
                "chart": None
            }
        
        stats = self.analytics.get_country_statistics(country)
        
        response = [f"📊 Statistics for {country}:\n"]
        
        # Generate multiple charts for different indicators
        charts = []
        
        if stats["indicators"]:
            response.append("Mortality Indicators:")
            
            # Generate charts for top indicators
            key_indicators = ["Under-five mortality rate", "Infant mortality rate", "Neonatal mortality rate"]
            for indicator in key_indicators:
                if indicator in stats["indicators"]:
                    chart = self.chart_generator.create_trend_chart(country, indicator)
                    if chart:
                        charts.append(chart)
                    break  # Use first available key indicator
            
            # If no key indicator found, use first available
            if not charts and stats["indicators"]:
                first_indicator = list(stats["indicators"].keys())[0]
                chart = self.chart_generator.create_trend_chart(country, first_indicator)
                if chart:
                    charts.append(chart)
            
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
        
        # Add link to interactive visualizer
        response.append(f"\n\n💡 For customizable charts with projections (2000-2023 observed, 2024-2030 projected), prediction methods, and maps, visit the 📈 Interactive Charts page!")
        
        return {
            "text": "\n".join(response),
            "chart": charts[0] if charts else None,
            "charts": charts  # Multiple charts support
        }
    
    def _handle_compare(self, query: str) -> Dict[str, Any]:
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
            return {
                "text": "Please specify at least two countries to compare, for example: 'Compare Kenya and Uganda' or 'Kenya vs Uganda'",
                "chart": None
            }
        
        indicator = self._extract_indicator(query)
        if not indicator:
            indicator = "Under-five mortality rate"  # Default
        
        comparison = self.analytics.compare_countries(found_countries[:5], indicator)
        
        # Generate comparison chart
        chart = self.chart_generator.create_country_comparison_chart(found_countries[:5], indicator)
        
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
        
        return {
            "text": "\n".join(response),
            "chart": chart
        }
    
    def _handle_trend(self, query: str) -> Dict[str, Any]:
        """Handle trend analysis queries"""
        # Check if it's a trend with projection request
        if re.search(r"trend.*\d{4}.*\d{4}.*projection", query.lower()) or \
           re.search(r"\d{4}.*\d{4}.*projection", query.lower()):
            return self._handle_trend_with_projection(query)
        
        country = self._extract_country(query)
        indicator = self._extract_indicator(query)
        
        if not country:
            return {
                "text": "Please specify a country for trend analysis, for example: 'What is the trend for Kenya?' or 'Trend of MMR for Nigeria 2000-2023 with projection 2024-2030'",
                "chart": None
            }
        
        if not indicator:
            # Get trend for all indicators
            stats = self.analytics.get_country_statistics(country)
            response = [f"📉 Trends for {country}:\n"]
            
            for ind, data in list(stats["indicators"].items())[:5]:
                response.append(f"• {ind}: {data['trend']}")
            
            return {
                "text": "\n".join(response),
                "chart": None
            }
        else:
            trend_analysis = self.analytics.get_trend_analysis(country, indicator)
            
            if "error" in trend_analysis:
                return {
                    "text": f"Sorry, I couldn't find trend data for {indicator} in {country}.",
                    "chart": None
                }
            
            # Generate trend chart with projection if visualizer available
            chart = None
            if self.visualizer:
                chart = self.visualizer.create_custom_trend_chart(
                    country=country,
                    indicator=indicator,
                    prediction_method='linear',
                    show_projection=True,
                    start_year=2000,
                    end_year=2030
                )
            else:
                chart = self.chart_generator.create_trend_chart(country, indicator)
            
            response = [
                f"📉 Trend Analysis: {indicator} in {country}\n",
                f"Observed Period: 2000-2023",
                f"Projected Period: 2024-2030 (shown in chart)",
                f"\nCurrent Value: {trend_analysis['current_value']:.2f}",
                f"Baseline Value: {trend_analysis['baseline_value']:.2f}",
                f"Change: {trend_analysis['change']:.2f} ({trend_analysis['change_pct']:.1f}%)",
                f"Trend: {trend_analysis['trend']}",
                f"Year Range: {trend_analysis['year_range'][0]} - {trend_analysis['year_range'][1]}"
            ]
            
            return {
                "text": "\n".join(response),
                "chart": chart
            }
    
    def _handle_projections(self, query: str) -> Dict[str, Any]:
        """Handle projection queries"""
        country = self._extract_country(query)
        indicator = self._extract_indicator(query)
        
        if not indicator:
            indicator = "MMR"  # Default to MMR
        
        analysis = self.analytics.analyze_projections(country)
        
        # Generate projection chart
        chart = None
        if country:
            chart = self.chart_generator.create_projection_timeline(country, indicator)
        else:
            chart = self.chart_generator.create_projection_chart(None, indicator)
        
        response = ["🔮 Projections Analysis:\n"]
        
        if country:
            response.append(f"For {country}:\n")
        
        if analysis["mmr_projections"]:
            mmr_proj = analysis["mmr_projections"]
            response.append("Maternal Mortality Ratio (MMR):")
            response.append(f"  On Track: {mmr_proj['on_track_count']} indicator(s)")
            response.append(f"  Off Track: {mmr_proj['off_track_count']} indicator(s)")
            response.append(f"  Average Projected MMR 2030: {mmr_proj['avg_proj_2030']:.2f}")
            
            if indicator == "MMR":
                response.append(f"\n  SDG Target 2030: <70 per 100,000 live births")
            
            if mmr_proj.get("countries_on_track"):
                response.append(f"\n  Countries On Track: {', '.join(mmr_proj['countries_on_track'][:5])}")
        
        return {
            "text": "\n".join(response),
            "chart": chart
        }
    
    def _handle_top_countries(self, query: str) -> Dict[str, Any]:
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
            return {
                "text": f"Sorry, I couldn't find data for {indicator}.",
                "chart": None
            }
        
        # Generate chart
        chart = self.chart_generator.create_top_countries_chart(indicator, top_n, ascending)
        
        response = [f"🏆 Top {top_n} Countries by {indicator}:\n"]
        
        for i, row in top_df.iterrows():
            response.append(f"{i+1}. {row['country']}: {row['value']:.2f} (Year: {int(row['year'])})")
        
        return {
            "text": "\n".join(response),
            "chart": chart
        }
    
    def _handle_summary(self, query: str) -> Dict[str, Any]:
        """Handle summary queries"""
        country = self._extract_country(query)
        
        report = self.analytics.generate_summary_report(country)
        
        # Generate on-track chart if no country specified
        chart = None
        if not country:
            chart = self.chart_generator.create_on_track_chart()
        
        return {
            "text": report,
            "chart": chart
        }
    
    def _handle_map(self, query: str) -> Dict[str, Any]:
        """Handle map visualization queries"""
        indicator = self._extract_indicator(query)
        if not indicator:
            # Try to detect indicator from query
            if "mmr" in query.lower() or "maternal" in query.lower():
                indicator = "MMR"
            elif "under-five" in query.lower() or "under five" in query.lower():
                indicator = "Under-five mortality rate"
            elif "infant" in query.lower():
                indicator = "Infant mortality rate"
            elif "neonatal" in query.lower():
                indicator = "Neonatal mortality rate"
            else:
                indicator = "MMR"  # Default to MMR
        
        # Extract year if mentioned
        year_match = re.search(r"20\d{2}", query)
        year = int(year_match.group()) if year_match else 2023
        
        # Generate enhanced map
        chart = self.chart_generator.create_enhanced_map(indicator, year)
        
        if not chart:
            return {
                "text": f"Sorry, I couldn't generate a map for {indicator}. Please try a different indicator.",
                "chart": None
            }
        
        response = [
            f"🗺️ Map Visualization: {indicator} ({year})\n",
            f"Showing all African countries with {indicator} values.",
            "Hover over countries to see details. Country names are displayed on the map."
        ]
        
        return {
            "text": "\n".join(response),
            "chart": chart
        }
    
    def _handle_indicator_info(self, query: str) -> Dict[str, Any]:
        """Handle indicator information queries"""
        indicator = self._extract_indicator(query)
        
        if not indicator:
            return {
                "text": "Please specify an indicator, for example: 'Tell me about neonatal mortality rate'",
                "chart": None
            }
        
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
            return {
                "text": "\n".join(response),
                "chart": None
            }
        
        return {
            "text": f"Information about {indicator} is available. Try asking for specific country statistics.",
            "chart": None
        }
    
    def _handle_trend_with_projection(self, query: str) -> Dict[str, Any]:
        """Handle trend queries with specific projection requests like 'Trend of MMR for Nigeria 2000-2023 with projection 2024-2030'"""
        country = self._extract_country(query)
        indicator = self._extract_indicator(query)
        
        if not country:
            return {
                "text": "Please specify a country, for example: 'Trend of MMR for Nigeria 2000-2023 with projection 2024-2030'",
                "chart": None
            }
        
        if not indicator:
            # Try to detect indicator from query
            if "mmr" in query.lower() or "maternal" in query.lower():
                indicator = "MMR"
            elif "under-five" in query.lower() or "under five" in query.lower():
                indicator = "Under-five mortality rate"
            elif "infant" in query.lower():
                indicator = "Infant mortality rate"
            elif "neonatal" in query.lower():
                indicator = "Neonatal mortality rate"
            else:
                indicator = "MMR"  # Default
        
        # Use interactive visualizer for better charts with projections
        chart = None
        if self.visualizer:
            chart = self.visualizer.create_custom_trend_chart(
                country=country,
                indicator=indicator,
                prediction_method='linear',
                show_projection=True,
                start_year=2000,
                end_year=2030
            )
        else:
            # Fallback to chart generator
            chart = self.chart_generator.create_trend_chart(country, indicator)
        
        response = [
            f"📈 Trend Analysis with Projections: {indicator} - {country}\n",
            f"Observed Period: 2000-2023 (blue line)",
            f"Projected Period: 2024-2030 (orange dashed line with light shading)",
            f"\nThe chart shows historical data and future projections based on current trends."
        ]
        
        return {
            "text": "\n".join(response),
            "chart": chart
        }
    
    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Handle general queries"""
        # Check if it's a trend with projection query
        if re.search(r"trend.*\d{4}.*\d{4}.*projection", query.lower()) or \
           re.search(r"projection.*\d{4}.*\d{4}", query.lower()):
            return self._handle_trend_with_projection(query)
        
        # Try to provide helpful response
        response = [
            "I can help you analyze mortality data for African countries. Here's what I can do:\n",
            "• Provide statistics for specific countries (with charts)",
            "• Compare countries (with charts)",
            "• Analyze trends with projections (2000-2023 observed, 2024-2030 projected)",
            "• Show maps of Africa (with country names)",
            "• Show projections for 2030 vs targets (with charts)",
            "• List top countries by indicators (with charts)",
            "• Generate summary reports\n",
            "Try asking:",
            "- 'Trend of MMR for Nigeria 2000-2023 with projection 2024-2030'",
            "- 'Show me a map of MMR in Africa'",
            "- 'What are the statistics for Kenya?'",
            "- 'Compare Kenya and Uganda'",
            "- 'Top 10 countries by under-five mortality rate'"
        ]
        
        return {
            "text": "\n".join(response),
            "chart": None
        }
    
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

