"""
Configuration Module for RAG Pipeline
Environment-specific configurations and deployment settings
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5000
    username: str = ""
    password: str = ""
    database: str = "fitness_data"
    ssl_mode: str = "disable"
    connection_timeout: int = 30
    max_connections: int = 10


@dataclass
class VectorStoreConfig:
    """Vector store configuration"""
    type: str = "chromadb"  # chromadb, pinecone, faiss
    collection_name: str = "fitness_embeddings"
    persist_directory: str = "./chroma_db"
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimension: int = 1536
    similarity_metric: str = "cosine"
    max_results: int = 20
    similarity_threshold: float = 0.7


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "openai"  # openai, anthropic, google
    model: str = "gpt-3.5-turbo"
    api_key: str = ""
    api_base: str = ""
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1


@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    response_cache_size: int = 1000
    vector_cache_size: int = 500
    embedding_cache_size: int = 2000
    response_ttl: int = 3600
    vector_ttl: int = 1800
    embedding_ttl: int = 7200
    persistence_enabled: bool = True
    persistence_file: str = "./cache_state.json"


@dataclass
class OptimizationConfig:
    """Optimization configuration"""
    enabled: bool = True
    max_concurrent_requests: int = 10
    batch_size: int = 10
    max_workers: int = 4
    performance_monitoring: bool = True
    max_metrics: int = 10000
    cleanup_interval_hours: int = 24


@dataclass
class WebInterfaceConfig:
    """Web interface configuration"""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    secret_key: str = "dev-secret-key"
    cors_enabled: bool = True
    cors_origins: List[str] = None
    static_folder: str = "./static"
    template_folder: str = "./templates"


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    log_level: str = "INFO"
    log_file: str = "./logs/rag_pipeline.log"
    metrics_enabled: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 60
    alerting_enabled: bool = False
    alert_webhook: str = ""


@dataclass
class SecurityConfig:
    """Security configuration"""
    authentication_enabled: bool = False
    jwt_secret: str = ""
    jwt_expiration_hours: int = 24
    rate_limiting_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    cors_origins: List[str] = None


@dataclass
class RAGPipelineConfig:
    """Main RAG pipeline configuration"""
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Core components
    database: DatabaseConfig = None
    vector_store: VectorStoreConfig = None
    llm: LLMConfig = None
    
    # Advanced features
    cache: CacheConfig = None
    optimization: OptimizationConfig = None
    web_interface: WebInterfaceConfig = None
    
    # System features
    monitoring: MonitoringConfig = None
    security: SecurityConfig = None
    
    # Integration
    auto_sync_enabled: bool = True
    sync_interval_minutes: int = 30
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    
    def __post_init__(self):
        """Initialize default configurations"""
        if self.database is None:
            self.database = DatabaseConfig()
        if self.vector_store is None:
            self.vector_store = VectorStoreConfig()
        if self.llm is None:
            self.llm = LLMConfig()
        if self.cache is None:
            self.cache = CacheConfig()
        if self.optimization is None:
            self.optimization = OptimizationConfig()
        if self.web_interface is None:
            self.web_interface = WebInterfaceConfig()
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()
        if self.security is None:
            self.security = SecurityConfig()


class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_file: str = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = None
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from file and environment"""
        try:
            # Load from file if provided
            if self.config_file and os.path.exists(self.config_file):
                self._load_from_file()
            else:
                # Load from environment variables
                self._load_from_environment()
            
            # Validate configuration
            self._validate_configuration()
            
            print("✅ Configuration loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            # Use default configuration
            self.config = RAGPipelineConfig()
    
    def _load_from_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Convert to configuration objects
            self.config = self._dict_to_config(config_data)
            
        except Exception as e:
            print(f"❌ Error loading configuration from file: {e}")
            raise
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        try:
            # Create base configuration
            self.config = RAGPipelineConfig()
            
            # Environment
            self.config.environment = os.getenv("RAG_ENVIRONMENT", "development")
            self.config.debug = os.getenv("RAG_DEBUG", "false").lower() == "true"
            
            # Database configuration
            self.config.database.host = os.getenv("DB_HOST", "localhost")
            self.config.database.port = int(os.getenv("DB_PORT", "5000"))
            self.config.database.username = os.getenv("DB_USERNAME", "")
            self.config.database.password = os.getenv("DB_PASSWORD", "")
            self.config.database.database = os.getenv("DB_NAME", "fitness_data")
            
            # Vector store configuration
            self.config.vector_store.type = os.getenv("VECTOR_STORE_TYPE", "chromadb")
            self.config.vector_store.collection_name = os.getenv("VECTOR_COLLECTION", "fitness_embeddings")
            self.config.vector_store.persist_directory = os.getenv("VECTOR_PERSIST_DIR", "./chroma_db")
            self.config.vector_store.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
            
            # LLM configuration
            self.config.llm.provider = os.getenv("LLM_PROVIDER", "openai")
            self.config.llm.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
            self.config.llm.api_key = os.getenv("LLM_API_KEY", "")
            self.config.llm.api_base = os.getenv("LLM_API_BASE", "")
            
            # Cache configuration
            self.config.cache.enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
            self.config.cache.response_cache_size = int(os.getenv("CACHE_RESPONSE_SIZE", "1000"))
            self.config.cache.vector_cache_size = int(os.getenv("CACHE_VECTOR_SIZE", "500"))
            
            # Optimization configuration
            self.config.optimization.enabled = os.getenv("OPTIMIZATION_ENABLED", "true").lower() == "true"
            self.config.optimization.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
            
            # Web interface configuration
            self.config.web_interface.enabled = os.getenv("WEB_INTERFACE_ENABLED", "true").lower() == "true"
            self.config.web_interface.host = os.getenv("WEB_HOST", "0.0.0.0")
            self.config.web_interface.port = int(os.getenv("WEB_PORT", "8080"))
            self.config.web_interface.secret_key = os.getenv("WEB_SECRET_KEY", "dev-secret-key")
            
            # Monitoring configuration
            self.config.monitoring.enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
            self.config.monitoring.log_level = os.getenv("LOG_LEVEL", "INFO")
            self.config.monitoring.log_file = os.getenv("LOG_FILE", "./logs/rag_pipeline.log")
            
            # Security configuration
            self.config.security.authentication_enabled = os.getenv("AUTH_ENABLED", "false").lower() == "true"
            self.config.security.jwt_secret = os.getenv("JWT_SECRET", "")
            self.config.security.rate_limiting_enabled = os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
            
            # Integration configuration
            self.config.auto_sync_enabled = os.getenv("AUTO_SYNC_ENABLED", "true").lower() == "true"
            self.config.sync_interval_minutes = int(os.getenv("SYNC_INTERVAL_MINUTES", "30"))
            
        except Exception as e:
            print(f"❌ Error loading configuration from environment: {e}")
            raise
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> RAGPipelineConfig:
        """Convert dictionary to configuration object"""
        try:
            # Create base configuration
            config = RAGPipelineConfig()
            
            # Update with file data
            for key, value in config_data.items():
                if hasattr(config, key):
                    if key == "database" and isinstance(value, dict):
                        config.database = DatabaseConfig(**value)
                    elif key == "vector_store" and isinstance(value, dict):
                        config.vector_store = VectorStoreConfig(**value)
                    elif key == "llm" and isinstance(value, dict):
                        config.llm = LLMConfig(**value)
                    elif key == "cache" and isinstance(value, dict):
                        config.cache = CacheConfig(**value)
                    elif key == "optimization" and isinstance(value, dict):
                        config.optimization = OptimizationConfig(**value)
                    elif key == "web_interface" and isinstance(value, dict):
                        config.web_interface = WebInterfaceConfig(**value)
                    elif key == "monitoring" and isinstance(value, dict):
                        config.monitoring = MonitoringConfig(**value)
                    elif key == "security" and isinstance(value, dict):
                        config.security = SecurityConfig(**value)
                    else:
                        setattr(config, key, value)
            
            return config
            
        except Exception as e:
            print(f"❌ Error converting dictionary to config: {e}")
            raise
    
    def _validate_configuration(self):
        """Validate configuration settings"""
        try:
            errors = []
            
            # Validate required settings
            if not self.config.llm.api_key:
                errors.append("LLM API key is required")
            
            if self.config.vector_store.type not in ["chromadb", "pinecone", "faiss"]:
                errors.append("Invalid vector store type")
            
            if self.config.llm.provider not in ["openai", "anthropic", "google"]:
                errors.append("Invalid LLM provider")
            
            if self.config.web_interface.port < 1 or self.config.web_interface.port > 65535:
                errors.append("Invalid web interface port")
            
            if self.config.cache.response_cache_size < 1:
                errors.append("Cache size must be positive")
            
            if self.config.optimization.max_concurrent_requests < 1:
                errors.append("Max concurrent requests must be positive")
            
            # Check for errors
            if errors:
                raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
            
            print("✅ Configuration validation passed")
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            raise
    
    def get_config(self) -> RAGPipelineConfig:
        """Get the current configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        try:
            for key, value in updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    print(f"⚠️  Unknown configuration key: {key}")
            
            # Re-validate
            self._validate_configuration()
            
            print("✅ Configuration updated successfully")
            
        except Exception as e:
            print(f"❌ Error updating configuration: {e}")
    
    def save_config(self, filepath: str = None):
        """Save configuration to file"""
        try:
            filepath = filepath or self.config_file or "rag_config.json"
            
            # Convert to dictionary
            config_dict = self._config_to_dict(self.config)
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            print(f"✅ Configuration saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def _config_to_dict(self, config: RAGPipelineConfig) -> Dict[str, Any]:
        """Convert configuration object to dictionary"""
        try:
            config_dict = asdict(config)
            
            # Handle nested objects
            config_dict["database"] = asdict(config.database)
            config_dict["vector_store"] = asdict(config.vector_store)
            config_dict["llm"] = asdict(config.llm)
            config_dict["cache"] = asdict(config.cache)
            config_dict["optimization"] = asdict(config.optimization)
            config_dict["web_interface"] = asdict(config.web_interface)
            config_dict["monitoring"] = asdict(config.monitoring)
            config_dict["security"] = asdict(config.security)
            
            return config_dict
            
        except Exception as e:
            print(f"❌ Error converting config to dictionary: {e}")
            raise
    
    def get_environment_config(self, environment: str) -> RAGPipelineConfig:
        """Get environment-specific configuration"""
        try:
            # Create environment-specific config
            env_config = RAGPipelineConfig()
            
            if environment == "development":
                env_config.debug = True
                env_config.monitoring.log_level = "DEBUG"
                env_config.cache.enabled = False
                env_config.optimization.enabled = False
                
            elif environment == "testing":
                env_config.debug = True
                env_config.monitoring.log_level = "DEBUG"
                env_config.web_interface.enabled = False
                env_config.auto_sync_enabled = False
                
            elif environment == "production":
                env_config.debug = False
                env_config.monitoring.log_level = "WARNING"
                env_config.security.authentication_enabled = True
                env_config.security.rate_limiting_enabled = True
                env_config.cache.enabled = True
                env_config.optimization.enabled = True
                
            elif environment == "staging":
                env_config.debug = False
                env_config.monitoring.log_level = "INFO"
                env_config.security.authentication_enabled = False
                env_config.cache.enabled = True
                env_config.optimization.enabled = True
            
            return env_config
            
        except Exception as e:
            print(f"❌ Error getting environment config: {e}")
            return RAGPipelineConfig()
    
    def create_sample_config(self, filepath: str = "rag_config_sample.json"):
        """Create a sample configuration file"""
        try:
            sample_config = RAGPipelineConfig()
            
            # Set sample values
            sample_config.environment = "development"
            sample_config.debug = True
            
            sample_config.database.host = "localhost"
            sample_config.database.port = 5000
            sample_config.database.database = "fitness_data"
            
            sample_config.vector_store.type = "chromadb"
            sample_config.vector_store.collection_name = "fitness_embeddings"
            sample_config.vector_store.embedding_model = "text-embedding-ada-002"
            
            sample_config.llm.provider = "openai"
            sample_config.llm.model = "gpt-3.5-turbo"
            sample_config.llm.api_key = "your-api-key-here"
            
            sample_config.web_interface.host = "0.0.0.0"
            sample_config.web_interface.port = 5000
            sample_config.web_interface.secret_key = "your-secret-key-here"
            
            # Convert to dictionary and save
            config_dict = self._config_to_dict(sample_config)
            
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            print(f"✅ Sample configuration created: {filepath}")
            
        except Exception as e:
            print(f"❌ Error creating sample config: {e}")


def get_config(config_file: str = None) -> RAGPipelineConfig:
    """
    Get configuration instance
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration object
    """
    config_manager = ConfigManager(config_file)
    return config_manager.get_config()


def create_deployment_config(environment: str, output_dir: str = "./deploy"):
    """
    Create deployment configuration files
    
    Args:
        environment: Target environment
        output_dir: Output directory
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create configuration manager
        config_manager = ConfigManager()
        
        # Get environment-specific config
        env_config = config_manager.get_environment_config(environment)
        
        # Save configuration
        config_file = os.path.join(output_dir, f"rag_config_{environment}.json")
        config_manager.config = env_config
        config_manager.save_config(config_file)
        
        # Create Docker configuration
        dockerfile_content = f"""
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE {env_config.web_interface.port}

CMD ["python", "-m", "rag.main", "--config", "rag_config_{environment}.json"]
"""
        
        dockerfile_path = os.path.join(output_dir, "Dockerfile")
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        # Create docker-compose configuration
        compose_content = f"""
version: '3.8'

services:
  rag-pipeline:
    build: .
    ports:
      - "{env_config.web_interface.port}:{env_config.web_interface.port}"
    environment:
      - RAG_ENVIRONMENT={environment}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
"""
        
        compose_path = os.path.join(output_dir, "docker-compose.yml")
        with open(compose_path, 'w') as f:
            f.write(compose_content)
        
        # Create environment file
        env_content = f"""
RAG_ENVIRONMENT={environment}
RAG_DEBUG={'true' if env_config.debug else 'false'}
LLM_PROVIDER={env_config.llm.provider}
LLM_MODEL={env_config.llm.model}
LLM_API_KEY=your-api-key-here
WEB_HOST={env_config.web_interface.host}
WEB_PORT={env_config.web_interface.port}
WEB_SECRET_KEY=your-secret-key-here
LOG_LEVEL={env_config.monitoring.log_level}
"""
        
        env_path = os.path.join(output_dir, ".env")
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Deployment configuration created in {output_dir}")
        print(f"   - Configuration: rag_config_{environment}.json")
        print(f"   - Dockerfile: Dockerfile")
        print(f"   - Docker Compose: docker-compose.yml")
        print(f"   - Environment: .env")
        
    except Exception as e:
        print(f"❌ Error creating deployment config: {e}") 