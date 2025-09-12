"""
Optimization Module for RAG Pipeline
Performance optimization, batch processing, and load balancing
"""

import time
import threading
import queue
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from .vector_store import VectorStore
from .cache import CacheManager


@dataclass
class PerformanceMetrics:
    """Represents performance metrics"""
    operation: str
    duration_ms: float
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] = None


@dataclass
class BatchJob:
    """Represents a batch processing job"""
    id: str
    items: List[Any]
    processor: Callable
    max_workers: int
    created_at: datetime
    status: str  # 'pending', 'processing', 'completed', 'failed'
    results: List[Any] = None
    errors: List[str] = None


class PerformanceMonitor:
    """Monitors and tracks performance metrics"""
    
    def __init__(self, max_metrics: int = 10000):
        """
        Initialize performance monitor
        
        Args:
            max_metrics: Maximum number of metrics to store
        """
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetrics] = []
        self.lock = threading.Lock()
    
    def record_metric(self, operation: str, duration_ms: float, success: bool, 
                     metadata: Dict[str, Any] = None):
        """
        Record a performance metric
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            success: Whether operation was successful
            metadata: Additional metadata
        """
        try:
            metric = PerformanceMetrics(
                operation=operation,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                success=success,
                metadata=metadata or {}
            )
            
            with self.lock:
                self.metrics.append(metric)
                
                # Remove old metrics if exceeding max
                if len(self.metrics) > self.max_metrics:
                    self.metrics = self.metrics[-self.max_metrics:]
                    
        except Exception as e:
            print(f"❌ Error recording metric: {e}")
    
    def get_metrics(self, operation: str = None, time_window: timedelta = None) -> List[PerformanceMetrics]:
        """
        Get performance metrics
        
        Args:
            operation: Filter by operation name
            time_window: Filter by time window
            
        Returns:
            List of performance metrics
        """
        try:
            with self.lock:
                metrics = self.metrics.copy()
            
            # Filter by operation
            if operation:
                metrics = [m for m in metrics if m.operation == operation]
            
            # Filter by time window
            if time_window:
                cutoff_time = datetime.now() - time_window
                metrics = [m for m in metrics if m.timestamp > cutoff_time]
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error getting metrics: {e}")
            return []
    
    def get_statistics(self, operation: str = None, time_window: timedelta = None) -> Dict[str, Any]:
        """
        Get performance statistics
        
        Args:
            operation: Filter by operation name
            time_window: Filter by time window
            
        Returns:
            Performance statistics
        """
        try:
            metrics = self.get_metrics(operation, time_window)
            
            if not metrics:
                return {"error": "No metrics available"}
            
            durations = [m.duration_ms for m in metrics]
            success_count = sum(1 for m in metrics if m.success)
            
            stats = {
                "total_operations": len(metrics),
                "successful_operations": success_count,
                "success_rate": round((success_count / len(metrics)) * 100, 2),
                "average_duration_ms": round(np.mean(durations), 2),
                "median_duration_ms": round(np.median(durations), 2),
                "min_duration_ms": round(min(durations), 2),
                "max_duration_ms": round(max(durations), 2),
                "std_duration_ms": round(np.std(durations), 2),
                "p95_duration_ms": round(np.percentile(durations, 95), 2),
                "p99_duration_ms": round(np.percentile(durations, 99), 2)
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {"error": str(e)}
    
    def clear_metrics(self):
        """Clear all metrics"""
        with self.lock:
            self.metrics.clear()


class BatchProcessor:
    """Handles batch processing of operations"""
    
    def __init__(self, max_workers: int = 4, max_queue_size: int = 100):
        """
        Initialize batch processor
        
        Args:
            max_workers: Maximum number of worker threads
            max_queue_size: Maximum queue size
        """
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.job_queue = queue.Queue(maxsize=max_queue_size)
        self.active_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: Dict[str, BatchJob] = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = True
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def submit_batch(self, items: List[Any], processor: Callable, 
                    max_workers: int = None) -> str:
        """
        Submit a batch job
        
        Args:
            items: Items to process
            processor: Processing function
            max_workers: Maximum workers for this job
            
        Returns:
            Job ID
        """
        try:
            job_id = f"batch_{int(time.time() * 1000)}"
            max_workers = max_workers or self.max_workers
            
            job = BatchJob(
                id=job_id,
                items=items,
                processor=processor,
                max_workers=max_workers,
                created_at=datetime.now(),
                status='pending',
                results=[],
                errors=[]
            )
            
            with self.lock:
                self.active_jobs[job_id] = job
            
            # Add to queue
            self.job_queue.put(job)
            
            return job_id
            
        except Exception as e:
            print(f"❌ Error submitting batch job: {e}")
            return None
    
    def _worker_loop(self):
        """Main worker loop"""
        while self.running:
            try:
                # Get job from queue
                job = self.job_queue.get(timeout=1)
                
                # Process job
                self._process_job(job)
                
                # Mark as done
                self.job_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error in worker loop: {e}")
    
    def _process_job(self, job: BatchJob):
        """Process a batch job"""
        try:
            job.status = 'processing'
            
            # Split items into chunks
            chunk_size = max(1, len(job.items) // job.max_workers)
            chunks = [job.items[i:i + chunk_size] for i in range(0, len(job.items), chunk_size)]
            
            # Process chunks in parallel
            futures = []
            for chunk in chunks:
                future = self.executor.submit(self._process_chunk, job.processor, chunk)
                futures.append(future)
            
            # Collect results
            results = []
            errors = []
            
            for future in as_completed(futures):
                try:
                    chunk_results = future.result()
                    results.extend(chunk_results)
                except Exception as e:
                    errors.append(str(e))
            
            # Update job
            job.results = results
            job.errors = errors
            job.status = 'completed' if not errors else 'failed'
            
            # Move to completed jobs
            with self.lock:
                if job.id in self.active_jobs:
                    del self.active_jobs[job.id]
                self.completed_jobs[job.id] = job
            
        except Exception as e:
            job.status = 'failed'
            job.errors = [str(e)]
            print(f"❌ Error processing batch job: {e}")
    
    def _process_chunk(self, processor: Callable, items: List[Any]) -> List[Any]:
        """Process a chunk of items"""
        results = []
        for item in items:
            try:
                result = processor(item)
                results.append(result)
            except Exception as e:
                print(f"❌ Error processing item: {e}")
                results.append(None)
        return results
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status information
        """
        try:
            with self.lock:
                # Check active jobs
                if job_id in self.active_jobs:
                    job = self.active_jobs[job_id]
                elif job_id in self.completed_jobs:
                    job = self.completed_jobs[job_id]
                else:
                    return None
            
            return {
                "id": job.id,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "total_items": len(job.items),
                "completed_items": len(job.results) if job.results else 0,
                "error_count": len(job.errors) if job.errors else 0,
                "errors": job.errors[:5] if job.errors else []  # Show first 5 errors
            }
            
        except Exception as e:
            print(f"❌ Error getting job status: {e}")
            return None
    
    def get_job_results(self, job_id: str) -> Optional[List[Any]]:
        """
        Get job results
        
        Args:
            job_id: Job ID
            
        Returns:
            Job results
        """
        try:
            with self.lock:
                if job_id in self.completed_jobs:
                    return self.completed_jobs[job_id].results
                return None
                
        except Exception as e:
            print(f"❌ Error getting job results: {e}")
            return None
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Clean up old completed jobs
        
        Args:
            max_age_hours: Maximum age in hours
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            with self.lock:
                old_jobs = [
                    job_id for job_id, job in self.completed_jobs.items()
                    if job.created_at < cutoff_time
                ]
                
                for job_id in old_jobs:
                    del self.completed_jobs[job_id]
            
            if old_jobs:
                print(f"✅ Cleaned up {len(old_jobs)} old jobs")
                
        except Exception as e:
            print(f"❌ Error cleaning up old jobs: {e}")
    
    def shutdown(self):
        """Shutdown the batch processor"""
        self.running = False
        self.executor.shutdown(wait=True)


class VectorSearchOptimizer:
    """Optimizes vector search performance"""
    
    def __init__(self, vector_store: VectorStore, cache_manager: CacheManager = None):
        """
        Initialize vector search optimizer
        
        Args:
            vector_store: Vector store instance
            cache_manager: Cache manager instance
        """
        self.vector_store = vector_store
        self.cache_manager = cache_manager
        self.performance_monitor = PerformanceMonitor()
        
        # Optimization settings
        self.batch_size = 10
        self.similarity_threshold = 0.7
        self.max_results = 20
    
    def optimize_search(self, query: str, n_results: int = 5, 
                       filters: Dict = None) -> List[Dict]:
        """
        Optimized vector search
        
        Args:
            query: Search query
            n_results: Number of results
            filters: Search filters
            
        Returns:
            Search results
        """
        start_time = time.time()
        
        try:
            # Check cache first
            if self.cache_manager:
                cached_results = self.cache_manager.get_vector_results(query, n_results, filters)
                if cached_results:
                    duration = (time.time() - start_time) * 1000
                    self.performance_monitor.record_metric(
                        "vector_search_cache_hit", duration, True,
                        {"query": query, "results_count": len(cached_results)}
                    )
                    return cached_results
            
            # Perform search
            results = self.vector_store.search(query, n_results=n_results)
            
            # Apply filters if provided
            if filters:
                results = self._apply_filters(results, filters)
            
            # Cache results
            if self.cache_manager:
                self.cache_manager.set_vector_results(query, n_results, filters, results)
            
            # Record metrics
            duration = (time.time() - start_time) * 1000
            self.performance_monitor.record_metric(
                "vector_search", duration, True,
                {"query": query, "results_count": len(results)}
            )
            
            return results
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.performance_monitor.record_metric(
                "vector_search", duration, False,
                {"query": query, "error": str(e)}
            )
            print(f"❌ Error in optimized search: {e}")
            return []
    
    def _apply_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to search results"""
        try:
            filtered_results = []
            
            for result in results:
                metadata = result.get('metadata', {})
                matches = True
                
                for key, value in filters.items():
                    if key in metadata:
                        if isinstance(value, (list, tuple)):
                            if metadata[key] not in value:
                                matches = False
                                break
                        else:
                            if metadata[key] != value:
                                matches = False
                                break
                    else:
                        matches = False
                        break
                
                if matches:
                    filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            print(f"❌ Error applying filters: {e}")
            return results
    
    def batch_search(self, queries: List[str], n_results: int = 5) -> List[List[Dict]]:
        """
        Perform batch search
        
        Args:
            queries: List of queries
            n_results: Number of results per query
            
        Returns:
            List of search results for each query
        """
        start_time = time.time()
        
        try:
            # Process in batches
            all_results = []
            
            for i in range(0, len(queries), self.batch_size):
                batch_queries = queries[i:i + self.batch_size]
                batch_results = []
                
                for query in batch_queries:
                    results = self.optimize_search(query, n_results)
                    batch_results.append(results)
                
                all_results.extend(batch_results)
            
            # Record metrics
            duration = (time.time() - start_time) * 1000
            self.performance_monitor.record_metric(
                "batch_vector_search", duration, True,
                {"queries_count": len(queries), "batch_size": self.batch_size}
            )
            
            return all_results
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.performance_monitor.record_metric(
                "batch_vector_search", duration, False,
                {"queries_count": len(queries), "error": str(e)}
            )
            print(f"❌ Error in batch search: {e}")
            return []
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search performance statistics"""
        return self.performance_monitor.get_statistics("vector_search")


class LoadBalancer:
    """Simple load balancer for RAG operations"""
    
    def __init__(self, max_concurrent_requests: int = 10):
        """
        Initialize load balancer
        
        Args:
            max_concurrent_requests: Maximum concurrent requests
        """
        self.max_concurrent_requests = max_concurrent_requests
        self.active_requests = 0
        self.request_queue = queue.Queue()
        self.lock = threading.Lock()
        self.performance_monitor = PerformanceMonitor()
    
    def submit_request(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Submit a request through load balancer
        
        Args:
            operation: Operation to execute
            *args: Operation arguments
            **kwargs: Operation keyword arguments
            
        Returns:
            Operation result
        """
        start_time = time.time()
        
        try:
            # Check if we can process immediately
            with self.lock:
                if self.active_requests < self.max_concurrent_requests:
                    self.active_requests += 1
                    immediate = True
                else:
                    immediate = False
            
            if immediate:
                try:
                    result = operation(*args, **kwargs)
                    
                    # Record metrics
                    duration = (time.time() - start_time) * 1000
                    self.performance_monitor.record_metric(
                        "load_balanced_operation", duration, True,
                        {"operation": operation.__name__, "immediate": True}
                    )
                    
                    return result
                    
                finally:
                    with self.lock:
                        self.active_requests -= 1
            else:
                # Queue the request
                future = queue.Queue()
                self.request_queue.put((operation, args, kwargs, future))
                
                # Wait for result
                result = future.get()
                
                # Record metrics
                duration = (time.time() - start_time) * 1000
                self.performance_monitor.record_metric(
                    "load_balanced_operation", duration, True,
                    {"operation": operation.__name__, "immediate": False}
                )
                
                return result
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.performance_monitor.record_metric(
                "load_balanced_operation", duration, False,
                {"operation": operation.__name__, "error": str(e)}
            )
            print(f"❌ Error in load balanced operation: {e}")
            raise
    
    def _process_queued_requests(self):
        """Process queued requests"""
        while True:
            try:
                operation, args, kwargs, future = self.request_queue.get(timeout=1)
                
                with self.lock:
                    self.active_requests += 1
                
                try:
                    result = operation(*args, **kwargs)
                    future.put(result)
                except Exception as e:
                    future.put(e)
                finally:
                    with self.lock:
                        self.active_requests -= 1
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error processing queued request: {e}")
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        try:
            with self.lock:
                active = self.active_requests
                queued = self.request_queue.qsize()
            
            return {
                "active_requests": active,
                "queued_requests": queued,
                "max_concurrent_requests": self.max_concurrent_requests,
                "utilization_percentage": round((active / self.max_concurrent_requests) * 100, 2)
            }
        except Exception as e:
            print(f"❌ Error getting load statistics: {e}")
            return {"error": str(e)}


class RAGOptimizer:
    """Main optimizer for the RAG pipeline"""
    
    def __init__(self, vector_store: VectorStore, cache_manager: CacheManager = None):
        """
        Initialize RAG optimizer
        
        Args:
            vector_store: Vector store instance
            cache_manager: Cache manager instance
        """
        self.vector_store = vector_store
        self.cache_manager = cache_manager
        
        # Initialize components
        self.performance_monitor = PerformanceMonitor()
        self.batch_processor = BatchProcessor()
        self.vector_optimizer = VectorSearchOptimizer(vector_store, cache_manager)
        self.load_balancer = LoadBalancer()
        
        # Start background processes
        self._start_background_processes()
    
    def _start_background_processes(self):
        """Start background optimization processes"""
        # Start load balancer worker
        self.load_balancer_worker = threading.Thread(
            target=self.load_balancer._process_queued_requests, daemon=True
        )
        self.load_balancer_worker.start()
        
        # Start periodic cleanup
        self.cleanup_thread = threading.Thread(
            target=self._periodic_cleanup, daemon=True
        )
        self.cleanup_thread.start()
    
    def _periodic_cleanup(self):
        """Periodic cleanup tasks"""
        while True:
            try:
                time.sleep(3600)  # Run every hour
                
                # Clean up old batch jobs
                self.batch_processor.cleanup_old_jobs()
                
                # Optimize caches
                if self.cache_manager:
                    self.cache_manager.optimize_caches()
                
                print("✅ Periodic cleanup completed")
                
            except Exception as e:
                print(f"❌ Error in periodic cleanup: {e}")
    
    def optimize_query(self, query: str, context: List[Dict], 
                      query_type: str) -> Dict[str, Any]:
        """
        Optimized query processing
        
        Args:
            query: User query
            context: Retrieved context
            query_type: Query type
            
        Returns:
            Optimized response
        """
        start_time = time.time()
        
        try:
            # Check cache first
            if self.cache_manager:
                cached_response = self.cache_manager.get_response(query, context, query_type)
                if cached_response:
                    duration = (time.time() - start_time) * 1000
                    self.performance_monitor.record_metric(
                        "query_cache_hit", duration, True,
                        {"query": query, "query_type": query_type}
                    )
                    return cached_response
            
            # Process through load balancer
            def process_query():
                # This would integrate with the actual query processor and generator
                # For now, return a placeholder response
                return {
                    "response": f"Optimized response for: {query}",
                    "query_type": query_type,
                    "context_used": len(context),
                    "optimized": True
                }
            
            result = self.load_balancer.submit_request(process_query)
            
            # Cache result
            if self.cache_manager:
                self.cache_manager.set_response(query, context, query_type, result)
            
            # Record metrics
            duration = (time.time() - start_time) * 1000
            self.performance_monitor.record_metric(
                "optimized_query", duration, True,
                {"query": query, "query_type": query_type}
            )
            
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.performance_monitor.record_metric(
                "optimized_query", duration, False,
                {"query": query, "error": str(e)}
            )
            print(f"❌ Error in optimized query: {e}")
            return {"error": str(e)}
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        try:
            return {
                "performance": self.performance_monitor.get_statistics(),
                "load_balancer": self.load_balancer.get_load_statistics(),
                "vector_search": self.vector_optimizer.get_search_statistics(),
                "cache": self.cache_manager.get_all_stats() if self.cache_manager else {},
                "batch_processor": {
                    "active_jobs": len(self.batch_processor.active_jobs),
                    "completed_jobs": len(self.batch_processor.completed_jobs)
                }
            }
        except Exception as e:
            print(f"❌ Error getting optimization statistics: {e}")
            return {"error": str(e)}
    
    def shutdown(self):
        """Shutdown the optimizer"""
        try:
            self.batch_processor.shutdown()
            print("✅ RAG optimizer shutdown completed")
        except Exception as e:
            print(f"❌ Error shutting down optimizer: {e}") 