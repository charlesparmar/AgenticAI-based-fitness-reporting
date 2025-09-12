#!/usr/bin/env python3
"""
RAG System Test Script
Tests all components of the RAG pipeline to ensure everything is properly configured
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    try:
        import chromadb
        print(f"   ✅ ChromaDB {chromadb.__version__}")
    except ImportError as e:
        print(f"   ❌ ChromaDB import failed: {e}")
        return False
    
    try:
        import sentence_transformers
        print(f"   ✅ Sentence Transformers {sentence_transformers.__version__}")
    except ImportError as e:
        print(f"   ❌ Sentence Transformers import failed: {e}")
        return False
    
    try:
        import flask
        print(f"   ✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"   ❌ Flask import failed: {e}")
        return False
    
    try:
        import numpy
        print(f"   ✅ NumPy {numpy.__version__}")
    except ImportError as e:
        print(f"   ❌ NumPy import failed: {e}")
        return False
    
    try:
        import sklearn
        print(f"   ✅ Scikit-learn {sklearn.__version__}")
    except ImportError as e:
        print(f"   ❌ Scikit-learn import failed: {e}")
        return False
    
    return True

def test_rag_modules():
    """Test that all RAG modules can be imported"""
    print("\n🔍 Testing RAG module imports...")
    
    try:
        from rag.config import get_config
        print("   ✅ RAG config module")
    except ImportError as e:
        print(f"   ❌ RAG config import failed: {e}")
        return False
    
    try:
        from rag.vector_store import VectorStore
        print("   ✅ RAG vector store module")
    except ImportError as e:
        print(f"   ❌ RAG vector store import failed: {e}")
        return False
    
    try:
        from rag.data_preparation import DataPreparation
        print("   ✅ RAG data preparation module")
    except ImportError as e:
        print(f"   ❌ RAG data preparation import failed: {e}")
        return False
    
    try:
        from rag.query_processor import QueryProcessor
        print("   ✅ RAG query processor module")
    except ImportError as e:
        print(f"   ❌ RAG query processor import failed: {e}")
        return False
    
    try:
        from rag.retriever import Retriever
        print("   ✅ RAG retriever module")
    except ImportError as e:
        print(f"   ❌ RAG retriever import failed: {e}")
        return False
    
    try:
        from rag.generator import ResponseGenerator
        print("   ✅ RAG generator module")
    except ImportError as e:
        print(f"   ❌ RAG generator import failed: {e}")
        return False
    
    try:
        from rag.chat_interface import ChatInterface
        print("   ✅ RAG chat interface module")
    except ImportError as e:
        print(f"   ❌ RAG chat interface import failed: {e}")
        return False
    
    try:
        from rag.web_interface import WebInterface
        print("   ✅ RAG web interface module")
    except ImportError as e:
        print(f"   ❌ RAG web interface import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from rag.config import get_config
        config = get_config()
        print("   ✅ Configuration loaded successfully")
        print(f"   📋 Vector store type: {config.vector_store.type}")
        print(f"   📋 LLM provider: {config.llm.provider}")
        print(f"   📋 Web interface enabled: {config.web_interface.enabled}")
        return True
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_directories():
    """Test that required directories exist"""
    print("\n🔍 Testing directory structure...")
    
    required_dirs = [
        "logs",
        "templates", 
        "static",
        "chroma_db"
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/ directory exists")
        else:
            print(f"   ❌ {dir_name}/ directory missing")
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"   ✅ Created {dir_name}/ directory")
            except Exception as e:
                print(f"   ❌ Failed to create {dir_name}/ directory: {e}")
                return False
    
    return True

def test_vector_store():
    """Test vector store initialization"""
    print("\n🔍 Testing vector store...")
    
    try:
        from rag.vector_store import VectorStore
        vector_store = VectorStore()
        print("   ✅ Vector store initialized successfully")
        
        # Test collection info
        info = vector_store.get_collection_info()
        print(f"   📋 Collection count: {info.get('count', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"   ❌ Vector store test failed: {e}")
        return False

def test_embedding_model():
    """Test embedding model"""
    print("\n🔍 Testing embedding model...")
    
    try:
        from rag.utils.embeddings import EmbeddingManager
        embedding_manager = EmbeddingManager()
        print("   ✅ Embedding manager initialized")
        
        # Test embedding generation
        test_texts = ["Hello world", "Fitness data"]
        embeddings = embedding_manager.get_embeddings(test_texts)
        if embeddings and len(embeddings) == 2:
            print(f"   ✅ Generated {len(embeddings)} embeddings")
            print(f"   📋 Embedding dimension: {len(embeddings[0])}")
        else:
            print("   ❌ Failed to generate embeddings")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ Embedding model test failed: {e}")
        return False

def test_web_interface():
    """Test web interface initialization"""
    print("\n🔍 Testing web interface...")
    
    try:
        from rag.web_interface import WebInterface
        web_interface = WebInterface()
        print("   ✅ Web interface initialized successfully")
        
        # Test template creation
        web_interface.create_templates()
        print("   ✅ Templates created successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ Web interface test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 RAG System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("RAG Modules", test_rag_modules),
        ("Configuration", test_configuration),
        ("Directories", test_directories),
        ("Vector Store", test_vector_store),
        ("Embedding Model", test_embedding_model),
        ("Web Interface", test_web_interface),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ❌ {test_name} test failed")
        except Exception as e:
            print(f"   ❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RAG system is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Set up your .env file with required API keys")
        print("   2. Run: python3 test_rag_phase1.py (Data preparation)")
        print("   3. Run: python3 test_rag_phase2.py (Query processing)")
        print("   4. Run: python3 test_rag_phase3.py (LLM integration)")
        print("   5. Run: python3 test_rag_phase4.py (Web interface)")
        print("   6. Run: python3 test_rag_phase5.py (Advanced features)")
        print("   7. Run: python3 test_rag_phase6.py (Integration)")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 