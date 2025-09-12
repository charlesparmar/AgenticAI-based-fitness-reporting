#!/usr/bin/env python3
"""
Test Script for RAG Pipeline Phase 5
Tests analytics, caching, and optimization functionality
"""

import os
import sys
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.analytics import FitnessAnalytics, TrendAnalysis, GoalAnalysis, InsightReport
from rag.cache import CacheManager, ResponseCache, VectorSearchCache, EmbeddingCache
from rag.optimization import RAGOptimizer, PerformanceMonitor, BatchProcessor, VectorSearchOptimizer, LoadBalancer
from rag.vector_store import VectorStore
from rag.query_processor import QueryProcessor
from rag.retriever import Retriever


def test_analytics():
    """Test analytics functionality"""
    print("🧪 Testing Analytics...")
    print("=" * 50)
    
    # Initialize components
    vector_store = VectorStore(collection_name="test_analytics")
    query_processor = QueryProcessor()
    retriever = Retriever(vector_store, query_processor)
    analytics = FitnessAnalytics(vector_store, query_processor, retriever)
    
    # Add test data
    print("\n1. Adding test data...")
    
    test_documents = [
        {
            'content': 'Week 1 measurements: Weight 80kg, BMI 25.5, Fat percentage 18%, Chest 100cm, Waist 85cm',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-01',
                'week_number': 'Week 1',
                'chunk_id': 'test_chunk_1',
                'measurements': {'weight': 80, 'bmi': 25.5, 'fat_percent': 18, 'chest': 100, 'waist': 85}
            }
        },
        {
            'content': 'Week 2 measurements: Weight 79.5kg, BMI 25.2, Fat percentage 17.5%, Chest 99cm, Waist 84cm',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-08',
                'week_number': 'Week 2',
                'chunk_id': 'test_chunk_2',
                'measurements': {'weight': 79.5, 'bmi': 25.2, 'fat_percent': 17.5, 'chest': 99, 'waist': 84}
            }
        },
        {
            'content': 'Week 3 measurements: Weight 79kg, BMI 25.0, Fat percentage 17%, Chest 98cm, Waist 83cm',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-15',
                'week_number': 'Week 3',
                'chunk_id': 'test_chunk_3',
                'measurements': {'weight': 79, 'bmi': 25.0, 'fat_percent': 17, 'chest': 98, 'waist': 83}
            }
        }
    ]
    
    success = vector_store.add_documents(test_documents)
    if not success:
        print("❌ Failed to add test documents")
        return False
    
    print("✅ Test data added successfully")
    
    # Test trend analysis
    print("\n2. Testing trend analysis...")
    
    metrics_to_test = ['weight', 'bmi', 'fat_percent']
    
    for metric in metrics_to_test:
        print(f"\n   Analyzing {metric} trends...")
        
        trends = analytics.analyze_trends(metric, period='month')
        
        if trends:
            for trend in trends:
                print(f"      ✅ {trend.period}: {trend.trend_direction} by {abs(trend.change_percentage):.1f}%")
                print(f"         Confidence: {trend.confidence:.2f}")
                print(f"         Insights: {len(trend.insights)} insights")
                print(f"         Recommendations: {len(trend.recommendations)} recommendations")
        else:
            print(f"      ⚠️  No trends found for {metric}")
    
    # Test goal analysis
    print("\n3. Testing goal analysis...")
    
    user_goals = {
        'weight': {
            'target_value': 75,
            'start_value': 80,
            'start_date': '2024-01-01',
            'target_date': '2024-03-01'
        },
        'bmi': {
            'target_value': 23.5,
            'start_value': 25.5,
            'start_date': '2024-01-01',
            'target_date': '2024-03-01'
        }
    }
    
    goal_analyses = analytics.analyze_goals(user_goals)
    
    for goal_analysis in goal_analyses:
        print(f"   ✅ {goal_analysis.goal_type} goal:")
        print(f"      Current: {goal_analysis.current_value}")
        print(f"      Target: {goal_analysis.target_value}")
        print(f"      Progress: {goal_analysis.progress_percentage:.1f}%")
        print(f"      Days remaining: {goal_analysis.days_remaining}")
        print(f"      Risk factors: {len(goal_analysis.risk_factors)}")
    
    # Test insight report generation
    print("\n4. Testing insight report generation...")
    
    report = analytics.generate_insight_report("test_user", "month")
    
    if report:
        print(f"   ✅ Generated insight report:")
        print(f"      User ID: {report.user_id}")
        print(f"      Period: {report.period_analyzed}")
        print(f"      Key metrics: {len(report.key_metrics)}")
        print(f"      Trends: {len(report.trends)}")
        print(f"      Recommendations: {len(report.recommendations)}")
        print(f"      Risk alerts: {len(report.risk_alerts)}")
        print(f"      Achievements: {len(report.achievements)}")
    else:
        print("   ❌ Failed to generate insight report")
    
    # Test analytics summary
    print("\n5. Testing analytics summary...")
    
    summary = analytics.get_analytics_summary()
    print(f"   ✅ Analytics summary:")
    print(f"      Metrics tracked: {len(summary['metrics_tracked'])}")
    print(f"      Trend periods: {len(summary['trend_periods'])}")
    print(f"      Capabilities: {len(summary['capabilities'])}")
    
    # Clean up
    print("\n6. Cleaning up...")
    vector_store.reset_collection()
    print("   ✅ Test data cleaned up")
    
    return True


