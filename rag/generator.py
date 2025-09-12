"""
Generator Module for RAG Pipeline
Handles LLM integration and response generation
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from config.environment import env_config
from .prompts import FitnessPrompts
from .utils.formatting import ResponseFormatter
from .analytics import FitnessAnalytics
from .utils.calculations import FitnessCalculations


class ResponseGenerator:
    """Handles LLM integration and response generation for fitness data queries"""
    
    def __init__(self, vector_store=None, query_processor=None, retriever=None,
                 llm_provider: str = None, llm_model: str = None):
        """
        Initialize response generator
        
        Args:
            llm_provider: LLM provider to use (openai, anthropic, google)
            llm_model: Specific model name
            vector_store: Vector store instance for analytics
            query_processor: Query processor instance for analytics
            retriever: Retriever instance for analytics
        """
        self.llm_provider = llm_provider or os.getenv("LLM_PROVIDER", "openai")
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.prompts = FitnessPrompts()
        self.formatter = ResponseFormatter()
        self.llm_client = None
        
        # Initialize analytics and calculations
        self.analytics = FitnessAnalytics(vector_store, query_processor, retriever) if vector_store else None
        self.calculations = FitnessCalculations()
        
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client based on provider"""
        try:
            # Ensure llm_provider is a string
            if hasattr(self.llm_provider, 'lower'):
                provider = self.llm_provider.lower()
            else:
                provider = str(self.llm_provider).lower()
            
            if provider == "openai":
                self._initialize_openai()
            elif provider == "anthropic":
                self._initialize_anthropic()
            elif provider == "google":
                self._initialize_google()
            else:
                print(f"❌ Unsupported LLM provider: {self.llm_provider}")
                print("🔄 Falling back to OpenAI...")
                self.llm_provider = "openai"
                self._initialize_openai()
                
        except Exception as e:
            print(f"❌ Error initializing LLM: {e}")
            self.llm_client = None
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            openai.api_key = api_key
            self.llm_client = openai
            print(f"✅ Initialized OpenAI client with model: {self.llm_model}")
            
        except Exception as e:
            print(f"❌ Error initializing OpenAI: {e}")
            self.llm_client = None
    
    def _initialize_anthropic(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            
            self.llm_client = anthropic.Anthropic(api_key=api_key)
            print(f"✅ Initialized Anthropic client with model: {self.llm_model}")
            
        except Exception as e:
            print(f"❌ Error initializing Anthropic: {e}")
            self.llm_client = None
    
    def _initialize_google(self):
        """Initialize Google client"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")
            
            genai.configure(api_key=api_key)
            self.llm_client = genai
            print(f"✅ Initialized Google client with model: {self.llm_model}")
            
        except Exception as e:
            print(f"❌ Error initializing Google: {e}")
            self.llm_client = None
    
    def generate_response(self, query: str, context: List[Dict[str, Any]], 
                         query_type: str = None, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response using LLM with analytics integration
        
        Args:
            query: User query
            context: Retrieved context from vector database
            query_type: Type of query (optional)
            conversation_history: Previous conversation (optional)
            
        Returns:
            Dictionary with generated response and metadata
        """
        try:
            if not self.llm_client:
                return self._generate_fallback_response(query, context)
            
            # Determine query type if not provided
            if not query_type:
                query_type = self._classify_query_type(query)
            
            # Perform analytics and calculations before generating response
            analytics_data = self._perform_analytics(query, context, query_type)
            
            # Create prompt with analytics data
            prompt = self.prompts.get_prompt_for_query(query_type, context, query, analytics_data)
            
            # Generate response
            response_text = self._call_llm(prompt)
            
            if not response_text:
                return self._generate_fallback_response(query, context)
            
            # Format and structure response
            formatted_response = self._format_response(response_text, query, context, query_type)
            
            # Validate response with calculations
            validation_result = self._validate_response(formatted_response, query, context, analytics_data)
            
            return {
                "response": formatted_response,
                "raw_response": response_text,
                "query": query,
                "query_type": query_type,
                "context_used": len(context),
                "analytics_data": analytics_data,
                "validation_result": validation_result,
                "generated_at": datetime.now().isoformat(),
                "llm_provider": self.llm_provider,
                "llm_model": self.llm_model,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return self._generate_error_response(query, str(e))
    
    def _call_llm(self, prompt: str) -> Optional[str]:
        """
        Call the LLM with a prompt
        
        Args:
            prompt: Prompt to send to LLM
            
        Returns:
            Generated response text or None
        """
        try:
            if self.llm_provider.lower() == "openai":
                return self._call_openai(prompt)
            elif self.llm_provider.lower() == "anthropic":
                return self._call_anthropic(prompt)
            elif self.llm_provider.lower() == "google":
                return self._call_google(prompt)
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            return None
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful fitness data assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return None
    
    def _call_anthropic(self, prompt: str) -> Optional[str]:
        """Call Anthropic API"""
        try:
            response = self.llm_client.messages.create(
                model=self.llm_model,
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"❌ Anthropic API error: {e}")
            return None
    
    def _call_google(self, prompt: str) -> Optional[str]:
        """Call Google API"""
        try:
            model = self.llm_client.GenerativeModel(self.llm_model)
            response = model.generate_content(
                prompt,
                generation_config=self.llm_client.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1000
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Google API error: {e}")
            return None
    
    def _classify_query_type(self, query: str) -> str:
        """
        Classify query type for prompt selection
        
        Args:
            query: User query
            
        Returns:
            Query type
        """
        query_lower = query.lower()
        
        # Simple classification based on keywords
        if any(word in query_lower for word in ["trend", "changed", "progress", "improved", "decreased", "increased"]):
            return "trend"
        elif any(word in query_lower for word in ["compare", "difference", "vs", "versus", "between"]):
            return "comparison"
        elif any(word in query_lower for word in ["summary", "overview", "journey", "overall"]):
            return "summary"
        elif any(word in query_lower for word in ["goal", "target", "achieving", "progress toward"]):
            return "goal"
        else:
            return "specific"
    
    def _format_response(self, response_text: str, query: str, context: List[Dict[str, Any]], 
                        query_type: str) -> str:
        """
        Format and structure the LLM response
        
        Args:
            response_text: Raw LLM response
            query: Original query
            context: Context used
            query_type: Query type
            
        Returns:
            Formatted response
        """
        try:
            # Basic formatting - return only the response text without metadata
            formatted = response_text.strip()
            
            # Remove any metadata that might be in the response
            if "*Based on" in formatted:
                formatted = formatted.split("*Based on")[0].strip()
            
            return formatted
            
        except Exception as e:
            print(f"❌ Error formatting response: {e}")
            return response_text
    
    def _generate_fallback_response(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a fallback response when LLM is not available
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Fallback response
        """
        try:
            # Use the formatter to create a response from context
            if context:
                response = self.formatter.format_search_results(context, query)
            else:
                response = f"I don't have enough fitness data to answer your question: '{query}'. Please make sure you have some fitness measurements recorded."
            
            return {
                "response": response,
                "raw_response": response,
                "query": query,
                "query_type": "fallback",
                "context_used": len(context),
                "generated_at": datetime.now().isoformat(),
                "llm_provider": "fallback",
                "llm_model": "none",
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error generating fallback response: {e}")
            return self._generate_error_response(query, "Failed to generate response")
    
    def _generate_error_response(self, query: str, error_message: str) -> Dict[str, Any]:
        """
        Generate an error response
        
        Args:
            query: User query
            error_message: Error message
            
        Returns:
            Error response
        """
        try:
            # Use prompts to generate helpful error response
            error_prompt = self.prompts.get_error_prompt(query, error_message)
            
            if self.llm_client:
                error_response = self._call_llm(error_prompt)
            else:
                error_response = f"I'm sorry, I encountered an error while processing your question: '{query}'. Please try rephrasing your question or contact support if the issue persists."
            
            return {
                "response": error_response,
                "raw_response": error_response,
                "query": query,
                "query_type": "error",
                "context_used": 0,
                "generated_at": datetime.now().isoformat(),
                "llm_provider": self.llm_provider,
                "llm_model": self.llm_model,
                "success": False,
                "error": error_message
            }
            
        except Exception as e:
            print(f"❌ Error generating error response: {e}")
            return {
                "response": f"Error processing query: {error_message}",
                "raw_response": f"Error: {error_message}",
                "query": query,
                "query_type": "error",
                "context_used": 0,
                "generated_at": datetime.now().isoformat(),
                "llm_provider": "none",
                "llm_model": "none",
                "success": False,
                "error": error_message
            }
    
    def generate_follow_up_response(self, original_query: str, original_response: str,
                                  follow_up_query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a response for follow-up questions
        
        Args:
            original_query: Original user query
            original_response: Previous response
            follow_up_query: New follow-up query
            context: Updated context data
            
        Returns:
            Generated response
        """
        try:
            if not self.llm_client:
                return self._generate_fallback_response(follow_up_query, context)
            
            # Create follow-up prompt
            prompt = self.prompts.get_follow_up_prompt(
                original_query, original_response, follow_up_query, context
            )
            
            # Generate response
            response_text = self._call_llm(prompt)
            
            if not response_text:
                return self._generate_fallback_response(follow_up_query, context)
            
            # Format response
            formatted_response = self._format_response(response_text, follow_up_query, context, "follow_up")
            
            return {
                "response": formatted_response,
                "raw_response": response_text,
                "query": follow_up_query,
                "original_query": original_query,
                "query_type": "follow_up",
                "context_used": len(context),
                "generated_at": datetime.now().isoformat(),
                "llm_provider": self.llm_provider,
                "llm_model": self.llm_model,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error generating follow-up response: {e}")
            return self._generate_error_response(follow_up_query, str(e))
    
    def generate_help_response(self) -> Dict[str, Any]:
        """
        Generate a help response
        
        Returns:
            Help response
        """
        try:
            if not self.llm_client:
                return {
                    "response": self.formatter.format_help_response(),
                    "raw_response": self.formatter.format_help_response(),
                    "query": "help",
                    "query_type": "help",
                    "context_used": 0,
                    "generated_at": datetime.now().isoformat(),
                    "llm_provider": "fallback",
                    "llm_model": "none",
                    "success": True
                }
            
            # Create help prompt
            help_prompt = self.prompts.get_help_prompt()
            
            # Generate response
            response_text = self._call_llm(help_prompt)
            
            if not response_text:
                response_text = self.formatter.format_help_response()
            
            return {
                "response": response_text,
                "raw_response": response_text,
                "query": "help",
                "query_type": "help",
                "context_used": 0,
                "generated_at": datetime.now().isoformat(),
                "llm_provider": self.llm_provider,
                "llm_model": self.llm_model,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error generating help response: {e}")
            return self._generate_error_response("help", str(e))
    
    def generate_summary_response(self, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary response
        
        Args:
            context: Context data
            
        Returns:
            Summary response
        """
        try:
            if not self.llm_client:
                return self._generate_fallback_response("Provide a summary of my fitness journey", context)
            
            # Create summary prompt
            summary_prompt = self.prompts.get_summary_prompt(context)
            
            # Generate response
            response_text = self._call_llm(summary_prompt)
            
            if not response_text:
                return self._generate_fallback_response("Provide a summary of my fitness journey", context)
            
            # Format response
            formatted_response = self._format_response(response_text, "summary", context, "summary")
            
            return {
                "response": formatted_response,
                "raw_response": response_text,
                "query": "summary",
                "query_type": "summary",
                "context_used": len(context),
                "generated_at": datetime.now().isoformat(),
                "llm_provider": self.llm_provider,
                "llm_model": self.llm_model,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Error generating summary response: {e}")
            return self._generate_error_response("summary", str(e))
    
    def _perform_analytics(self, query: str, context: List[Dict[str, Any]], query_type: str) -> Dict[str, Any]:
        """
        Perform analytics and calculations based on query type
        
        Args:
            query: User query
            context: Retrieved context
            query_type: Type of query
            
        Returns:
            Analytics data dictionary
        """
        try:
            analytics_data = {
                'query_type': query_type,
                'data_summary': {},
                'calculations': {},
                'validation': {},
                'trends': {},
                'warnings': []
            }
            
            if not context:
                analytics_data['warnings'].append('No context data available for analysis')
                return analytics_data
            
            # Extract data from context
            fitness_data = self._extract_fitness_data(context)
            
            # Log data extraction results
            print(f"🔍 Extracted {len(fitness_data)} fitness records from {len(context)} context items")
            if fitness_data:
                print(f"📊 Sample data: {fitness_data[0]}")
            else:
                print(f"⚠️ No fitness data extracted from context")
                print(f"🔍 Context items: {[item.get('content', '')[:100] + '...' if len(str(item.get('content', ''))) > 100 else item.get('content', '') for item in context[:3]]}")
            
            # Basic data validation
            validation_result = self.calculations.validate_data_consistency(fitness_data)
            analytics_data['validation'] = validation_result
            
            # Calculate total weight loss
            total_loss_result = self.calculations.calculate_total_weight_loss(fitness_data)
            analytics_data['calculations']['total_weight_loss'] = {
                'value': total_loss_result.value,
                'unit': total_loss_result.unit,
                'confidence': total_loss_result.confidence,
                'warnings': total_loss_result.warnings
            }
            
            # Count actual weeks of data
            weeks_count = self.calculations.count_actual_weeks_of_data(fitness_data)
            analytics_data['calculations']['weeks_of_data'] = weeks_count
            
            # Data summary
            analytics_data['data_summary'] = {
                'total_records': len(fitness_data),
                'date_range': validation_result.get('date_range', {}),
                'weeks_count': weeks_count,
                'total_weight_loss': total_loss_result.value
            }
            
            # Query-specific analytics
            if query_type in ['time_range_analysis', 'calculation_request']:
                analytics_data.update(self._perform_query_specific_analytics(query, fitness_data, query_type))
            
            # Add analytics insights if available
            if self.analytics:
                try:
                    trends = self.analytics.analyze_trends('weight', 'month', 10)
                    analytics_data['trends'] = {
                        'weight_trends': [trend.__dict__ for trend in trends[:3]]  # Top 3 trends
                    }
                except Exception as e:
                    analytics_data['warnings'].append(f'Analytics error: {str(e)}')
            
            return analytics_data
            
        except Exception as e:
            print(f"❌ Error performing analytics: {e}")
            return {
                'query_type': query_type,
                'error': str(e),
                'warnings': ['Analytics processing failed']
            }
    
    def _extract_fitness_data(self, context: List[Dict[str, Any]]) -> List[Dict]:
        """
        Extract fitness data from context
        
        Args:
            context: Retrieved context
            
        Returns:
            List of fitness measurements
        """
        fitness_data = []
        
        for item in context:
            if isinstance(item, dict):
                # Extract data from content if it's a string
                if 'content' in item and isinstance(item['content'], str):
                    # Try to parse JSON from content
                    try:
                        import json
                        data = json.loads(item['content'])
                        if isinstance(data, dict) and 'date' in data:
                            fitness_data.append(data)
                    except json.JSONDecodeError:
                        # Try to extract structured data from text content
                        structured_data = self._extract_structured_data(item['content'])
                        if structured_data:
                            fitness_data.append(structured_data)
                
                # Also check metadata for fitness data
                if 'metadata' in item and isinstance(item['metadata'], dict):
                    metadata = item['metadata']
                    if 'date' in metadata and any(key in metadata for key in ['weight', 'bmi', 'fat_percent']):
                        fitness_data.append(metadata)
                        extracted = self._extract_structured_data(item['content'])
                        if extracted:
                            fitness_data.append(extracted)
                else:
                    # Direct data
                    if 'date' in item:
                        fitness_data.append(item)
        
        return fitness_data
    
    def _extract_structured_data(self, content: str) -> Optional[Dict]:
        """
        Extract structured fitness data from text content
        
        Args:
            content: Text content
            
        Returns:
            Structured data or None
        """
        try:
            # Simple pattern matching for common fitness data formats
            import re
            from datetime import datetime
            
            # Look for date patterns
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            date_match = re.search(date_pattern, content)
            
            if not date_match:
                return None
            
            date_str = date_match.group(1)
            
            # Look for weight patterns
            weight_pattern = r'weight[:\s]*(\d+\.?\d*)'
            weight_match = re.search(weight_pattern, content, re.IGNORECASE)
            
            data = {'date': date_str}
            
            if weight_match:
                data['weight'] = float(weight_match.group(1))
            
            # Look for other measurements
            measurements = ['bmi', 'fat_percent', 'chest', 'waist', 'arms', 'legs']
            for measurement in measurements:
                pattern = rf'{measurement}[:\s]*(\d+\.?\d*)'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    data[measurement] = float(match.group(1))
            
            return data if len(data) > 1 else None  # Must have at least date and one measurement
            
        except Exception as e:
            print(f"Error extracting structured data: {e}")
            return None
    
    def _perform_query_specific_analytics(self, query: str, fitness_data: List[Dict], query_type: str) -> Dict[str, Any]:
        """
        Perform analytics specific to query type
        
        Args:
            query: User query
            fitness_data: Fitness measurements
            query_type: Type of query
            
        Returns:
            Query-specific analytics data
        """
        analytics_data = {}
        
        try:
            if query_type == 'time_range_analysis':
                # Extract date ranges from query
                date_ranges = self._extract_date_ranges(query)
                for range_name, (start_date, end_date) in date_ranges.items():
                    period_result = self.calculations.calculate_weight_loss_in_period(
                        start_date, end_date, fitness_data
                    )
                    analytics_data[f'{range_name}_weight_loss'] = {
                        'value': period_result.value,
                        'unit': period_result.unit,
                        'confidence': period_result.confidence,
                        'warnings': period_result.warnings,
                        'data_points': period_result.data_points_used
                    }
            
            elif query_type == 'calculation_request':
                # Extract specific calculations from query
                calculations = self._extract_calculation_requests(query, fitness_data)
                analytics_data['requested_calculations'] = calculations
            
        except Exception as e:
            analytics_data['error'] = f'Query-specific analytics error: {str(e)}'
        
        return analytics_data
    
    def _extract_date_ranges(self, query: str) -> Dict[str, Tuple[datetime, datetime]]:
        """
        Extract date ranges from query
        
        Args:
            query: User query
            
        Returns:
            Dictionary of date ranges
        """
        date_ranges = {}
        
        try:
            from datetime import datetime, timedelta
            import re
            
            # Current date
            now = datetime.now()
            
            # Common date patterns
            patterns = {
                'this_week': (now - timedelta(days=7), now),
                'this_month': (now - timedelta(days=30), now),
                'last_month': (now - timedelta(days=60), now - timedelta(days=30)),
                'this_year': (datetime(now.year, 1, 1), now),
                'last_year': (datetime(now.year-1, 1, 1), datetime(now.year-1, 12, 31))
            }
            
            query_lower = query.lower()
            
            for range_name, (start, end) in patterns.items():
                if range_name.replace('_', ' ') in query_lower:
                    date_ranges[range_name] = (start, end)
            
            # Look for specific date mentions
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            dates = re.findall(date_pattern, query)
            
            if len(dates) >= 2:
                try:
                    start_date = datetime.strptime(dates[0], '%Y-%m-%d')
                    end_date = datetime.strptime(dates[1], '%Y-%m-%d')
                    date_ranges['custom_range'] = (start_date, end_date)
                except:
                    pass
            
        except Exception as e:
            print(f"Error extracting date ranges: {e}")
        
        return date_ranges
    
    def _extract_calculation_requests(self, query: str, fitness_data: List[Dict]) -> Dict[str, Any]:
        """
        Extract specific calculation requests from query
        
        Args:
            query: User query
            fitness_data: Fitness measurements
            
        Returns:
            Calculation results
        """
        calculations = {}
        
        try:
            query_lower = query.lower()
            
            # Check for specific calculation requests
            if 'total weight loss' in query_lower or 'overall weight loss' in query_lower:
                total_result = self.calculations.calculate_total_weight_loss(fitness_data)
                calculations['total_weight_loss'] = {
                    'value': total_result.value,
                    'unit': total_result.unit,
                    'confidence': total_result.confidence
                }
            
            if 'weeks' in query_lower and ('count' in query_lower or 'how many' in query_lower):
                weeks_count = self.calculations.count_actual_weeks_of_data(fitness_data)
                calculations['weeks_count'] = weeks_count
            
            if 'average' in query_lower and 'weight' in query_lower:
                if fitness_data:
                    weights = [record.get('weight', 0) for record in fitness_data if record.get('weight')]
                    if weights:
                        avg_weight = sum(weights) / len(weights)
                        calculations['average_weight'] = {
                            'value': avg_weight,
                            'unit': 'kg',
                            'data_points': len(weights)
                        }
            
        except Exception as e:
            calculations['error'] = f'Calculation extraction error: {str(e)}'
        
        return calculations
    
    def _validate_response(self, response: str, query: str, context: List[Dict[str, Any]], 
                          analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate response using analytics data
        
        Args:
            response: Generated response
            query: Original query
            context: Retrieved context
            analytics_data: Analytics data
            
        Returns:
            Validation result
        """
        validation_result = {
            'valid': True,
            'warnings': [],
            'suggestions': [],
            'confidence': 1.0
        }
        
        try:
            # Check for impossible calculations
            if 'calculations' in analytics_data:
                for calc_name, calc_data in analytics_data['calculations'].items():
                    if 'warnings' in calc_data and calc_data['warnings']:
                        validation_result['warnings'].extend(calc_data['warnings'])
                        validation_result['confidence'] *= 0.8
            
            # Check for data consistency issues
            if 'validation' in analytics_data:
                validation = analytics_data['validation']
                if not validation.get('valid', True):
                    validation_result['warnings'].extend(validation.get('issues', []))
                    validation_result['confidence'] *= 0.7
            
            # Check for week count discrepancies
            if 'weeks' in query.lower() and 'calculations' in analytics_data:
                weeks_calc = analytics_data['calculations'].get('weeks_of_data', 0)
                if weeks_calc == 0:
                    validation_result['warnings'].append('No weekly data available')
                    validation_result['confidence'] *= 0.6
            
            # Check for weight loss calculation accuracy
            if 'weight loss' in query.lower() and 'calculations' in analytics_data:
                weight_loss_calcs = [k for k in analytics_data['calculations'].keys() if 'weight_loss' in k]
                for calc_key in weight_loss_calcs:
                    calc_data = analytics_data['calculations'][calc_key]
                    if 'warnings' in calc_data and calc_data['warnings']:
                        validation_result['warnings'].extend(calc_data['warnings'])
                        validation_result['confidence'] *= 0.8
            
            # Adjust confidence based on warnings
            if validation_result['warnings']:
                validation_result['valid'] = False
                validation_result['suggestions'] = [
                    'Please verify the data accuracy',
                    'Consider checking the date ranges',
                    'Review the calculation methods used'
                ]
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['warnings'].append(f'Validation error: {str(e)}')
            validation_result['confidence'] = 0.0
        
        return validation_result
    
    def get_generator_info(self) -> Dict[str, Any]:
        """
        Get information about the response generator
        
        Returns:
            Generator information
        """
        return {
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "client_initialized": self.llm_client is not None,
            "available_providers": ["openai", "anthropic", "google"],
            "current_config": {
                "provider": self.llm_provider,
                "model": self.llm_model,
                "temperature": 0.3,
                "max_tokens": 1000
            }
        } 