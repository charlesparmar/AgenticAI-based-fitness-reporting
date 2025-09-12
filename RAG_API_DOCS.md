# RAG Pipeline API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Integration API](#integration-api)
4. [Configuration API](#configuration-api)
5. [Analytics API](#analytics-api)
6. [Caching API](#caching-api)
7. [Optimization API](#optimization-api)
8. [Web Interface API](#web-interface-api)
9. [Data Models](#data-models)
10. [Error Handling](#error-handling)

## Overview

The RAG Pipeline API provides comprehensive access to all system functionality through Python classes and methods. This documentation covers all public APIs, data models, and usage examples.

### API Version
- **Current Version**: 1.0.0
- **Compatibility**: Python 3.9+

### Import Statement
```python
from rag import *
```

## Core Classes

### RAGAgent

The main entry point for the RAG pipeline system.

#### Constructor
```python
RAGAgent(config: IntegrationConfig = None)
```

**Parameters:**
- `config` (IntegrationConfig, optional): Configuration for the agent

**Example:**
```python
from rag.integration import RAGAgent, IntegrationConfig

config = IntegrationConfig(
    auto_sync_enabled=True,
    cache_enabled=True,
    optimization_enabled=True
)
agent = RAGAgent(config)
```

#### Methods

##### `process_query(query: str, user_id: str = None, context: dict = None) -> dict`

Process a natural language query and return a response.

**Parameters:**
- `query` (str): The user's question
- `user_id` (str, optional): User identifier for personalization
- `context` (dict, optional): Additional context for the query

**Returns:**
- `dict`: Response containing:
  - `response` (str): The generated answer
  - `agent_id` (str): Agent identifier
  - `processing_time_ms` (float): Processing time in milliseconds
  - `user_id` (str): User identifier
  - `timestamp` (str): ISO timestamp
  - `query_type` (str): Type of query processed
  - `context_used` (int): Number of context items used

**Example:**
```python
response = agent.process_query(
    "How has my weight changed?",
    user_id="user123",
    context={"time_period": "last_month"}
)

print(f"Answer: {response['response']}")
print(f"Processing time: {response['processing_time_ms']}ms")
```

##### `get_analytics(user_id: str, period: str = "month") -> dict`

Get comprehensive analytics for a user.

**Parameters:**
- `user_id` (str): User identifier
- `period` (str): Analysis period ("week", "month", "quarter", "year")

**Returns:**
- `dict`: Analytics report containing:
  - `success` (bool): Whether analytics generation was successful
  - `report` (dict): Analytics data (if successful)
  - `error` (str): Error message (if failed)

**Example:**
```python
analytics = agent.get_analytics("user123", "month")

if analytics['success']:
    report = analytics['report']
    print(f"User: {report['user_id']}")
    print(f"Period: {report['period_analyzed']}")
    print(f"Key metrics: {report['key_metrics']}")
    print(f"Recommendations: {report['recommendations']}")
else:
    print(f"Error: {analytics['error']}")
```

##### `get_system_status() -> dict`

Get system health and status information.

**Returns:**
- `dict`: System status containing:
  - `agent_id` (str): Agent identifier
  - `overall_health` (str): Overall system health ("healthy", "warning", "error")
  - `healthy_components` (int): Number of healthy components
  - `total_components` (int): Total number of components
  - `components` (dict): Status of individual components
  - `config` (dict): Current configuration
  - `timestamp` (str): ISO timestamp

**Example:**
```python
status = agent.get_system_status()
print(f"System health: {status['overall_health']}")
print(f"Healthy components: {status['healthy_components']}/{status['total_components']}")

for component, info in status['components'].items():
    print(f"{component}: {info['status']}")
```

##### `start_web_interface(host: str = "0.0.0.0", port: int = 5000, debug: bool = False)`

Start the web interface server.

**Parameters:**
- `host` (str): Host to bind to
- `port` (int): Port to bind to
- `debug` (bool): Enable debug mode

**Example:**
```python
agent.start_web_interface(
    host="localhost",
    port=8080,
    debug=True
)
```

##### `shutdown()`

Shutdown the agent and clean up resources.

**Example:**
```python
agent.shutdown()
```

### SystemIntegrator

Manages system integration and workflow connections.

#### Constructor
```python
SystemIntegrator(rag_agent: RAGAgent = None)
```

**Parameters:**
- `rag_agent` (RAGAgent, optional): RAG agent instance

#### Methods

##### `register_integration_hook(hook_name: str, hook_function: callable)`

Register an integration hook function.

**Parameters:**
- `hook_name` (str): Name of the hook
- `hook_function` (callable): Function to execute

**Example:**
```python
def pre_processing_hook(config):
    print("Pre-processing started")
    return {"status": "ready"}

integrator.register_integration_hook("pre_processing", pre_processing_hook)
```

##### `trigger_integration_hook(hook_name: str, *args, **kwargs) -> any`

Trigger an integration hook.

**Parameters:**
- `hook_name` (str): Name of the hook to trigger
- `*args`: Positional arguments for the hook
- `**kwargs`: Keyword arguments for the hook

**Returns:**
- `any`: Result from the hook function

**Example:**
```python
result = integrator.trigger_integration_hook("pre_processing", {"data": "test"})
print(f"Hook result: {result}")
```

##### `register_data_source(source_name: str, data_source: any)`

Register a data source.

**Parameters:**
- `source_name` (str): Name of the data source
- `data_source` (any): Data source object

**Example:**
```python
class MyDataSource:
    def get_data(self, query=None):
        return {"custom_data": "value"}

integrator.register_data_source("my_source", MyDataSource())
```

##### `get_data_from_source(source_name: str, query: str = None) -> any`

Get data from a registered source.

**Parameters:**
- `source_name` (str): Name of the data source
- `query` (str, optional): Query for the data source

**Returns:**
- `any`: Data from the source

**Example:**
```python
data = integrator.get_data_from_source("my_source", "get_fitness_data")
print(f"Data: {data}")
```

##### `integrate_with_existing_workflow(workflow_config: dict) -> bool`

Integrate with existing workflow.

**Parameters:**
- `workflow_config` (dict): Workflow configuration

**Returns:**
- `bool`: Success status

**Example:**
```python
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
print(f"Integration successful: {success}")
```

##### `get_integration_status() -> dict`

Get integration status information.

**Returns:**
- `dict`: Integration status

**Example:**
```python
status = integrator.get_integration_status()
print(f"Registered hooks: {status['registered_hooks']}")
print(f"Registered sources: {status['registered_sources']}")
```

### DataSynchronizer

Handles data synchronization between systems.

#### Constructor
```python
DataSynchronizer(rag_agent: RAGAgent)
```

**Parameters:**
- `rag_agent` (RAGAgent): RAG agent instance

#### Methods

##### `sync_all_data() -> dict`

Synchronize all data sources.

**Returns:**
- `dict`: Synchronization results

**Example:**
```python
results = synchronizer.sync_all_data()
print(f"Fitness data sync: {results['fitness_data']['success']}")
print(f"Analytics data sync: {results['analytics_data']['success']}")
```

##### `get_sync_history(limit: int = 10) -> list`

Get synchronization history.

**Parameters:**
- `limit` (int): Number of records to return

**Returns:**
- `list`: Sync history records

**Example:**
```python
history = synchronizer.get_sync_history(limit=5)
for record in history:
    print(f"Sync at {record['start_time']}: {record['success']}")
```

##### `get_sync_statistics() -> dict`

Get synchronization statistics.

**Returns:**
- `dict`: Sync statistics

**Example:**
```python
stats = synchronizer.get_sync_statistics()
print(f"Total syncs: {stats['total_syncs']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Average duration: {stats['average_duration_seconds']}s")
```

## Configuration API

### ConfigManager

Manages configuration loading and validation.

#### Constructor
```python
ConfigManager(config_file: str = None)
```

**Parameters:**
- `config_file` (str, optional): Path to configuration file

#### Methods

##### `get_config() -> RAGPipelineConfig`

Get the current configuration.

**Returns:**
- `RAGPipelineConfig`: Configuration object

**Example:**
```python
config_manager = ConfigManager()
config = config_manager.get_config()
print(f"Environment: {config.environment}")
print(f"Debug mode: {config.debug}")
```

##### `update_config(updates: dict)`

Update configuration with new values.

**Parameters:**
- `updates` (dict): Configuration updates

**Example:**
```python
updates = {
    "debug": True,
    "cache": {"enabled": False}
}
config_manager.update_config(updates)
```

##### `save_config(filepath: str = None)`

Save configuration to file.

**Parameters:**
- `filepath` (str, optional): Path to save configuration

**Example:**
```python
config_manager.save_config("my_config.json")
```

##### `get_environment_config(environment: str) -> RAGPipelineConfig`

Get environment-specific configuration.

**Parameters:**
- `environment` (str): Environment name ("development", "testing", "staging", "production")

**Returns:**
- `RAGPipelineConfig`: Environment-specific configuration

**Example:**
```python
prod_config = config_manager.get_environment_config("production")
print(f"Production debug: {prod_config.debug}")
print(f"Production cache: {prod_config.cache.enabled}")
```

##### `create_sample_config(filepath: str = "rag_config_sample.json")`

Create a sample configuration file.

**Parameters:**
- `filepath` (str): Path for the sample configuration

**Example:**
```python
config_manager.create_sample_config("sample_config.json")
```

### Configuration Classes

#### RAGPipelineConfig

Main configuration class containing all system settings.

**Attributes:**
- `environment` (str): Environment name
- `debug` (bool): Debug mode flag
- `database` (DatabaseConfig): Database configuration
- `vector_store` (VectorStoreConfig): Vector store configuration
- `llm` (LLMConfig): LLM configuration
- `cache` (CacheConfig): Cache configuration
- `optimization` (OptimizationConfig): Optimization configuration
- `web_interface` (WebInterfaceConfig): Web interface configuration
- `monitoring` (MonitoringConfig): Monitoring configuration
- `security` (SecurityConfig): Security configuration

#### DatabaseConfig

Database connection configuration.

**Attributes:**
- `host` (str): Database host
- `port` (int): Database port
- `username` (str): Database username
- `password` (str): Database password
- `database` (str): Database name
- `ssl_mode` (str): SSL mode
- `connection_timeout` (int): Connection timeout
- `max_connections` (int): Maximum connections

#### LLMConfig

LLM provider configuration.

**Attributes:**
- `provider` (str): LLM provider ("openai", "anthropic", "google")
- `model` (str): Model name
- `api_key` (str): API key
- `api_base` (str): API base URL
- `max_tokens` (int): Maximum tokens
- `temperature` (float): Temperature setting
- `timeout` (int): Request timeout
- `retry_attempts` (int): Retry attempts
- `retry_delay` (int): Retry delay

#### CacheConfig

Cache configuration.

**Attributes:**
- `enabled` (bool): Cache enabled flag
- `response_cache_size` (int): Response cache size
- `vector_cache_size` (int): Vector cache size
- `embedding_cache_size` (int): Embedding cache size
- `response_ttl` (int): Response TTL in seconds
- `vector_ttl` (int): Vector TTL in seconds
- `embedding_ttl` (int): Embedding TTL in seconds
- `persistence_enabled` (bool): Persistence enabled flag
- `persistence_file` (str): Persistence file path

## Analytics API

### FitnessAnalytics

Provides fitness analytics and insights.

#### Constructor
```python
FitnessAnalytics(vector_store: VectorStore, query_processor: QueryProcessor = None, retriever: Retriever = None)
```

#### Methods

##### `analyze_trends(metric: str, period: str = "month", n_results: int = 20) -> list`

Analyze trends for a specific metric.

**Parameters:**
- `metric` (str): Metric to analyze
- `period` (str): Analysis period
- `n_results` (int): Number of results to retrieve

**Returns:**
- `list`: List of TrendAnalysis objects

**Example:**
```python
trends = analytics.analyze_trends("weight", "month")
for trend in trends:
    print(f"{trend.metric}: {trend.trend_direction} by {trend.change_percentage:.1f}%")
```

##### `analyze_goals(user_goals: dict) -> list`

Analyze progress towards user goals.

**Parameters:**
- `user_goals` (dict): User goals configuration

**Returns:**
- `list`: List of GoalAnalysis objects

**Example:**
```python
goals = {
    'weight': {
        'target_value': 75,
        'start_value': 80,
        'start_date': '2024-01-01',
        'target_date': '2024-03-01'
    }
}

goal_analyses = analytics.analyze_goals(goals)
for analysis in goal_analyses:
    print(f"{analysis.goal_type}: {analysis.progress_percentage:.1f}% complete")
```

##### `generate_insight_report(user_id: str, period: str = "month") -> InsightReport`

Generate comprehensive insight report.

**Parameters:**
- `user_id` (str): User identifier
- `period` (str): Analysis period

**Returns:**
- `InsightReport`: Comprehensive insight report

**Example:**
```python
report = analytics.generate_insight_report("user123", "month")
print(f"User: {report.user_id}")
print(f"Period: {report.period_analyzed}")
print(f"Key metrics: {report.key_metrics}")
print(f"Recommendations: {report.recommendations}")
```

### Data Models

#### TrendAnalysis

Represents a trend analysis result.

**Attributes:**
- `metric` (str): Metric name
- `period` (str): Analysis period
- `start_value` (float): Starting value
- `end_value` (float): Ending value
- `change` (float): Absolute change
- `change_percentage` (float): Percentage change
- `trend_direction` (str): Trend direction ("increasing", "decreasing", "stable")
- `confidence` (float): Confidence score
- `insights` (list): List of insights
- `recommendations` (list): List of recommendations

#### GoalAnalysis

Represents a goal analysis result.

**Attributes:**
- `goal_type` (str): Goal type
- `current_value` (float): Current value
- `target_value` (float): Target value
- `progress_percentage` (float): Progress percentage
- `days_remaining` (int): Days remaining
- `projected_completion` (datetime): Projected completion date
- `recommendations` (list): List of recommendations
- `risk_factors` (list): List of risk factors

#### InsightReport

Represents a comprehensive insight report.

**Attributes:**
- `user_id` (str): User identifier
- `generated_at` (datetime): Generation timestamp
- `period_analyzed` (str): Analysis period
- `key_metrics` (dict): Key metrics
- `trends` (list): List of trends
- `goals` (list): List of goals
- `recommendations` (list): List of recommendations
- `risk_alerts` (list): List of risk alerts
- `achievements` (list): List of achievements

## Caching API

### CacheManager

Manages all caching systems.

#### Constructor
```python
CacheManager(response_cache_size: int = 1000, vector_cache_size: int = 500, embedding_cache_size: int = 2000)
```

#### Methods

##### `get_response(query: str, context: list, query_type: str) -> dict`

Get cached response.

**Parameters:**
- `query` (str): User query
- `context` (list): Retrieved context
- `query_type` (str): Query type

**Returns:**
- `dict`: Cached response or None

**Example:**
```python
cached_response = cache_manager.get_response(query, context, "trend")
if cached_response:
    print("Using cached response")
else:
    print("No cache hit")
```

##### `set_response(query: str, context: list, query_type: str, response: dict, ttl: int = None) -> bool`

Cache a response.

**Parameters:**
- `query` (str): User query
- `context` (list): Retrieved context
- `query_type` (str): Query type
- `response` (dict): Response to cache
- `ttl` (int, optional): Time-to-live in seconds

**Returns:**
- `bool`: Success status

**Example:**
```python
success = cache_manager.set_response(query, context, "trend", response, ttl=3600)
print(f"Response cached: {success}")
```

##### `get_all_stats() -> dict`

Get statistics for all caches.

**Returns:**
- `dict`: Cache statistics

**Example:**
```python
stats = cache_manager.get_all_stats()
print(f"Total entries: {stats['total_entries']}")
print(f"Response cache hit rate: {stats['response_cache']['hit_rate']}%")
```

##### `clear_all()`

Clear all caches.

**Example:**
```python
cache_manager.clear_all()
print("All caches cleared")
```

##### `optimize_caches()`

Optimize cache performance.

**Example:**
```python
cache_manager.optimize_caches()
print("Caches optimized")
```

## Optimization API

### RAGOptimizer

Main optimizer for the RAG pipeline.

#### Constructor
```python
RAGOptimizer(vector_store: VectorStore, cache_manager: CacheManager = None)
```

#### Methods

##### `optimize_query(query: str, context: list, query_type: str) -> dict`

Optimized query processing.

**Parameters:**
- `query` (str): User query
- `context` (list): Retrieved context
- `query_type` (str): Query type

**Returns:**
- `dict`: Optimized response

**Example:**
```python
response = optimizer.optimize_query(query, context, "trend")
print(f"Optimized response: {response['response']}")
```

##### `get_optimization_statistics() -> dict`

Get comprehensive optimization statistics.

**Returns:**
- `dict`: Optimization statistics

**Example:**
```python
stats = optimizer.get_optimization_statistics()
print(f"Performance metrics: {stats['performance']['total_operations']}")
print(f"Cache hit rate: {stats['cache']['response_cache']['hit_rate']}%")
```

##### `shutdown()`

Shutdown the optimizer.

**Example:**
```python
optimizer.shutdown()
```

### PerformanceMonitor

Monitors and tracks performance metrics.

#### Methods

##### `record_metric(operation: str, duration_ms: float, success: bool, metadata: dict = None)`

Record a performance metric.

**Parameters:**
- `operation` (str): Operation name
- `duration_ms` (float): Duration in milliseconds
- `success` (bool): Success status
- `metadata` (dict, optional): Additional metadata

**Example:**
```python
monitor.record_metric("query_processing", 150.5, True, {"query_type": "trend"})
```

##### `get_statistics(operation: str = None, time_window: timedelta = None) -> dict`

Get performance statistics.

**Parameters:**
- `operation` (str, optional): Filter by operation
- `time_window` (timedelta, optional): Filter by time window

**Returns:**
- `dict`: Performance statistics

**Example:**
```python
stats = monitor.get_statistics("query_processing")
print(f"Average duration: {stats['average_duration_ms']}ms")
print(f"Success rate: {stats['success_rate']}%")
```

## Web Interface API

### WebInterface

Flask-based web application for the RAG chat interface.

#### Constructor
```python
WebInterface(vector_store: VectorStore = None, chat_interface: ChatInterface = None, host: str = "0.0.0.0", port: int = 5000)
```

#### Methods

##### `run(debug: bool = False)`

Start the web interface server.

**Parameters:**
- `debug` (bool): Enable debug mode

**Example:**
```python
web_interface.run(debug=True)
```

##### `create_templates()`

Create basic HTML templates.

**Example:**
```python
web_interface.create_templates()
```

### REST API Endpoints

#### Chat Endpoints

##### `POST /api/chat/send`

Send a message to the chat interface.

**Request Body:**
```json
{
    "message": "How has my weight changed?",
    "user_id": "user123"
}
```

**Response:**
```json
{
    "success": true,
    "response": "Your weight has decreased by 2kg over the last month...",
    "processing_time_ms": 150.5
}
```

##### `GET /api/chat/conversations`

Get list of conversations.

**Response:**
```json
{
    "conversations": [
        {
            "id": "conv_123",
            "title": "Weight Analysis",
            "created_at": "2024-01-01T10:00:00Z",
            "message_count": 5
        }
    ]
}
```

##### `POST /api/chat/conversations`

Create a new conversation.

**Request Body:**
```json
{
    "title": "New Conversation"
}
```

**Response:**
```json
{
    "success": true,
    "conversation_id": "conv_456"
}
```

#### System Endpoints

##### `GET /api/system/health`

Get system health status.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T10:00:00Z",
    "components": {
        "vector_store": "healthy",
        "query_processor": "healthy",
        "retriever": "healthy"
    }
}
```

##### `GET /api/system/info`

Get system information.

**Response:**
```json
{
    "version": "1.0.0",
    "environment": "production",
    "uptime": "2h 30m",
    "total_queries": 150,
    "average_response_time": 120.5
}
```

#### Analytics Endpoints

##### `GET /api/analytics/{user_id}`

Get analytics for a user.

**Parameters:**
- `user_id` (path): User identifier
- `period` (query): Analysis period (default: "month")

**Response:**
```json
{
    "success": true,
    "report": {
        "user_id": "user123",
        "period_analyzed": "month",
        "key_metrics": {
            "weight": 75.5,
            "bmi": 24.2
        },
        "trends_count": 3,
        "recommendations": [
            "Continue your current exercise routine",
            "Monitor your caloric intake"
        ]
    }
}
```

### Socket.IO Events

#### Client to Server

##### `send_message`

Send a message to the chat.

**Data:**
```json
{
    "message": "How has my weight changed?",
    "user_id": "user123"
}
```

##### `typing_start`

Indicate user is typing.

**Data:**
```json
{}
```

##### `typing_stop`

Indicate user stopped typing.

**Data:**
```json
{}
```

#### Server to Client

##### `message_received`

Receive a response message.

**Data:**
```json
{
    "assistant_message": {
        "content": "Your weight has decreased by 2kg...",
        "timestamp": "2024-01-01T10:00:00Z"
    }
}
```

##### `user_typing`

Indicate another user is typing.

**Data:**
```json
{
    "user_id": "user123"
}
```

##### `error`

Receive an error message.

**Data:**
```json
{
    "error": "Failed to process query"
}
```

## Data Models

### IntegrationConfig

Configuration for system integration.

**Attributes:**
- `auto_sync_enabled` (bool): Enable automatic data synchronization
- `sync_interval_minutes` (int): Sync interval in minutes
- `max_retry_attempts` (int): Maximum retry attempts
- `retry_delay_seconds` (int): Retry delay in seconds
- `enable_monitoring` (bool): Enable system monitoring
- `enable_logging` (bool): Enable logging
- `cache_enabled` (bool): Enable caching
- `optimization_enabled` (bool): Enable optimization

### SystemStatus

System status information.

**Attributes:**
- `component` (str): Component name
- `status` (str): Status ("healthy", "warning", "error", "offline")
- `last_check` (datetime): Last check timestamp
- `response_time_ms` (float): Response time in milliseconds
- `error_count` (int): Error count
- `metadata` (dict, optional): Additional metadata

### Message

Represents a chat message.

**Attributes:**
- `id` (str): Message identifier
- `content` (str): Message content
- `sender` (str): Sender ("user" or "assistant")
- `timestamp` (datetime): Message timestamp
- `message_type` (str): Message type ("text", "error", "system")
- `metadata` (dict, optional): Additional metadata

### Conversation

Represents a chat conversation.

**Attributes:**
- `id` (str): Conversation identifier
- `title` (str): Conversation title
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp
- `messages` (list): List of messages
- `metadata` (dict, optional): Additional metadata

## Error Handling

### Error Types

#### ConfigurationError
Raised when configuration is invalid.

**Example:**
```python
try:
    config = ConfigManager("invalid_config.json")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

#### IntegrationError
Raised when integration fails.

**Example:**
```python
try:
    success = integrator.integrate_with_existing_workflow(config)
except IntegrationError as e:
    print(f"Integration error: {e}")
```

#### DataSyncError
Raised when data synchronization fails.

**Example:**
```python
try:
    results = synchronizer.sync_all_data()
except DataSyncError as e:
    print(f"Data sync error: {e}")
```

### Error Response Format

All API endpoints return consistent error responses:

```json
{
    "success": false,
    "error": "Error message",
    "error_code": "ERROR_CODE",
    "timestamp": "2024-01-01T10:00:00Z"
}
```

### Common Error Codes

- `CONFIG_INVALID`: Invalid configuration
- `DB_CONNECTION_FAILED`: Database connection failed
- `LLM_API_ERROR`: LLM API error
- `VECTOR_STORE_ERROR`: Vector store error
- `CACHE_ERROR`: Cache error
- `INTEGRATION_ERROR`: Integration error
- `SYNC_ERROR`: Synchronization error

### Debug Mode

Enable debug mode for detailed error information:

```python
from rag.config import RAGPipelineConfig

config = RAGPipelineConfig()
config.debug = True
config.monitoring.log_level = "DEBUG"
```

---

*This API documentation covers all public interfaces of the RAG Pipeline. For implementation details and advanced usage, refer to the source code and developer guides.* 