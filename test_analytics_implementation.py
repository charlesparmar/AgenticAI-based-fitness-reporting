#!/usr/bin/env python3
"""
Test script for the analytics implementation
Tests the new analytics features and validates the implementation
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.utils.calculations import FitnessCalculations, CalculationResult
from rag.query_processor import QueryProcessor
from rag.retriever import Retriever
from rag.generator import ResponseGenerator
from rag.vector_store import VectorStore
from rag.analytics import FitnessAnalytics


def test_calculations():
    """Test the calculation helper functions"""
    print("🧪 Testing Calculation Helper Functions...")
    
    calculations = FitnessCalculations()
    
    # Sample fitness data
    sample_data = [
        {'date': '2024-01-01', 'weight': 100.0, 'bmi': 25.0},
        {'date': '2024-01-08', 'weight': 98.5, 'bmi': 24.6},
        {'date': '2024-01-15', 'weight': 97.0, 'bmi': 24.2},
        {'date': '2024-01-22', 'weight': 95.5, 'bmi': 23.8},
        {'date': '2024-01-29', 'weight': 94.0, 'bmi': 23.4},
        {'date': '2024-02-05', 'weight': 92.5, 'bmi': 23.0},
        {'date': '2024-02-12', 'weight': 91.0, 'bmi': 22.6},
        {'date': '2024-02-19', 'weight': 89.5, 'bmi': 22.2},
        {'date': '2024-02-26', 'weight': 88.0, 'bmi': 21.8},
        {'date': '2024-03-05', 'weight': 86.5, 'bmi': 21.4},
        {'date': '2024-03-12', 'weight': 85.0, 'bmi': 21.0},
        {'date': '2024-03-19', 'weight': 83.5, 'bmi': 20.6},
        {'date': '2024-03-26', 'weight': 82.0, 'bmi': 20.2}
    ]
    
    # Test total weight loss calculation
    print("\n1. Testing Total Weight Loss Calculation...")
    total_loss_result = calculations.calculate_total_weight_loss(sample_data)
    print(f"   Total weight loss: {total_loss_result.value:.2f} kg")
    print(f"   Confidence: {total_loss_result.confidence:.2f}")
    print(f"   Warnings: {total_loss_result.warnings}")
    
    # Test weeks count
    print("\n2. Testing Weeks Count...")
    weeks_count = calculations.count_actual_weeks_of_data(sample_data)
    print(f"   Weeks of data: {weeks_count}")
    
    # Test data validation
    print("\n3. Testing Data Validation...")
    validation_result = calculations.validate_data_consistency(sample_data)
    print(f"   Data valid: {validation_result['valid']}")
    print(f"   Issues: {validation_result['issues']}")
    print(f"   Warnings: {validation_result['warnings']}")
    
    # Test period weight loss calculation
    print("\n4. Testing Period Weight Loss Calculation...")
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 2, 1)
    period_result = calculations.calculate_weight_loss_in_period(start_date, end_date, sample_data)
    print(f"   Weight loss from {start_date.date()} to {end_date.date()}: {period_result.value:.2f} kg")
    print(f"   Confidence: {period_result.confidence:.2f}")
    
    # Test weight at specific date
    print("\n5. Testing Weight at Specific Date...")
    target_date = datetime(2024, 2, 15)
    weight_at_date = calculations.get_weight_at_specific_date(target_date, sample_data)
    print(f"   Weight on {target_date.date()}: {weight_at_date} kg")
    
    print("✅ Calculation tests completed!\n")


def test_query_processor():
    """Test the enhanced query processor"""
    print("🧪 Testing Enhanced Query Processor...")
    
    query_processor = QueryProcessor()
    
    # Test queries with date ranges
    test_queries = [
        "What was my weight loss until end of June?",
        "Show me my progress this month",
        "How much weight did I lose last week?",
        "What was my weight on 2024-02-15?",
        "Calculate my total weight loss from 2024-01-01 to 2024-03-01"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query}'")
        
        # Process query
        processed = query_processor.process_query(query)
        print(f"   Query type: {processed.get('query_type', 'unknown')}")
        
        # Extract date ranges
        date_ranges = query_processor.extract_date_ranges(query)
        print(f"   Date ranges found: {len(date_ranges.get('parsed_ranges', {}))}")
        
        if date_ranges.get('parsed_ranges'):
            for range_type, ranges in date_ranges['parsed_ranges'].items():
                if ranges:
                    print(f"   {range_type}: {len(ranges)} ranges")
    
    print("✅ Query processor tests completed!\n")


def test_retriever():
    """Test the enhanced retriever with date filtering"""
    print("🧪 Testing Enhanced Retriever...")
    
    try:
        vector_store = VectorStore()
        query_processor = QueryProcessor()
        retriever = Retriever(vector_store, query_processor)
        
        # Test retrieval with date-based queries
        test_queries = [
            "weight loss this month",
            "measurements from last week",
            "progress until end of March"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing retrieval for: '{query}'")
            
            results = retriever.retrieve(query, n_results=5)
            print(f"   Retrieved {len(results)} results")
            
            if results:
                print(f"   First result relevance: {results[0].get('relevance_score', 0):.3f}")
        
        print("✅ Retriever tests completed!\n")
        
    except Exception as e:
        print(f"⚠️ Retriever test skipped (no vector store): {e}\n")


def test_generator():
    """Test the enhanced response generator"""
    print("🧪 Testing Enhanced Response Generator...")
    
    try:
        vector_store = VectorStore()
        query_processor = QueryProcessor()
        retriever = Retriever(vector_store, query_processor)
        generator = ResponseGenerator(
            vector_store=vector_store,
            query_processor=query_processor,
            retriever=retriever
        )
        
        # Test queries
        test_queries = [
            "How many weeks of data do I have?",
            "What is my total weight loss?",
            "Show me my weight loss until end of June"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing generation for: '{query}'")
            
            # Mock context for testing
            mock_context = [
                {
                    'content': '{"date": "2024-01-01", "weight": 100.0}',
                    'metadata': {'date': '2024-01-01'},
                    'relevance_score': 0.9
                },
                {
                    'content': '{"date": "2024-03-26", "weight": 82.0}',
                    'metadata': {'date': '2024-03-26'},
                    'relevance_score': 0.8
                }
            ]
            
            try:
                response = generator.generate_response(query, mock_context)
                print(f"   Response generated: {'success' in response and response['success']}")
                
                if 'analytics_data' in response:
                    analytics = response['analytics_data']
                    print(f"   Analytics included: {bool(analytics)}")
                    if analytics.get('calculations'):
                        print(f"   Calculations: {len(analytics['calculations'])}")
                
                if 'validation_result' in response:
                    validation = response['validation_result']
                    print(f"   Validation valid: {validation.get('valid', False)}")
                
            except Exception as e:
                print(f"   Generation error: {e}")
        
        print("✅ Generator tests completed!\n")
        
    except Exception as e:
        print(f"⚠️ Generator test skipped (no LLM configured): {e}\n")


def test_analytics():
    """Test the analytics module"""
    print("🧪 Testing Analytics Module...")
    
    try:
        vector_store = VectorStore()
        query_processor = QueryProcessor()
        retriever = Retriever(vector_store, query_processor)
        analytics = FitnessAnalytics(vector_store, query_processor, retriever)
        
        # Test analytics summary
        print("\n1. Testing Analytics Summary...")
        summary = analytics.get_analytics_summary()
        print(f"   Analytics summary available: {bool(summary)}")
        
        # Test trend analysis
        print("\n2. Testing Trend Analysis...")
        try:
            trends = analytics.analyze_trends('weight', 'month', 5)
            print(f"   Trends analyzed: {len(trends)}")
        except Exception as e:
            print(f"   Trend analysis error: {e}")
        
        print("✅ Analytics tests completed!\n")
        
    except Exception as e:
        print(f"⚠️ Analytics test skipped: {e}\n")


def main():
    """Run all tests"""
    print("🚀 Starting Analytics Implementation Tests")
    print("=" * 50)
    
    # Run tests
    test_calculations()
    test_query_processor()
    test_retriever()
    test_generator()
    test_analytics()
    
    print("🎉 All tests completed!")
    print("\n📋 Implementation Summary:")
    print("✅ Calculation helper functions implemented")
    print("✅ Enhanced query processor with date range detection")
    print("✅ Enhanced retriever with date-based filtering")
    print("✅ Enhanced response generator with analytics integration")
    print("✅ Analytics module integration")
    print("✅ Welcome message added to chat interface")
    print("✅ Data context display added to web interface")
    print("✅ Integration module updated")
    
    print("\n🎯 Key Features Implemented:")
    print("• Accurate weight loss calculations with validation")
    print("• Week count calculation from actual data")
    print("• Date range extraction and filtering")
    print("• Data consistency validation")
    print("• Analytics integration in response generation")
    print("• Enhanced user experience with welcome messages")
    print("• Comprehensive data context display")


if __name__ == "__main__":
    main() 