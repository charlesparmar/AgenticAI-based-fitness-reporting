"""
Response Formatting Utilities for RAG Pipeline
Handles formatting and structuring of RAG responses
"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class ResponseFormatter:
    """Handles formatting and structuring of RAG responses"""
    
    def __init__(self):
        """Initialize response formatter"""
        pass
    
    def format_search_results(self, results: List[Dict[str, Any]], 
                            query: str, max_results: int = 5) -> str:
        """
        Format search results into a readable response
        
        Args:
            results: List of search results with content and metadata
            query: Original query
            max_results: Maximum number of results to include
            
        Returns:
            Formatted response string
        """
        try:
            if not results:
                return f"No relevant information found for: '{query}'"
            
            # Limit results
            limited_results = results[:max_results]
            
            # Create response
            response = f"Found {len(limited_results)} relevant results for: '{query}'\n\n"
            
            for i, result in enumerate(limited_results, 1):
                content = result.get('content', '')
                metadata = result.get('metadata', {})
                score = result.get('score', 0.0)
                
                # Add result header
                response += f"**Result {i}** (Relevance: {score:.2f})\n"
                
                # Add metadata info
                if metadata:
                    response += self._format_metadata(metadata)
                
                # Add content
                response += f"{content}\n\n"
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ Error formatting search results: {e}")
            return f"Error formatting results for: '{query}'"
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into readable text"""
        try:
            metadata_text = ""
            
            # Add type information
            if 'type' in metadata:
                metadata_text += f"Type: {metadata['type'].replace('_', ' ').title()}\n"
            
            # Add date information
            if 'date' in metadata:
                metadata_text += f"Date: {metadata['date']}\n"
            elif 'date_from' in metadata and 'date_to' in metadata:
                metadata_text += f"Period: {metadata['date_from']} to {metadata['date_to']}\n"
            
            # Add week information
            if 'week_number' in metadata:
                metadata_text += f"Week: {metadata['week_number']}\n"
            elif 'week_from' in metadata and 'week_to' in metadata:
                metadata_text += f"Weeks: {metadata['week_from']} to {metadata['week_to']}\n"
            
            # Add measurement count
            if 'measurements' in metadata:
                count = len(metadata['measurements'])
                metadata_text += f"Measurements: {count}\n"
            
            # Add record count
            if 'record_count' in metadata:
                metadata_text += f"Records: {metadata['record_count']}\n"
            
            return metadata_text
            
        except Exception as e:
            print(f"❌ Error formatting metadata: {e}")
            return ""
    
    def format_trend_analysis(self, trend_data: Dict[str, Any]) -> str:
        """
        Format trend analysis into a readable response
        
        Args:
            trend_data: Trend analysis data
            
        Returns:
            Formatted trend analysis
        """
        try:
            response = "**Trend Analysis**\n\n"
            
            # Add period information
            if 'period' in trend_data:
                response += f"**Period:** {trend_data['period']}\n\n"
            
            # Add overall trends
            if 'overall_trends' in trend_data:
                response += "**Overall Trends:**\n"
                for metric, trend in trend_data['overall_trends'].items():
                    direction = trend.get('direction', 'stable')
                    change = trend.get('change', 0)
                    response += f"- {metric.replace('_', ' ').title()}: {direction} ({change:+.2f})\n"
                response += "\n"
            
            # Add weekly changes
            if 'weekly_changes' in trend_data:
                response += "**Weekly Changes:**\n"
                for week, changes in trend_data['weekly_changes'].items():
                    response += f"\nWeek {week}:\n"
                    for metric, change in changes.items():
                        direction = "increased" if change > 0 else "decreased" if change < 0 else "unchanged"
                        response += f"- {metric.replace('_', ' ').title()}: {direction} by {abs(change):.2f}\n"
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ Error formatting trend analysis: {e}")
            return "Error formatting trend analysis"
    
    def format_comparison(self, comparison_data: Dict[str, Any]) -> str:
        """
        Format comparison data into a readable response
        
        Args:
            comparison_data: Comparison data
            
        Returns:
            Formatted comparison
        """
        try:
            response = "**Comparison Analysis**\n\n"
            
            # Add comparison periods
            if 'period1' in comparison_data and 'period2' in comparison_data:
                response += f"**Comparing:** {comparison_data['period1']} vs {comparison_data['period2']}\n\n"
            
            # Add metric comparisons
            if 'metrics' in comparison_data:
                response += "**Metric Comparisons:**\n"
                for metric, data in comparison_data['metrics'].items():
                    value1 = data.get('value1', 'N/A')
                    value2 = data.get('value2', 'N/A')
                    difference = data.get('difference', 0)
                    
                    response += f"\n{metric.replace('_', ' ').title()}:\n"
                    response += f"- Period 1: {value1}\n"
                    response += f"- Period 2: {value2}\n"
                    response += f"- Difference: {difference:+.2f}\n"
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ Error formatting comparison: {e}")
            return "Error formatting comparison"
    
    def format_summary(self, summary_data: Dict[str, Any]) -> str:
        """
        Format summary data into a readable response
        
        Args:
            summary_data: Summary data
            
        Returns:
            Formatted summary
        """
        try:
            response = "**Fitness Data Summary**\n\n"
            
            # Add basic info
            if 'total_records' in summary_data:
                response += f"**Total Records:** {summary_data['total_records']}\n"
            
            if 'date_range' in summary_data:
                response += f"**Date Range:** {summary_data['date_range']}\n"
            
            response += "\n"
            
            # Add statistics
            if 'statistics' in summary_data:
                response += "**Statistics:**\n"
                for metric, stats in summary_data['statistics'].items():
                    response += f"\n{metric.replace('_', ' ').title()}:\n"
                    response += f"- Range: {stats.get('min', 'N/A')} to {stats.get('max', 'N/A')}\n"
                    response += f"- Average: {stats.get('avg', 'N/A'):.2f}\n"
                    response += f"- Measurements: {stats.get('count', 'N/A')}\n"
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ Error formatting summary: {e}")
            return "Error formatting summary"
    
    def format_error_response(self, error: str, query: str = "") -> str:
        """
        Format error responses
        
        Args:
            error: Error message
            query: Original query (optional)
            
        Returns:
            Formatted error response
        """
        try:
            response = "❌ **Error**\n\n"
            
            if query:
                response += f"Query: '{query}'\n\n"
            
            response += f"Error: {error}\n\n"
            response += "Please try rephrasing your question or contact support if the issue persists."
            
            return response
            
        except Exception as e:
            print(f"❌ Error formatting error response: {e}")
            return f"Error: {error}"
    
    def format_help_response(self) -> str:
        """Format help response with available query types"""
        try:
            help_text = """
**Fitness Data Assistant Help**

You can ask me questions about your fitness data in natural language. Here are some examples:

**Trend Analysis:**
- "How has my weight changed over the last month?"
- "Show me my fat percentage trends"
- "What's my BMI progression?"

**Comparisons:**
- "Compare my measurements from week 1 to week 10"
- "How did my body composition change between January and March?"

**Specific Measurements:**
- "What was my weight on January 15th?"
- "Show me my chest measurements"
- "What are my current body measurements?"

**Summaries:**
- "Give me a summary of my fitness journey"
- "What are my overall statistics?"
- "Show me my progress summary"

**Goals and Insights:**
- "Am I making progress toward my goals?"
- "What are my strongest areas?"
- "Where do I need to focus more?"

Just ask your question naturally, and I'll find the most relevant information from your fitness data!
"""
            return help_text.strip()
            
        except Exception as e:
            print(f"❌ Error formatting help response: {e}")
            return "Error formatting help response" 