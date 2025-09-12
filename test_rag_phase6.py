#!/usr/bin/env python3
"""
Test Script for RAG Pipeline Phase 6
Tests integration, configuration, and deployment functionality
"""

import os
import sys
import time
import json
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.integration import RAGAgent, SystemIntegrator, DataSynchronizer, IntegrationConfig
from rag.config import RAGPipelineConfig, ConfigManager, get_config, create_deployment_config


def test_rag_agent():
    """Test RAG Agent functionality"""
    print("🧪 Testing RAG Agent...")
    print("=" * 50)
    
    # Initialize agent with minimal configuration
    config = IntegrationConfig(
        auto_sync_enabled=False,
        enable_monitoring=False,
        cache_enabled=True,
        optimization_enabled=True
    )
    
    agent = RAGAgent(config)
    
    try:
        # Test agent initialization
        print("\n1. Testing agent initialization...")
        
        self.assertIsNotNone(agent.agent_id)
        self.assertIsNotNone(agent.vector_store)
        self.assertIsNotNone(agent.query_processor)
        self.assertIsNotNone(agent.retriever)
        self.assertIsNotNone(agent.generator)
        self.assertIsNotNone(agent.chat_interface)
        self.assertIsNotNone(agent.analytics)
        
        print("   ✅ Agent components initialized successfully")
        
        # Test query processing
        print("\n2. Testing query processing...")
        
        test_queries = [
            "How has my weight changed?",
            "What are my current measurements?",
            "Give me a summary of my progress"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"   Query {i}: '{query}'")
            
            response = agent.process_query(query, f"test_user_{i}")
            
            if "error" not in response:
                print(f"      ✅ Response: {response.get('response', '')[:50]}...")
                print(f"      📊 Processing time: {response.get('processing_time_ms', 0):.2f}ms")
                print(f"      🆔 Agent ID: {response.get('agent_id', '')}")
            else:
                print(f"      ❌ Error: {response['error']}")
        
        # Test analytics generation
        print("\n3. Testing analytics generation...")
        
        analytics = agent.get_analytics("test_user", "month")
        
        if analytics.get("success"):
            report = analytics.get("report", {})
            print(f"   ✅ Analytics report generated:")
            print(f"      - User ID: {report.get('user_id', '')}")
            print(f"      - Period: {report.get('period_analyzed', '')}")
            print(f"      - Key metrics: {len(report.get('key_metrics', {}))}")
            print(f"      - Trends: {report.get('trends_count', 0)}")
            print(f"      - Recommendations: {len(report.get('recommendations', []))}")
        else:
            print(f"   ❌ Analytics error: {analytics.get('error', 'Unknown error')}")
        
        # Test system status
        print("\n4. Testing system status monitoring...")
        
        status = agent.get_system_status()
        
        print(f"   ✅ System status:")
        print(f"      - Agent ID: {status.get('agent_id', '')}")
        print(f"      - Overall health: {status.get('overall_health', '')}")
        print(f"      - Healthy components: {status.get('healthy_components', 0)}/{status.get('total_components', 0)}")
        print(f"      - Components: {list(status.get('components', {}).keys())}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ RAG Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        agent.shutdown()


def test_system_integration():
    """Test system integration functionality"""
    print("\n🧪 Testing System Integration...")
    print("=" * 50)
    
    # Initialize components
    config = IntegrationConfig(
        auto_sync_enabled=False,
        enable_monitoring=False
    )
    
    rag_agent = RAGAgent(config)
    integrator = SystemIntegrator(rag_agent)
    
    try:
        # Test integration hook registration
        print("\n1. Testing integration hook registration...")
        
        def test_hook(param):
            return f"hook_result_{param}"
        
        integrator.register_integration_hook("test_hook", test_hook)
        
        if "test_hook" in integrator.integration_hooks:
            print("   ✅ Integration hook registered successfully")
        else:
            print("   ❌ Failed to register integration hook")
            return False
        
        # Test integration hook triggering
        print("\n2. Testing integration hook triggering...")
        
        result = integrator.trigger_integration_hook("test_hook", "test_param")
        
        if result == "hook_result_test_param":
            print("   ✅ Integration hook triggered successfully")
        else:
            print(f"   ❌ Hook result mismatch: {result}")
            return False
        
        # Test data source registration
        print("\n3. Testing data source registration...")
        
        test_data_source = {
            "fitness_data": [
                {"weight": 80, "date": "2024-01-01"},
                {"weight": 79.5, "date": "2024-01-08"}
            ]
        }
        
        integrator.register_data_source("fitness_db", test_data_source)
        
        if "fitness_db" in integrator.data_sources:
            print("   ✅ Data source registered successfully")
        else:
            print("   ❌ Failed to register data source")
            return False
        
        # Test data source retrieval
        print("\n4. Testing data source retrieval...")
        
        data = integrator.get_data_from_source("fitness_db")
        
        if data == test_data_source:
            print("   ✅ Data source retrieved successfully")
        else:
            print(f"   ❌ Data source retrieval failed: {data}")
            return False
        
        # Test workflow integration
        print("\n5. Testing workflow integration...")
        
        workflow_config = {
            "rag_config": {
                "auto_sync_enabled": True,
                "sync_interval_minutes": 30
            },
            "data_sources": {
                "fitness_db": {"type": "database"},
                "analytics_db": {"type": "analytics"}
            }
        }
        
        success = integrator.integrate_with_existing_workflow(workflow_config)
        
        if success:
            print("   ✅ Workflow integration completed successfully")
        else:
            print("   ❌ Workflow integration failed")
            return False
        
        # Test integration status
        print("\n6. Testing integration status...")
        
        status = integrator.get_integration_status()
        
        print(f"   ✅ Integration status:")
        print(f"      - Registered hooks: {len(status.get('registered_hooks', []))}")
        print(f"      - Registered sources: {len(status.get('registered_sources', []))}")
        print(f"      - Integration timestamp: {status.get('integration_timestamp', '')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ System integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        rag_agent.shutdown()


def test_data_synchronization():
    """Test data synchronization functionality"""
    print("\n🧪 Testing Data Synchronization...")
    print("=" * 50)
    
    # Initialize components
    config = IntegrationConfig(
        auto_sync_enabled=False,
        enable_monitoring=False
    )
    
    rag_agent = RAGAgent(config)
    synchronizer = DataSynchronizer(rag_agent)
    
    try:
        # Test data synchronization
        print("\n1. Testing data synchronization...")
        
        # Mock the sync methods to avoid actual operations
        import unittest.mock
        with unittest.mock.patch.object(rag_agent, 'sync_fitness_data', return_value=True):
            with unittest.mock.patch.object(synchronizer, '_sync_analytics_data', return_value=True):
                with unittest.mock.patch.object(synchronizer, '_sync_cache_data', return_value=True):
                    results = synchronizer.sync_all_data()
                    
                    if isinstance(results, dict):
                        print("   ✅ Data synchronization completed")
                        print(f"      - Fitness data: {results.get('fitness_data', {}).get('success', False)}")
                        print(f"      - Analytics data: {results.get('analytics_data', {}).get('success', False)}")
                        print(f"      - Cache data: {results.get('cache_data', {}).get('success', False)}")
                    else:
                        print(f"   ❌ Synchronization failed: {results}")
                        return False
        
        # Test sync history
        print("\n2. Testing sync history tracking...")
        
        history = synchronizer.get_sync_history()
        
        if isinstance(history, list) and len(history) > 0:
            print("   ✅ Sync history tracked successfully")
            print(f"      - History records: {len(history)}")
            
            # Check latest record
            latest = history[-1]
            print(f"      - Latest sync: {latest.get('start_time', '')}")
            print(f"      - Duration: {latest.get('duration_seconds', 0):.2f}s")
            print(f"      - Success: {latest.get('success', False)}")
        else:
            print("   ❌ Sync history tracking failed")
            return False
        
        # Test sync statistics
        print("\n3. Testing sync statistics...")
        
        stats = synchronizer.get_sync_statistics()
        
        if isinstance(stats, dict) and "total_syncs" in stats:
            print("   ✅ Sync statistics generated")
            print(f"      - Total syncs: {stats.get('total_syncs', 0)}")
            print(f"      - Successful syncs: {stats.get('successful_syncs', 0)}")
            print(f"      - Success rate: {stats.get('success_rate', 0)}%")
            print(f"      - Average duration: {stats.get('average_duration_seconds', 0):.2f}s")
        else:
            print(f"   ❌ Sync statistics failed: {stats}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data synchronization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        rag_agent.shutdown()


def test_configuration():
    """Test configuration functionality"""
    print("\n🧪 Testing Configuration...")
    print("=" * 50)
    
    try:
        # Test configuration loading
        print("\n1. Testing configuration loading...")
        
        config = get_config()
        
        if isinstance(config, RAGPipelineConfig):
            print("   ✅ Configuration loaded successfully")
            print(f"      - Environment: {config.environment}")
            print(f"      - Debug mode: {config.debug}")
            print(f"      - Vector store: {config.vector_store.type}")
            print(f"      - LLM provider: {config.llm.provider}")
            print(f"      - Cache enabled: {config.cache.enabled}")
            print(f"      - Optimization enabled: {config.optimization.enabled}")
        else:
            print("   ❌ Configuration loading failed")
            return False
        
        # Test configuration manager
        print("\n2. Testing configuration manager...")
        
        config_manager = ConfigManager()
        
        # Test environment-specific configs
        environments = ["development", "testing", "staging", "production"]
        
        for env in environments:
            env_config = config_manager.get_environment_config(env)
            print(f"      - {env.capitalize()}: debug={env_config.debug}, cache={env_config.cache.enabled}")
        
        print("   ✅ Environment configurations generated")
        
        # Test sample configuration creation
        print("\n3. Testing sample configuration creation...")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            sample_file = f.name
        
        try:
            config_manager.create_sample_config(sample_file)
            
            if os.path.exists(sample_file):
                with open(sample_file, 'r') as f:
                    sample_data = json.load(f)
                
                print("   ✅ Sample configuration created")
                print(f"      - File: {sample_file}")
                print(f"      - Environment: {sample_data.get('environment', '')}")
                print(f"      - LLM provider: {sample_data.get('llm', {}).get('provider', '')}")
            else:
                print("   ❌ Sample configuration creation failed")
                return False
                
        finally:
            if os.path.exists(sample_file):
                os.unlink(sample_file)
        
        # Test configuration validation
        print("\n4. Testing configuration validation...")
        
        # Test with valid configuration
        valid_config = RAGPipelineConfig()
        valid_config.llm.api_key = "test-key"
        
        try:
            config_manager.config = valid_config
            config_manager._validate_configuration()
            print("   ✅ Valid configuration validation passed")
        except Exception as e:
            print(f"   ❌ Valid configuration validation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_deployment():
    """Test deployment configuration"""
    print("\n🧪 Testing Deployment Configuration...")
    print("=" * 50)
    
    try:
        # Create temporary deployment directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"\n1. Creating deployment configuration in: {temp_dir}")
            
            # Test deployment config creation for different environments
            environments = ["development", "staging", "production"]
            
            for env in environments:
                print(f"\n   Creating {env} deployment config...")
                
                deploy_dir = os.path.join(temp_dir, env)
                create_deployment_config(env, deploy_dir)
                
                # Check if files were created
                expected_files = [
                    f"rag_config_{env}.json",
                    "Dockerfile",
                    "docker-compose.yml",
                    ".env"
                ]
                
                for file_name in expected_files:
                    file_path = os.path.join(deploy_dir, file_name)
                    if os.path.exists(file_path):
                        print(f"      ✅ {file_name}")
                    else:
                        print(f"      ❌ {file_name} not found")
                        return False
            
            print("   ✅ Deployment configurations created successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Deployment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test full integration"""
    print("\n🧪 Testing Full Integration...")
    print("=" * 50)
    
    try:
        # Initialize complete system
        print("\n1. Initializing complete RAG system...")
        
        config = IntegrationConfig(
            auto_sync_enabled=False,
            enable_monitoring=False,
            cache_enabled=True,
            optimization_enabled=True
        )
        
        agent = RAGAgent(config)
        integrator = SystemIntegrator(agent)
        synchronizer = DataSynchronizer(agent)
        
        print("   ✅ Complete system initialized")
        
        # Test complete workflow
        print("\n2. Testing complete workflow...")
        
        # Register integration hooks
        def pre_hook(config):
            return {"status": "pre_integration"}
        
        def post_hook(config):
            return {"status": "post_integration"}
        
        integrator.register_integration_hook("pre_integration", pre_hook)
        integrator.register_integration_hook("post_integration", post_hook)
        
        # Register data sources
        test_data = {"fitness_data": [{"weight": 80, "date": "2024-01-01"}]}
        integrator.register_data_source("fitness_db", test_data)
        
        # Integrate workflow
        workflow_config = {
            "rag_config": {
                "auto_sync_enabled": True,
                "sync_interval_minutes": 30
            },
            "data_sources": {
                "fitness_db": {"type": "database"}
            }
        }
        
        integration_success = integrator.integrate_with_existing_workflow(workflow_config)
        
        if not integration_success:
            print("   ❌ Workflow integration failed")
            return False
        
        print("   ✅ Workflow integration completed")
        
        # Test data synchronization
        print("\n3. Testing data synchronization...")
        
        with unittest.mock.patch.object(agent, 'sync_fitness_data', return_value=True):
            with unittest.mock.patch.object(synchronizer, '_sync_analytics_data', return_value=True):
                with unittest.mock.patch.object(synchronizer, '_sync_cache_data', return_value=True):
                    sync_results = synchronizer.sync_all_data()
                    
                    if isinstance(sync_results, dict):
                        print("   ✅ Data synchronization completed")
                    else:
                        print("   ❌ Data synchronization failed")
                        return False
        
        # Test query processing
        print("\n4. Testing query processing...")
        
        test_queries = [
            "How has my weight changed?",
            "What are my current measurements?",
            "Give me a summary of my progress"
        ]
        
        for query in test_queries:
            response = agent.process_query(query, "integration_test_user")
            
            if "error" not in response:
                print(f"      ✅ Query processed: {query[:30]}...")
            else:
                print(f"      ❌ Query failed: {response['error']}")
        
        # Test analytics
        print("\n5. Testing analytics generation...")
        
        analytics = agent.get_analytics("integration_test_user", "month")
        
        if analytics.get("success"):
            print("   ✅ Analytics generated successfully")
        else:
            print(f"   ❌ Analytics failed: {analytics.get('error', 'Unknown error')}")
        
        # Test system status
        print("\n6. Testing system status...")
        
        agent_status = agent.get_system_status()
        integration_status = integrator.get_integration_status()
        
        print(f"   ✅ System status:")
        print(f"      - Agent health: {agent_status.get('overall_health', '')}")
        print(f"      - Integration hooks: {len(integration_status.get('registered_hooks', []))}")
        print(f"      - Data sources: {len(integration_status.get('registered_sources', []))}")
        
        # Clean up
        agent.shutdown()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 RAG Pipeline Phase 6 Test")
    print("=" * 60)
    
    # Check environment
    print("🔍 Environment Check:")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not set (will use fallback responses)")
    
    print()
    
    # Run tests
    try:
        # Test RAG Agent
        agent_success = test_rag_agent()
        
        # Test System Integration
        integration_success = test_system_integration()
        
        # Test Data Synchronization
        sync_success = test_data_synchronization()
        
        # Test Configuration
        config_success = test_configuration()
        
        # Test Deployment
        deployment_success = test_deployment()
        
        # Test Full Integration
        full_integration_success = test_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Phase 6 Test Summary:")
        print(f"   RAG Agent: {'✅ PASS' if agent_success else '❌ FAIL'}")
        print(f"   System Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
        print(f"   Data Synchronization: {'✅ PASS' if sync_success else '❌ FAIL'}")
        print(f"   Configuration: {'✅ PASS' if config_success else '❌ FAIL'}")
        print(f"   Deployment: {'✅ PASS' if deployment_success else '❌ FAIL'}")
        print(f"   Full Integration: {'✅ PASS' if full_integration_success else '❌ FAIL'}")
        
        if all([agent_success, integration_success, sync_success, config_success, deployment_success, full_integration_success]):
            print("\n🎉 Phase 6 implementation is working correctly!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Set up environment variables in .env file")
            print("3. Run the test script again to verify functionality")
            print("4. Deploy the RAG pipeline using the generated configuration")
            print("5. Proceed to Phase 7: Documentation and User Guide")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 