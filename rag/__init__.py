"""
RAG Pipeline for Fitness Data
Retrieval-Augmented Generation system for fitness measurement data
"""

__version__ = "1.0.0"
__author__ = "Fitness Reporting System"

from .data_preparation import DataPreparation
from .vector_store import VectorStore
from .query_processor import QueryProcessor
from .retriever import Retriever
from .prompts import FitnessPrompts
from .generator import ResponseGenerator
from .chat_interface import ChatInterface, Message, Conversation
from .web_interface import WebInterface
from .analytics import FitnessAnalytics, TrendAnalysis, GoalAnalysis, InsightReport
from .cache import CacheManager, ResponseCache, VectorSearchCache, EmbeddingCache, CacheEntry
from .optimization import RAGOptimizer, PerformanceMonitor, BatchProcessor, VectorSearchOptimizer, LoadBalancer
from .integration import RAGAgent, SystemIntegrator, DataSynchronizer, IntegrationConfig, SystemStatus
from .config import RAGPipelineConfig, ConfigManager, get_config, create_deployment_config

__all__ = [
    "DataPreparation",
    "VectorStore",
    "QueryProcessor", 
    "Retriever",
    "FitnessPrompts",
    "ResponseGenerator",
    "ChatInterface",
    "Message",
    "Conversation",
    "WebInterface",
    "FitnessAnalytics",
    "TrendAnalysis",
    "GoalAnalysis",
    "InsightReport",
    "CacheManager",
    "ResponseCache",
    "VectorSearchCache",
    "EmbeddingCache",
    "CacheEntry",
    "RAGOptimizer",
    "PerformanceMonitor",
    "BatchProcessor",
    "VectorSearchOptimizer",
    "LoadBalancer",
    "RAGAgent",
    "SystemIntegrator",
    "DataSynchronizer",
    "IntegrationConfig",
    "SystemStatus",
    "RAGPipelineConfig",
    "ConfigManager",
    "get_config",
    "create_deployment_config"
] 