"""
Cache Module for RAG Pipeline
Response caching, vector search optimization, and query result caching
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pickle
import os


@dataclass
class CacheEntry:
    """Represents a cache entry"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    access_count: int
    last_accessed: datetime
    metadata: Dict[str, Any] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data


class ResponseCache:
    """Caches LLM responses for improved performance"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize response cache
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
    
    def _generate_key(self, query: str, context: List[Dict], query_type: str) -> str:
        """Generate cache key from query and context"""
        try:
            # Create a hash of the query and context
            context_str = json.dumps(context, sort_keys=True)
            key_data = f"{query}:{context_str}:{query_type}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception as e:
            print(f"❌ Error generating cache key: {e}")
            return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str, context: List[Dict], query_type: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response
        
        Args:
            query: User query
            context: Retrieved context
            query_type: Type of query
            
        Returns:
            Cached response or None
        """
        try:
            key = self._generate_key(query, context, query_type)
            
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if entry.is_expired():
                    self._remove_entry(key)
                    return None
                
                # Update access statistics
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                # Update access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return entry.value
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting from cache: {e}")
            return None
    
    def set(self, query: str, context: List[Dict], query_type: str, 
            response: Dict[str, Any], ttl: int = None) -> bool:
        """
        Cache a response
        
        Args:
            query: User query
            context: Retrieved context
            query_type: Type of query
            response: Response to cache
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._generate_key(query, context, query_type)
            ttl = ttl or self.default_ttl
            
            # Check cache size and evict if necessary
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # Create cache entry
            now = datetime.now()
            entry = CacheEntry(
                key=key,
                value=response,
                created_at=now,
                expires_at=now + timedelta(seconds=ttl),
                access_count=1,
                last_accessed=now,
                metadata={
                    'query': query,
                    'query_type': query_type,
                    'context_count': len(context)
                }
            )
            
            # Add to cache
            self.cache[key] = entry
            self.access_order.append(key)
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting cache: {e}")
            return False
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)
    
    def _evict_oldest(self):
        """Evict oldest accessed entry"""
        if self.access_order:
            oldest_key = self.access_order[0]
            self._remove_entry(oldest_key)
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
            
            if total_entries > 0:
                avg_access_count = sum(entry.access_count for entry in self.cache.values()) / total_entries
                hit_rate = sum(1 for entry in self.cache.values() if entry.access_count > 1) / total_entries
            else:
                avg_access_count = 0
                hit_rate = 0
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "average_access_count": round(avg_access_count, 2),
                "hit_rate": round(hit_rate * 100, 2),
                "max_size": self.max_size,
                "utilization": round((total_entries / self.max_size) * 100, 2)
            }
        except Exception as e:
            print(f"❌ Error getting cache stats: {e}")
            return {"error": str(e)}


class VectorSearchCache:
    """Caches vector search results for improved performance"""
    
    def __init__(self, max_size: int = 500, default_ttl: int = 1800):
        """
        Initialize vector search cache
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
    
    def _generate_key(self, query: str, n_results: int, filters: Dict = None) -> str:
        """Generate cache key from query and parameters"""
        try:
            filters_str = json.dumps(filters, sort_keys=True) if filters else "{}"
            key_data = f"{query}:{n_results}:{filters_str}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception as e:
            print(f"❌ Error generating vector cache key: {e}")
            return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str, n_results: int, filters: Dict = None) -> Optional[List[Dict]]:
        """
        Get cached search results
        
        Args:
            query: Search query
            n_results: Number of results requested
            filters: Search filters
            
        Returns:
            Cached results or None
        """
        try:
            key = self._generate_key(query, n_results, filters)
            
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if entry.is_expired():
                    self._remove_entry(key)
                    return None
                
                # Update access statistics
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                # Update access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return entry.value
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting from vector cache: {e}")
            return None
    
    def set(self, query: str, n_results: int, filters: Dict, 
            results: List[Dict], ttl: int = None) -> bool:
        """
        Cache search results
        
        Args:
            query: Search query
            n_results: Number of results requested
            filters: Search filters
            results: Search results to cache
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._generate_key(query, n_results, filters)
            ttl = ttl or self.default_ttl
            
            # Check cache size and evict if necessary
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # Create cache entry
            now = datetime.now()
            entry = CacheEntry(
                key=key,
                value=results,
                created_at=now,
                expires_at=now + timedelta(seconds=ttl),
                access_count=1,
                last_accessed=now,
                metadata={
                    'query': query,
                    'n_results': n_results,
                    'filters': filters,
                    'results_count': len(results)
                }
            )
            
            # Add to cache
            self.cache[key] = entry
            self.access_order.append(key)
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting vector cache: {e}")
            return False
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)
    
    def _evict_oldest(self):
        """Evict oldest accessed entry"""
        if self.access_order:
            oldest_key = self.access_order[0]
            self._remove_entry(oldest_key)
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
            
            if total_entries > 0:
                avg_access_count = sum(entry.access_count for entry in self.cache.values()) / total_entries
                hit_rate = sum(1 for entry in self.cache.values() if entry.access_count > 1) / total_entries
                avg_results = sum(entry.metadata.get('results_count', 0) for entry in self.cache.values()) / total_entries
            else:
                avg_access_count = 0
                hit_rate = 0
                avg_results = 0
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "average_access_count": round(avg_access_count, 2),
                "hit_rate": round(hit_rate * 100, 2),
                "average_results_per_query": round(avg_results, 2),
                "max_size": self.max_size,
                "utilization": round((total_entries / self.max_size) * 100, 2)
            }
        except Exception as e:
            print(f"❌ Error getting vector cache stats: {e}")
            return {"error": str(e)}


class EmbeddingCache:
    """Caches embeddings for improved performance"""
    
    def __init__(self, max_size: int = 2000, default_ttl: int = 7200):
        """
        Initialize embedding cache
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
    
    def _generate_key(self, text: str, model_name: str) -> str:
        """Generate cache key from text and model"""
        try:
            key_data = f"{text}:{model_name}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception as e:
            print(f"❌ Error generating embedding cache key: {e}")
            return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str, model_name: str) -> Optional[List[float]]:
        """
        Get cached embedding
        
        Args:
            text: Text to embed
            model_name: Embedding model name
            
        Returns:
            Cached embedding or None
        """
        try:
            key = self._generate_key(text, model_name)
            
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if entry.is_expired():
                    self._remove_entry(key)
                    return None
                
                # Update access statistics
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                # Update access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return entry.value
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting from embedding cache: {e}")
            return None
    
    def set(self, text: str, model_name: str, embedding: List[float], 
            ttl: int = None) -> bool:
        """
        Cache an embedding
        
        Args:
            text: Text that was embedded
            model_name: Embedding model name
            embedding: Embedding vector
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            key = self._generate_key(text, model_name)
            ttl = ttl or self.default_ttl
            
            # Check cache size and evict if necessary
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # Create cache entry
            now = datetime.now()
            entry = CacheEntry(
                key=key,
                value=embedding,
                created_at=now,
                expires_at=now + timedelta(seconds=ttl),
                access_count=1,
                last_accessed=now,
                metadata={
                    'text_length': len(text),
                    'model_name': model_name,
                    'embedding_dimension': len(embedding)
                }
            )
            
            # Add to cache
            self.cache[key] = entry
            self.access_order.append(key)
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting embedding cache: {e}")
            return False
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            self.access_order.remove(key)
    
    def _evict_oldest(self):
        """Evict oldest accessed entry"""
        if self.access_order:
            oldest_key = self.access_order[0]
            self._remove_entry(oldest_key)
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
            
            if total_entries > 0:
                avg_access_count = sum(entry.access_count for entry in self.cache.values()) / total_entries
                hit_rate = sum(1 for entry in self.cache.values() if entry.access_count > 1) / total_entries
                avg_dimension = sum(entry.metadata.get('embedding_dimension', 0) for entry in self.cache.values()) / total_entries
            else:
                avg_access_count = 0
                hit_rate = 0
                avg_dimension = 0
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "average_access_count": round(avg_access_count, 2),
                "hit_rate": round(hit_rate * 100, 2),
                "average_embedding_dimension": round(avg_dimension, 2),
                "max_size": self.max_size,
                "utilization": round((total_entries / self.max_size) * 100, 2)
            }
        except Exception as e:
            print(f"❌ Error getting embedding cache stats: {e}")
            return {"error": str(e)}


class CacheManager:
    """Manages all caching systems"""
    
    def __init__(self, response_cache_size: int = 1000, vector_cache_size: int = 500, 
                 embedding_cache_size: int = 2000):
        """
        Initialize cache manager
        
        Args:
            response_cache_size: Size of response cache
            vector_cache_size: Size of vector search cache
            embedding_cache_size: Size of embedding cache
        """
        self.response_cache = ResponseCache(max_size=response_cache_size)
        self.vector_cache = VectorSearchCache(max_size=vector_cache_size)
        self.embedding_cache = EmbeddingCache(max_size=embedding_cache_size)
    
    def get_response(self, query: str, context: List[Dict], query_type: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        return self.response_cache.get(query, context, query_type)
    
    def set_response(self, query: str, context: List[Dict], query_type: str, 
                    response: Dict[str, Any], ttl: int = None) -> bool:
        """Cache response"""
        return self.response_cache.set(query, context, query_type, response, ttl)
    
    def get_vector_results(self, query: str, n_results: int, filters: Dict = None) -> Optional[List[Dict]]:
        """Get cached vector search results"""
        return self.vector_cache.get(query, n_results, filters)
    
    def set_vector_results(self, query: str, n_results: int, filters: Dict, 
                          results: List[Dict], ttl: int = None) -> bool:
        """Cache vector search results"""
        return self.vector_cache.set(query, n_results, filters, results, ttl)
    
    def get_embedding(self, text: str, model_name: str) -> Optional[List[float]]:
        """Get cached embedding"""
        return self.embedding_cache.get(text, model_name)
    
    def set_embedding(self, text: str, model_name: str, embedding: List[float], 
                     ttl: int = None) -> bool:
        """Cache embedding"""
        return self.embedding_cache.set(text, model_name, embedding, ttl)
    
    def clear_all(self):
        """Clear all caches"""
        self.response_cache.clear()
        self.vector_cache.clear()
        self.embedding_cache.clear()
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches"""
        try:
            return {
                "response_cache": self.response_cache.get_stats(),
                "vector_cache": self.vector_cache.get_stats(),
                "embedding_cache": self.embedding_cache.get_stats(),
                "total_entries": (
                    self.response_cache.get_stats().get("total_entries", 0) +
                    self.vector_cache.get_stats().get("total_entries", 0) +
                    self.embedding_cache.get_stats().get("total_entries", 0)
                )
            }
        except Exception as e:
            print(f"❌ Error getting all cache stats: {e}")
            return {"error": str(e)}
    
    def optimize_caches(self):
        """Optimize cache performance"""
        try:
            # Remove expired entries
            for cache in [self.response_cache, self.vector_cache, self.embedding_cache]:
                expired_keys = [key for key, entry in cache.cache.items() if entry.is_expired()]
                for key in expired_keys:
                    cache._remove_entry(key)
            
            print(f"✅ Cache optimization completed")
            
        except Exception as e:
            print(f"❌ Error optimizing caches: {e}")
    
    def save_cache_state(self, filepath: str):
        """Save cache state to file"""
        try:
            cache_state = {
                "response_cache": {k: v.to_dict() for k, v in self.response_cache.cache.items()},
                "vector_cache": {k: v.to_dict() for k, v in self.vector_cache.cache.items()},
                "embedding_cache": {k: v.to_dict() for k, v in self.embedding_cache.cache.items()},
                "timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(cache_state, f, indent=2)
            
            print(f"✅ Cache state saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error saving cache state: {e}")
    
    def load_cache_state(self, filepath: str):
        """Load cache state from file"""
        try:
            if not os.path.exists(filepath):
                print(f"⚠️  Cache state file not found: {filepath}")
                return
            
            with open(filepath, 'r') as f:
                cache_state = json.load(f)
            
            # Load response cache
            for key, entry_data in cache_state.get("response_cache", {}).items():
                entry = CacheEntry(
                    key=entry_data["key"],
                    value=entry_data["value"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    expires_at=datetime.fromisoformat(entry_data["expires_at"]),
                    access_count=entry_data["access_count"],
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    metadata=entry_data.get("metadata")
                )
                if not entry.is_expired():
                    self.response_cache.cache[key] = entry
                    self.response_cache.access_order.append(key)
            
            # Load vector cache
            for key, entry_data in cache_state.get("vector_cache", {}).items():
                entry = CacheEntry(
                    key=entry_data["key"],
                    value=entry_data["value"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    expires_at=datetime.fromisoformat(entry_data["expires_at"]),
                    access_count=entry_data["access_count"],
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    metadata=entry_data.get("metadata")
                )
                if not entry.is_expired():
                    self.vector_cache.cache[key] = entry
                    self.vector_cache.access_order.append(key)
            
            # Load embedding cache
            for key, entry_data in cache_state.get("embedding_cache", {}).items():
                entry = CacheEntry(
                    key=entry_data["key"],
                    value=entry_data["value"],
                    created_at=datetime.fromisoformat(entry_data["created_at"]),
                    expires_at=datetime.fromisoformat(entry_data["expires_at"]),
                    access_count=entry_data["access_count"],
                    last_accessed=datetime.fromisoformat(entry_data["last_accessed"]),
                    metadata=entry_data.get("metadata")
                )
                if not entry.is_expired():
                    self.embedding_cache.cache[key] = entry
                    self.embedding_cache.access_order.append(key)
            
            print(f"✅ Cache state loaded from {filepath}")
            
        except Exception as e:
            print(f"❌ Error loading cache state: {e}") 