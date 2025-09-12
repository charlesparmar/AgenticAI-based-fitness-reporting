# RAG Pipeline User Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Web Interface](#web-interface)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)
10. [Support](#support)

## Overview

The RAG (Retrieval-Augmented Generation) Pipeline for Fitness Data is an intelligent system that allows you to chat with your fitness data using natural language. It provides personalized insights, trend analysis, and recommendations based on your fitness measurements.

### Key Features
- **Natural Language Queries**: Ask questions about your fitness data in plain English
- **Trend Analysis**: Get insights into your progress over time
- **Personalized Recommendations**: Receive tailored fitness advice
- **Real-time Chat Interface**: Interactive web-based chat interface
- **Analytics Dashboard**: Comprehensive fitness analytics and reports
- **Goal Tracking**: Monitor progress towards your fitness goals

### System Architecture
```
User Query → Query Processing → Vector Search → Context Retrieval → LLM Generation → Response
     ↓              ↓              ↓              ↓              ↓              ↓
Chat Interface → Query Parser → Vector DB → Fitness Data → LLM Model → Formatted Answer
```

## Installation

### Prerequisites
- Python 3.9 or higher
- SQLite Cloud database access
- OpenAI API key (or other LLM provider)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd AgenticAI-based-fitness-reporting
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables
Create a `.env` file in the project root:
```bash
# LLM Configuration
OPENAI_API_KEY=your-openai-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# Database Configuration
DB_HOST=localhost
DB_PORT=5000
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_NAME=fitness_data

# Web Interface Configuration
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_SECRET_KEY=your-secret-key-here

# Optional: Other LLM Providers
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here
```

### Step 4: Verify Installation
```bash
python test_rag_phase1.py
```

## Quick Start

### 1. Initialize the RAG Pipeline
```python
from rag.integration import RAGAgent, IntegrationConfig

# Create configuration
config = IntegrationConfig(
    auto_sync_enabled=True,
    cache_enabled=True,
    optimization_enabled=True
)

# Initialize agent
agent = RAGAgent(config)
```

### 2. Ask Your First Question
```python
# Process a query
response = agent.process_query("How has my weight changed?", "user123")
print(response['response'])
```

### 3. Start the Web Interface
```python
# Start web interface
agent.start_web_interface(host="0.0.0.0", port=5000)
```

### 4. Access the Chat Interface
Open your browser and navigate to `http://localhost:5000`

## Configuration

### Environment-Specific Configurations

#### Development Environment
```python
from rag.config import ConfigManager

config_manager = ConfigManager()
dev_config = config_manager.get_environment_config("development")
# Features: Debug mode, detailed logging, no caching
```

#### Production Environment
```python
prod_config = config_manager.get_environment_config("production")
# Features: Optimized performance, caching, security enabled
```

### Configuration Options

#### LLM Configuration
```python
from rag.config import LLMConfig

llm_config = LLMConfig(
    provider="openai",  # openai, anthropic, google
    model="gpt-3.5-turbo",
    api_key="your-api-key",
    max_tokens=1000,
    temperature=0.7
)
```

#### Cache Configuration
```python
from rag.config import CacheConfig

cache_config = CacheConfig(
    enabled=True,
    response_cache_size=1000,
    vector_cache_size=500,
    embedding_cache_size=2000,
    response_ttl=3600  # 1 hour
)
```

#### Optimization Configuration
```python
from rag.config import OptimizationConfig

opt_config = OptimizationConfig(
    enabled=True,
    max_concurrent_requests=10,
    batch_size=10,
    max_workers=4
)
```

## Usage Examples

### Basic Query Processing
```python
from rag.integration import RAGAgent

agent = RAGAgent()

# Simple queries
queries = [
    "How has my weight changed?",
    "What are my current measurements?",
    "Show me my BMI trends",
    "Give me a summary of my progress"
]

for query in queries:
    response = agent.process_query(query, "user123")
    print(f"Q: {query}")
    print(f"A: {response['response']}")
    print(f"Processing time: {response['processing_time_ms']:.2f}ms")
    print()
```

### Analytics and Insights
```python
# Get comprehensive analytics
analytics = agent.get_analytics("user123", "month")

if analytics['success']:
    report = analytics['report']
    print(f"User: {report['user_id']}")
    print(f"Period: {report['period_analyzed']}")
    print(f"Key Metrics: {report['key_metrics']}")
    print(f"Recommendations: {report['recommendations']}")
    print(f"Risk Alerts: {report['risk_alerts']}")
    print(f"Achievements: {report['achievements']}")
```

### System Integration
```python
from rag.integration import SystemIntegrator

integrator = SystemIntegrator(agent)

# Register custom data sources
def custom_data_source():
    return {"custom_data": "value"}

integrator.register_data_source("custom_source", custom_data_source)

# Register integration hooks
def pre_processing_hook(config):
    print("Pre-processing started")
    return {"status": "ready"}

integrator.register_integration_hook("pre_processing", pre_processing_hook)

# Integrate with existing workflow
workflow_config = {
    "rag_config": {
        "auto_sync_enabled": True,
        "sync_interval_minutes": 30
    },
    "data_sources": {
        "fitness_db": {"type": "database"}
    }
}

success = integrator.integrate_with_existing_workflow(workflow_config)
```

### Data Synchronization
```python
from rag.integration import DataSynchronizer

synchronizer = DataSynchronizer(agent)

# Sync all data
sync_results = synchronizer.sync_all_data()
print(f"Sync results: {sync_results}")

# Get sync history
history = synchronizer.get_sync_history(limit=10)
for record in history:
    print(f"Sync at {record['start_time']}: {record['success']}")

# Get sync statistics
stats = synchronizer.get_sync_statistics()
print(f"Success rate: {stats['success_rate']}%")
```

## Web Interface

### Starting the Web Interface
```python
# Start with default settings
agent.start_web_interface()

# Start with custom settings
agent.start_web_interface(
    host="0.0.0.0",
    port=8080,
    debug=False
)
```

### Web Interface Features
- **Real-time Chat**: Interactive chat interface
- **Conversation History**: View and manage chat history
- **Analytics Dashboard**: Visual fitness analytics
- **Export Functionality**: Export conversations and reports
- **Responsive Design**: Works on desktop and mobile

### Web Interface Usage
1. Open your browser and navigate to the web interface URL
2. Start typing your fitness questions
3. View real-time responses and insights
4. Access analytics and reports
5. Export data as needed

## API Reference

### RAGAgent Class

#### Methods

##### `process_query(query, user_id=None, context=None)`
Process a natural language query.

**Parameters:**
- `query` (str): The user's question
- `user_id` (str, optional): User identifier
- `context` (dict, optional): Additional context

**Returns:**
- `dict`: Response with answer and metadata

**Example:**
```python
response = agent.process_query("How has my weight changed?", "user123")
```

##### `get_analytics(user_id, period="month")`
Get comprehensive analytics for a user.

**Parameters:**
- `user_id` (str): User identifier
- `period` (str): Analysis period (week, month, quarter, year)

**Returns:**
- `dict`: Analytics report

**Example:**
```python
analytics = agent.get_analytics("user123", "month")
```

##### `get_system_status()`
Get system health and status information.

**Returns:**
- `dict`: System status information

**Example:**
```python
status = agent.get_system_status()
print(f"System health: {status['overall_health']}")
```

##### `start_web_interface(host="0.0.0.0", port=5000, debug=False)`
Start the web interface.

**Parameters:**
- `host` (str): Host to bind to
- `port` (int): Port to bind to
- `debug` (bool): Enable debug mode

**Example:**
```python
agent.start_web_interface(host="localhost", port=8080)
```

##### `shutdown()`
Shutdown the agent and clean up resources.

**Example:**
```python
agent.shutdown()
```

### SystemIntegrator Class

#### Methods

##### `register_integration_hook(hook_name, hook_function)`
Register an integration hook.

**Parameters:**
- `hook_name` (str): Name of the hook
- `hook_function` (callable): Function to execute

**Example:**
```python
def my_hook(config):
    return {"status": "processed"}

integrator.register_integration_hook("my_hook", my_hook)
```

##### `register_data_source(source_name, data_source)`
Register a data source.

**Parameters:**
- `source_name` (str): Name of the data source
- `data_source` (any): Data source object

**Example:**
```python
integrator.register_data_source("my_db", database_connection)
```

##### `integrate_with_existing_workflow(workflow_config)`
Integrate with existing workflow.

**Parameters:**
- `workflow_config` (dict): Workflow configuration

**Returns:**
- `bool`: Success status

**Example:**
```python
config = {"rag_config": {"auto_sync_enabled": True}}
success = integrator.integrate_with_existing_workflow(config)
```

### DataSynchronizer Class

#### Methods

##### `sync_all_data()`
Synchronize all data sources.

**Returns:**
- `dict`: Synchronization results

**Example:**
```python
results = synchronizer.sync_all_data()
```

##### `get_sync_history(limit=10)`
Get synchronization history.

**Parameters:**
- `limit` (int): Number of records to return

**Returns:**
- `list`: Sync history records

**Example:**
```python
history = synchronizer.get_sync_history(limit=5)
```

##### `get_sync_statistics()`
Get synchronization statistics.

**Returns:**
- `dict`: Sync statistics

**Example:**
```python
stats = synchronizer.get_sync_statistics()
print(f"Success rate: {stats['success_rate']}%")
```

## Troubleshooting

### Common Issues

#### 1. "LLM API key not found" Error
**Problem:** The system cannot find your LLM API key.

**Solution:**
```bash
# Check your .env file
cat .env

# Ensure the API key is set correctly
export OPENAI_API_KEY="your-actual-api-key"
```

#### 2. "Database connection failed" Error
**Problem:** Cannot connect to the database.

**Solution:**
```bash
# Verify database settings
python -c "from rag.config import get_config; print(get_config().database)"

# Check network connectivity
ping your-database-host
```

#### 3. "Vector store initialization failed" Error
**Problem:** ChromaDB or vector store cannot be initialized.

**Solution:**
```bash
# Check disk space
df -h

# Clear existing vector store
rm -rf ./chroma_db

# Reinitialize
python test_rag_phase1.py
```

#### 4. "Web interface not accessible" Error
**Problem:** Cannot access the web interface.

**Solution:**
```bash
# Check if port is in use
lsof -i :5000

# Try different port
agent.start_web_interface(port=8080)

# Check firewall settings
sudo ufw status
```

#### 5. "Cache performance issues" Error
**Problem:** Slow response times or cache issues.

**Solution:**
```python
# Clear cache
agent.cache_manager.clear_all()

# Optimize cache
agent.cache_manager.optimize_caches()

# Check cache statistics
stats = agent.cache_manager.get_all_stats()
print(stats)
```

### Performance Optimization

#### 1. Enable Caching
```python
config = IntegrationConfig(cache_enabled=True)
agent = RAGAgent(config)
```

#### 2. Optimize Vector Search
```python
# Increase batch size for better performance
config = OptimizationConfig(batch_size=20)
```

#### 3. Monitor System Performance
```python
# Get performance statistics
stats = agent.optimizer.get_optimization_statistics()
print(f"Average response time: {stats['performance']['average_duration_ms']}ms")
```

### Debug Mode

Enable debug mode for detailed logging:
```python
from rag.config import RAGPipelineConfig

config = RAGPipelineConfig()
config.debug = True
config.monitoring.log_level = "DEBUG"
```

## FAQ

### Q: What types of questions can I ask?
A: You can ask questions about:
- Weight changes and trends
- BMI and body composition
- Measurement comparisons
- Progress summaries
- Goal tracking
- Fitness recommendations

### Q: How often should I sync my data?
A: The system automatically syncs every 30 minutes by default. You can adjust this in the configuration.

### Q: Can I use different LLM providers?
A: Yes, the system supports OpenAI, Anthropic, and Google LLM providers. Configure this in your settings.

### Q: Is my data secure?
A: Yes, the system includes security features like authentication, rate limiting, and secure API key management.

### Q: Can I export my conversations?
A: Yes, the web interface includes export functionality for conversations and analytics reports.

### Q: How do I update the system?
A: Pull the latest changes and reinstall dependencies:
```bash
git pull
pip install -r requirements.txt
```

### Q: Can I customize the analytics?
A: Yes, you can customize analytics by modifying the analytics configuration and adding custom metrics.

### Q: What if I encounter an error?
A: Check the troubleshooting section above, enable debug mode for detailed logs, and contact support if needed.

## Support

### Getting Help

1. **Check the Documentation**: Review this guide and the API documentation
2. **Enable Debug Mode**: Use debug mode for detailed error information
3. **Check Logs**: Review system logs for error details
4. **Contact Support**: Reach out to the development team

### Debug Information

When reporting issues, include:
- Error messages and stack traces
- System configuration
- Steps to reproduce the issue
- Debug logs (if available)

### Log Files

Log files are located at:
- Application logs: `./logs/rag_pipeline.log`
- Error logs: `./logs/errors.log`
- Performance logs: `./logs/performance.log`

### Community Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the latest documentation
- **Examples**: Review example code and configurations

---

## Quick Reference

### Common Commands
```bash
# Start the system
python -c "from rag.integration import RAGAgent; RAGAgent().start_web_interface()"

# Run tests
python test_rag_phase6.py

# Check system status
python -c "from rag.integration import RAGAgent; print(RAGAgent().get_system_status())"

# Generate deployment config
python -c "from rag.config import create_deployment_config; create_deployment_config('production')"
```

### Configuration Files
- `.env`: Environment variables
- `rag_config.json`: Main configuration
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container configuration
- `docker-compose.yml`: Multi-container setup

### Key URLs
- Web Interface: `http://localhost:5000`
- API Documentation: `http://localhost:5000/api/docs`
- Health Check: `http://localhost:5000/api/health`

---

*This user guide covers the basic usage of the RAG Pipeline. For advanced features and customization, refer to the API documentation and developer guides.* 