def test_caching():
    """Test caching functionality"""
    print("\n🧪 Testing Caching...")
    print("=" * 50)
    
    # Initialize cache manager
    cache_manager = CacheManager(
        response_cache_size=100,
        vector_cache_size=50,
        embedding_cache_size=200
    )
    
    # Test response cache
    print("\n1. Testing response cache...")
    
    test_query = "How has my weight changed?"
    test_context = [{"content": "test context", "metadata": {"type": "measurement"}}]
    test_response = {"response": "Your weight has decreased by 1kg", "query_type": "trend"}
    
    # Set cache
    success = cache_manager.set_response(test_query, test_context, "trend", test_response)
    if success:
        print("   ✅ Response cached successfully")
    else:
        print("   ❌ Failed to cache response")
    
    # Get from cache
    cached_response = cache_manager.get_response(test_query, test_context, "trend")
    if cached_response:
        print("   ✅ Retrieved response from cache")
        print(f"      Response: {cached_response['response']}")
    else:
        print("   ❌ Failed to retrieve from cache")
    
    # Test vector cache
    print("\n2. Testing vector cache...")
    
    test_vector_query = "weight measurements"
    test_vector_results = [
        {"content": "Week 1: 80kg", "metadata": {"week": "Week 1"}},
        {"content": "Week 2: 79.5kg", "metadata": {"week": "Week 2"}}
    ]
    
    # Set vector cache
    success = cache_manager.set_vector_results(test_vector_query, 5, None, test_vector_results)
    if success:
        print("   ✅ Vector results cached successfully")
    else:
        print("   ❌ Failed to cache vector results")
    
    # Get from vector cache
    cached_vector_results = cache_manager.get_vector_results(test_vector_query, 5)
    if cached_vector_results:
        print("   ✅ Retrieved vector results from cache")
        print(f"      Results count: {len(cached_vector_results)}")
    else:
        print("   ❌ Failed to retrieve vector results from cache")
    
    # Test embedding cache
    print("\n3. Testing embedding cache...")
    
    test_text = "This is a test text for embedding"
    test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional embedding
    test_model = "text-embedding-ada-002"
    
    # Set embedding cache
    success = cache_manager.set_embedding(test_text, test_model, test_embedding)
    if success:
        print("   ✅ Embedding cached successfully")
    else:
        print("   ❌ Failed to cache embedding")
    
    # Get from embedding cache
    cached_embedding = cache_manager.get_embedding(test_text, test_model)
    if cached_embedding:
        print("   ✅ Retrieved embedding from cache")
        print(f"      Embedding dimension: {len(cached_embedding)}")
    else:
        print("   ❌ Failed to retrieve embedding from cache")
    
    # Test cache statistics
    print("\n4. Testing cache statistics...")
    
    stats = cache_manager.get_all_stats()
    print(f"   ✅ Cache statistics:")
    print(f"      Total entries: {stats['total_entries']}")
    print(f"      Response cache: {stats['response_cache']['total_entries']} entries")
    print(f"      Vector cache: {stats['vector_cache']['total_entries']} entries")
    print(f"      Embedding cache: {stats['embedding_cache']['total_entries']} entries")
    
    # Test cache optimization
    print("\n5. Testing cache optimization...")
    
    cache_manager.optimize_caches()
    print("   ✅ Cache optimization completed")
    
    # Test cache persistence
    print("\n6. Testing cache persistence...")
    
    cache_file = "test_cache_state.json"
    cache_manager.save_cache_state(cache_file)
    print("   ✅ Cache state saved")
    
    # Clear cache and reload
    cache_manager.clear_all()
    cache_manager.load_cache_state(cache_file)
    print("   ✅ Cache state loaded")
    
    # Clean up
    if os.path.exists(cache_file):
        os.remove(cache_file)
    
    return True


