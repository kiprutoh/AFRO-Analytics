"""
Unified Chatbot for Mortality Analytics
Handles both Maternal and Child Mortality queries using the website's analytics
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from mortality_analytics import MaternalMortalityAnalytics, ChildMortalityAnalytics
from mortality_charts import MaternalMortalityChartGenerator, ChildMortalityChartGenerator


class UnifiedMortalityChatbot:
    """Unified chatbot for both Maternal and Child Mortality data"""
    
    def __init__(self, maternal_analytics: MaternalMortalityAnalytics, 
                 child_analytics: ChildMortalityAnalytics,
                 maternal_chart_gen: MaternalMortalityChartGenerator = None,
                 child_chart_gen: ChildMortalityChartGenerator = None):
        """
        Initialize unified chatbot with both analytics engines
        
        Args:
            maternal_analytics: MaternalMortalityAnalytics instance
            child_analytics: ChildMortalityAnalytics instance
            maternal_chart_gen: Optional MaternalMortalityChartGenerator
            child_chart_gen: Optional ChildMortalityChartGenerator
        """
        self.maternal_analytics = maternal_analytics
        self.child_analytics = child_analytics
        self.maternal_chart_gen = maternal_chart_gen
        self.child_chart_gen = child_chart_gen
        
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
                r"sdg.*target"
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
        # Try child analytics first (has more countries typically)
        try:
            countries = self.child_analytics.get_country_list()
        except:
            try:
                countries = self.maternal_analytics.get_country_list()
            except:
                return None
        
        query_lower = query.lower()
        sorted_countries = sorted(countries, key=len, reverse=True)
        
        for country in sorted_countries:
            country_lower = country.lower()
            if country_lower in query_lower:
                idx = query_lower.find(country_lower)
                if idx == 0 or query_lower[idx-1] == ' ':
                    if idx + len(country_lower) == len(query_lower) or query_lower[idx + len(country_lower)] in [' ', ',', '.', '?', '!']:
                        return country
        return None
    
    def _extract_indicator(self, query: str) -> Optional[str]:
        """Extract indicator name from query"""
        query_lower = query.lower()
        
        # Child mortality indicators
        if re.search(r"under.?five|u5mr", query_lower):
            return "Under-five mortality rate"
        elif re.search(r"infant", query_lower):
            return "Infant mortality rate"
        elif re.search(r"neonatal", query_lower):
            return "Neonatal mortality rate"
        # Maternal indicators
        elif re.search(r"maternal|mmr", query_lower):
            return "Maternal Mortality Ratio"
        
        return None
    
    def _handle_country_stats(self, query: str) -> Dict[str, Any]:
        """Handle country statistics queries"""
        country = self._extract_country(query)
        if not country:
            return {
                "text": "Please specify a country name. For example: 'What are the statistics for Kenya?'",
                "chart": None
            }
        
        response = [f"📊 Statistics for {country}:\n"]
        charts = []
        
        # Get child mortality stats
        try:
            latest_year = self.child_analytics.get_latest_year('Under-five mortality rate')
            summary = self.child_analytics.get_mortality_summary(latest_year)
            
            response.append(f"\n**Child Mortality Indicators ({latest_year}):**")
            
            # Get top mortality countries for context
            top_high = self.child_analytics.get_top_mortality_countries(
                indicator='Under-five mortality rate', n=1, year=latest_year, ascending=False
            )
            top_low = self.child_analytics.get_top_mortality_countries(
                indicator='Under-five mortality rate', n=1, year=latest_year, ascending=True
            )
            
            # Get country-specific data
            country_data = self.child_analytics.get_top_mortality_countries(
                indicator='Under-five mortality rate', n=100, year=latest_year, ascending=False
            )
            country_row = country_data[country_data['country_clean'] == country]
            
            if len(country_row) > 0:
                u5mr = country_row.iloc[0]['value']
                response.append(f"• Under-five mortality rate: {u5mr:.1f} per 1,000 live births")
                
                # Generate trend chart
                if self.child_chart_gen:
                    trend_data = self.child_analytics.get_mortality_over_time(country, 'Under-five mortality rate')
                    if len(trend_data) > 0:
                        chart = self.child_chart_gen.create_trend_chart(country, 'Under-five mortality rate')
                        if chart:
                            charts.append(chart)
        except Exception as e:
            response.append(f"\n⚠️ Could not retrieve child mortality data: {str(e)}")
        
        # Get maternal mortality stats
        try:
            latest_year_mm = self.maternal_analytics.get_latest_year()
            mmr_data = self.maternal_analytics.get_top_mmr_countries(n=100, year=latest_year_mm, ascending=False)
            country_mmr = mmr_data[mmr_data['country_clean'] == country]
            
            if len(country_mmr) > 0:
                mmr = country_mmr.iloc[0]['mmr']
                response.append(f"\n**Maternal Mortality ({latest_year_mm}):**")
                response.append(f"• Maternal Mortality Ratio: {mmr:.0f} per 100,000 live births")
                
                # Generate MMR trend chart
                if self.maternal_chart_gen:
                    mmr_trend = self.maternal_analytics.get_mmr_over_time(country)
                    if len(mmr_trend) > 0:
                        chart = self.maternal_chart_gen.create_trend_chart(country)
                        if chart:
                            charts.append(chart)
        except Exception as e:
            response.append(f"\n⚠️ Could not retrieve maternal mortality data: {str(e)}")
        
        return {
            "text": "\n".join(response),
            "chart": charts[0] if charts else None,
            "charts": charts
        }
    
    def _handle_compare(self, query: str) -> Dict[str, Any]:
        """Handle comparison queries"""
        # Extract countries
        countries = self.child_analytics.get_country_list()
        query_lower = query.lower()
        found_countries = []
        
        sorted_countries = sorted(countries, key=len, reverse=True)
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
                "text": "Please specify at least two countries to compare. Example: 'Compare Kenya and Uganda'",
                "chart": None
            }
        
        indicator = self._extract_indicator(query) or "Under-five mortality rate"
        latest_year = self.child_analytics.get_latest_year(indicator)
        
        # Get data for each country
        comparison_data = []
        for country in found_countries[:5]:
            top_data = self.child_analytics.get_top_mortality_countries(
                indicator=indicator, n=100, year=latest_year, ascending=False
            )
            country_row = top_data[top_data['country_clean'] == country]
            if len(country_row) > 0:
                comparison_data.append({
                    'country': country,
                    'value': country_row.iloc[0]['value']
                })
        
        if not comparison_data:
            return {
                "text": f"No comparison data available for {indicator} in the requested countries.",
                "chart": None
            }
        
        # Generate comparison chart
        chart = None
        if self.child_chart_gen and len(comparison_data) > 0:
            import plotly.graph_objects as go
            fig = go.Figure()
            countries_list = [d['country'] for d in comparison_data]
            values_list = [d['value'] for d in comparison_data]
            
            fig.add_trace(go.Bar(
                x=countries_list,
                y=values_list,
                marker_color='#0066CC'
            ))
            fig.update_layout(
                title=f"{indicator} Comparison ({latest_year})",
                xaxis_title="Country",
                yaxis_title=indicator,
                height=400
            )
            chart = fig
        
        response = [f"📈 Comparison of {indicator} ({latest_year}):\n"]
        for i, data in enumerate(comparison_data, 1):
            response.append(f"{i}. {data['country']}: {data['value']:.1f}")
        
        return {
            "text": "\n".join(response),
            "chart": chart
        }
    
    def _handle_trend(self, query: str) -> Dict[str, Any]:
        """Handle trend analysis queries"""
        country = self._extract_country(query)
        indicator = self._extract_indicator(query) or "Under-five mortality rate"
        
        if not country:
            return {
                "text": "Please specify a country. Example: 'What is the trend for neonatal mortality in Angola?'",
                "chart": None
            }
        
        try:
            trend_data = self.child_analytics.get_mortality_over_time(country, indicator)
            if len(trend_data) == 0:
                return {
                    "text": f"No trend data available for {indicator} in {country}.",
                    "chart": None
                }
            
            # Generate trend chart
            chart = None
            if self.child_chart_gen:
                chart = self.child_chart_gen.create_trend_chart(country, indicator)
            
            response = [f"📈 Trend Analysis: {indicator} in {country}\n"]
            response.append(f"Latest value: {trend_data.iloc[-1]['value']:.1f} ({int(trend_data.iloc[-1]['year'])})")
            if len(trend_data) > 1:
                change = trend_data.iloc[-1]['value'] - trend_data.iloc[0]['value']
                pct_change = (change / trend_data.iloc[0]['value']) * 100 if trend_data.iloc[0]['value'] > 0 else 0
                response.append(f"Change since {int(trend_data.iloc[0]['year'])}: {change:+.1f} ({pct_change:+.1f}%)")
            
            return {
                "text": "\n".join(response),
                "chart": chart
            }
        except Exception as e:
            return {
                "text": f"Error retrieving trend data: {str(e)}",
                "chart": None
            }
    
    def _handle_projections(self, query: str) -> Dict[str, Any]:
        """Handle projection queries"""
        country = self._extract_country(query)
        indicator = self._extract_indicator(query) or "Under-five mortality rate"
        
        try:
            projection = self.child_analytics.project_to_2030(
                indicator=indicator,
                country=country,
                method='log_linear'
            )
            
            if projection.get('error'):
                return {
                    "text": projection['error'],
                    "chart": None
                }
            
            response = [f"🎯 SDG 2030 Projection: {indicator}\n"]
            if country:
                response.append(f"Country: {country}\n")
            else:
                response.append("Region: AFRO\n")
            
            latest_year = projection.get('latest_year', 2023)
            latest_value = projection.get('latest_value', 0)
            projected_value = projection.get('projected_value', 0)
            sdg_target = projection.get('sdg_target', 0)
            
            response.append(f"Current ({latest_year}): {latest_value:.1f}")
            response.append(f"Projected 2030: {projected_value:.1f}")
            
            if sdg_target > 0:
                response.append(f"SDG Target 2030: {sdg_target:.0f}")
                gap = projection.get('gap_to_target', 0)
                if projection.get('on_track', False):
                    response.append("✅ On track to meet target!")
                else:
                    response.append(f"⚠️ Gap to target: {gap:.1f}")
                    if projection.get('required_aarr'):
                        response.append(f"Required AARR: {projection['required_aarr']:.2f}%")
            
            # Generate projection chart using chart generator if available
            chart = None
            if self.child_chart_gen:
                chart = self.child_chart_gen.create_projection_chart(
                    indicator=indicator,
                    indicator_name=indicator,
                    country=country,
                    projection_data=projection,
                    target_year=2030
                )
            
            return {
                "text": "\n".join(response),
                "chart": chart
            }
        except Exception as e:
            return {
                "text": f"Error generating projection: {str(e)}",
                "chart": None
            }
    
    def _handle_top_countries(self, query: str) -> Dict[str, Any]:
        """Handle top countries queries"""
        query_lower = query.lower()
        ascending = any(word in query_lower for word in ['lowest', 'best', 'low'])
        n = 10
        
        # Extract number if specified
        num_match = re.search(r'top\s+(\d+)', query_lower)
        if num_match:
            n = int(num_match.group(1))
        
        indicator = self._extract_indicator(query) or "Under-five mortality rate"
        latest_year = self.child_analytics.get_latest_year(indicator)
        
        try:
            top_data = self.child_analytics.get_top_mortality_countries(
                indicator=indicator, n=n, year=latest_year, ascending=ascending
            )
            
            if len(top_data) == 0:
                return {
                    "text": f"No data available for {indicator} in {latest_year}.",
                    "chart": None
                }
            
            # Generate chart
            chart = None
            if self.child_chart_gen:
                chart = self.child_chart_gen.create_top_mortality_chart(
                    indicator=indicator,
                    indicator_name=indicator,
                    n=n,
                    year=latest_year,
                    high_burden=not ascending
                )
            
            response = [f"🏆 Top {n} Countries: {indicator} ({latest_year})\n"]
            response.append("Highest" if not ascending else "Lowest")
            response.append("")
            for i, row in top_data.iterrows():
                response.append(f"{i+1}. {row['country_clean']}: {row['value']:.1f}")
            
            return {
                "text": "\n".join(response),
                "chart": chart
            }
        except Exception as e:
            return {
                "text": f"Error retrieving top countries: {str(e)}",
                "chart": None
            }
    
    def _handle_summary(self, query: str) -> Dict[str, Any]:
        """Handle summary/overview queries"""
        try:
            latest_year = self.child_analytics.get_latest_year('Under-five mortality rate')
            summary = self.child_analytics.get_mortality_summary(latest_year)
            
            response = [f"📊 Regional Summary - {latest_year}\n"]
            response.append(f"Countries with data: {summary.get('total_countries', 0)}\n")
            
            if summary.get('under_five_mortality_rate_median'):
                response.append(f"Under-five mortality rate:")
                response.append(f"  Median: {summary['under_five_mortality_rate_median']:.1f}")
                response.append(f"  Range: {summary.get('under_five_mortality_rate_min', 0):.1f} - {summary.get('under_five_mortality_rate_max', 0):.1f}")
            
            if summary.get('infant_mortality_rate_median'):
                response.append(f"\nInfant mortality rate:")
                response.append(f"  Median: {summary['infant_mortality_rate_median']:.1f}")
            
            if summary.get('neonatal_mortality_rate_median'):
                response.append(f"\nNeonatal mortality rate:")
                response.append(f"  Median: {summary['neonatal_mortality_rate_median']:.1f}")
            
            return {
                "text": "\n".join(response),
                "chart": None
            }
        except Exception as e:
            return {
                "text": f"Error generating summary: {str(e)}",
                "chart": None
            }
    
    def _handle_indicator_info(self, query: str) -> Dict[str, Any]:
        """Handle indicator information queries"""
        indicator = self._extract_indicator(query)
        if not indicator:
            return {
                "text": "Available indicators:\n• Under-five mortality rate\n• Infant mortality rate\n• Neonatal mortality rate\n• Maternal Mortality Ratio",
                "chart": None
            }
        
        definitions = self.child_analytics.indicator_definitions
        definition = definitions.get(indicator, "No definition available")
        
        return {
            "text": f"📋 {indicator}\n\n{definition}",
            "chart": None
        }
    
    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Handle general queries"""
        return {
            "text": """I can help you with mortality data analysis! Here's what I can do:

📊 **Country Statistics**: "What are the statistics for Kenya?"
📈 **Comparisons**: "Compare Kenya and Uganda"
📉 **Trends**: "What is the trend for neonatal mortality in Angola?"
🎯 **Projections**: "Show me projections for 2030"
🏆 **Top Countries**: "Top 10 countries by under-five mortality rate"
📋 **Summary**: "Give me a regional summary"

Try asking a specific question about the data!""",
            "chart": None
        }

