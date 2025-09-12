"""
Prompts Module for RAG Pipeline
Specialized prompt templates for fitness data queries
"""

from typing import List, Dict, Any, Optional


class FitnessPrompts:
    """Specialized prompts for fitness data analysis"""
    
    def __init__(self):
        """Initialize fitness prompts"""
        self.system_prompt = self._get_system_prompt()
        self.query_prompts = self._get_query_prompts()
    
    def _get_system_prompt(self) -> str:
        """Get the main system prompt"""
        return """You are a fitness data assistant that provides concise, accurate answers about fitness measurements.

**CRITICAL INSTRUCTIONS:**
- Be CONCISE and TO THE POINT - no extra information unless specifically asked
- When asked for "current" measurements, use the MOST RECENT data (FIRST entry in the context)
- Data is sorted by week number (most recent first), so the FIRST entry is the most recent
- ALWAYS specify the exact date when providing current measurements
- Provide ONLY the requested information - no health implications, recommendations, or extra context unless asked
- For "current" or "today" questions, ALWAYS use the most recent data (first entry)
- For "starting" or "beginning" questions, use the OLDEST data (last entry in context)
- NEVER include metadata like "Based on X relevant data points" in your response

**UNIT INFORMATION:**
- Weight: KILOGRAMS (kg)
- Body measurements: INCHES
- BMI: standard units
- Body fat percentage: percentage (%)
- Fat weight and lean weight: KILOGRAMS (kg)

**RESPONSE FORMAT:**
- Direct answer to the question
- Include the date for current measurements
- Use correct units
- Keep responses brief and focused

Example: "Your current weight is 125.0 kg as of 01-08-2025."

**SPECIFIC INSTRUCTIONS FOR WEIGHT QUERIES:**
- When asked "what is my current weight?" or "what is my weight as of today?" - provide ONLY the weight and date from the MOST RECENT entry (first in the data)
- When asked "what was my starting weight?" or "what was my weight in the start?" - provide ONLY the weight and date from the OLDEST entry (last in the data)
- Data is sorted by week_number DESC (most recent first), so FIRST entry = current, LAST entry = starting
- Do NOT include BMI, fat percentage, or any other measurements unless specifically asked
- Do NOT include historical context, trends, or comparisons unless asked
- NEVER include "Based on X relevant data points" or similar metadata
- NEVER say "No weight data available" if you can see weight data in the context

Do NOT include:
- Historical context unless asked
- Health implications unless asked  
- Recommendations unless asked
- Extra explanations unless asked"""
    
    def _get_query_prompts(self) -> Dict[str, str]:
        """Get specialized prompts for different query types"""
        return {
            'trend': """Analyze the fitness data to identify trends and patterns. Focus on:

1. **Trend Direction**: Is the measurement increasing, decreasing, or staying stable?
2. **Rate of Change**: How quickly is the change happening?
3. **Consistency**: Is the trend consistent or are there fluctuations?
4. **Context**: What might be causing these changes?
5. **Recommendations**: What actions could help continue positive trends or address negative ones?

Provide a clear, structured analysis with specific numbers and actionable insights.""",
            
            'comparison': """Compare the fitness data between different periods or measurements. Focus on:

1. **Direct Comparison**: What are the specific differences between the periods?
2. **Percentage Changes**: Calculate and explain percentage changes where relevant
3. **Significance**: Are the changes meaningful or within normal variation?
4. **Patterns**: What patterns emerge from the comparison?
5. **Insights**: What does this comparison tell us about progress?

Present the comparison clearly with specific numbers and context.""",
            
            'specific': """Provide ONLY the specific measurement requested. Focus on:

1. **Current Value**: What is the specific measurement?
2. **Date**: When was this measurement taken?

Give ONLY the requested information with the date. No extra context, implications, or recommendations unless specifically asked.""",
            
            'summary': """Provide a comprehensive summary of the fitness journey. Focus on:

1. **Overall Progress**: What has been achieved over the entire period?
2. **Key Metrics**: Highlight the most important measurements and changes
3. **Patterns**: What patterns or trends emerge from the full dataset?
4. **Achievements**: What are the notable accomplishments?
5. **Areas for Focus**: What areas need attention or could be improved?
6. **Recommendations**: What should be the focus going forward?

Create a motivating but realistic summary that celebrates progress and identifies opportunities.""",
            
            'goal': """Analyze progress toward fitness goals and provide goal-oriented insights. Focus on:

1. **Goal Assessment**: How well are current goals being met?
2. **Progress Tracking**: What progress has been made toward specific goals?
3. **Strengths**: What areas are showing the most improvement?
4. **Challenges**: What areas need more attention or adjustment?
5. **Goal Adjustment**: Should goals be modified based on current progress?
6. **Action Plan**: What specific actions will help achieve goals?

Provide goal-focused analysis with clear next steps and motivation."""
        }
    
    def get_prompt_for_query(self, query_type: str, context: List[Dict[str, Any]], 
                           query: str, analytics_data: Dict[str, Any] = None) -> str:
        """
        Get a complete prompt for a specific query type
        
        Args:
            query_type: Type of query (trend, comparison, specific, summary, goal)
            context: Retrieved context from vector database
            query: Original user query
            
        Returns:
            Complete prompt string
        """
        try:
            # Get base prompt for query type
            base_prompt = self.query_prompts.get(query_type, self.query_prompts.get('specific', ''))
            
            # Format context
            context_text = self._format_context(context)
            
            # Add analytics data to prompt if available
            analytics_text = self._format_analytics_data(analytics_data) if analytics_data else ""
            
            # Build complete prompt
            prompt = f"""{self.system_prompt}

{base_prompt}

**User Query**: {query}

**Available Fitness Data**:
{context_text}

{analytics_text}

**Instructions**: 
Based on the fitness data and analytics above, provide a comprehensive answer to the user's query. Be specific, accurate, and helpful. Use the analytics data to validate your calculations and ensure accuracy.

**IMPORTANT**: If the analytics data shows warnings about "no data available" but you can see fitness data in the context above, IGNORE those warnings and use the actual data you can see. The analytics warnings may be incorrect - trust the actual fitness data in the context.

**Response Format**:
- Start with a direct answer to the query
- Provide specific numbers and measurements when available
- Include relevant trends or patterns
- Offer actionable insights or recommendations
- Be encouraging and supportive
- If analytics data shows warnings or validation issues, address them in your response

Please provide your analysis:"""
            
            return prompt
            
        except Exception as e:
            print(f"❌ Error creating prompt: {e}")
            return self._get_fallback_prompt(query, context)
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """
        Format context data for the prompt
        
        Args:
            context: List of context documents
            
        Returns:
            Formatted context string
        """
        try:
            if not context:
                return "No fitness data available."
            
            # Sort context by date (most recent first)
            sorted_context = sorted(context, key=lambda x: x.get('metadata', {}).get('date', ''), reverse=True)
            
            formatted_context = []
            
            for i, doc in enumerate(sorted_context, 1):
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                score = doc.get('relevance_score', 0)
                
                # Add document header
                doc_header = f"Document {i} (Relevance: {score:.2f})"
                
                # Add metadata info
                metadata_info = []
                if metadata.get('type'):
                    metadata_info.append(f"Type: {metadata['type']}")
                if metadata.get('date'):
                    metadata_info.append(f"Date: {metadata['date']}")
                if metadata.get('week_number'):
                    metadata_info.append(f"Week: {metadata['week_number']}")
                
                if metadata_info:
                    doc_header += f" - {', '.join(metadata_info)}"
                
                # Highlight most recent data
                if i == 1:
                    doc_header += " [MOST RECENT DATA]"
                
                formatted_context.append(f"{doc_header}\n{content}")
            
            return "\n\n".join(formatted_context)
            
        except Exception as e:
            print(f"❌ Error formatting context: {e}")
            return "Error formatting fitness data context."
    
    def _format_analytics_data(self, analytics_data: Dict[str, Any]) -> str:
        """
        Format analytics data for inclusion in prompts
        
        Args:
            analytics_data: Analytics data dictionary
            
        Returns:
            Formatted analytics text
        """
        try:
            if not analytics_data:
                return ""
            
            analytics_lines = ["**Analytics Data**:", ""]
            
            # Add data summary
            if 'data_summary' in analytics_data:
                summary = analytics_data['data_summary']
                analytics_lines.append("**Data Summary**:")
                if 'total_records' in summary:
                    analytics_lines.append(f"- Total records: {summary['total_records']}")
                if 'weeks_count' in summary:
                    analytics_lines.append(f"- Weeks of data: {summary['weeks_count']}")
                if 'total_weight_loss' in summary:
                    analytics_lines.append(f"- Total weight loss: {summary['total_weight_loss']:.2f} kg")
                if 'date_range' in summary:
                    date_range = summary['date_range']
                    if 'start' in date_range and 'end' in date_range:
                        analytics_lines.append(f"- Date range: {date_range['start']} to {date_range['end']}")
                analytics_lines.append("")
            
            # Add calculations
            if 'calculations' in analytics_data:
                calculations = analytics_data['calculations']
                analytics_lines.append("**Calculations**:")
                for calc_name, calc_data in calculations.items():
                    if isinstance(calc_data, dict):
                        if 'value' in calc_data:
                            unit = calc_data.get('unit', '')
                            confidence = calc_data.get('confidence', 0)
                            analytics_lines.append(f"- {calc_name}: {calc_data['value']:.2f} {unit} (confidence: {confidence:.2f})")
                        else:
                            analytics_lines.append(f"- {calc_name}: {calc_data}")
                    else:
                        analytics_lines.append(f"- {calc_name}: {calc_data}")
                analytics_lines.append("")
            
            # Add validation results
            if 'validation' in analytics_data:
                validation = analytics_data['validation']
                analytics_lines.append("**Data Validation**:")
                if 'valid' in validation:
                    status = "✅ Valid" if validation['valid'] else "❌ Invalid"
                    analytics_lines.append(f"- Data quality: {status}")
                if 'issues' in validation and validation['issues']:
                    analytics_lines.append("- Issues found:")
                    for issue in validation['issues']:
                        analytics_lines.append(f"  • {issue}")
                if 'warnings' in validation and validation['warnings']:
                    analytics_lines.append("- Warnings:")
                    for warning in validation['warnings']:
                        analytics_lines.append(f"  • {warning}")
                analytics_lines.append("")
            
            # Add warnings
            if 'warnings' in analytics_data and analytics_data['warnings']:
                analytics_lines.append("**Analytics Warnings**:")
                for warning in analytics_data['warnings']:
                    analytics_lines.append(f"- ⚠️ {warning}")
                analytics_lines.append("")
            
            # Add trends if available
            if 'trends' in analytics_data and analytics_data['trends']:
                trends = analytics_data['trends']
                analytics_lines.append("**Trend Analysis**:")
                if 'weight_trends' in trends:
                    weight_trends = trends['weight_trends']
                    for i, trend in enumerate(weight_trends[:3], 1):  # Top 3 trends
                        if isinstance(trend, dict):
                            metric = trend.get('metric', 'Unknown')
                            period = trend.get('period', 'Unknown')
                            change = trend.get('change', 0)
                            direction = trend.get('trend_direction', 'Unknown')
                            analytics_lines.append(f"- {i}. {metric} ({period}): {change:.2f} ({direction})")
                analytics_lines.append("")
            
            return "\n".join(analytics_lines)
            
        except Exception as e:
            print(f"❌ Error formatting analytics data: {e}")
            return ""
    
    def _get_fallback_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        """
        Get a fallback prompt if the main prompt creation fails
        
        Args:
            query: User query
            context: Context data
            
        Returns:
            Fallback prompt string
        """
        context_text = self._format_context(context)
        
        return f"""You are a fitness data assistant. Help the user understand their fitness data.

User Query: {query}

Fitness Data:
{context_text}

Please provide a helpful response based on the available data. If you don't have enough information, let the user know what additional data would be helpful."""
    
    def get_follow_up_prompt(self, original_query: str, original_response: str,
                           follow_up_query: str, context: List[Dict[str, Any]]) -> str:
        """
        Get a prompt for follow-up questions
        
        Args:
            original_query: Original user query
            original_response: Previous response
            follow_up_query: New follow-up query
            context: Updated context data
            
        Returns:
            Follow-up prompt string
        """
        try:
            context_text = self._format_context(context)
            
            return f"""{self.system_prompt}

**Previous Conversation**:
User: {original_query}
Assistant: {original_response}

**New Follow-up Question**: {follow_up_query}

**Available Fitness Data**:
{context_text}

**Instructions**: 
Answer the follow-up question while considering the previous conversation. Build upon your previous response and provide additional insights or clarification as needed.

Please provide your response:"""
            
        except Exception as e:
            print(f"❌ Error creating follow-up prompt: {e}")
            return self._get_fallback_prompt(follow_up_query, context)
    
    def get_error_prompt(self, query: str, error_message: str) -> str:
        """
        Get a prompt for handling errors
        
        Args:
            query: User query
            error_message: Error message
            
        Returns:
            Error handling prompt string
        """
        return f"""You are a fitness data assistant. There was an error processing the user's request.

User Query: {query}
Error: {error_message}

Please provide a helpful response that:
1. Acknowledges the error
2. Suggests alternative ways to get the information they need
3. Offers to help with a rephrased question
4. Remains supportive and encouraging

Provide your response:"""
    
    def get_help_prompt(self) -> str:
        """Get a prompt for help responses"""
        return f"""{self.system_prompt}

The user is asking for help or clarification about how to use the fitness data assistant.

**Instructions**:
Provide a helpful guide that explains:
1. What types of questions you can answer
2. How to ask questions effectively
3. What kind of insights you can provide
4. Examples of good questions to ask
5. How to interpret the responses

Be encouraging and make it easy for users to get started with analyzing their fitness data.

Provide your help response:"""
    
    def get_summary_prompt(self, context: List[Dict[str, Any]]) -> str:
        """
        Get a prompt for generating data summaries
        
        Args:
            context: Context data
            
        Returns:
            Summary prompt string
        """
        try:
            context_text = self._format_context(context)
            
            return f"""{self.system_prompt}

{self.query_prompts['summary']}

**Available Fitness Data**:
{context_text}

**Instructions**: 
Create a comprehensive summary of the fitness journey based on the available data. Focus on overall progress, key achievements, patterns, and recommendations for the future.

**Summary Structure**:
1. **Overview**: Brief summary of the fitness journey
2. **Key Metrics**: Most important measurements and changes
3. **Progress Analysis**: Trends and patterns identified
4. **Achievements**: Notable accomplishments and improvements
5. **Areas for Focus**: Opportunities for continued improvement
6. **Recommendations**: Suggested next steps and focus areas

Please provide your comprehensive summary:"""
            
        except Exception as e:
            print(f"❌ Error creating summary prompt: {e}")
            return self._get_fallback_prompt("Provide a summary of my fitness journey", context) 