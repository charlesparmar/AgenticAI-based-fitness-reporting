"""
Integration Tests for RAG Pipeline
Tests system integration and end-to-end functionality
"""

import unittest
import os
import sys
import time
import json
from unittest.mock import Mock, patch
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.integration import RAGAgent, SystemIntegrator, DataSynchronizer, IntegrationConfig
from rag.config import RAGPipelineConfig, get_config


class TestRAGAgent(unittest.TestCase):
    """Test RAG Agent functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = IntegrationConfig(
            auto_sync_enabled=False,
            enable_monitoring=False,
            cache_enabled=True,
            optimization_enabled=True
        )
        self.agent = RAGAgent(self.config)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.agent:
            self.agent.shutdown()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent.agent_id)
        self.assertIsNotNone(self.agent.vector_store)
        self.assertIsNotNone(self.agent.query_processor)
        self.assertIsNotNone(self.agent.retriever)
        self.assertIsNotNone(self.agent.generator)
        self.assertIsNotNone(self.agent.chat_interface)
        self.assertIsNotNone(self.agent.analytics)
    
    def test_query_processing(self):
        """Test query processing"""
        query = "How has my weight changed?"
        response = self.agent.process_query(query, "test_user")
        
        self.assertIsInstance(response, dict)
        self.assertIn("agent_id", response)
        self.assertIn("processing_time_ms", response)
        self.assertIn("user_id", response)
        self.assertIn("timestamp", response)
    
    def test_analytics_generation(self):
        """Test analytics generation"""
        analytics = self.agent.get_analytics("test_user", "month")
        
        self.assertIsInstance(analytics, dict)
        self.assertIn("success", analytics)
    
    def test_system_status(self):
        """Test system status monitoring"""
        status = self.agent.get_system_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("agent_id", status)
        self.assertIn("overall_health", status)
        self.assertIn("components", status)
        self.assertIn("config", status)
    
    def test_data_synchronization(self):
        """Test data synchronization"""
        # Mock data preparation to avoid actual database calls
        with patch('rag.integration.DataPreparation') as mock_data_prep:
            mock_instance = Mock()
            mock_instance.prepare_vector_data.return_value = True
            mock_data_prep.return_value = mock_instance
            
            success = self.agent.sync_fitness_data()
            self.assertTrue(success)


class TestSystemIntegrator(unittest.TestCase):
    """Test system integrator functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = IntegrationConfig(
            auto_sync_enabled=False,
            enable_monitoring=False
        )
        self.rag_agent = RAGAgent(self.config)
        self.integrator = SystemIntegrator(self.rag_agent)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.rag_agent:
            self.rag_agent.shutdown()
    
    def test_integration_hook_registration(self):
        """Test integration hook registration"""
        def test_hook():
            return "test_result"
        
        self.integrator.register_integration_hook("test_hook", test_hook)
        
        self.assertIn("test_hook", self.integrator.integration_hooks)
        self.assertEqual(self.integrator.integration_hooks["test_hook"], test_hook)
    
    def test_integration_hook_triggering(self):
        """Test integration hook triggering"""
        def test_hook(param):
            return f"result_{param}"
        
        self.integrator.register_integration_hook("test_hook", test_hook)
        
        result = self.integrator.trigger_integration_hook("test_hook", "test_param")
        self.assertEqual(result, "result_test_param")
    
    def test_data_source_registration(self):
        """Test data source registration"""
        test_source = {"data": "test"}
        self.integrator.register_data_source("test_source", test_source)
        
        self.assertIn("test_source", self.integrator.data_sources)
        self.assertEqual(self.integrator.data_sources["test_source"], test_source)
    
    def test_data_source_retrieval(self):
        """Test data source retrieval"""
        test_source = {"data": "test"}
        self.integrator.register_data_source("test_source", test_source)
        
        data = self.integrator.get_data_from_source("test_source")
        self.assertEqual(data, test_source)
    
    def test_workflow_integration(self):
        """Test workflow integration"""
        workflow_config = {
            "rag_config": {
                "auto_sync_enabled": False,
                "sync_interval_minutes": 60
            },
            "data_sources": {
                "fitness_data": {"type": "database"}
            }
        }
        
        success = self.integrator.integrate_with_existing_workflow(workflow_config)
        self.assertTrue(success)
    
    def test_integration_status(self):
        """Test integration status"""
        status = self.integrator.get_integration_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("rag_agent_status", status)
        self.assertIn("registered_hooks", status)
        self.assertIn("registered_sources", status)
        self.assertIn("integration_timestamp", status)


