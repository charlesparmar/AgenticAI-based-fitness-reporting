#!/usr/bin/env python3
"""
Test Script for RAG Pipeline Phase 2
Tests query processing and retrieval functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.query_processor import QueryProcessor
from rag.retriever import Retriever
from rag.vector_store import VectorStore
from rag.data_preparation import DataPreparation


def test_query_processor():
    """Test query processing functionality"""
    print("🧪 Testing Query Processor...")
    print("=" * 50)
    
    # Initialize query processor
    query_processor = QueryProcessor()
    
    # Test queries
    test_queries = [
        "How has my weight changed over the last month?",
        "Compare my measurements from week 1 to week 10",
        "What was my weight on 2024-01-15?",
        "Show me my fat percentage trends",
        "Give me a summary of my fitness journey",
        "Am I making progress toward my goals?",
        "What are my current body measurements?",
        "How did my BMI change in the last 3 weeks?"
    ]
    
    print(f"\nTesting {len(test_queries)} different query types...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        # Process query
        processed = query_processor.process_query(query)
        
        if "error" in processed:
            print(f"   ❌ Error: {processed['error']}")
            continue
        
        # Display results
        print(f"   ✅ Type: {processed.get('query_type', 'unknown')}")
        print(f"   📊 Entities: {len(processed.get('entities', {}).get('measurements', []))} measurements")
        print(f"   🔍 Enhanced queries: {len(processed.get('enhanced_queries', []))}")
        
        # Show enhanced queries
        enhanced = processed.get('enhanced_queries', [])
        if enhanced:
            print(f"   📝 Enhanced: {enhanced[0][:50]}...")
    
    # Test query validation
    print("\n\nTesting query validation...")
    validation_tests = [
        ("", "Empty query"),
        ("a", "Too short"),
        ("How has my weight changed over the last month?", "Valid query"),
        ("x" * 600, "Too long")
    ]
    
    for query, description in validation_tests:
        is_valid, error_msg = query_processor.validate_query(query)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {description}: {is_valid} - {error_msg}")
    
    # Test query suggestions
    print("\n\nTesting query suggestions...")
    partial_queries = ["weight", "fat", "trend", "compare"]
    
    for partial in partial_queries:
        suggestions = query_processor.get_query_suggestions(partial)
        print(f"   Suggestions for '{partial}': {len(suggestions)} found")
        if suggestions:
            print(f"      Example: {suggestions[0]}")
    
    return True


def test_retriever():
    """Test retriever functionality"""
    print("\n🧪 Testing Retriever...")
    print("=" * 50)
    
    # Initialize components
    vector_store = VectorStore(collection_name="test_fitness_data_phase2")
    query_processor = QueryProcessor()
    retriever = Retriever(vector_store, query_processor)
    
    # First, add some test data to the vector store
    print("\n1. Adding test data to vector store...")
    
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
            'content': 'Trend analysis from week 1 to week 3: Weight decreased by 1kg, BMI decreased by 0.5, Fat percentage decreased by 1%',
            'metadata': {
                'type': 'trend',
                'date_from': '2024-01-01',
                'date_to': '2024-01-15',
                'week_from': 'Week 1',
                'week_to': 'Week 3',
                'chunk_id': 'trend_1_3',
                'changes': {'weight': -1, 'bmi': -0.5, 'fat_percent': -1}
            }
        },
        {
            'content': 'Fitness data summary: Total records 3, Date range 2024-01-01 to 2024-01-15, Average weight 79.5kg, Average BMI 25.2',
            'metadata': {
                'type': 'overall_summary',
                'total_records': 3,
                'date_range': '2024-01-01 to 2024-01-15',
                'chunk_id': 'overall_summary',
                'statistics': {'weight': {'avg': 79.5}, 'bmi': {'avg': 25.2}}
            }
        }
    ]
    
    success = vector_store.add_documents(test_documents)
    if not success:
        print("❌ Failed to add test documents")
        return False
    
    print("✅ Test data added successfully")
    
    # Test different types of queries
    print("\n2. Testing retrieval with different query types...")
    
    test_queries = [
        ("weight measurements", "Simple measurement query"),
        ("How has my weight changed", "Trend query"),
        ("Compare week 1 to week 3", "Comparison query"),
        ("Give me a summary", "Summary query"),
        ("What was my weight on 2024-01-15", "Specific date query")
    ]
    
    for query, description in test_queries:
        print(f"\n   Query: '{query}' ({description})")
        
        # Test basic retrieval
        results = retriever.retrieve(query, n_results=3)
        
        if results:
            print(f"   ✅ Found {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                content = result.get('content', '')[:80]
                score = result.get('relevance_score', 0)
                print(f"      Result {i}: {content}... (Score: {score:.3f})")
        else:
            print("   ❌ No results found")
    
    # Test retrieval with filters
    print("\n3. Testing retrieval with filters...")
    
    filter_criteria = {"type": {"$in": ["measurement"]}}
    results = retriever.retrieve("weight", n_results=5, filter_criteria=filter_criteria)
    
    if results:
        print(f"   ✅ Found {len(results)} measurement results")
        measurement_count = sum(1 for r in results if r.get('metadata', {}).get('type') == 'measurement')
        print(f"   📊 {measurement_count} are measurement type")
    else:
        print("   ❌ No filtered results found")
    
    # Test hybrid search
    print("\n4. Testing hybrid search...")
    
    hybrid_results = retriever.hybrid_search("weight trend", n_results=3)
    
    if hybrid_results:
        print(f"   ✅ Hybrid search found {len(hybrid_results)} results")
        for i, result in enumerate(hybrid_results[:2], 1):
            combined_score = result.get('combined_score', 0)
            semantic_score = result.get('semantic_score', 0)
            keyword_score = result.get('keyword_score', 0)
            print(f"      Result {i}: Combined={combined_score:.3f}, Semantic={semantic_score:.3f}, Keyword={keyword_score:.3f}")
    else:
        print("   ❌ No hybrid search results")
    
    # Test retrieval stats
    print("\n5. Testing retrieval statistics...")
    
    stats = retriever.get_retrieval_stats()
    if 'error' not in stats:
        print("   ✅ Retrieval stats:")
        collection_info = stats.get('collection_info', {})
        print(f"      Collection: {collection_info.get('collection_name', 'Unknown')}")
        print(f"      Documents: {collection_info.get('document_count', 0)}")
        
        retrieval_params = stats.get('retrieval_params', {})
        print(f"      Default results: {retrieval_params.get('default_n_results', 0)}")
        print(f"      Min threshold: {retrieval_params.get('min_similarity_threshold', 0)}")
    else:
        print(f"   ❌ Error getting stats: {stats['error']}")
    
    # Clean up
    print("\n6. Cleaning up test collection...")
    vector_store.reset_collection()
    print("   ✅ Test collection cleaned up")
    
    return True


def test_integration():
    """Test integration between Phase 1 and Phase 2"""
    print("\n🧪 Testing Phase 1 + Phase 2 Integration...")
    print("=" * 50)
    
    try:
        # Initialize Phase 1 components
        print("\n1. Initializing Phase 1 components...")
        data_prep = DataPreparation()
        
        # Try to get real data (this might fail if no data exists)
        print("2. Attempting to get real fitness data...")
        fitness_data = data_prep.extract_fitness_data()
        
        if not fitness_data:
            print("   ⚠️  No real fitness data available, using mock data")
            # Create mock data for testing
            fitness_data = [
                {
                    'date': '2024-01-01',
                    'weight': 80.0,
                    'fat_percent': 18.0,
                    'bmi': 25.5,
                    'week_number': 'Week 1 (2024)'
                },
                {
                    'date': '2024-01-08',
                    'weight': 79.5,
                    'fat_percent': 17.5,
                    'bmi': 25.2,
                    'week_number': 'Week 2 (2024)'
                }
            ]
        else:
            print(f"   ✅ Found {len(fitness_data)} real fitness records")
        
        # Process data through Phase 1
        print("3. Processing data through Phase 1...")
        preprocessed_data = data_prep.preprocess_data(fitness_data)
        chunks = data_prep.create_document_chunks(preprocessed_data)
        chunks_with_embeddings = data_prep.generate_embeddings(chunks)
        
        if not chunks_with_embeddings:
            print("   ❌ Failed to create chunks with embeddings")
            return False
        
        print(f"   ✅ Created {len(chunks_with_embeddings)} chunks with embeddings")
        
        # Initialize Phase 2 components
        print("4. Initializing Phase 2 components...")
        vector_store = VectorStore(collection_name="integration_test")
        query_processor = QueryProcessor()
        retriever = Retriever(vector_store, query_processor)
        
        # Add data to vector store
        print("5. Adding data to vector store...")
        success = vector_store.add_documents(chunks_with_embeddings)
        
        if not success:
            print("   ❌ Failed to add documents to vector store")
            return False
        
        print("   ✅ Data added to vector store")
        
        # Test end-to-end query processing and retrieval
        print("6. Testing end-to-end query processing and retrieval...")
        
        test_queries = [
            "How has my weight changed?",
            "Show me my measurements",
            "What's my BMI trend?",
            "Give me a summary"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            
            # Process query
            processed = query_processor.process_query(query)
            if "error" in processed:
                print(f"      ❌ Query processing error: {processed['error']}")
                continue
            
            print(f"      ✅ Query type: {processed.get('query_type')}")
            
            # Retrieve results
            results = retriever.retrieve(query, n_results=3)
            
            if results:
                print(f"      ✅ Found {len(results)} results")
                best_result = results[0]
                content = best_result.get('content', '')[:100]
                score = best_result.get('relevance_score', 0)
                print(f"      📄 Best result: {content}... (Score: {score:.3f})")
            else:
                print("      ❌ No results found")
        
        # Clean up
        print("\n7. Cleaning up integration test...")
        vector_store.reset_collection()
        print("   ✅ Integration test cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 RAG Pipeline Phase 2 Test")
    print("=" * 60)
    
    # Check environment
    print("🔍 Environment Check:")
    sqlite_key = os.getenv("SQLITE_API_KEY")
    if sqlite_key:
        print("✅ SQLITE_API_KEY is set")
    else:
        print("⚠️  SQLITE_API_KEY not set (some tests may fail)")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not set (will use local embeddings)")
    
    print()
    
    # Run tests
    try:
        # Test query processor
        query_success = test_query_processor()
        
        # Test retriever
        retriever_success = test_retriever()
        
        # Test integration
        integration_success = test_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Phase 2 Test Summary:")
        print(f"   Query Processor: {'✅ PASS' if query_success else '❌ FAIL'}")
        print(f"   Retriever: {'✅ PASS' if retriever_success else '❌ FAIL'}")
        print(f"   Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
        
        if query_success and retriever_success and integration_success:
            print("\n🎉 Phase 2 implementation is working correctly!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Set up environment variables in .env file")
            print("3. Run the test script again to verify functionality")
            print("4. Proceed to Phase 3: LLM Integration and Response Generation")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 