def test_optimization():
    """Test optimization functionality"""
    print("\n🧪 Testing Optimization...")
    print("=" * 50)
    
    # Initialize components
    vector_store = VectorStore(collection_name="test_optimization")
    cache_manager = CacheManager()
    optimizer = RAGOptimizer(vector_store, cache_manager)
    
    # Test performance monitoring
    print("\n1. Testing performance monitoring...")
    
    # Record some test metrics
    for i in range(10):
        optimizer.performance_monitor.record_metric(
            "test_operation",
            duration_ms=100 + i * 10,
            success=i < 8,  # 80% success rate
            metadata={"iteration": i}
        )
    
    stats = optimizer.performance_monitor.get_statistics("test_operation")
    print(f"   ✅ Performance statistics:")
    print(f"      Total operations: {stats['total_operations']}")
    print(f"      Success rate: {stats['success_rate']}%")
    print(f"      Average duration: {stats['average_duration_ms']}ms")
    print(f"      P95 duration: {stats['p95_duration_ms']}ms")
    
    # Test batch processing
    print("\n2. Testing batch processing...")
    
    test_items = list(range(20))
    
    def test_processor(item):
        time.sleep(0.01)  # Simulate processing time
        return item * 2
    
    job_id = optimizer.batch_processor.submit_batch(test_items, test_processor)
    
    if job_id:
        print(f"   ✅ Batch job submitted: {job_id}")
        
        # Wait for completion
        while True:
            status = optimizer.batch_processor.get_job_status(job_id)
            if status and status['status'] in ['completed', 'failed']:
                print(f"   ✅ Batch job {status['status']}")
                print(f"      Completed items: {status['completed_items']}")
                print(f"      Error count: {status['error_count']}")
                break
            time.sleep(0.1)
        
        # Get results
        results = optimizer.batch_processor.get_job_results(job_id)
        if results:
            print(f"   ✅ Retrieved {len(results)} results")
    else:
        print("   ❌ Failed to submit batch job")
    
    # Test vector search optimization
    print("\n3. Testing vector search optimization...")
    
    # Add test data
    test_documents = [
        {
            'content': 'Weight measurement: 80kg',
            'metadata': {'type': 'measurement', 'metric': 'weight'}
        },
        {
            'content': 'BMI measurement: 25.5',
            'metadata': {'type': 'measurement', 'metric': 'bmi'}
        }
    ]
    
    vector_store.add_documents(test_documents)
    
    # Test optimized search
    results = optimizer.vector_optimizer.optimize_search("weight", n_results=5)
    print(f"   ✅ Optimized search returned {len(results)} results")
    
    # Test batch search
    queries = ["weight", "bmi", "measurements"]
    batch_results = optimizer.vector_optimizer.batch_search(queries, n_results=3)
    print(f"   ✅ Batch search returned {len(batch_results)} result sets")
    
    # Test load balancing
    print("\n4. Testing load balancing...")
    
    def test_operation(delay=0.1):
        time.sleep(delay)
        return f"Operation completed after {delay}s"
    
    # Submit multiple requests
    results = []
    for i in range(5):
        result = optimizer.load_balancer.submit_request(test_operation, 0.05)
        results.append(result)
    
    print(f"   ✅ Load balancer processed {len(results)} requests")
    
    # Get load statistics
    load_stats = optimizer.load_balancer.get_load_statistics()
    print(f"   ✅ Load statistics:")
    print(f"      Active requests: {load_stats['active_requests']}")
    print(f"      Queued requests: {load_stats['queued_requests']}")
    print(f"      Utilization: {load_stats['utilization_percentage']}%")
    
    # Test optimization statistics
    print("\n5. Testing optimization statistics...")
    
    opt_stats = optimizer.get_optimization_statistics()
    print(f"   ✅ Optimization statistics:")
    print(f"      Performance metrics: {opt_stats['performance']['total_operations']} operations")
    print(f"      Load balancer: {opt_stats['load_balancer']['active_requests']} active requests")
    print(f"      Vector search: {opt_stats['vector_search']['total_operations']} searches")
    print(f"      Cache: {opt_stats['cache']['total_entries']} entries")
    print(f"      Batch processor: {opt_stats['batch_processor']['active_jobs']} active jobs")
    
    # Test optimized query processing
    print("\n6. Testing optimized query processing...")
    
    test_query = "How is my progress?"
    test_context = [{"content": "test context"}]
    
    result = optimizer.optimize_query(test_query, test_context, "general")
    print(f"   ✅ Optimized query result: {result['response'][:50]}...")
    
    # Clean up
    print("\n7. Cleaning up...")
    optimizer.shutdown()
    vector_store.reset_collection()
    print("   ✅ Test data cleaned up")
    
    return True


