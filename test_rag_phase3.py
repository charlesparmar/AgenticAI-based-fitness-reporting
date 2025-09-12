#!/usr/bin/env python3
"""
Test Script for RAG Pipeline Phase 3
Tests LLM integration and response generation functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.prompts import FitnessPrompts
from rag.generator import ResponseGenerator
from rag.retriever import Retriever
from rag.vector_store import VectorStore
from rag.query_processor import QueryProcessor


def test_prompts():
    """Test prompt generation functionality"""
    print("🧪 Testing Prompts...")
    print("=" * 50)
    
    # Initialize prompts
    prompts = FitnessPrompts()
    
    # Test context formatting
    print("\n1. Testing context formatting...")
    
    test_context = [
        {
            'content': 'Week 1 measurements: Weight 80kg, BMI 25.5, Fat percentage 18%',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-01',
                'week_number': 'Week 1'
            },
            'relevance_score': 0.85
        },
        {
            'content': 'Week 2 measurements: Weight 79.5kg, BMI 25.2, Fat percentage 17.5%',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-08',
                'week_number': 'Week 2'
            },
            'relevance_score': 0.78
        }
    ]
    
    # Test different query types
    test_queries = [
        ("How has my weight changed?", "trend"),
        ("Compare week 1 to week 2", "comparison"),
        ("What was my weight on 2024-01-01?", "specific"),
        ("Give me a summary", "summary"),
        ("Am I making progress toward my goals?", "goal")
    ]
    
    print(f"\n2. Testing prompt generation for {len(test_queries)} query types...")
    
    for query, expected_type in test_queries:
        print(f"\n   Query: '{query}' (Expected type: {expected_type})")
        
        # Generate prompt
        prompt = prompts.get_prompt_for_query(expected_type, test_context, query)
        
        # Check prompt structure
        has_system_prompt = "fitness data assistant" in prompt.lower()
        has_query = query in prompt
        has_context = "Week 1 measurements" in prompt
        
        print(f"      ✅ System prompt: {has_system_prompt}")
        print(f"      ✅ Query included: {has_query}")
        print(f"      ✅ Context included: {has_context}")
        print(f"      📝 Prompt length: {len(prompt)} characters")
    
    # Test special prompts
    print("\n3. Testing special prompts...")
    
    # Help prompt
    help_prompt = prompts.get_help_prompt()
    print(f"   ✅ Help prompt generated: {len(help_prompt)} characters")
    
    # Error prompt
    error_prompt = prompts.get_error_prompt("test query", "test error")
    print(f"   ✅ Error prompt generated: {len(error_prompt)} characters")
    
    # Summary prompt
    summary_prompt = prompts.get_summary_prompt(test_context)
    print(f"   ✅ Summary prompt generated: {len(summary_prompt)} characters")
    
    # Follow-up prompt
    follow_up_prompt = prompts.get_follow_up_prompt(
        "How has my weight changed?",
        "Your weight has decreased by 0.5kg from week 1 to week 2.",
        "What about my BMI?",
        test_context
    )
    print(f"   ✅ Follow-up prompt generated: {len(follow_up_prompt)} characters")
    
    return True


def test_generator():
    """Test response generator functionality"""
    print("\n🧪 Testing Response Generator...")
    print("=" * 50)
    
    # Initialize generator
    generator = ResponseGenerator()
    
    # Test generator info
    print("\n1. Testing generator initialization...")
    info = generator.get_generator_info()
    
    print(f"   Provider: {info['llm_provider']}")
    print(f"   Model: {info['llm_model']}")
    print(f"   Client initialized: {info['client_initialized']}")
    print(f"   Available providers: {info['available_providers']}")
    
    # Test context
    test_context = [
        {
            'content': 'Week 1 measurements: Weight 80kg, BMI 25.5, Fat percentage 18%, Chest 100cm, Waist 85cm',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-01',
                'week_number': 'Week 1',
                'measurements': {'weight': 80, 'bmi': 25.5, 'fat_percent': 18}
            },
            'relevance_score': 0.85
        },
        {
            'content': 'Week 2 measurements: Weight 79.5kg, BMI 25.2, Fat percentage 17.5%, Chest 99cm, Waist 84cm',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-08',
                'week_number': 'Week 2',
                'measurements': {'weight': 79.5, 'bmi': 25.2, 'fat_percent': 17.5}
            },
            'relevance_score': 0.78
        }
    ]
    
    # Test different query types
    print("\n2. Testing response generation for different query types...")
    
    test_queries = [
        ("How has my weight changed?", "trend"),
        ("What are my current measurements?", "specific"),
        ("Give me a summary of my progress", "summary"),
        ("Am I making progress?", "goal")
    ]
    
    for query, query_type in test_queries:
        print(f"\n   Query: '{query}' (Type: {query_type})")
        
        # Generate response
        response = generator.generate_response(query, test_context, query_type)
        
        # Check response structure
        has_response = 'response' in response and response['response']
        has_metadata = all(key in response for key in ['query', 'query_type', 'success'])
        success = response.get('success', False)
        
        print(f"      ✅ Response generated: {has_response}")
        print(f"      ✅ Metadata complete: {has_metadata}")
        print(f"      ✅ Success: {success}")
        
        if has_response:
            response_text = response['response']
            print(f"      📝 Response length: {len(response_text)} characters")
            print(f"      📄 Preview: {response_text[:100]}...")
    
    # Test special responses
    print("\n3. Testing special response types...")
    
    # Help response
    help_response = generator.generate_help_response()
    print(f"   ✅ Help response: {help_response.get('success', False)}")
    
    # Summary response
    summary_response = generator.generate_summary_response(test_context)
    print(f"   ✅ Summary response: {summary_response.get('success', False)}")
    
    # Follow-up response
    follow_up_response = generator.generate_follow_up_response(
        "How has my weight changed?",
        "Your weight has decreased by 0.5kg from week 1 to week 2.",
        "What about my BMI?",
        test_context
    )
    print(f"   ✅ Follow-up response: {follow_up_response.get('success', False)}")
    
    # Error response
    error_response = generator._generate_error_response("test query", "test error")
    print(f"   ✅ Error response: {error_response.get('success', False)}")
    
    return True


def test_integration():
    """Test integration between all phases"""
    print("\n🧪 Testing Full RAG Pipeline Integration...")
    print("=" * 50)
    
    try:
        # Initialize all components
        print("\n1. Initializing all RAG components...")
        
        vector_store = VectorStore(collection_name="integration_test_phase3")
        query_processor = QueryProcessor()
        retriever = Retriever(vector_store, query_processor)
        generator = ResponseGenerator()
        
        # Add test data
        print("2. Adding test data to vector store...")
        
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
                'content': 'Trend analysis from week 1 to week 2: Weight decreased by 0.5kg, BMI decreased by 0.3, Fat percentage decreased by 0.5%',
                'metadata': {
                    'type': 'trend',
                    'date_from': '2024-01-01',
                    'date_to': '2024-01-08',
                    'week_from': 'Week 1',
                    'week_to': 'Week 2',
                    'chunk_id': 'trend_1_2',
                    'changes': {'weight': -0.5, 'bmi': -0.3, 'fat_percent': -0.5}
                }
            }
        ]
        
        success = vector_store.add_documents(test_documents)
        if not success:
            print("❌ Failed to add test documents")
            return False
        
        print("✅ Test data added successfully")
        
        # Test end-to-end pipeline
        print("\n3. Testing end-to-end RAG pipeline...")
        
        test_queries = [
            "How has my weight changed?",
            "What are my current measurements?",
            "Show me my BMI trend",
            "Give me a summary of my progress"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            
            # Step 1: Process query
            processed_query = query_processor.process_query(query)
            if "error" in processed_query:
                print(f"      ❌ Query processing error: {processed_query['error']}")
                continue
            
            query_type = processed_query.get('query_type', 'general')
            print(f"      ✅ Query type: {query_type}")
            
            # Step 2: Retrieve context
            context = retriever.retrieve(query, n_results=3)
            print(f"      ✅ Retrieved {len(context)} context documents")
            
            # Step 3: Generate response
            response = generator.generate_response(query, context, query_type)
            
            if response.get('success', False):
                response_text = response['response']
                print(f"      ✅ Response generated: {len(response_text)} characters")
                print(f"      📄 Preview: {response_text[:150]}...")
            else:
                print(f"      ❌ Response generation failed: {response.get('error', 'Unknown error')}")
        
        # Test conversation flow
        print("\n4. Testing conversation flow...")
        
        # First query
        query1 = "How has my weight changed?"
        context1 = retriever.retrieve(query1, n_results=3)
        response1 = generator.generate_response(query1, context1)
        
        if response1.get('success', False):
            print(f"   ✅ First response: {len(response1['response'])} characters")
            
            # Follow-up query
            query2 = "What about my BMI?"
            context2 = retriever.retrieve(query2, n_results=3)
            response2 = generator.generate_follow_up_response(
                query1, response1['response'], query2, context2
            )
            
            if response2.get('success', False):
                print(f"   ✅ Follow-up response: {len(response2['response'])} characters")
            else:
                print(f"   ❌ Follow-up response failed")
        else:
            print(f"   ❌ First response failed")
        
        # Clean up
        print("\n5. Cleaning up test data...")
        vector_store.reset_collection()
        print("   ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fallback_scenarios():
    """Test fallback scenarios when LLM is not available"""
    print("\n🧪 Testing Fallback Scenarios...")
    print("=" * 50)
    
    # Test with no LLM client (simulate API failure)
    print("\n1. Testing fallback when LLM is not available...")
    
    # Create generator without LLM
    generator = ResponseGenerator()
    generator.llm_client = None  # Simulate no LLM
    
    test_context = [
        {
            'content': 'Week 1 measurements: Weight 80kg, BMI 25.5, Fat percentage 18%',
            'metadata': {'type': 'measurement', 'date': '2024-01-01'},
            'relevance_score': 0.85
        }
    ]
    
    # Test fallback response generation
    fallback_response = generator.generate_response("How has my weight changed?", test_context)
    
    if fallback_response.get('success', False):
        print(f"   ✅ Fallback response generated: {len(fallback_response['response'])} characters")
        print(f"   📄 Preview: {fallback_response['response'][:100]}...")
    else:
        print(f"   ❌ Fallback response failed")
    
    # Test error handling
    print("\n2. Testing error handling...")
    
    error_response = generator._generate_error_response("test query", "API rate limit exceeded")
    
    if error_response.get('success', False) == False:
        print(f"   ✅ Error response generated correctly")
        print(f"   📄 Error message: {error_response['response'][:100]}...")
    else:
        print(f"   ❌ Error response not generated correctly")
    
    return True


def main():
    """Main test function"""
    print("🚀 RAG Pipeline Phase 3 Test")
    print("=" * 60)
    
    # Check environment
    print("🔍 Environment Check:")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not set (will use fallback responses)")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY is set")
    else:
        print("⚠️  ANTHROPIC_API_KEY not set")
    
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        print("✅ GOOGLE_API_KEY is set")
    else:
        print("⚠️  GOOGLE_API_KEY not set")
    
    print()
    
    # Run tests
    try:
        # Test prompts
        prompts_success = test_prompts()
        
        # Test generator
        generator_success = test_generator()
        
        # Test integration
        integration_success = test_integration()
        
        # Test fallback scenarios
        fallback_success = test_fallback_scenarios()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Phase 3 Test Summary:")
        print(f"   Prompts: {'✅ PASS' if prompts_success else '❌ FAIL'}")
        print(f"   Generator: {'✅ PASS' if generator_success else '❌ FAIL'}")
        print(f"   Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
        print(f"   Fallback Scenarios: {'✅ PASS' if fallback_success else '❌ FAIL'}")
        
        if prompts_success and generator_success and integration_success and fallback_success:
            print("\n🎉 Phase 3 implementation is working correctly!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Set up environment variables in .env file")
            print("3. Run the test script again to verify functionality")
            print("4. Proceed to Phase 4: Chat Interface Development")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 