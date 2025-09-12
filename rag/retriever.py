"""
Retriever Module for RAG Pipeline
Handles semantic search and context retrieval from vector database
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from .vector_store import VectorStore
from .query_processor import QueryProcessor
from .utils.embeddings import EmbeddingManager


class Retriever:
    """Handles semantic search and context retrieval for fitness data"""
    
    def __init__(self, vector_store: VectorStore, 
                 query_processor: QueryProcessor = None,
                 embedding_provider: str = "sentence-transformers"):
        """
        Initialize retriever
        
        Args:
            vector_store: Vector store instance
            query_processor: Query processor instance (optional)
            embedding_provider: Embedding provider to use
        """
        self.vector_store = vector_store
        self.query_processor = query_processor or QueryProcessor(embedding_provider)
        self.embedding_manager = EmbeddingManager(embedding_provider)
        
        # Retrieval parameters
        self.default_n_results = 5
        self.max_n_results = 20
        self.min_similarity_threshold = 0.1
    
    def retrieve(self, query: str, n_results: int = None, 
                filter_criteria: Optional[Dict[str, Any]] = None,
                use_enhanced_queries: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query with date-based filtering
        
        Args:
            query: Natural language query
            n_results: Number of results to return
            filter_criteria: Optional filter criteria
            use_enhanced_queries: Whether to use enhanced queries
            
        Returns:
            List of retrieved documents with scores
        """
        try:
            if not query or not query.strip():
                return []
            
            n_results = n_results or self.default_n_results
            n_results = min(n_results, self.max_n_results)
            
            # Process query
            processed_query = self.query_processor.process_query(query)
            
            if "error" in processed_query:
                print(f"❌ Query processing error: {processed_query['error']}")
                return []
            
            # Extract date ranges for filtering
            date_ranges = self.query_processor.extract_date_ranges(query)
            
            # Build enhanced filter criteria with date ranges
            enhanced_filter_criteria = self._build_enhanced_filters(
                filter_criteria, date_ranges, processed_query
            )
            
            # Simplify filter criteria for ChromaDB compatibility
            if enhanced_filter_criteria and isinstance(enhanced_filter_criteria, dict):
                # Remove complex filter structures that ChromaDB can't handle
                simplified_filters = {}
                for key, value in enhanced_filter_criteria.items():
                    if isinstance(value, (str, int, float, bool)):
                        simplified_filters[key] = value
                    elif isinstance(value, list) and all(isinstance(v, (str, int, float, bool)) for v in value):
                        simplified_filters[key] = value
                enhanced_filter_criteria = simplified_filters if simplified_filters else None
            
            # Perform retrieval with fallback
            results = []
            try:
                if use_enhanced_queries and processed_query.get("enhanced_queries"):
                    results = self._retrieve_with_enhanced_queries(
                        processed_query, n_results, enhanced_filter_criteria
                    )
                else:
                    results = self._retrieve_single_query(
                        query, n_results, enhanced_filter_criteria
                    )
            except Exception as e:
                print(f"⚠️ Enhanced retrieval failed: {e}")
                # Fallback to simple retrieval without filters
                try:
                    results = self._retrieve_single_query(query, n_results, None)
                except Exception as fallback_error:
                    print(f"❌ Fallback retrieval also failed: {fallback_error}")
                    results = []
            
            # Filter results based on date ranges
            filtered_results = self._filter_results_by_date_ranges(
                results, date_ranges, processed_query
            )
            
            # Post-process results
            processed_results = self._post_process_results(filtered_results, processed_query)
            
            return processed_results
            
        except Exception as e:
            print(f"❌ Error in retrieval: {e}")
            return []
    
    def _retrieve_with_enhanced_queries(self, processed_query: Dict[str, Any], 
                                      n_results: int, 
                                      filter_criteria: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Retrieve using enhanced queries for better results
        
        Args:
            processed_query: Processed query information
            n_results: Number of results to return
            filter_criteria: Filter criteria
            
        Returns:
            List of retrieved documents
        """
        try:
            all_results = []
            enhanced_queries = processed_query.get("enhanced_queries", [])
            
            # Retrieve for each enhanced query
            for enhanced_query in enhanced_queries:
                results = self._retrieve_single_query(
                    enhanced_query, 
                    n_results * 2,  # Get more results to allow for deduplication
                    filter_criteria
                )
                all_results.extend(results)
            
            # Deduplicate and rank results
            unique_results = self._deduplicate_results(all_results)
            
            # Sort by score and take top results
            sorted_results = sorted(unique_results, key=lambda x: x.get('score', 0), reverse=True)
            
            return sorted_results[:n_results]
            
        except Exception as e:
            print(f"❌ Error in enhanced query retrieval: {e}")
            return []
    
    def _retrieve_single_query(self, query: str, n_results: int, 
                             filter_criteria: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Retrieve for a single query
        
        Args:
            query: Query string
            n_results: Number of results
            filter_criteria: Filter criteria
            
        Returns:
            List of retrieved documents
        """
        try:
            # Perform vector search
            results = self.vector_store.search(
                query=query,
                n_results=n_results,
                filter_dict=filter_criteria
            )
            
            return results
            
        except Exception as e:
            print(f"❌ Error in single query retrieval: {e}")
            return []
    
    def _post_process_results(self, results: List[Dict[str, Any]], 
                            processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Post-process retrieval results
        
        Args:
            results: Raw retrieval results
            processed_query: Processed query information
            
        Returns:
            Post-processed results
        """
        try:
            processed_results = []
            
            for result in results:
                # Apply similarity threshold
                score = result.get('score', 0)
                if score < self.min_similarity_threshold:
                    continue
                
                # Add query context
                processed_result = result.copy()
                processed_result['query_context'] = {
                    'query_type': processed_query.get('query_type'),
                    'entities': processed_query.get('entities'),
                    'original_query': processed_query.get('original_query')
                }
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(result, processed_query)
                processed_result['relevance_score'] = relevance_score
                
                processed_results.append(processed_result)
            
            # Sort by relevance score first, then by date (most recent first)
            def sort_key(x):
                relevance = x.get('relevance_score', 0)
                week_number = x.get('metadata', {}).get('week_number', '')
                
                # Extract week number for sorting (e.g., "Week 3 (2024)" -> 202403)
                try:
                    if week_number and 'Week' in week_number:
                        # Parse "Week X (YYYY)" format
                        import re
                        match = re.search(r'Week (\d+) \((\d+)\)', week_number)
                        if match:
                            week, year = match.groups()
                            sortable_week = f"{year}{int(week):02d}"
                            return (relevance, sortable_week)
                except:
                    pass
                
                # Fallback to date if week number not available
                date_str = x.get('metadata', {}).get('date', '')
                try:
                    if date_str and '-' in date_str:
                        parts = date_str.split('-')
                        if len(parts) == 3:
                            day, month, year = parts
                            sortable_date = f"{year}{month.zfill(2)}{day.zfill(2)}"
                            return (relevance, sortable_date)
                except:
                    pass
                
                return (relevance, week_number or date_str)
            
            processed_results.sort(key=sort_key, reverse=True)
            
            return processed_results
            
        except Exception as e:
            print(f"❌ Error in post-processing results: {e}")
            return results
    
    def _calculate_relevance_score(self, result: Dict[str, Any], 
                                 processed_query: Dict[str, Any]) -> float:
        """
        Calculate relevance score for a result
        
        Args:
            result: Retrieval result
            processed_query: Processed query information
            
        Returns:
            Relevance score
        """
        try:
            base_score = result.get('score', 0)
            relevance_score = base_score
            
            # Boost score based on query type match
            query_type = processed_query.get('query_type')
            metadata = result.get('metadata', {})
            result_type = metadata.get('type')
            
            if query_type and result_type:
                if query_type == 'trend' and result_type in ['trend', 'monthly_summary']:
                    relevance_score *= 1.2
                elif query_type == 'comparison' and result_type == 'trend':
                    relevance_score *= 1.1
                elif query_type == 'specific' and result_type == 'measurement':
                    relevance_score *= 1.15
                elif query_type == 'summary' and result_type == 'overall_summary':
                    relevance_score *= 1.3
            
            # Boost score based on entity matches
            entities = processed_query.get('entities', {})
            measurements = entities.get('measurements', [])
            
            if measurements and metadata.get('measurements'):
                result_measurements = metadata.get('measurements', {})
                for measurement in measurements:
                    category = measurement.get('category')
                    if category in result_measurements:
                        relevance_score *= 1.1
            
            return min(relevance_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            print(f"❌ Error calculating relevance score: {e}")
            return result.get('score', 0)
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate results based on content similarity
        
        Args:
            results: List of results
            
        Returns:
            Deduplicated results
        """
        try:
            unique_results = []
            seen_contents = set()
            
            for result in results:
                content = result.get('content', '')
                if not content:
                    continue
                
                # Create a hash of the content for deduplication
                content_hash = hash(content[:100])  # Use first 100 chars
                
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    unique_results.append(result)
            
            return unique_results
            
        except Exception as e:
            print(f"❌ Error deduplicating results: {e}")
            return results
    
    def retrieve_by_embedding(self, embedding: List[float], n_results: int = None,
                            filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve using a pre-computed embedding
        
        Args:
            embedding: Query embedding vector
            n_results: Number of results
            filter_criteria: Filter criteria
            
        Returns:
            List of retrieved documents
        """
        try:
            n_results = n_results or self.default_n_results
            n_results = min(n_results, self.max_n_results)
            
            results = self.vector_store.search_by_embedding(
                embedding=embedding,
                n_results=n_results,
                filter_dict=filter_criteria
            )
            
            # Apply similarity threshold
            filtered_results = [
                result for result in results 
                if result.get('score', 0) >= self.min_similarity_threshold
            ]
            
            return filtered_results
            
        except Exception as e:
            print(f"❌ Error in embedding-based retrieval: {e}")
            return []
    
    def hybrid_search(self, query: str, n_results: int = None,
                     filter_criteria: Optional[Dict[str, Any]] = None,
                     semantic_weight: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword matching
        
        Args:
            query: Query string
            n_results: Number of results
            filter_criteria: Filter criteria
            semantic_weight: Weight for semantic search (0-1)
            
        Returns:
            List of retrieved documents
        """
        try:
            n_results = n_results or self.default_n_results
            
            # Semantic search
            semantic_results = self.retrieve(query, n_results * 2, filter_criteria)
            
            # Keyword search (simple implementation)
            keyword_results = self._keyword_search(query, n_results * 2, filter_criteria)
            
            # Combine results
            combined_results = self._combine_search_results(
                semantic_results, keyword_results, semantic_weight
            )
            
            return combined_results[:n_results]
            
        except Exception as e:
            print(f"❌ Error in hybrid search: {e}")
            return []
    
    def _keyword_search(self, query: str, n_results: int,
                       filter_criteria: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search
        
        Args:
            query: Query string
            n_results: Number of results
            filter_criteria: Filter criteria
            
        Returns:
            List of keyword search results
        """
        try:
            # This is a simplified keyword search
            # In a real implementation, you might use BM25 or similar
            
            # For now, just return semantic search results
            # as a placeholder for keyword search
            return self.retrieve(query, n_results, filter_criteria, use_enhanced_queries=False)
            
        except Exception as e:
            print(f"❌ Error in keyword search: {e}")
            return []
    
    def _combine_search_results(self, semantic_results: List[Dict[str, Any]],
                              keyword_results: List[Dict[str, Any]],
                              semantic_weight: float) -> List[Dict[str, Any]]:
        """
        Combine semantic and keyword search results
        
        Args:
            semantic_results: Semantic search results
            keyword_results: Keyword search results
            semantic_weight: Weight for semantic search
            
        Returns:
            Combined results
        """
        try:
            combined_scores = {}
            
            # Process semantic results
            for result in semantic_results:
                doc_id = result.get('id')
                semantic_score = result.get('score', 0)
                
                if doc_id not in combined_scores:
                    combined_scores[doc_id] = {
                        'result': result,
                        'semantic_score': semantic_score,
                        'keyword_score': 0
                    }
                else:
                    combined_scores[doc_id]['semantic_score'] = max(
                        combined_scores[doc_id]['semantic_score'], semantic_score
                    )
            
            # Process keyword results
            for result in keyword_results:
                doc_id = result.get('id')
                keyword_score = result.get('score', 0)
                
                if doc_id not in combined_scores:
                    combined_scores[doc_id] = {
                        'result': result,
                        'semantic_score': 0,
                        'keyword_score': keyword_score
                    }
                else:
                    combined_scores[doc_id]['keyword_score'] = max(
                        combined_scores[doc_id]['keyword_score'], keyword_score
                    )
            
            # Calculate combined scores
            combined_results = []
            for doc_id, scores in combined_scores.items():
                combined_score = (
                    semantic_weight * scores['semantic_score'] +
                    (1 - semantic_weight) * scores['keyword_score']
                )
                
                result = scores['result'].copy()
                result['combined_score'] = combined_score
                result['semantic_score'] = scores['semantic_score']
                result['keyword_score'] = scores['keyword_score']
                
                combined_results.append(result)
            
            # Sort by combined score
            combined_results.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
            
            return combined_results
            
        except Exception as e:
            print(f"❌ Error combining search results: {e}")
            return semantic_results
    
    def _build_enhanced_filters(self, filter_criteria: Optional[Dict[str, Any]], 
                               date_ranges: Dict[str, Any], 
                               processed_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build enhanced filter criteria with date ranges
        
        Args:
            filter_criteria: Original filter criteria
            date_ranges: Extracted date ranges
            processed_query: Processed query information
            
        Returns:
            Enhanced filter criteria
        """
        try:
            enhanced_filters = filter_criteria or {}
            
            # Add date range filters if available
            if date_ranges and not date_ranges.get('error'):
                parsed_ranges = date_ranges.get('parsed_ranges', {})
                
                # Extract date filters from parsed ranges
                date_filters = []
                
                # Add explicit date filters
                if parsed_ranges.get('explicit'):
                    for date_info in parsed_ranges['explicit']:
                        date_filters.append({
                            'type': 'exact_date',
                            'date': date_info['parsed'],
                            'original': date_info['original']
                        })
                
                # Add relative range filters
                if parsed_ranges.get('relative'):
                    for range_info in parsed_ranges['relative']:
                        date_filters.append({
                            'type': 'date_range',
                            'start_date': range_info['start_date'],
                            'end_date': range_info['end_date'],
                            'range_name': range_info['range_name']
                        })
                
                # Add monthly range filters
                if parsed_ranges.get('monthly'):
                    for range_info in parsed_ranges['monthly']:
                        date_filters.append({
                            'type': 'date_range',
                            'start_date': range_info['start_date'],
                            'end_date': range_info['end_date'],
                            'month': range_info['month']
                        })
                
                # Add seasonal range filters
                if parsed_ranges.get('seasonal'):
                    for range_info in parsed_ranges['seasonal']:
                        date_filters.append({
                            'type': 'date_range',
                            'start_date': range_info['start_date'],
                            'end_date': range_info['end_date'],
                            'season': range_info['season']
                        })
                
                if date_filters:
                    enhanced_filters['date_filters'] = date_filters
            
            # Add query type specific filters
            query_type = processed_query.get('query_type', 'general')
            if query_type in ['time_range_analysis', 'calculation_request']:
                enhanced_filters['query_type'] = query_type
            
            return enhanced_filters if enhanced_filters else None
            
        except Exception as e:
            print(f"❌ Error building enhanced filters: {e}")
            return filter_criteria
    
    def _filter_results_by_date_ranges(self, results: List[Dict[str, Any]], 
                                      date_ranges: Dict[str, Any], 
                                      processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter results based on date ranges
        
        Args:
            results: Retrieved results
            date_ranges: Extracted date ranges
            processed_query: Processed query information
            
        Returns:
            Filtered results
        """
        try:
            if not date_ranges or date_ranges.get('error'):
                return results
            
            parsed_ranges = date_ranges.get('parsed_ranges', {})
            if not parsed_ranges:
                return results
            
            filtered_results = []
            
            for result in results:
                # Extract date from result
                result_date = self._extract_date_from_result(result)
                
                if result_date is None:
                    # If no date found, include the result (don't filter out)
                    filtered_results.append(result)
                    continue
                
                # Check if result date matches any of the date ranges
                if self._date_matches_ranges(result_date, parsed_ranges):
                    filtered_results.append(result)
            
            # If no results match date ranges, return original results
            if not filtered_results and results:
                print("⚠️ No results match date ranges, returning all results")
                return results
            
            return filtered_results
            
        except Exception as e:
            print(f"❌ Error filtering results by date ranges: {e}")
            return results
    
    def _extract_date_from_result(self, result: Dict[str, Any]) -> Optional[str]:
        """
        Extract date from result content
        
        Args:
            result: Result dictionary
            
        Returns:
            Extracted date string or None
        """
        try:
            from datetime import datetime
            import re
            
            # Try to extract date from content
            content = result.get('content', '')
            if not content:
                return None
            
            # Look for date patterns in content
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
                r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, content)
                if match:
                    date_str = match.group(0)
                    # Validate date format
                    try:
                        if '-' in date_str and len(date_str.split('-')[0]) == 4:
                            datetime.strptime(date_str, '%Y-%m-%d')
                        elif '/' in date_str:
                            datetime.strptime(date_str, '%m/%d/%Y')
                        elif '-' in date_str and len(date_str.split('-')[0]) == 2:
                            datetime.strptime(date_str, '%m-%d-%Y')
                        return date_str
                    except ValueError:
                        continue
            
            # Try to extract from metadata
            metadata = result.get('metadata', {})
            if 'date' in metadata:
                return str(metadata['date'])
            
            return None
            
        except Exception as e:
            print(f"Error extracting date from result: {e}")
            return None
    
    def _date_matches_ranges(self, result_date: str, parsed_ranges: Dict[str, Any]) -> bool:
        """
        Check if result date matches any of the parsed ranges
        
        Args:
            result_date: Date string from result
            parsed_ranges: Parsed date ranges
            
        Returns:
            True if date matches any range
        """
        try:
            from datetime import datetime
            
            # Parse result date
            try:
                if '-' in result_date and len(result_date.split('-')[0]) == 4:
                    parsed_result_date = datetime.strptime(result_date, '%Y-%m-%d')
                elif '/' in result_date:
                    parsed_result_date = datetime.strptime(result_date, '%m/%d/%Y')
                elif '-' in result_date and len(result_date.split('-')[0]) == 2:
                    parsed_result_date = datetime.strptime(result_date, '%m-%d-%Y')
                else:
                    return False
            except ValueError:
                return False
            
            # Check explicit dates
            if parsed_ranges.get('explicit'):
                for date_info in parsed_ranges['explicit']:
                    if parsed_result_date.date() == date_info['parsed'].date():
                        return True
            
            # Check relative ranges
            if parsed_ranges.get('relative'):
                for range_info in parsed_ranges['relative']:
                    start_date = range_info['start_date']
                    end_date = range_info['end_date']
                    if start_date.date() <= parsed_result_date.date() <= end_date.date():
                        return True
            
            # Check monthly ranges
            if parsed_ranges.get('monthly'):
                for range_info in parsed_ranges['monthly']:
                    start_date = range_info['start_date']
                    end_date = range_info['end_date']
                    if start_date.date() <= parsed_result_date.date() <= end_date.date():
                        return True
            
            # Check seasonal ranges
            if parsed_ranges.get('seasonal'):
                for range_info in parsed_ranges['seasonal']:
                    start_date = range_info['start_date']
                    end_date = range_info['end_date']
                    if start_date.date() <= parsed_result_date.date() <= end_date.date():
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking date matches: {e}")
            return False
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get retrieval statistics
        
        Returns:
            Dictionary with retrieval statistics
        """
        try:
            collection_info = self.vector_store.get_collection_info()
            
            return {
                "collection_info": collection_info,
                "retrieval_params": {
                    "default_n_results": self.default_n_results,
                    "max_n_results": self.max_n_results,
                    "min_similarity_threshold": self.min_similarity_threshold
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting retrieval stats: {e}")
            return {"error": str(e)} 