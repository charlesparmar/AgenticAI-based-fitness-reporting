"""
Query Processor Module for RAG Pipeline
Handles natural language query processing and enhancement
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from .utils.embeddings import EmbeddingManager


class QueryProcessor:
    """Processes and enhances natural language queries for fitness data"""
    
    def __init__(self, embedding_provider: str = "sentence-transformers"):
        """
        Initialize query processor
        
        Args:
            embedding_provider: Embedding provider to use
        """
        self.embedding_manager = EmbeddingManager(embedding_provider)
        
        # Define query patterns
        self.query_patterns = {
            'trend': [
                r'(how|what).*(changed|trend|progress|improved|decreased|increased)',
                r'(trend|progress|change).*(over|during|in|for)',
                r'(weight|fat|bmi|measurements).*(trend|change|progress)'
            ],
            'comparison': [
                r'(compare|difference|vs|versus|between)',
                r'(week|month|period).*(to|vs|versus)',
                r'(then|now|before|after).*(vs|versus|compared)'
            ],
            'specific': [
                r'(what|show|get).*(weight|fat|bmi|measurements)',
                r'(current|latest|recent).*(measurements|data)',
                r'(on|at|for).*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})'
            ],
            'summary': [
                r'(summary|overview|statistics|stats)',
                r'(all|total|overall).*(data|measurements)',
                r'(journey|progress|fitness).*(summary|overview)'
            ],
            'goal': [
                r'(goal|target|objective)',
                r'(am i|are you|how).*(progress|achieving|meeting)',
                r'(strongest|weakest|best|worst).*(areas|measurements)'
            ],
            'time_range_analysis': [
                r'(until|till|up to|through|during|in|for).*(end|start|beginning|middle)',
                r'(since|from|starting|beginning).*(until|till|up to|end)',
                r'(last|this|next|previous).*(week|month|year|quarter)',
                r'(january|february|march|april|may|june|july|august|september|october|november|december)',
                r'(weight|fat|bmi).*(loss|change|progress).*(in|during|for).*(specific|period|time|date)'
            ],
            'calculation_request': [
                r'(calculate|compute|total|sum|how much|how many)',
                r'(weeks|months|days).*(of|with|data)',
                r'(average|mean|median|total).*(weight|fat|bmi)',
                r'(weight loss|fat loss).*(total|overall|in|during)'
            ],
            'data_summary': [
                r'(statistics|stats|summary|overview).*(data|measurements)',
                r'(how many|count|number).*(records|measurements|data points)',
                r'(data|measurements).*(summary|overview|statistics)'
            ]
        }
        
        # Define measurement keywords
        self.measurement_keywords = {
            'weight': ['weight', 'kg', 'pounds', 'lbs'],
            'fat_percent': ['fat', 'fat percentage', 'body fat', 'fat%'],
            'bmi': ['bmi', 'body mass index'],
            'fat_weight': ['fat weight', 'fat mass'],
            'lean_weight': ['lean weight', 'lean mass', 'muscle mass'],
            'body_measurements': ['neck', 'shoulders', 'biceps', 'forearms', 'chest', 
                                'above navel', 'navel', 'waist', 'hips', 'thighs', 'calves']
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with processed query information
        """
        try:
            if not query or not query.strip():
                return {"error": "Empty query"}
            
            query = query.strip().lower()
            
            # Analyze query type
            query_type = self._classify_query(query)
            
            # Extract entities
            entities = self._extract_entities(query)
            
            # Generate query embedding
            embedding = self.embedding_manager.get_single_embedding(query)
            
            # Create enhanced queries
            enhanced_queries = self._enhance_query(query, query_type, entities)
            
            # Build filter criteria
            filter_criteria = self._build_filter_criteria(query_type, entities)
            
            return {
                "original_query": query,
                "query_type": query_type,
                "entities": entities,
                "embedding": embedding,
                "enhanced_queries": enhanced_queries,
                "filter_criteria": filter_criteria,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return {"error": str(e)}
    
    def _classify_query(self, query: str) -> str:
        """
        Classify the type of query
        
        Args:
            query: Query string
            
        Returns:
            Query type (trend, comparison, specific, summary, goal, general)
        """
        try:
            # Define priority order for query types (more specific first)
            priority_order = [
                'time_range_analysis',
                'calculation_request', 
                'data_summary',
                'trend',
                'comparison',
                'goal',
                'summary',
                'specific'
            ]
            
            # Check patterns in priority order
            for query_type in priority_order:
                if query_type in self.query_patterns:
                    patterns = self.query_patterns[query_type]
                    for pattern in patterns:
                        if re.search(pattern, query, re.IGNORECASE):
                            return query_type
            
            return "general"
            
        except Exception as e:
            print(f"❌ Error classifying query: {e}")
            return "general"
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extract entities from the query
        
        Args:
            query: Query string
            
        Returns:
            Dictionary with extracted entities
        """
        try:
            entities = {
                "measurements": [],
                "dates": [],
                "time_periods": [],
                "comparison_terms": [],
                "numbers": []
            }
            
            # Extract measurements
            for category, keywords in self.measurement_keywords.items():
                for keyword in keywords:
                    if keyword in query:
                        entities["measurements"].append({
                            "category": category,
                            "keyword": keyword
                        })
            
            # Extract dates (YYYY-MM-DD format)
            date_pattern = r'\d{4}-\d{2}-\d{2}'
            dates = re.findall(date_pattern, query)
            entities["dates"].extend(dates)
            
            # Extract time periods
            time_patterns = {
                "week": r'(\d+)\s*(week|wk)s?',
                "month": r'(\d+)\s*(month|mo)s?',
                "year": r'(\d+)\s*(year|yr)s?',
                "days": r'(\d+)\s*(day|d)s?'
            }
            
            for period_type, pattern in time_patterns.items():
                matches = re.findall(pattern, query, re.IGNORECASE)
                for match in matches:
                    entities["time_periods"].append({
                        "type": period_type,
                        "value": int(match[0]),
                        "unit": match[1]
                    })
            
            # Extract comparison terms
            comparison_terms = ["vs", "versus", "compare", "difference", "between"]
            for term in comparison_terms:
                if term in query:
                    entities["comparison_terms"].append(term)
            
            # Extract numbers
            number_pattern = r'\d+(?:\.\d+)?'
            numbers = re.findall(number_pattern, query)
            entities["numbers"] = [float(num) for num in numbers]
            
            return entities
            
        except Exception as e:
            print(f"❌ Error extracting entities: {e}")
            return {"measurements": [], "dates": [], "time_periods": [], "comparison_terms": [], "numbers": []}
    
    def _enhance_query(self, query: str, query_type: str, entities: Dict[str, Any]) -> List[str]:
        """
        Generate enhanced queries for better retrieval
        
        Args:
            query: Original query
            query_type: Type of query
            entities: Extracted entities
            
        Returns:
            List of enhanced queries
        """
        try:
            enhanced_queries = [query]
            
            # Add measurement-specific queries
            if entities["measurements"]:
                for measurement in entities["measurements"]:
                    category = measurement["category"]
                    keyword = measurement["keyword"]
                    
                    if query_type == "trend":
                        enhanced_queries.append(f"{keyword} trend over time")
                        enhanced_queries.append(f"{keyword} changes progress")
                    
                    elif query_type == "comparison":
                        enhanced_queries.append(f"{keyword} comparison")
                        enhanced_queries.append(f"{keyword} difference")
                    
                    elif query_type == "specific":
                        enhanced_queries.append(f"{keyword} measurements")
                        enhanced_queries.append(f"current {keyword}")
            
            # Add time-based enhancements
            if entities["time_periods"]:
                for period in entities["time_periods"]:
                    if query_type == "trend":
                        enhanced_queries.append(f"trend over {period['value']} {period['type']}s")
                        enhanced_queries.append(f"changes in last {period['value']} {period['type']}s")
            
            # Add summary enhancements
            if query_type == "summary":
                enhanced_queries.extend([
                    "fitness data summary",
                    "overall statistics",
                    "complete measurements overview"
                ])
            
            # Add goal-related enhancements
            if query_type == "goal":
                enhanced_queries.extend([
                    "progress toward goals",
                    "achievement analysis",
                    "performance evaluation"
                ])
            
            # Remove duplicates while preserving order
            seen = set()
            unique_queries = []
            for q in enhanced_queries:
                if q not in seen:
                    seen.add(q)
                    unique_queries.append(q)
            
            return unique_queries
            
        except Exception as e:
            print(f"❌ Error enhancing query: {e}")
            return [query]
    
    def _build_filter_criteria(self, query_type: str, entities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build filter criteria for vector search
        
        Args:
            query_type: Type of query
            entities: Extracted entities
            
        Returns:
            Filter criteria dictionary or None
        """
        try:
            filter_criteria = {}
            
            # Add measurement type filters
            if entities["measurements"]:
                measurement_types = [m["category"] for m in entities["measurements"]]
                if measurement_types:
                    filter_criteria["type"] = {"$in": measurement_types}
            
            # Add date filters
            if entities["dates"]:
                # For specific date queries
                if query_type == "specific":
                    filter_criteria["date"] = {"$in": entities["dates"]}
            
            # Add time period filters
            if entities["time_periods"] and query_type in ["trend", "comparison"]:
                # Calculate date range based on time periods
                end_date = datetime.now()
                for period in entities["time_periods"]:
                    if period["type"] == "week":
                        start_date = end_date - timedelta(weeks=period["value"])
                    elif period["type"] == "month":
                        start_date = end_date - timedelta(days=period["value"] * 30)
                    elif period["type"] == "year":
                        start_date = end_date - timedelta(days=period["value"] * 365)
                    else:
                        start_date = end_date - timedelta(days=period["value"])
                    
                    filter_criteria["date"] = {
                        "$gte": start_date.strftime("%Y-%m-%d"),
                        "$lte": end_date.strftime("%Y-%m-%d")
                    }
            
            return filter_criteria if filter_criteria else None
            
        except Exception as e:
            print(f"❌ Error building filter criteria: {e}")
            return None
    
    def normalize_query(self, query: str) -> str:
        """
        Normalize query for better matching
        
        Args:
            query: Query string
            
        Returns:
            Normalized query string
        """
        try:
            # Convert to lowercase
            normalized = query.lower()
            
            # Remove extra whitespace
            normalized = re.sub(r'\s+', ' ', normalized)
            
            # Remove punctuation (keep some important ones)
            normalized = re.sub(r'[^\w\s\-]', ' ', normalized)
            
            # Normalize common variations
            replacements = {
                'weight': 'weight',
                'fat %': 'fat_percent',
                'fat percent': 'fat_percent',
                'body mass index': 'bmi',
                'body fat': 'fat_percent',
                'vs': 'versus',
                'wk': 'week',
                'mo': 'month',
                'yr': 'year'
            }
            
            for old, new in replacements.items():
                normalized = normalized.replace(old, new)
            
            return normalized.strip()
            
        except Exception as e:
            print(f"❌ Error normalizing query: {e}")
            return query
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Validate if query is suitable for processing
        
        Args:
            query: Query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not query or not query.strip():
                return False, "Query is empty"
            
            if len(query.strip()) < 3:
                return False, "Query is too short"
            
            if len(query.strip()) > 500:
                return False, "Query is too long"
            
            # Check for minimum meaningful content
            words = query.strip().split()
            if len(words) < 2:
                return False, "Query needs at least 2 words"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def extract_date_ranges(self, query: str) -> Dict[str, Any]:
        """
        Extract date ranges from query
        
        Args:
            query: User query
            
        Returns:
            Dictionary with extracted date ranges
        """
        try:
            date_ranges = {
                'explicit_dates': [],
                'relative_ranges': [],
                'month_ranges': [],
                'seasonal_ranges': [],
                'parsed_ranges': {}
            }
            
            # Extract explicit dates
            explicit_dates = self._extract_explicit_dates(query)
            date_ranges['explicit_dates'] = explicit_dates
            
            # Extract relative date ranges
            relative_ranges = self._extract_relative_ranges(query)
            date_ranges['relative_ranges'] = relative_ranges
            
            # Extract month-based ranges
            month_ranges = self._extract_month_ranges(query)
            date_ranges['month_ranges'] = month_ranges
            
            # Extract seasonal ranges
            seasonal_ranges = self._extract_seasonal_ranges(query)
            date_ranges['seasonal_ranges'] = seasonal_ranges
            
            # Parse all ranges into datetime objects
            parsed_ranges = self._parse_date_ranges(date_ranges)
            date_ranges['parsed_ranges'] = parsed_ranges
            
            return date_ranges
            
        except Exception as e:
            print(f"❌ Error extracting date ranges: {e}")
            return {'error': str(e)}
    
    def _extract_explicit_dates(self, query: str) -> List[str]:
        """
        Extract explicit date mentions from query
        
        Args:
            query: User query
            
        Returns:
            List of explicit dates found
        """
        dates = []
        
        # Date patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY or DD-MM-YYYY
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # MM.DD.YYYY or DD.MM.YYYY
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            dates.extend(matches)
        
        return list(set(dates))  # Remove duplicates
    
    def _extract_relative_ranges(self, query: str) -> List[Dict[str, str]]:
        """
        Extract relative date ranges from query
        
        Args:
            query: User query
            
        Returns:
            List of relative ranges
        """
        ranges = []
        query_lower = query.lower()
        
        # Relative time patterns
        relative_patterns = {
            'this_week': r'(this\s+week|current\s+week|past\s+7\s+days)',
            'last_week': r'(last\s+week|previous\s+week|past\s+week)',
            'this_month': r'(this\s+month|current\s+month|past\s+30\s+days)',
            'last_month': r'(last\s+month|previous\s+month|past\s+month)',
            'this_year': r'(this\s+year|current\s+year|past\s+year)',
            'last_year': r'(last\s+year|previous\s+year|past\s+year)',
            'yesterday': r'(yesterday|day\s+before)',
            'today': r'(today|current\s+day)',
            'tomorrow': r'(tomorrow|next\s+day)'
        }
        
        for range_name, pattern in relative_patterns.items():
            if re.search(pattern, query_lower):
                ranges.append({
                    'type': 'relative',
                    'range': range_name,
                    'pattern': pattern
                })
        
        return ranges
    
    def _extract_month_ranges(self, query: str) -> List[Dict[str, str]]:
        """
        Extract month-based ranges from query
        
        Args:
            query: User query
            
        Returns:
            List of month ranges
        """
        ranges = []
        query_lower = query.lower()
        
        # Month patterns
        months = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        
        # Look for month mentions
        for month_name, month_num in months.items():
            if month_name in query_lower:
                # Check for "until end of [month]" pattern
                if f'until end of {month_name}' in query_lower or f'till end of {month_name}' in query_lower:
                    ranges.append({
                        'type': 'month_end',
                        'month': month_name,
                        'month_num': month_num,
                        'pattern': f'until end of {month_name}'
                    })
                # Check for "in [month]" pattern
                elif f'in {month_name}' in query_lower:
                    ranges.append({
                        'type': 'month_period',
                        'month': month_name,
                        'month_num': month_num,
                        'pattern': f'in {month_name}'
                    })
                # Check for "since [month]" pattern
                elif f'since {month_name}' in query_lower:
                    ranges.append({
                        'type': 'month_since',
                        'month': month_name,
                        'month_num': month_num,
                        'pattern': f'since {month_name}'
                    })
        
        return ranges
    
    def _extract_seasonal_ranges(self, query: str) -> List[Dict[str, str]]:
        """
        Extract seasonal ranges from query
        
        Args:
            query: User query
            
        Returns:
            List of seasonal ranges
        """
        ranges = []
        query_lower = query.lower()
        
        # Seasonal patterns
        seasons = {
            'spring': {'start_month': '03', 'end_month': '05'},
            'summer': {'start_month': '06', 'end_month': '08'},
            'autumn': {'start_month': '09', 'end_month': '11'},
            'fall': {'start_month': '09', 'end_month': '11'},
            'winter': {'start_month': '12', 'end_month': '02'}
        }
        
        for season_name, season_data in seasons.items():
            if season_name in query_lower:
                ranges.append({
                    'type': 'seasonal',
                    'season': season_name,
                    'start_month': season_data['start_month'],
                    'end_month': season_data['end_month'],
                    'pattern': season_name
                })
        
        return ranges
    
    def _parse_date_ranges(self, date_ranges: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse date ranges into datetime objects
        
        Args:
            date_ranges: Extracted date ranges
            
        Returns:
            Parsed date ranges with datetime objects
        """
        parsed_ranges = {}
        
        try:
            from datetime import datetime, timedelta
            
            current_date = datetime.now()
            
            # Parse explicit dates
            if date_ranges.get('explicit_dates'):
                parsed_ranges['explicit'] = []
                for date_str in date_ranges['explicit_dates']:
                    try:
                        # Try different date formats
                        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y']:
                            try:
                                parsed_date = datetime.strptime(date_str, fmt)
                                parsed_ranges['explicit'].append({
                                    'original': date_str,
                                    'parsed': parsed_date,
                                    'format': fmt
                                })
                                break
                            except ValueError:
                                continue
                    except Exception as e:
                        print(f"Error parsing explicit date {date_str}: {e}")
            
            # Parse relative ranges
            if date_ranges.get('relative_ranges'):
                parsed_ranges['relative'] = []
                for range_info in date_ranges['relative_ranges']:
                    range_name = range_info['range']
                    
                    if range_name == 'this_week':
                        start_date = current_date - timedelta(days=7)
                        end_date = current_date
                    elif range_name == 'last_week':
                        start_date = current_date - timedelta(days=14)
                        end_date = current_date - timedelta(days=7)
                    elif range_name == 'this_month':
                        start_date = current_date - timedelta(days=30)
                        end_date = current_date
                    elif range_name == 'last_month':
                        start_date = current_date - timedelta(days=60)
                        end_date = current_date - timedelta(days=30)
                    elif range_name == 'this_year':
                        start_date = datetime(current_date.year, 1, 1)
                        end_date = current_date
                    elif range_name == 'last_year':
                        start_date = datetime(current_date.year - 1, 1, 1)
                        end_date = datetime(current_date.year - 1, 12, 31)
                    elif range_name == 'yesterday':
                        start_date = current_date - timedelta(days=1)
                        end_date = current_date - timedelta(days=1)
                    elif range_name == 'today':
                        start_date = current_date
                        end_date = current_date
                    elif range_name == 'tomorrow':
                        start_date = current_date + timedelta(days=1)
                        end_date = current_date + timedelta(days=1)
                    else:
                        continue
                    
                    parsed_ranges['relative'].append({
                        'range_name': range_name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'pattern': range_info['pattern']
                    })
            
            # Parse month ranges
            if date_ranges.get('month_ranges'):
                parsed_ranges['monthly'] = []
                for range_info in date_ranges['month_ranges']:
                    month_num = int(range_info['month_num'])
                    current_year = current_date.year
                    
                    if range_info['type'] == 'month_end':
                        # Until end of month
                        if current_date.month > month_num:
                            year = current_year
                        else:
                            year = current_year - 1
                        
                        end_date = datetime(year, month_num, 1)
                        if month_num == 12:
                            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                        else:
                            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
                        
                        start_date = datetime(year, 1, 1)  # Start of year
                        
                    elif range_info['type'] == 'month_period':
                        # In month
                        if current_date.month > month_num:
                            year = current_year
                        else:
                            year = current_year - 1
                        
                        start_date = datetime(year, month_num, 1)
                        if month_num == 12:
                            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                        else:
                            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
                    
                    elif range_info['type'] == 'month_since':
                        # Since month
                        if current_date.month > month_num:
                            year = current_year
                        else:
                            year = current_year - 1
                        
                        start_date = datetime(year, month_num, 1)
                        end_date = current_date
                    
                    parsed_ranges['monthly'].append({
                        'month': range_info['month'],
                        'type': range_info['type'],
                        'start_date': start_date,
                        'end_date': end_date,
                        'pattern': range_info['pattern']
                    })
            
            # Parse seasonal ranges
            if date_ranges.get('seasonal_ranges'):
                parsed_ranges['seasonal'] = []
                for range_info in date_ranges['seasonal_ranges']:
                    current_year = current_date.year
                    start_month = int(range_info['start_month'])
                    end_month = int(range_info['end_month'])
                    
                    start_date = datetime(current_year, start_month, 1)
                    
                    if end_month < start_month:  # Crosses year boundary (winter)
                        end_date = datetime(current_year + 1, end_month, 1)
                        if end_month == 2:
                            end_date = datetime(current_year + 1, 3, 1) - timedelta(days=1)
                        else:
                            end_date = datetime(current_year + 1, end_month + 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(current_year, end_month + 1, 1) - timedelta(days=1)
                    
                    parsed_ranges['seasonal'].append({
                        'season': range_info['season'],
                        'start_date': start_date,
                        'end_date': end_date,
                        'pattern': range_info['pattern']
                    })
            
        except Exception as e:
            print(f"❌ Error parsing date ranges: {e}")
            parsed_ranges['error'] = str(e)
        
        return parsed_ranges
    
    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """
        Get query suggestions based on partial input
        
        Args:
            partial_query: Partial query string
            
        Returns:
            List of suggested queries
        """
        try:
            suggestions = []
            partial = partial_query.lower().strip()
            
            # Common fitness query patterns
            common_patterns = [
                "How has my weight changed",
                "Show me my fat percentage trends",
                "What's my BMI progression",
                "Compare my measurements from week",
                "Give me a summary of my fitness journey",
                "What are my current body measurements",
                "Am I making progress toward my goals",
                "Show me my chest measurements",
                "What was my weight on",
                "How did my body composition change"
            ]
            
            # Filter suggestions based on partial query
            for pattern in common_patterns:
                if partial in pattern.lower():
                    suggestions.append(pattern)
            
            # Add measurement-specific suggestions
            for category, keywords in self.measurement_keywords.items():
                for keyword in keywords:
                    if keyword in partial:
                        suggestions.extend([
                            f"Show me my {keyword} trends",
                            f"What's my current {keyword}",
                            f"Compare my {keyword} over time"
                        ])
            
            # Remove duplicates and limit results
            unique_suggestions = list(dict.fromkeys(suggestions))
            return unique_suggestions[:10]
            
        except Exception as e:
            print(f"❌ Error getting query suggestions: {e}")
            return [] 