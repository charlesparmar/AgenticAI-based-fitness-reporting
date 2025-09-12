#!/usr/bin/env python3
"""
RAG System Runner
Main script to run the RAG fitness chat system
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function to run the RAG system"""
    
    print("🚀 Starting RAG Fitness Chat System")
    print("=" * 50)
    
    try:
        # Import required modules
        print("📦 Loading RAG modules...")
        
        from rag.web_interface import WebInterface
        from rag.vector_store import VectorStore
        from rag.chat_interface import ChatInterface
        from rag.query_processor import QueryProcessor
        from rag.retriever import Retriever
        from rag.generator import ResponseGenerator
        from rag.data_preparation import DataPreparation
        
        print("✅ All modules loaded successfully")
        
        # Initialize components
        print("\n🔧 Initializing RAG components...")
        
        # Initialize vector store
        print("   📚 Initializing vector store...")
        vector_store = VectorStore()
        
        # Initialize query processor
        print("   🔍 Initializing query processor...")
        query_processor = QueryProcessor()
        
        # Initialize retriever
        print("   📖 Initializing retriever...")
        retriever = Retriever(vector_store, query_processor)
        
        # Initialize response generator
        print("   ✍️  Initializing response generator...")
        generator = ResponseGenerator()
        
        # Initialize chat interface
        print("   💬 Initializing chat interface...")
        chat_interface = ChatInterface(vector_store, query_processor, retriever, generator)
        
        # Initialize data preparation
        print("   📊 Initializing data preparation...")
        data_prep = DataPreparation()
        
        print("✅ All components initialized successfully")
        
        # Prepare vector data if needed
        print("\n📊 Preparing vector data...")
        try:
            chunks = data_prep.prepare_vector_data()
            if chunks:
                print(f"✅ Prepared {len(chunks)} data chunks")
                
                # Add to vector store
                print("   📚 Adding data to vector store...")
                vector_store.add_documents(chunks)
                print("✅ Data added to vector store")
            else:
                print("⚠️  No data chunks prepared - continuing with empty vector store")
        except Exception as e:
            print(f"⚠️  Data preparation warning: {e}")
            print("   Continuing with existing vector store data...")
        
        # Initialize web interface
        print("\n🌐 Initializing web interface...")
        web_interface = WebInterface(
            vector_store=vector_store,
            chat_interface=chat_interface,
            host="0.0.0.0",
            port=8080
        )
        
        print("✅ Web interface initialized successfully")
        
        # Display system information
        print("\n📋 System Information:")
        print(f"   🌐 Web Interface: http://localhost:8080")
        print(f"   📚 Vector Store: {type(vector_store).__name__}")
        print(f"   💬 Chat Interface: {type(chat_interface).__name__}")
        print(f"   🔍 Query Processor: {type(query_processor).__name__}")
        print(f"   📖 Retriever: {type(retriever).__name__}")
        print(f"   ✍️  Generator: {type(generator).__name__}")
        
        print("\n🎉 RAG System is ready!")
        print("=" * 50)
        print("🌐 Open your browser and go to: http://localhost:8080")
        print("💬 Start chatting with your fitness data!")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run the web interface
        web_interface.run(debug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ Error starting RAG system: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 