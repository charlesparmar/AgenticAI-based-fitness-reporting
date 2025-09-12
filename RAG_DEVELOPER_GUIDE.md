# RAG Pipeline Developer Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Development Setup](#development-setup)
4. [Code Structure](#code-structure)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Contributing](#contributing)
8. [Advanced Usage](#advanced-usage)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

## Overview

The RAG Pipeline is a comprehensive system for enabling natural language interactions with fitness data. This developer guide provides detailed information for developers who want to understand, extend, or contribute to the system.

### Key Design Principles
- **Modularity**: Each component is designed to be independent and replaceable
- **Extensibility**: Easy to add new features and integrations
- **Performance**: Optimized for speed and efficiency
- **Reliability**: Robust error handling and monitoring
- **Scalability**: Designed to handle growing data and user loads

### Technology Stack
- **Python 3.9+**: Core programming language
- **ChromaDB**: Vector database for embeddings
- **OpenAI/Anthropic/Google**: LLM providers
- **Flask**: Web framework for the interface
- **SQLite Cloud**: Primary data storage
- **Socket.IO**: Real-time communication

## Architecture

### System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Chat Interface│    │   REST API      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   RAG Agent     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Query Processor │    │    Retriever    │    │   Generator     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Vector Store   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Data Sources   │
                    └─────────────────┘
```

### Component Architecture

#### Core Components
1. **RAG Agent**: Main orchestrator that coordinates all components
2. **Query Processor**: Analyzes and enhances user queries
3. **Retriever**: Performs semantic search and context retrieval
4. **Generator**: Generates responses using LLMs
5. **Vector Store**: Manages embeddings and similarity search
6. **Analytics**: Provides insights and trend analysis

#### Integration Components
1. **System Integrator**: Manages external system integrations
2. **Data Synchronizer**: Handles data synchronization
3. **Configuration Manager**: Manages system configuration
4. **Cache Manager**: Optimizes performance through caching
5. **Performance Monitor**: Tracks system performance

#### Interface Components
1. **Web Interface**: Flask-based web application
2. **Chat Interface**: Manages conversations and messaging
3. **REST API**: Programmatic access to system functionality

### Data Flow

```
User Query → Query Processing → Vector Search → Context Retrieval → LLM Generation → Response
     ↓              ↓              ↓              ↓              ↓              ↓
Chat Interface → Query Parser → Vector DB → Fitness Data → LLM Model → Formatted Answer
     ↓              ↓              ↓              ↓              ↓              ↓
Web Interface → Query Enhancer → Embeddings → Context Filter → Prompt Engine → Response Formatter
```

## Development Setup

### Prerequisites
- Python 3.9 or higher
- Git
- SQLite Cloud access
- LLM API keys (OpenAI, Anthropic, or Google)

### Environment Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd AgenticAI-based-fitness-reporting
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables
Create a `.env` file:
```bash
# Development settings
RAG_ENVIRONMENT=development
RAG_DEBUG=true

# LLM Configuration
OPENAI_API_KEY=your-openai-api-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# Database Configuration
DB_HOST=localhost
DB_PORT=5000
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_NAME=fitness_data

# Web Interface
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_SECRET_KEY=dev-secret-key

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=./logs/rag_pipeline.log
```

#### 5. Create Required Directories
```bash
mkdir -p logs
mkdir -p data
mkdir -p chroma_db
mkdir -p static
mkdir -p templates
```

#### 6. Verify Setup
```bash
python test_rag_phase1.py
```

### Development Tools

#### Recommended IDE Setup
- **VS Code** with Python extension
- **PyCharm** Professional
- **Jupyter Notebook** for experimentation

#### Code Quality Tools
```bash
# Install development dependencies
pip install black flake8 mypy pytest pytest-cov

# Code formatting
black rag/ tests/

# Linting
flake8 rag/ tests/

# Type checking
mypy rag/

# Testing
pytest tests/ --cov=rag
```

## Code Structure

### Directory Structure
```
rag/
├── __init__.py                 # Package initialization
├── data_preparation.py         # Data extraction and preprocessing
├── vector_store.py            # Vector database operations
├── query_processor.py         # Query processing and enhancement
├── retriever.py              # Semantic search and retrieval
├── prompts.py                # Prompt templates
├── generator.py              # LLM integration and response generation
├── chat_interface.py         # Chat interface management
├── web_interface.py          # Web application
├── analytics.py              # Analytics and insights
├── cache.py                  # Caching system
├── optimization.py           # Performance optimization
├── integration.py            # System integration
├── config.py                 # Configuration management
└── utils/                    # Utility modules
    ├── __init__.py
    ├── embeddings.py         # Embedding utilities
    ├── chunking.py           # Document chunking
    └── formatting.py         # Response formatting

tests/                        # Test suite
├── __init__.py
├── test_integration.py       # Integration tests
└── test_*.py                # Individual component tests

docs/                         # Documentation
├── RAG_USER_GUIDE.md
├── RAG_API_DOCS.md
└── RAG_DEVELOPER_GUIDE.md
```

### Module Dependencies

```
rag/
├── __init__.py
├── config.py                 # No dependencies
├── data_preparation.py       # Depends on: config, utils
├── vector_store.py          # Depends on: config, utils
├── query_processor.py       # Depends on: config, utils
├── retriever.py             # Depends on: vector_store, query_processor
├── prompts.py               # No dependencies
├── generator.py             # Depends on: prompts, config
├── chat_interface.py        # Depends on: retriever, generator
├── web_interface.py         # Depends on: chat_interface
├── analytics.py             # Depends on: vector_store, retriever
├── cache.py                 # No dependencies
├── optimization.py          # Depends on: cache, vector_store
├── integration.py           # Depends on: all other modules
└── utils/
    ├── __init__.py
    ├── embeddings.py         # No dependencies
    ├── chunking.py           # No dependencies
    └── formatting.py         # No dependencies
```

## Development Workflow

### 1. Feature Development

#### Creating a New Feature
```bash
# Create a feature branch
git checkout -b feature/new-feature

# Make changes
# Add tests
# Update documentation

# Commit changes
git add .
git commit -m "Add new feature: description"

# Push and create pull request
git push origin feature/new-feature
```

#### Code Style Guidelines
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

#### Example Code Structure
```python
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class MyDataClass:
    """Represents a data structure."""
    
    field1: str
    field2: int
    optional_field: Optional[str] = None

class MyClass:
    """Main class for feature implementation."""
    
    def __init__(self, config: Dict[str, any]):
        """
        Initialize the class.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize internal components."""
        # Implementation here
        pass
    
    def process_data(self, data: List[str]) -> Dict[str, any]:
        """
        Process the input data.
        
        Args:
            data: List of data items to process
            
        Returns:
            Dictionary containing processed results
            
        Raises:
            ValueError: If data is empty
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Implementation here
        return {"result": "processed"}
```

### 2. Testing Strategy

#### Unit Tests
- Test individual functions and methods
- Use mocking for external dependencies
- Aim for 90%+ code coverage

#### Integration Tests
- Test component interactions
- Test end-to-end workflows
- Use test databases and mock APIs

#### Performance Tests
- Test system performance under load
- Monitor memory usage and response times
- Test caching effectiveness

#### Example Test Structure
```python
import unittest
from unittest.mock import Mock, patch
from rag.my_module import MyClass

class TestMyClass(unittest.TestCase):
    """Test cases for MyClass."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {"test": "config"}
        self.instance = MyClass(self.config)
    
    def test_initialization(self):
        """Test class initialization."""
        self.assertIsNotNone(self.instance)
        self.assertEqual(self.instance.config, self.config)
    
    def test_process_data_empty(self):
        """Test processing empty data."""
        with self.assertRaises(ValueError):
            self.instance.process_data([])
    
    def test_process_data_valid(self):
        """Test processing valid data."""
        data = ["item1", "item2"]
        result = self.instance.process_data(data)
        self.assertIn("result", result)
    
    @patch('rag.my_module.external_api')
    def test_external_dependency(self, mock_api):
        """Test external dependency interaction."""
        mock_api.return_value = "mocked_response"
        # Test implementation
```

### 3. Documentation

#### Code Documentation
- Use docstrings for all public functions and classes
- Include type hints
- Provide usage examples

#### API Documentation
- Document all public APIs
- Include request/response examples
- Document error codes and handling

#### User Documentation
- Write clear user guides
- Include troubleshooting sections
- Provide step-by-step tutorials

## Testing

### Running Tests

#### All Tests
```bash
pytest tests/ -v
```

#### Specific Test File
```bash
pytest tests/test_integration.py -v
```

#### With Coverage
```bash
pytest tests/ --cov=rag --cov-report=html
```

#### Performance Tests
```bash
pytest tests/ -m "performance" -v
```

### Test Categories

#### Unit Tests
```bash
# Test individual components
python test_rag_phase1.py  # Data preparation
python test_rag_phase2.py  # Query processing
python test_rag_phase3.py  # LLM integration
python test_rag_phase4.py  # Chat interface
python test_rag_phase5.py  # Analytics and optimization
python test_rag_phase6.py  # Integration and testing
```

#### Integration Tests
```bash
# Test component interactions
python -m pytest tests/test_integration.py -v
```

#### End-to-End Tests
```bash
# Test complete workflows
python -m pytest tests/ -m "e2e" -v
```

### Test Data Management

#### Test Databases
```python
# Use in-memory SQLite for tests
import sqlite3
import tempfile

def create_test_db():
    """Create a temporary test database."""
    db_fd, db_path = tempfile.mkstemp()
    conn = sqlite3.connect(db_path)
    # Create test tables and data
    return conn, db_path
```

#### Mock External Services
```python
# Mock LLM API calls
@patch('rag.generator.openai.ChatCompletion.create')
def test_llm_integration(self, mock_openai):
    mock_openai.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response"))]
    )
    # Test implementation
```

## Contributing

### Contribution Guidelines

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/AgenticAI-based-fitness-reporting.git
cd AgenticAI-based-fitness-reporting
```

#### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

#### 3. Make Changes
- Follow the coding style guidelines
- Write tests for new functionality
- Update documentation
- Ensure all tests pass

#### 4. Commit Changes
```bash
git add .
git commit -m "Add feature: brief description

- Detailed description of changes
- Any breaking changes
- Related issues"
```

#### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

### Pull Request Guidelines

#### Required Information
- Clear description of the feature/fix
- Link to related issues
- Test coverage information
- Performance impact assessment
- Breaking changes documentation

#### Review Process
- Code review by maintainers
- Automated tests must pass
- Documentation must be updated
- Performance benchmarks (if applicable)

### Code Review Checklist

#### Functionality
- [ ] Feature works as expected
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance is acceptable

#### Code Quality
- [ ] Code follows style guidelines
- [ ] Functions are well-documented
- [ ] Type hints are used
- [ ] No code duplication

#### Testing
- [ ] Unit tests are written
- [ ] Integration tests are updated
- [ ] Test coverage is adequate
- [ ] All tests pass

#### Documentation
- [ ] Code is documented
- [ ] API documentation is updated
- [ ] User documentation is updated
- [ ] Examples are provided

## Advanced Usage

### Custom LLM Integration

#### Adding a New LLM Provider
```python
from rag.generator import ResponseGenerator

class CustomLLMProvider:
    """Custom LLM provider implementation."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using custom LLM."""
        # Implementation here
        return "Custom response"

# Register the provider
ResponseGenerator.register_provider("custom", CustomLLMProvider)
```

### Custom Analytics

#### Adding Custom Metrics
```python
from rag.analytics import FitnessAnalytics

class CustomAnalytics(FitnessAnalytics):
    """Extended analytics with custom metrics."""
    
    def analyze_custom_metric(self, data: List[Dict]) -> Dict:
        """Analyze custom fitness metric."""
        # Implementation here
        return {"custom_metric": "value"}
    
    def generate_custom_report(self, user_id: str) -> Dict:
        """Generate custom analytics report."""
        # Implementation here
        return {"custom_report": "data"}
```

### Custom Data Sources

#### Adding New Data Sources
```python
from rag.integration import SystemIntegrator

class CustomDataSource:
    """Custom data source implementation."""
    
    def get_data(self, query: str = None) -> Dict:
        """Retrieve data from custom source."""
        # Implementation here
        return {"custom_data": "value"}
    
    def sync_data(self) -> bool:
        """Synchronize data with external source."""
        # Implementation here
        return True

# Register the data source
integrator = SystemIntegrator()
integrator.register_data_source("custom_source", CustomDataSource())
```

### Custom Caching Strategies

#### Implementing Custom Cache
```python
from rag.cache import CacheManager

class CustomCache:
    """Custom caching implementation."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
    
    def get(self, key: str) -> any:
        """Get value from cache."""
        return self.cache.get(key)
    
    def set(self, key: str, value: any, ttl: int = None) -> bool:
        """Set value in cache."""
        if len(self.cache) >= self.max_size:
            # Implement eviction strategy
            pass
        self.cache[key] = value
        return True

# Use custom cache
cache_manager = CacheManager()
cache_manager.response_cache = CustomCache()
```

## Performance Optimization

### Caching Strategies

#### Response Caching
```python
# Enable response caching
config = IntegrationConfig(cache_enabled=True)
agent = RAGAgent(config)

# Monitor cache performance
stats = agent.cache_manager.get_all_stats()
print(f"Cache hit rate: {stats['response_cache']['hit_rate']}%")
```

#### Vector Search Optimization
```python
# Optimize vector search
from rag.optimization import VectorSearchOptimizer

optimizer = VectorSearchOptimizer(vector_store, cache_manager)
results = optimizer.optimize_search("query", n_results=10)
```

### Database Optimization

#### Connection Pooling
```python
# Configure connection pooling
from rag.config import DatabaseConfig

db_config = DatabaseConfig(
    max_connections=20,
    connection_timeout=30
)
```

#### Query Optimization
```python
# Optimize database queries
def optimized_query():
    """Optimized database query."""
    # Use indexes
    # Limit result sets
    # Use connection pooling
    pass
```

### Memory Management

#### Garbage Collection
```python
import gc

# Force garbage collection
gc.collect()

# Monitor memory usage
import psutil
process = psutil.Process()
memory_info = process.memory_info()
print(f"Memory usage: {memory_info.rss / 1024 / 1024} MB")
```

#### Resource Cleanup
```python
# Proper resource cleanup
class ResourceManager:
    def __init__(self):
        self.resources = []
    
    def add_resource(self, resource):
        self.resources.append(resource)
    
    def cleanup(self):
        for resource in self.resources:
            resource.close()
        self.resources.clear()
```

### Load Balancing

#### Request Distribution
```python
from rag.optimization import LoadBalancer

# Configure load balancer
load_balancer = LoadBalancer(max_concurrent_requests=20)

# Submit requests through load balancer
def process_request():
    return load_balancer.submit_request(agent.process_query, "query")
```

## Troubleshooting

### Common Development Issues

#### 1. Import Errors
**Problem:** Module import failures
**Solution:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Add project root to path
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

#### 2. Configuration Issues
**Problem:** Configuration not loading correctly
**Solution:**
```python
# Debug configuration loading
from rag.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.get_config()
print(f"Config: {config}")
```

#### 3. Database Connection Issues
**Problem:** Cannot connect to database
**Solution:**
```python
# Test database connection
import sqlite3

try:
    conn = sqlite3.connect("test.db")
    print("Database connection successful")
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### 4. LLM API Issues
**Problem:** LLM API calls failing
**Solution:**
```python
# Test LLM API
import openai

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("LLM API working")
except Exception as e:
    print(f"LLM API error: {e}")
```

### Debug Mode

#### Enable Debug Mode
```python
from rag.config import RAGPipelineConfig

config = RAGPipelineConfig()
config.debug = True
config.monitoring.log_level = "DEBUG"
```

#### Debug Logging
```python
import logging

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Debugging

#### Monitor System Performance
```python
# Monitor CPU and memory usage
import psutil
import time

def monitor_performance():
    while True:
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        print(f"CPU: {cpu_percent}%, Memory: {memory_percent}%")
        time.sleep(5)
```

#### Profile Code Performance
```python
import cProfile
import pstats

# Profile function performance
def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

### Error Handling

#### Custom Exception Classes
```python
class RAGPipelineError(Exception):
    """Base exception for RAG pipeline."""
    pass

class ConfigurationError(RAGPipelineError):
    """Configuration-related errors."""
    pass

class IntegrationError(RAGPipelineError):
    """Integration-related errors."""
    pass

class DataSyncError(RAGPipelineError):
    """Data synchronization errors."""
    pass
```

#### Error Recovery
```python
def robust_operation():
    """Perform operation with error recovery."""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            # Perform operation
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay)
            retry_delay *= 2
```

---

## Quick Reference

### Development Commands
```bash
# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Code formatting
black rag/ tests/

# Linting
flake8 rag/ tests/

# Type checking
mypy rag/

# Start development server
python -c "from rag.integration import RAGAgent; RAGAgent().start_web_interface(debug=True)"
```

### Configuration Files
- `.env`: Environment variables
- `rag_config.json`: Main configuration
- `requirements.txt`: Python dependencies
- `setup.py`: Package setup
- `pyproject.toml`: Project configuration

### Key URLs
- Web Interface: `http://localhost:5000`
- API Documentation: `http://localhost:5000/api/docs`
- Health Check: `http://localhost:5000/api/health`
- Metrics: `http://localhost:5000/api/metrics`

---

*This developer guide provides comprehensive information for developers working with the RAG Pipeline. For additional support, refer to the API documentation and user guides.* 