"""
Integration Module for RAG Pipeline
System integration with existing workflow and data synchronization
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading
import queue

from .data_preparation import DataPreparation
from .vector_store import VectorStore
from .query_processor import QueryProcessor
from .retriever import Retriever
from .generator import ResponseGenerator
from .chat_interface import ChatInterface
from .web_interface import WebInterface
from .analytics import FitnessAnalytics
from .cache import CacheManager
from .optimization import RAGOptimizer


@dataclass
class SystemStatus:
    """Represents system status information"""
    component: str
    status: str  # 'healthy', 'warning', 'error', 'offline'
    last_check: datetime
    response_time_ms: float
    error_count: int
    metadata: Dict[str, Any] = None


@dataclass
class IntegrationConfig:
    """Configuration for system integration"""
    auto_sync_enabled: bool = True
    sync_interval_minutes: int = 30
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    enable_monitoring: bool = True
    enable_logging: bool = True
    cache_enabled: bool = True
    optimization_enabled: bool = True


class RAGAgent:
    """RAG Agent that integrates with the existing agent system"""
    
    def __init__(self, config: IntegrationConfig = None):
        """
        Initialize RAG Agent
        
        Args:
            config: Integration configuration
        """
        self.config = config or IntegrationConfig()
        self.agent_id = f"rag_agent_{int(time.time())}"
        
        # Initialize core components
        self._initialize_components()
        
        # System status tracking
        self.system_status: Dict[str, SystemStatus] = {}
        self.status_lock = threading.Lock()
        
        # Background tasks
        self.running = True
        self.sync_thread = None
        self.monitoring_thread = None
        
        # Start background processes
        self._start_background_processes()
    
    def _initialize_components(self):
        """Initialize all RAG components"""
        try:
            # Core components
            self.vector_store = VectorStore(collection_name="fitness_rag")
            self.query_processor = QueryProcessor()
            self.retriever = Retriever(self.vector_store, self.query_processor)
            self.generator = ResponseGenerator(
                vector_store=self.vector_store,
                query_processor=self.query_processor,
                retriever=self.retriever
            )
            
            # Advanced components (if enabled)
            if self.config.cache_enabled:
                self.cache_manager = CacheManager()
            else:
                self.cache_manager = None
            
            if self.config.optimization_enabled:
                self.optimizer = RAGOptimizer(self.vector_store, self.cache_manager)
            else:
                self.optimizer = None
            
            # Interface components
            self.chat_interface = ChatInterface(
                vector_store=self.vector_store,
                query_processor=self.query_processor,
                retriever=self.retriever,
                generator=self.generator
            )
            
            self.analytics = FitnessAnalytics(
                self.vector_store, 
                self.query_processor, 
                self.retriever
            )
            
            # Web interface (optional)
            self.web_interface = None
            
            print("✅ RAG components initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing RAG components: {e}")
            raise
    
    def _start_background_processes(self):
        """Start background processes"""
        try:
            # Start data synchronization
            if self.config.auto_sync_enabled:
                self.sync_thread = threading.Thread(target=self._sync_data_loop, daemon=True)
                self.sync_thread.start()
                print("✅ Data synchronization started")
            
            # Start system monitoring
            if self.config.enable_monitoring:
                self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
                self.monitoring_thread.start()
                print("✅ System monitoring started")
            
        except Exception as e:
            print(f"❌ Error starting background processes: {e}")
    
    def _sync_data_loop(self):
        """Background data synchronization loop"""
        while self.running:
            try:
                self.sync_fitness_data()
                time.sleep(self.config.sync_interval_minutes * 60)
            except Exception as e:
                print(f"❌ Error in data sync loop: {e}")
                time.sleep(self.config.retry_delay_seconds)
    
    def _monitoring_loop(self):
        """Background system monitoring loop"""
        while self.running:
            try:
                self._update_system_status()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)
    
    def sync_fitness_data(self) -> bool:
        """
        Synchronize fitness data from SQLite Cloud
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print("🔄 Starting fitness data synchronization...")
            
            # Initialize data preparation
            data_prep = DataPreparation()
            
            # Prepare vector data
            success = data_prep.prepare_vector_data()
            
            if success:
                print("✅ Fitness data synchronized successfully")
                self._update_component_status("data_sync", "healthy", 0)
                return True
            else:
                print("❌ Failed to synchronize fitness data")
                self._update_component_status("data_sync", "error", 0)
                return False
                
        except Exception as e:
            print(f"❌ Error synchronizing fitness data: {e}")
            self._update_component_status("data_sync", "error", 0)
            return False
    
    def _update_component_status(self, component: str, status: str, response_time_ms: float):
        """Update component status"""
        with self.status_lock:
            self.system_status[component] = SystemStatus(
                component=component,
                status=status,
                last_check=datetime.now(),
                response_time_ms=response_time_ms,
                error_count=self.system_status.get(component, SystemStatus(component, "unknown", datetime.now(), 0, 0)).error_count + (1 if status == "error" else 0)
            )
    
    def _update_system_status(self):
        """Update system status for all components"""
        try:
            # Check vector store
            start_time = time.time()
            try:
                info = self.vector_store.get_collection_info()
                response_time = (time.time() - start_time) * 1000
                self._update_component_status("vector_store", "healthy", response_time)
            except Exception as e:
                self._update_component_status("vector_store", "error", 0)
            
            # Check query processor
            start_time = time.time()
            try:
                # Test query processing
                test_query = "test query"
                self.query_processor.process_query(test_query)
                response_time = (time.time() - start_time) * 1000
                self._update_component_status("query_processor", "healthy", response_time)
            except Exception as e:
                self._update_component_status("query_processor", "error", 0)
            
            # Check retriever
            start_time = time.time()
            try:
                # Test retrieval
                self.retriever.retrieve("test", n_results=1)
                response_time = (time.time() - start_time) * 1000
                self._update_component_status("retriever", "healthy", response_time)
            except Exception as e:
                self._update_component_status("retriever", "error", 0)
            
            # Check generator
            start_time = time.time()
            try:
                # Test response generation
                self.generator.generate_response("test", [], "general")
                response_time = (time.time() - start_time) * 1000
                self._update_component_status("generator", "healthy", response_time)
            except Exception as e:
                self._update_component_status("generator", "error", 0)
            
            # Check cache manager
            if self.cache_manager:
                start_time = time.time()
                try:
                    stats = self.cache_manager.get_all_stats()
                    response_time = (time.time() - start_time) * 1000
                    self._update_component_status("cache_manager", "healthy", response_time)
                except Exception as e:
                    self._update_component_status("cache_manager", "error", 0)
            
            # Check optimizer
            if self.optimizer:
                start_time = time.time()
                try:
                    stats = self.optimizer.get_optimization_statistics()
                    response_time = (time.time() - start_time) * 1000
                    self._update_component_status("optimizer", "healthy", response_time)
                except Exception as e:
                    self._update_component_status("optimizer", "error", 0)
            
        except Exception as e:
            print(f"❌ Error updating system status: {e}")
    
    def process_query(self, query: str, user_id: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline
        
        Args:
            query: User query
            user_id: User identifier
            context: Additional context
            
        Returns:
            Response dictionary
        """
        start_time = time.time()
        
        try:
            # Use optimized processing if available
            if self.optimizer:
                response = self.optimizer.optimize_query(query, [], "general")
            else:
                # Fallback to standard processing
                processed_query = self.query_processor.process_query(query)
                if "error" in processed_query:
                    return {"error": processed_query["error"]}
                
                context_results = self.retriever.retrieve(query, n_results=5)
                response = self.generator.generate_response(query, context_results, "general")
            
            # Add metadata
            response["agent_id"] = self.agent_id
            response["processing_time_ms"] = (time.time() - start_time) * 1000
            response["user_id"] = user_id
            response["timestamp"] = datetime.now().isoformat()
            
            return response
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "processing_time_ms": (time.time() - start_time) * 1000,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_analytics(self, user_id: str, period: str = "month") -> Dict[str, Any]:
        """
        Get analytics for a user
        
        Args:
            user_id: User identifier
            period: Analysis period
            
        Returns:
            Analytics data
        """
        try:
            report = self.analytics.generate_insight_report(user_id, period)
            
            if report:
                return {
                    "success": True,
                    "report": {
                        "user_id": report.user_id,
                        "generated_at": report.generated_at.isoformat(),
                        "period_analyzed": report.period_analyzed,
                        "key_metrics": report.key_metrics,
                        "trends_count": len(report.trends),
                        "recommendations": report.recommendations,
                        "risk_alerts": report.risk_alerts,
                        "achievements": report.achievements
                    }
                }
            else:
                return {"success": False, "error": "Failed to generate analytics report"}
                
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
            return {"success": False, "error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        try:
            with self.status_lock:
                status_data = {}
                for component, status in self.system_status.items():
                    status_data[component] = {
                        "status": status.status,
                        "last_check": status.last_check.isoformat(),
                        "response_time_ms": status.response_time_ms,
                        "error_count": status.error_count
                    }
                
                # Calculate overall system health
                healthy_components = sum(1 for s in self.system_status.values() if s.status == "healthy")
                total_components = len(self.system_status)
                overall_health = "healthy" if healthy_components == total_components else "warning" if healthy_components > total_components // 2 else "error"
                
                return {
                    "agent_id": self.agent_id,
                    "overall_health": overall_health,
                    "healthy_components": healthy_components,
                    "total_components": total_components,
                    "components": status_data,
                    "config": asdict(self.config),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error getting system status: {e}")
            return {"error": str(e)}
    
    def start_web_interface(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Start the web interface"""
        try:
            self.web_interface = WebInterface(
                vector_store=self.vector_store,
                chat_interface=self.chat_interface,
                host=host,
                port=port
            )
            
            print(f"🚀 Starting web interface on {host}:{port}")
            self.web_interface.run(debug=debug)
            
        except Exception as e:
            print(f"❌ Error starting web interface: {e}")
    
    def shutdown(self):
        """Shutdown the RAG agent"""
        try:
            self.running = False
            
            # Shutdown optimizer
            if self.optimizer:
                self.optimizer.shutdown()
            
            # Wait for background threads
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread.join(timeout=5)
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            print("✅ RAG agent shutdown completed")
            
        except Exception as e:
            print(f"❌ Error shutting down RAG agent: {e}")


class SystemIntegrator:
    """Integrates RAG pipeline with existing system"""
    
    def __init__(self, rag_agent: RAGAgent = None):
        """
        Initialize system integrator
        
        Args:
            rag_agent: RAG agent instance
        """
        self.rag_agent = rag_agent or RAGAgent()
        self.integration_hooks: Dict[str, Callable] = {}
        self.data_sources: Dict[str, Any] = {}
    
    def register_integration_hook(self, hook_name: str, hook_function: Callable):
        """
        Register an integration hook
        
        Args:
            hook_name: Name of the hook
            hook_function: Function to call
        """
        self.integration_hooks[hook_name] = hook_function
        print(f"✅ Registered integration hook: {hook_name}")
    
    def register_data_source(self, source_name: str, data_source: Any):
        """
        Register a data source
        
        Args:
            source_name: Name of the data source
            data_source: Data source object
        """
        self.data_sources[source_name] = data_source
        print(f"✅ Registered data source: {source_name}")
    
    def trigger_integration_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """
        Trigger an integration hook
        
        Args:
            hook_name: Name of the hook to trigger
            *args: Arguments to pass to the hook
            **kwargs: Keyword arguments to pass to the hook
            
        Returns:
            Hook result
        """
        try:
            if hook_name in self.integration_hooks:
                return self.integration_hooks[hook_name](*args, **kwargs)
            else:
                print(f"⚠️  Integration hook not found: {hook_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error triggering integration hook {hook_name}: {e}")
            return None
    
    def get_data_from_source(self, source_name: str, query: str = None) -> Any:
        """
        Get data from a registered source
        
        Args:
            source_name: Name of the data source
            query: Optional query for the data source
            
        Returns:
            Data from the source
        """
        try:
            if source_name in self.data_sources:
                source = self.data_sources[source_name]
                if hasattr(source, 'get_data'):
                    return source.get_data(query)
                else:
                    return source
            else:
                print(f"⚠️  Data source not found: {source_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting data from source {source_name}: {e}")
            return None
    
    def integrate_with_existing_workflow(self, workflow_config: Dict[str, Any]) -> bool:
        """
        Integrate with existing workflow
        
        Args:
            workflow_config: Workflow configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("🔄 Integrating with existing workflow...")
            
            # Trigger pre-integration hooks
            self.trigger_integration_hook("pre_integration", workflow_config)
            
            # Configure RAG agent based on workflow
            if "rag_config" in workflow_config:
                rag_config = workflow_config["rag_config"]
                
                # Update agent configuration
                if "auto_sync_enabled" in rag_config:
                    self.rag_agent.config.auto_sync_enabled = rag_config["auto_sync_enabled"]
                
                if "sync_interval_minutes" in rag_config:
                    self.rag_agent.config.sync_interval_minutes = rag_config["sync_interval_minutes"]
            
            # Register workflow-specific data sources
            if "data_sources" in workflow_config:
                for source_name, source_config in workflow_config["data_sources"].items():
                    # This would create appropriate data source objects
                    print(f"   Registering data source: {source_name}")
            
            # Trigger post-integration hooks
            self.trigger_integration_hook("post_integration", workflow_config)
            
            print("✅ Workflow integration completed")
            return True
            
        except Exception as e:
            print(f"❌ Error integrating with workflow: {e}")
            return False
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        try:
            return {
                "rag_agent_status": self.rag_agent.get_system_status(),
                "registered_hooks": list(self.integration_hooks.keys()),
                "registered_sources": list(self.data_sources.keys()),
                "integration_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error getting integration status: {e}")
            return {"error": str(e)}


class DataSynchronizer:
    """Handles data synchronization between systems"""
    
    def __init__(self, rag_agent: RAGAgent):
        """
        Initialize data synchronizer
        
        Args:
            rag_agent: RAG agent instance
        """
        self.rag_agent = rag_agent
        self.sync_history: List[Dict[str, Any]] = []
        self.sync_lock = threading.Lock()
    
    def sync_all_data(self) -> Dict[str, Any]:
        """
        Synchronize all data sources
        
        Returns:
            Synchronization results
        """
        try:
            print("🔄 Starting full data synchronization...")
            
            sync_start = datetime.now()
            results = {}
            
            # Sync fitness data
            fitness_sync = self.rag_agent.sync_fitness_data()
            results["fitness_data"] = {
                "success": fitness_sync,
                "timestamp": datetime.now().isoformat()
            }
            
            # Sync analytics data
            analytics_sync = self._sync_analytics_data()
            results["analytics_data"] = {
                "success": analytics_sync,
                "timestamp": datetime.now().isoformat()
            }
            
            # Sync cache data
            if self.rag_agent.cache_manager:
                cache_sync = self._sync_cache_data()
                results["cache_data"] = {
                    "success": cache_sync,
                    "timestamp": datetime.now().isoformat()
                }
            
            sync_end = datetime.now()
            sync_duration = (sync_end - sync_start).total_seconds()
            
            # Record sync history
            sync_record = {
                "start_time": sync_start.isoformat(),
                "end_time": sync_end.isoformat(),
                "duration_seconds": sync_duration,
                "results": results,
                "success": all(r["success"] for r in results.values())
            }
            
            with self.sync_lock:
                self.sync_history.append(sync_record)
                # Keep only last 100 records
                if len(self.sync_history) > 100:
                    self.sync_history = self.sync_history[-100:]
            
            print(f"✅ Data synchronization completed in {sync_duration:.2f} seconds")
            return results
            
        except Exception as e:
            print(f"❌ Error in data synchronization: {e}")
            return {"error": str(e)}
    
    def _sync_analytics_data(self) -> bool:
        """Synchronize analytics data"""
        try:
            # This would sync analytics data with external systems
            # For now, just return success
            return True
        except Exception as e:
            print(f"❌ Error syncing analytics data: {e}")
            return False
    
    def _sync_cache_data(self) -> bool:
        """Synchronize cache data"""
        try:
            if self.rag_agent.cache_manager:
                # Optimize caches
                self.rag_agent.cache_manager.optimize_caches()
                return True
            return False
        except Exception as e:
            print(f"❌ Error syncing cache data: {e}")
            return False
    
    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get synchronization history
        
        Args:
            limit: Number of records to return
            
        Returns:
            List of sync records
        """
        with self.sync_lock:
            return self.sync_history[-limit:] if self.sync_history else []
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        try:
            with self.sync_lock:
                if not self.sync_history:
                    return {"error": "No sync history available"}
                
                total_syncs = len(self.sync_history)
                successful_syncs = sum(1 for record in self.sync_history if record["success"])
                avg_duration = sum(record["duration_seconds"] for record in self.sync_history) / total_syncs
                
                return {
                    "total_syncs": total_syncs,
                    "successful_syncs": successful_syncs,
                    "success_rate": round((successful_syncs / total_syncs) * 100, 2),
                    "average_duration_seconds": round(avg_duration, 2),
                    "last_sync": self.sync_history[-1] if self.sync_history else None
                }
                
        except Exception as e:
            print(f"❌ Error getting sync statistics: {e}")
            return {"error": str(e)} 