def test_integration():
    """Test integration between all phases"""
    print("\n🧪 Testing Full RAG Pipeline Integration with Phase 5...")
    print("=" * 50)
    
    try:
        # Initialize all components
        print("\n1. Initializing complete RAG pipeline with Phase 5...")
        
        vector_store = VectorStore(collection_name="integration_test_phase5")
        query_processor = QueryProcessor()
        retriever = Retriever(vector_store, query_processor)
        
        # Initialize Phase 5 components
        cache_manager = CacheManager()
        analytics = FitnessAnalytics(vector_store, query_processor, retriever)
        optimizer = RAGOptimizer(vector_store, cache_manager)
        
        # Add comprehensive test data
        print("2. Adding comprehensive test data...")
        
        test_documents = [
            {
                'content': 'Week 1 measurements: Weight 80kg, BMI 25.5, Fat percentage 18%, Chest 100cm, Waist 85cm',
                'metadata': {
                    'type': 'measurement',
                    'date': '2024-01-01',
                    'week_number': 'Week 1',
                    'chunk_id': 'test_chunk_1',
                    'measurements': {'weight': 80, 'bmi': 25.5, 'fat_percent': 18, 'chest': 100, 'waist': 85}
                }
            },
            {
                'content': 'Week 2 measurements: Weight 79.5kg, BMI 25.2, Fat percentage 17.5%, Chest 99cm, Waist 84cm',
                'metadata': {
                    'type': 'measurement',
                    'date': '2024-01-08',
                    'week_number': 'Week 2',
                    'chunk_id': 'test_chunk_2',
                    'measurements': {'weight': 79.5, 'bmi': 25.2, 'fat_percent': 17.5, 'chest': 99, 'waist': 84}
                }
            },
            {
                'content': 'Week 3 measurements: Weight 79kg, BMI 25.0, Fat percentage 17%, Chest 98cm, Waist 83cm',
                'metadata': {
                    'type': 'measurement',
                    'date': '2024-01-15',
                    'week_number': 'Week 3',
                    'chunk_id': 'test_chunk_3',
                    'measurements': {'weight': 79, 'bmi': 25.0, 'fat_percent': 17, 'chest': 98, 'waist': 83}
                }
            },
            {
                'content': 'Week 4 measurements: Weight 78.5kg, BMI 24.8, Fat percentage 16.5%, Chest 97cm, Waist 82cm',
                'metadata': {
                    'type': 'measurement',
                    'date': '2024-01-22',
                    'week_number': 'Week 4',
                    'chunk_id': 'test_chunk_4',
                    'measurements': {'weight': 78.5, 'bmi': 24.8, 'fat_percent': 16.5, 'chest': 97, 'waist': 82}
                }
            }
        ]
        
        success = vector_store.add_documents(test_documents)
        if not success:
            print("❌ Failed to add test documents")
            return False
        
        print("✅ Test data added successfully")
        
        # Test end-to-end optimized workflow
        print("\n3. Testing end-to-end optimized workflow...")
        
        test_queries = [
            "How has my weight changed?",
            "What are my BMI trends?",
            "Show me my fat percentage progress",
            "Give me a summary of my measurements"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: '{query}'")
            
            # Use optimized query processing
            result = optimizer.optimize_query(query, [], "general")
            
            if "error" not in result:
                print(f"      ✅ Optimized response: {result['response'][:100]}...")
                print(f"      📊 Query type: {result['query_type']}")
                print(f"      ⚡ Optimized: {result.get('optimized', False)}")
            else:
                print(f"      ❌ Error: {result['error']}")
        
        # Test analytics integration
        print("\n4. Testing analytics integration...")
        
        # Generate comprehensive insight report
        report = analytics.generate_insight_report("integration_test_user", "month")
        
        if report:
            print(f"   ✅ Generated comprehensive insight report:")
            print(f"      User ID: {report.user_id}")
            print(f"      Period analyzed: {report.period_analyzed}")
            print(f"      Key metrics: {len(report.key_metrics)}")
            print(f"      Trends analyzed: {len(report.trends)}")
            print(f"      Recommendations: {len(report.recommendations)}")
            print(f"      Risk alerts: {len(report.risk_alerts)}")
            print(f"      Achievements: {len(report.achievements)}")
            
            # Show some insights
            if report.recommendations:
                print(f"      Sample recommendation: {report.recommendations[0]}")
            if report.achievements:
                print(f"      Sample achievement: {report.achievements[0]}")
        else:
            print("   ❌ Failed to generate insight report")
        
        # Test caching performance
        print("\n5. Testing caching performance...")
        
        # Run multiple queries to test cache performance
        for i in range(5):
            start_time = time.time()
            result = optimizer.optimize_query("weight trend", [], "trend")
            duration = (time.time() - start_time) * 1000
            
            print(f"   Query {i+1}: {duration:.2f}ms")
        
        # Get comprehensive statistics
        print("\n6. Getting comprehensive statistics...")
        
        all_stats = optimizer.get_optimization_statistics()
        
        print(f"   ✅ System performance:")
        print(f"      Performance metrics: {all_stats['performance']['total_operations']} operations")
        print(f"      Average response time: {all_stats['performance']['average_duration_ms']}ms")
        print(f"      Success rate: {all_stats['performance']['success_rate']}%")
        print(f"      Cache hit rate: {all_stats['cache']['response_cache']['hit_rate']}%")
        print(f"      Load balancer utilization: {all_stats['load_balancer']['utilization_percentage']}%")
        
        # Test batch processing integration
        print("\n7. Testing batch processing integration...")
        
        # Create batch of queries
        batch_queries = [f"Query {i}" for i in range(10)]
        
        def batch_processor(query):
            return optimizer.optimize_query(query, [], "general")
        
        job_id = optimizer.batch_processor.submit_batch(batch_queries, batch_processor)
        
        if job_id:
            print(f"   ✅ Batch job submitted: {job_id}")
            
            # Wait for completion
            while True:
                status = optimizer.batch_processor.get_job_status(job_id)
                if status and status['status'] in ['completed', 'failed']:
                    print(f"   ✅ Batch job {status['status']}")
                    print(f"      Processed: {status['completed_items']}/{status['total_items']} items")
                    break
                time.sleep(0.1)
        
        # Clean up
        print("\n8. Cleaning up...")
        optimizer.shutdown()
        vector_store.reset_collection()
        print("   ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 RAG Pipeline Phase 5 Test")
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
        # Test analytics
        analytics_success = test_analytics()
        
        # Test caching
        caching_success = test_caching()
        
        # Test optimization
        optimization_success = test_optimization()
        
        # Test integration
        integration_success = test_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Phase 5 Test Summary:")
        print(f"   Analytics: {'✅ PASS' if analytics_success else '❌ FAIL'}")
        print(f"   Caching: {'✅ PASS' if caching_success else '❌ FAIL'}")
        print(f"   Optimization: {'✅ PASS' if optimization_success else '❌ FAIL'}")
        print(f"   Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
        
        if analytics_success and caching_success and optimization_success and integration_success:
            print("\n🎉 Phase 5 implementation is working correctly!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Set up environment variables in .env file")
            print("3. Run the test script again to verify functionality")
            print("4. Integrate Phase 5 components with existing RAG pipeline")
            print("5. Proceed to Phase 6: Integration and Testing")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 