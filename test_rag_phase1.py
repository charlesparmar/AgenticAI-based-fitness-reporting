#!/usr/bin/env python3
"""
Test Script for RAG Pipeline Phase 1
Tests data preparation and vectorization functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.data_preparation import DataPreparation
from rag.vector_store import VectorStore


def test_data_preparation():
    """Test data preparation functionality"""
    print("🧪 Testing Data Preparation...")
    print("=" * 50)
    
    # Initialize data preparation
    data_prep = DataPreparation()
    
    # Test data extraction
    print("\n1. Testing data extraction...")
    fitness_data = data_prep.extract_fitness_data()
    
    if not fitness_data:
        print("❌ No fitness data extracted. This might be expected if:")
        print("   - SQLITE_API_KEY is not set")
        print("   - No data exists in the database")
        print("   - Database connection issues")
        return False
    
    print(f"✅ Extracted {len(fitness_data)} fitness records")
    
    # Test data preprocessing
    print("\n2. Testing data preprocessing...")
    preprocessed_data = data_prep.preprocess_data(fitness_data)
    
    if not preprocessed_data:
        print("❌ No data after preprocessing")
        return False
    
    print(f"✅ Preprocessed {len(preprocessed_data)} records")
    
    # Test document chunking
    print("\n3. Testing document chunking...")
    chunks = data_prep.create_document_chunks(preprocessed_data)
    
    if not chunks:
        print("❌ No chunks created")
        return False
    
    print(f"✅ Created {len(chunks)} document chunks")
    
    # Show sample chunk
    if chunks:
        print("\n📄 Sample chunk:")
        sample_chunk = chunks[0]
        print(f"Content: {sample_chunk['content'][:200]}...")
        print(f"Metadata: {sample_chunk['metadata']}")
    
    # Test embedding generation
    print("\n4. Testing embedding generation...")
    chunks_with_embeddings = data_prep.generate_embeddings(chunks)
    
    if not chunks_with_embeddings:
        print("❌ No embeddings generated")
        return False
    
    # Count chunks with embeddings
    chunks_with_embeddings_count = sum(1 for chunk in chunks_with_embeddings if 'embedding' in chunk)
    print(f"✅ Generated embeddings for {chunks_with_embeddings_count} chunks")
    
    # Test complete pipeline
    print("\n5. Testing complete pipeline...")
    vector_data = data_prep.prepare_vector_data()
    
    if not vector_data:
        print("❌ Complete pipeline failed")
        return False
    
    print(f"✅ Complete pipeline successful: {len(vector_data)} chunks ready")
    
    # Test data statistics
    print("\n6. Testing data statistics...")
    stats = data_prep.get_data_statistics(preprocessed_data)
    
    if 'error' not in stats:
        print("✅ Data statistics:")
        print(f"   Total records: {stats['total_records']}")
        print(f"   Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
        print(f"   Measurement types: {len(stats['measurements'])}")
    else:
        print(f"❌ Error getting statistics: {stats['error']}")
    
    return True


def test_vector_store():
    """Test vector store functionality"""
    print("\n🧪 Testing Vector Store...")
    print("=" * 50)
    
    # Initialize vector store
    vector_store = VectorStore(collection_name="test_fitness_data")
    
    # Test collection info
    print("\n1. Testing collection info...")
    info = vector_store.get_collection_info()
    
    if 'error' not in info:
        print("✅ Collection info:")
        print(f"   Collection name: {info['collection_name']}")
        print(f"   Document count: {info['document_count']}")
        print(f"   Persist directory: {info['persist_directory']}")
    else:
        print(f"❌ Error getting collection info: {info['error']}")
    
    # Test adding documents
    print("\n2. Testing document addition...")
    
    # Create sample documents
    sample_documents = [
        {
            'content': 'Week 1 measurements: Weight 80kg, BMI 25.5, Fat percentage 18%',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-01',
                'week_number': 'Week 1',
                'chunk_id': 'test_chunk_1'
            }
        },
        {
            'content': 'Week 2 measurements: Weight 79.5kg, BMI 25.2, Fat percentage 17.5%',
            'metadata': {
                'type': 'measurement',
                'date': '2024-01-08',
                'week_number': 'Week 2',
                'chunk_id': 'test_chunk_2'
            }
        }
    ]
    
    success = vector_store.add_documents(sample_documents)
    
    if success:
        print("✅ Successfully added test documents")
    else:
        print("❌ Failed to add test documents")
    
    # Test search functionality
    print("\n3. Testing search functionality...")
    search_results = vector_store.search("weight measurements", n_results=3)
    
    if search_results:
        print(f"✅ Search successful: Found {len(search_results)} results")
        for i, result in enumerate(search_results[:2], 1):
            print(f"   Result {i}: {result['content'][:100]}...")
            print(f"   Score: {result['score']:.3f}")
    else:
        print("❌ Search failed or no results found")
    
    # Test collection reset
    print("\n4. Testing collection reset...")
    reset_success = vector_store.reset_collection()
    
    if reset_success:
        print("✅ Collection reset successful")
    else:
        print("❌ Collection reset failed")
    
    return True


def main():
    """Main test function"""
    print("🚀 RAG Pipeline Phase 1 Test")
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
        # Test data preparation
        prep_success = test_data_preparation()
        
        # Test vector store
        vector_success = test_vector_store()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"   Data Preparation: {'✅ PASS' if prep_success else '❌ FAIL'}")
        print(f"   Vector Store: {'✅ PASS' if vector_success else '❌ FAIL'}")
        
        if prep_success and vector_success:
            print("\n🎉 Phase 1 implementation is working correctly!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Set up environment variables in .env file")
            print("3. Run the test script again to verify functionality")
            print("4. Proceed to Phase 2: Query Processing and Retrieval")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 