"""
Embedding Utilities for RAG Pipeline
Handles different embedding models and providers
"""

import os
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import openai
from config.environment import env_config


class EmbeddingManager:
    """Manages different embedding models and providers"""
    
    def __init__(self, provider: str = "openai", model: str = "text-embedding-ada-002"):
        """
        Initialize embedding manager
        
        Args:
            provider: Embedding provider ('openai', 'sentence-transformers', 'local')
            model: Model name for the provider
        """
        self.provider = provider.lower()
        self.model_name = model
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model based on provider"""
        try:
            if self.provider == "openai":
                # OpenAI embeddings
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("⚠️ OPENAI_API_KEY not found, falling back to sentence-transformers")
                    raise ValueError("OPENAI_API_KEY not found in environment")
                self.model = "openai"  # Just mark as OpenAI, we'll handle the client in _get_openai_embeddings
                
            elif self.provider == "sentence-transformers":
                # Local sentence transformers - use a proper model name
                if self.model_name == "text-embedding-ada-002":
                    # Use a compatible sentence-transformers model
                    self.model = SentenceTransformer('all-MiniLM-L6-v2')
                else:
                    self.model = SentenceTransformer(self.model_name)
                
            elif self.provider == "local":
                # Local embeddings (using sentence-transformers as default)
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                
            else:
                raise ValueError(f"Unsupported embedding provider: {self.provider}")
                
            print(f"✅ Initialized {self.provider} embedding model: {self.model_name}")
            
        except Exception as e:
            print(f"❌ Error initializing embedding model: {e}")
            # Fallback to sentence-transformers
            print("🔄 Falling back to sentence-transformers...")
            self.provider = "sentence-transformers"
            self.model_name = "all-MiniLM-L6-v2"
            self.model = SentenceTransformer(self.model_name)
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if self.provider == "openai":
                return self._get_openai_embeddings(texts)
            else:
                return self._get_local_embeddings(texts)
                
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            return []
    
    def _get_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.embeddings.create(
                input=texts,
                model=self.model_name
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"❌ OpenAI embedding error: {e}")
            return []
    
    def _get_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model"""
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings
        except Exception as e:
            print(f"❌ Local embedding error: {e}")
            return []
    
    def get_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        try:
            if self.provider == "openai":
                # OpenAI ada-002 has 1536 dimensions
                return 1536 if "ada-002" in self.model_name else 1536
            else:
                # Get dimension from model
                test_embedding = self.get_single_embedding("test")
                return len(test_embedding)
        except Exception as e:
            print(f"❌ Error getting embedding dimension: {e}")
            return 384  # Default for many sentence-transformers models
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Normalize vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            print(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def batch_similarity(self, query_embedding: List[float], 
                        document_embeddings: List[List[float]]) -> List[float]:
        """
        Calculate similarities between query and multiple documents
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: List of document embedding vectors
            
        Returns:
            List of similarity scores
        """
        try:
            similarities = []
            for doc_embedding in document_embeddings:
                sim = self.similarity(query_embedding, doc_embedding)
                similarities.append(sim)
            return similarities
            
        except Exception as e:
            print(f"❌ Error calculating batch similarity: {e}")
            return [0.0] * len(document_embeddings) 