class TestDataSynchronizer(unittest.TestCase):
    """Test data synchronizer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = IntegrationConfig(
            auto_sync_enabled=False,
            enable_monitoring=False
        )
        self.rag_agent = RAGAgent(self.config)
        self.synchronizer = DataSynchronizer(self.rag_agent)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.rag_agent:
            self.rag_agent.shutdown()
    
    def test_data_synchronization(self):
        """Test data synchronization"""
        # Mock the sync methods to avoid actual operations
        with patch.object(self.rag_agent, 'sync_fitness_data', return_value=True):
            with patch.object(self.synchronizer, '_sync_analytics_data', return_value=True):
                with patch.object(self.synchronizer, '_sync_cache_data', return_value=True):
                    results = self.synchronizer.sync_all_data()
                    
                    self.assertIsInstance(results, dict)
                    self.assertIn("fitness_data", results)
                    self.assertIn("analytics_data", results)
                    self.assertIn("cache_data", results)
    
    def test_sync_history(self):
        """Test sync history tracking"""
        # Perform a sync operation
        with patch.object(self.rag_agent, 'sync_fitness_data', return_value=True):
            with patch.object(self.synchronizer, '_sync_analytics_data', return_value=True):
                with patch.object(self.synchronizer, '_sync_cache_data', return_value=True):
                    self.synchronizer.sync_all_data()
        
        history = self.synchronizer.get_sync_history()
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        # Check history structure
        if history:
            record = history[0]
            self.assertIn("start_time", record)
            self.assertIn("end_time", record)
            self.assertIn("duration_seconds", record)
            self.assertIn("results", record)
            self.assertIn("success", record)
    
    def test_sync_statistics(self):
        """Test sync statistics"""
        # Perform multiple sync operations
        for _ in range(3):
            with patch.object(self.rag_agent, 'sync_fitness_data', return_value=True):
                with patch.object(self.synchronizer, '_sync_analytics_data', return_value=True):
                    with patch.object(self.synchronizer, '_sync_cache_data', return_value=True):
                        self.synchronizer.sync_all_data()
        
        stats = self.synchronizer.get_sync_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_syncs", stats)
        self.assertIn("successful_syncs", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("average_duration_seconds", stats)
        self.assertIn("last_sync", stats)
        
        self.assertGreater(stats["total_syncs"], 0)
        self.assertGreaterEqual(stats["success_rate"], 0)
        self.assertLessEqual(stats["success_rate"], 100)


class TestConfigurationIntegration(unittest.TestCase):
    """Test configuration integration"""
    
    def test_config_loading(self):
        """Test configuration loading"""
        config = get_config()
        
        self.assertIsInstance(config, RAGPipelineConfig)
        self.assertIsNotNone(config.database)
        self.assertIsNotNone(config.vector_store)
        self.assertIsNotNone(config.llm)
        self.assertIsNotNone(config.cache)
        self.assertIsNotNone(config.optimization)
        self.assertIsNotNone(config.web_interface)
        self.assertIsNotNone(config.monitoring)
        self.assertIsNotNone(config.security)
    
    def test_environment_configs(self):
        """Test environment-specific configurations"""
        from rag.config import ConfigManager
        
        config_manager = ConfigManager()
        
        # Test development config
        dev_config = config_manager.get_environment_config("development")
        self.assertTrue(dev_config.debug)
        self.assertEqual(dev_config.monitoring.log_level, "DEBUG")
        self.assertFalse(dev_config.cache.enabled)
        self.assertFalse(dev_config.optimization.enabled)
        
        # Test production config
        prod_config = config_manager.get_environment_config("production")
        self.assertFalse(prod_config.debug)
        self.assertEqual(prod_config.monitoring.log_level, "WARNING")
        self.assertTrue(prod_config.security.authentication_enabled)
        self.assertTrue(prod_config.cache.enabled)
        self.assertTrue(prod_config.optimization.enabled)


class TestEndToEndIntegration(unittest.TestCase):
    """Test end-to-end integration scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = IntegrationConfig(
            auto_sync_enabled=False,
            enable_monitoring=False,
            cache_enabled=True,
            optimization_enabled=True
        )
        self.agent = RAGAgent(self.config)
        self.integrator = SystemIntegrator(self.agent)
        self.synchronizer = DataSynchronizer(self.agent)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.agent:
            self.agent.shutdown()
    
    def test_complete_workflow(self):
        """Test complete workflow integration"""
        # 1. Register integration hooks
        def pre_integration_hook(config):
            return {"status": "pre_integration_complete"}
        
        def post_integration_hook(config):
            return {"status": "post_integration_complete"}
        
        self.integrator.register_integration_hook("pre_integration", pre_integration_hook)
        self.integrator.register_integration_hook("post_integration", post_integration_hook)
        
        # 2. Register data sources
        test_data_source = {"fitness_data": [{"weight": 80, "date": "2024-01-01"}]}
        self.integrator.register_data_source("fitness_db", test_data_source)
        
        # 3. Integrate with workflow
        workflow_config = {
            "rag_config": {
                "auto_sync_enabled": True,
                "sync_interval_minutes": 30
            },
            "data_sources": {
                "fitness_db": {"type": "database"}
            }
        }
        
        integration_success = self.integrator.integrate_with_existing_workflow(workflow_config)
        self.assertTrue(integration_success)
        
        # 4. Synchronize data
        with patch.object(self.agent, 'sync_fitness_data', return_value=True):
            with patch.object(self.synchronizer, '_sync_analytics_data', return_value=True):
                with patch.object(self.synchronizer, '_sync_cache_data', return_value=True):
                    sync_results = self.synchronizer.sync_all_data()
                    self.assertIsInstance(sync_results, dict)
        
        # 5. Process queries
        test_queries = [
            "How has my weight changed?",
            "What are my current measurements?",
            "Give me a summary of my progress"
        ]
        
        for query in test_queries:
            response = self.agent.process_query(query, "test_user")
            self.assertIsInstance(response, dict)
            self.assertIn("agent_id", response)
            self.assertIn("processing_time_ms", response)
        
        # 6. Generate analytics
        analytics = self.agent.get_analytics("test_user", "month")
        self.assertIsInstance(analytics, dict)
        
        # 7. Check system status
        status = self.agent.get_system_status()
        self.assertIsInstance(status, dict)
        self.assertIn("overall_health", status)
        
        # 8. Check integration status
        integration_status = self.integrator.get_integration_status()
        self.assertIsInstance(integration_status, dict)
        self.assertIn("rag_agent_status", integration_status)
    
    def test_error_handling(self):
        """Test error handling in integration"""
        # Test with invalid configuration
        invalid_config = IntegrationConfig(
            auto_sync_enabled=True,
            sync_interval_minutes=-1  # Invalid value
        )
        
        # Should handle gracefully
        try:
            agent = RAGAgent(invalid_config)
            agent.shutdown()
        except Exception as e:
            self.fail(f"Agent should handle invalid config gracefully: {e}")
        
        # Test with missing data sources
        data = self.integrator.get_data_from_source("nonexistent_source")
        self.assertIsNone(data)
        
        # Test with invalid integration hooks
        result = self.integrator.trigger_integration_hook("nonexistent_hook")
        self.assertIsNone(result)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestRAGAgent))
    test_suite.addTest(unittest.makeSuite(TestSystemIntegrator))
    test_suite.addTest(unittest.makeSuite(TestDataSynchronizer))
    test_suite.addTest(unittest.makeSuite(TestConfigurationIntegration))
    test_suite.addTest(unittest.makeSuite(TestEndToEndIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Integration Tests Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}") 