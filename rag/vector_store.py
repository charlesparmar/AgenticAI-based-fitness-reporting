"""
Vector Store Module for RAG Pipeline
Handles ChromaDB operations for storing and retrieving fitness data embeddings
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from .utils.embeddings import EmbeddingManager


class VectorStore:
    """Manages vector database operations for fitness data"""
    
    def __init__(self, collection_name: str = "fitness_data", 
                 persist_directory: str = "./chroma_db"):
        """
        Initialize vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist ChromaDB data
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_manager = EmbeddingManager()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=self._get_embedding_function()
                )
                print(f"✅ Connected to existing collection: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self._get_embedding_function(),
                    metadata={"description": "Fitness measurement data embeddings"}
                )
                print(f"✅ Created new collection: {self.collection_name}")
            
        except Exception as e:
            print(f"❌ Error initializing vector store: {e}")
            self.client = None
            self.collection = None
    
    def _get_embedding_function(self):
        """Get embedding function for ChromaDB"""
        try:
            # Use sentence-transformers as default
            import chromadb.utils.embedding_functions as embedding_functions
            
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        except Exception as e:
            print(f"❌ Error creating embedding function: {e}")
            # Return None to use default embedding function
            return None
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of document chunks with embeddings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.collection:
                print("❌ Vector store not initialized")
                return False
            
            if not chunks:
                print("❌ No chunks to add")
                return False
            
            print(f"🔄 Adding {len(chunks)} documents to vector store...")
            
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                # Extract content
                content = chunk.get('content', '')
                if not content:
                    continue
                
                # Extract metadata
                metadata = chunk.get('metadata', {})
                
                # Create unique ID
                chunk_id = metadata.get('chunk_id', f"chunk_{i}")
                
                documents.append(content)
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            if not documents:
                print("❌ No valid documents to add")
                return False
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Successfully added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            print(f"❌ Error adding documents to vector store: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5, 
               filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of search results with content, metadata, and scores
        """
        try:
            if not self.collection:
                print("❌ Vector store not initialized")
                return []
            
            if not query.strip():
                print("❌ Empty query")
                return []
            
            print(f"🔍 Searching for: '{query}'")
            
            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_dict
            )
            
            # Format results
            formatted_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'score': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0,
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else f"result_{i}"
                    }
                    formatted_results.append(result)
            
            print(f"✅ Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching vector store: {e}")
            return []
    
    def search_by_embedding(self, embedding: List[float], n_results: int = 5,
                          filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search using a pre-computed embedding
        
        Args:
            embedding: Query embedding vector
            n_results: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of search results
        """
        try:
            if not self.collection:
                print("❌ Vector store not initialized")
                return []
            
            if not embedding:
                print("❌ Empty embedding")
                return []
            
            # Perform search with embedding
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=filter_dict
            )
            
            # Format results
            formatted_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'score': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0,
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else f"result_{i}"
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching by embedding: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection
        
        Returns:
            Dictionary with collection information
        """
        try:
            if not self.collection:
                return {"error": "Vector store not initialized"}
            
            # Get collection count
            count = self.collection.count()
            
            # Get collection metadata
            metadata = self.collection.metadata or {}
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "metadata": metadata,
                "persist_directory": self.persist_directory
            }
            
        except Exception as e:
            print(f"❌ Error getting collection info: {e}")
            return {"error": str(e)}
    
    def delete_collection(self) -> bool:
        """
        Delete the current collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                print("❌ Client not initialized")
                return False
            
            # Delete collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
            
            print(f"✅ Deleted collection: {self.collection_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting collection: {e}")
            return False
    
    def reset_collection(self) -> bool:
        """
        Reset the collection (delete and recreate)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🔄 Resetting collection: {self.collection_name}")
            
            # Delete existing collection
            if self.collection:
                self.delete_collection()
            
            # Recreate collection
            self._initialize_client()
            
            return self.collection is not None
            
        except Exception as e:
            print(f"❌ Error resetting collection: {e}")
            return False
    
    def update_document(self, doc_id: str, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Update a specific document
        
        Args:
            doc_id: Document ID to update
            content: New content
            metadata: New metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.collection:
                print("❌ Vector store not initialized")
                return False
            
            # Update document
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata]
            )
            
            print(f"✅ Updated document: {doc_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating document: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a specific document
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.collection:
                print("❌ Vector store not initialized")
                return False
            
            # Delete document
            self.collection.delete(ids=[doc_id])
            
            print(f"✅ Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            if not self.collection:
                print("❌ Vector store not initialized")
                return None
            
            # Get document
            results = self.collection.get(ids=[doc_id])
            
            if results['documents'] and results['documents'][0]:
                return {
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0] if results['metadatas'] and results['metadatas'][0] else {},
                    'id': doc_id
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting document: {e}")
            return None 