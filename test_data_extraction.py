#!/usr/bin/env python3
"""
Test script to verify data extraction and storage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.query_processor import QueryProcessor
from rag.generator import ResponseGenerator

def test_data_extraction():
    """Test data extraction and retrieval"""
    
    print("🧪 Testing Data Extraction and Retrieval")
    print("=" * 50)
    
    try:
        # Initialize components
        print("📚 Initializing vector store...")
        vector_store = VectorStore()
        
        print("🔍 Initializing query processor...")
        query_processor = QueryProcessor()
        
        print("📖 Initializing retriever...")
        retriever = Retriever(vector_store, query_processor)
        
        print("✍️ Initializing response generator...")
        generator = ResponseGenerator(vector_store, query_processor, retriever)
        
        # Test simple queries
        test_queries = [
            "what is my current weight?",
            "what was my weight in the start?",
            "weight",
            "current weight"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            # Test retrieval
            context = retriever.retrieve(query, n_results=5)
            print(f"   📊 Retrieved {len(context)} context items")
            
            if context:
                print(f"   📄 First context item: {context[0].get('content', '')[:200]}...")
                print(f"   🏷️ Metadata: {context[0].get('metadata', {})}")
            else:
                print("   ❌ No context retrieved")
            
            # Test analytics
            analytics_data = generator._perform_analytics(query, context, "specific")
            print(f"   📈 Analytics data summary: {analytics_data.get('data_summary', {})}")
            
            if analytics_data.get('warnings'):
                print(f"   ⚠️ Analytics warnings: {analytics_data['warnings']}")
        
        print("\n✅ Data extraction test completed")
        
    except Exception as e:
        print(f"❌ Error in data extraction test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_extraction() 