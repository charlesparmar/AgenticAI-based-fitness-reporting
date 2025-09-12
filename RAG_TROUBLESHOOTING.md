# RAG Pipeline Troubleshooting Guide

## Table of Contents
1. [Quick Diagnosis](#quick-diagnosis)
2. [Common Issues](#common-issues)
3. [Error Codes](#error-codes)
4. [Performance Issues](#performance-issues)
5. [Configuration Problems](#configuration-problems)
6. [Integration Issues](#integration-issues)
7. [Debug Mode](#debug-mode)
8. [Recovery Procedures](#recovery-procedures)
9. [Support Resources](#support-resources)

## Quick Diagnosis

### System Health Check
```bash
# Check system status
python -c "from rag.integration import RAGAgent; print(RAGAgent().get_system_status())"

# Check configuration
python -c "from rag.config import get_config; print(get_config())"

# Test basic functionality
python test_rag_phase1.py
```

### Environment Check
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(rag|chroma|openai|flask)"

# Check environment variables
env | grep -E "(RAG|OPENAI|DB|WEB)"
```

### Log Analysis
```bash
# Check recent logs
tail -f logs/rag_pipeline.log

# Check error logs
grep "ERROR" logs/rag_pipeline.log | tail -20

# Check performance logs
grep "performance" logs/rag_pipeline.log | tail -10
```

## Common Issues

### 1. "LLM API key not found" Error

**Symptoms:**
- Error message: "LLM API key is required"
- Failed query processing
- Configuration validation errors

**Causes:**
- Missing or incorrect API key in environment
- Invalid API key format
- API key not set in configuration

**Solutions:**

#### Check Environment Variables
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Set API key if missing
export OPENAI_API_KEY="your-actual-api-key"
```

#### Verify .env File
```bash
# Check .env file content
cat .env | grep OPENAI

# Create or update .env file
cat > .env << EOF
OPENAI_API_KEY=your-actual-api-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
EOF
```

#### Test API Key
```python
import openai

try:
    openai.api_key = "your-api-key"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("API key is valid")
except Exception as e:
    print(f"API key error: {e}")
```

### 2. "Database connection failed" Error

**Symptoms:**
- Connection timeout errors
- Database initialization failures
- Data synchronization issues

**Causes:**
- Incorrect database credentials
- Network connectivity issues
- Database server down
- Firewall blocking connections

**Solutions:**

#### Check Database Connection
```bash
# Test network connectivity
ping your-database-host

# Test port connectivity
telnet your-database-host 5000

# Check database credentials
python -c "
from rag.config import get_config
config = get_config()
print(f'Host: {config.database.host}')
print(f'Port: {config.database.port}')
print(f'Database: {config.database.database}')
"
```

#### Verify Database Settings
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

#### Check Firewall Settings
```bash
# Check if port is blocked
sudo ufw status

# Allow database port if needed
sudo ufw allow 5000
```

### 3. "Vector store initialization failed" Error

**Symptoms:**
- ChromaDB initialization errors
- Vector search failures
- Embedding generation issues

**Causes:**
- Insufficient disk space
- Corrupted vector store
- Permission issues
- Memory constraints

**Solutions:**

#### Check Disk Space
```bash
# Check available disk space
df -h

# Check ChromaDB directory
du -sh ./chroma_db
```

#### Clear and Reinitialize Vector Store
```bash
# Backup existing data
cp -r ./chroma_db ./chroma_db_backup

# Clear vector store
rm -rf ./chroma_db

# Reinitialize
python test_rag_phase1.py
```

#### Check Permissions
```bash
# Check directory permissions
ls -la ./chroma_db

# Fix permissions if needed
chmod -R 755 ./chroma_db
```

### 4. "Web interface not accessible" Error

**Symptoms:**
- Cannot access web interface
- Port already in use errors
- Connection refused errors

**Causes:**
- Port already occupied
- Firewall blocking access
- Incorrect host/port configuration
- Service not started

**Solutions:**

#### Check Port Usage
```bash
# Check if port is in use
lsof -i :5000

# Kill process using port if needed
sudo kill -9 $(lsof -t -i:5000)
```

#### Test Different Port
```python
# Start with different port
from rag.integration import RAGAgent

agent = RAGAgent()
agent.start_web_interface(port=8080)
```

#### Check Firewall
```bash
# Check firewall status
sudo ufw status

# Allow web interface port
sudo ufw allow 5000
```

### 5. "Cache performance issues" Error

**Symptoms:**
- Slow response times
- High memory usage
- Cache hit rate issues

**Causes:**
- Cache size too large
- Memory pressure
- Cache corruption
- Inefficient cache configuration

**Solutions:**

#### Clear Cache
```python
# Clear all caches
from rag.integration import RAGAgent

agent = RAGAgent()
agent.cache_manager.clear_all()
print("Cache cleared")
```

#### Optimize Cache Configuration
```python
# Reduce cache sizes
from rag.config import CacheConfig

cache_config = CacheConfig(
    response_cache_size=500,  # Reduced from 1000
    vector_cache_size=250,    # Reduced from 500
    embedding_cache_size=1000 # Reduced from 2000
)
```

#### Monitor Cache Performance
```python
# Check cache statistics
stats = agent.cache_manager.get_all_stats()
print(f"Cache hit rate: {stats['response_cache']['hit_rate']}%")
print(f"Memory usage: {stats['response_cache']['utilization']}%")
```

## Error Codes

### Configuration Errors

#### CONFIG_INVALID
**Description:** Invalid configuration settings
**Solutions:**
```python
# Validate configuration
from rag.config import ConfigManager

config_manager = ConfigManager()
try:
    config = config_manager.get_config()
    print("Configuration is valid")
except Exception as e:
    print(f"Configuration error: {e}")
```

#### CONFIG_MISSING_REQUIRED
**Description:** Required configuration values missing
**Solutions:**
```python
# Check required fields
required_fields = ['OPENAI_API_KEY', 'DB_HOST', 'DB_NAME']
for field in required_fields:
    if not os.getenv(field):
        print(f"Missing required field: {field}")
```

### Database Errors

#### DB_CONNECTION_FAILED
**Description:** Database connection failed
**Solutions:**
```python
# Test database connection
import sqlite3

try:
    conn = sqlite3.connect("test.db")
    conn.close()
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### DB_QUERY_FAILED
**Description:** Database query execution failed
**Solutions:**
```python
# Test database queries
try:
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("Database query successful")
except Exception as e:
    print(f"Database query failed: {e}")
```

### LLM Errors

#### LLM_API_ERROR
**Description:** LLM API call failed
**Solutions:**
```python
# Test LLM API
import openai

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Test"}]
    )
    print("LLM API working")
except Exception as e:
    print(f"LLM API error: {e}")
```

#### LLM_RATE_LIMIT
**Description:** LLM API rate limit exceeded
**Solutions:**
```python
# Implement rate limiting
import time

def rate_limited_api_call():
    try:
        # API call
        pass
    except Exception as e:
        if "rate limit" in str(e).lower():
            time.sleep(60)  # Wait 1 minute
            # Retry
```

### Vector Store Errors

#### VECTOR_STORE_ERROR
**Description:** Vector store operation failed
**Solutions:**
```python
# Test vector store
from rag.vector_store import VectorStore

try:
    vector_store = VectorStore()
    info = vector_store.get_collection_info()
    print("Vector store working")
except Exception as e:
    print(f"Vector store error: {e}")
```

#### VECTOR_STORE_CORRUPTED
**Description:** Vector store data corrupted
**Solutions:**
```bash
# Rebuild vector store
rm -rf ./chroma_db
python test_rag_phase1.py
```

### Integration Errors

#### INTEGRATION_ERROR
**Description:** System integration failed
**Solutions:**
```python
# Test integration
from rag.integration import SystemIntegrator

integrator = SystemIntegrator()
status = integrator.get_integration_status()
print(f"Integration status: {status}")
```

#### SYNC_ERROR
**Description:** Data synchronization failed
**Solutions:**
```python
# Test data synchronization
from rag.integration import DataSynchronizer

synchronizer = DataSynchronizer(agent)
results = synchronizer.sync_all_data()
print(f"Sync results: {results}")
```

## Performance Issues

### Slow Query Processing

**Symptoms:**
- Long response times
- High CPU usage
- Memory pressure

**Solutions:**

#### Enable Caching
```python
# Enable response caching
from rag.integration import IntegrationConfig

config = IntegrationConfig(cache_enabled=True)
agent = RAGAgent(config)
```

#### Optimize Vector Search
```python
# Optimize search parameters
from rag.vector_store import VectorStore

vector_store = VectorStore()
vector_store.similarity_threshold = 0.8  # Increase threshold
vector_store.max_results = 10  # Reduce results
```

#### Monitor Performance
```python
# Monitor system performance
import psutil

cpu_percent = psutil.cpu_percent()
memory_percent = psutil.virtual_memory().percent
print(f"CPU: {cpu_percent}%, Memory: {memory_percent}%")
```

### High Memory Usage

**Symptoms:**
- Out of memory errors
- Slow system performance
- Cache eviction

**Solutions:**

#### Reduce Cache Sizes
```python
# Reduce cache sizes
cache_config = CacheConfig(
    response_cache_size=500,
    vector_cache_size=250,
    embedding_cache_size=1000
)
```

#### Optimize Data Loading
```python
# Use batch processing
def batch_process_data(data, batch_size=100):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        # Process batch
        yield batch
```

#### Monitor Memory Usage
```python
# Monitor memory usage
import psutil

process = psutil.Process()
memory_info = process.memory_info()
print(f"Memory usage: {memory_info.rss / 1024 / 1024} MB")
```

### Slow Vector Search

**Symptoms:**
- Long search times
- High CPU usage during search
- Poor search results

**Solutions:**

#### Optimize Search Parameters
```python
# Optimize search parameters
vector_store = VectorStore()
vector_store.similarity_threshold = 0.7
vector_store.max_results = 5
```

#### Use Caching
```python
# Enable vector search caching
cache_manager = CacheManager()
cache_manager.vector_cache.enabled = True
```

#### Monitor Search Performance
```python
# Monitor search performance
from rag.optimization import PerformanceMonitor

monitor = PerformanceMonitor()
stats = monitor.get_statistics("vector_search")
print(f"Average search time: {stats['average_duration_ms']}ms")
```

## Configuration Problems

### Environment Variable Issues

**Symptoms:**
- Configuration not loading
- Default values being used
- Environment-specific issues

**Solutions:**

#### Check Environment Variables
```bash
# List all environment variables
env | grep -E "(RAG|OPENAI|DB|WEB)"

# Set missing variables
export RAG_ENVIRONMENT=development
export RAG_DEBUG=true
```

#### Validate Configuration
```python
# Validate configuration
from rag.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.get_config()
print(f"Environment: {config.environment}")
print(f"Debug mode: {config.debug}")
```

### Configuration File Issues

**Symptoms:**
- Configuration file not found
- Invalid JSON format
- Missing required fields

**Solutions:**

#### Check Configuration File
```bash
# Check if file exists
ls -la rag_config.json

# Validate JSON format
python -m json.tool rag_config.json
```

#### Create Sample Configuration
```python
# Create sample configuration
from rag.config import ConfigManager

config_manager = ConfigManager()
config_manager.create_sample_config("sample_config.json")
```

## Integration Issues

### External System Integration

**Symptoms:**
- Integration hooks failing
- Data source errors
- Workflow integration issues

**Solutions:**

#### Test Integration Hooks
```python
# Test integration hooks
from rag.integration import SystemIntegrator

integrator = SystemIntegrator()

def test_hook():
    return {"status": "success"}

integrator.register_integration_hook("test", test_hook)
result = integrator.trigger_integration_hook("test")
print(f"Hook result: {result}")
```

#### Test Data Sources
```python
# Test data sources
class TestDataSource:
    def get_data(self):
        return {"test": "data"}

integrator.register_data_source("test", TestDataSource())
data = integrator.get_data_from_source("test")
print(f"Data: {data}")
```

### Data Synchronization Issues

**Symptoms:**
- Sync failures
- Data inconsistencies
- Sync history issues

**Solutions:**

#### Test Data Synchronization
```python
# Test data synchronization
from rag.integration import DataSynchronizer

synchronizer = DataSynchronizer(agent)
results = synchronizer.sync_all_data()
print(f"Sync results: {results}")
```

#### Check Sync History
```python
# Check sync history
history = synchronizer.get_sync_history(limit=10)
for record in history:
    print(f"Sync at {record['start_time']}: {record['success']}")
```

#### Monitor Sync Performance
```python
# Monitor sync performance
stats = synchronizer.get_sync_statistics()
print(f"Success rate: {stats['success_rate']}%")
print(f"Average duration: {stats['average_duration_seconds']}s")
```

## Debug Mode

### Enable Debug Mode

#### Configuration Debug
```python
# Enable debug mode
from rag.config import RAGPipelineConfig

config = RAGPipelineConfig()
config.debug = True
config.monitoring.log_level = "DEBUG"
```

#### Logging Debug
```python
# Configure debug logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### Debug Information Collection

#### System Information
```python
# Collect system information
import platform
import psutil

print(f"Python version: {platform.python_version()}")
print(f"Platform: {platform.platform()}")
print(f"CPU count: {psutil.cpu_count()}")
print(f"Memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f} GB")
```

#### Component Status
```python
# Check component status
from rag.integration import RAGAgent

agent = RAGAgent()
status = agent.get_system_status()
print(f"Overall health: {status['overall_health']}")
for component, info in status['components'].items():
    print(f"{component}: {info['status']}")
```

#### Performance Metrics
```python
# Collect performance metrics
from rag.optimization import PerformanceMonitor

monitor = PerformanceMonitor()
stats = monitor.get_statistics()
print(f"Total operations: {stats['total_operations']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Average duration: {stats['average_duration_ms']}ms")
```

## Recovery Procedures

### System Recovery

#### Complete System Reset
```bash
# Backup current data
cp -r ./chroma_db ./chroma_db_backup
cp rag_config.json rag_config_backup.json

# Clear all data
rm -rf ./chroma_db
rm -f rag_config.json

# Reinitialize system
python test_rag_phase1.py
```

#### Component Recovery
```python
# Reinitialize specific components
from rag.vector_store import VectorStore
from rag.cache import CacheManager

# Reset vector store
vector_store = VectorStore()
vector_store.reset_collection()

# Clear cache
cache_manager = CacheManager()
cache_manager.clear_all()
```

### Data Recovery

#### Backup and Restore
```bash
# Create backup
tar -czf rag_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    ./chroma_db \
    ./logs \
    rag_config.json \
    .env

# Restore from backup
tar -xzf rag_backup_20240101_120000.tar.gz
```

#### Selective Recovery
```python
# Recover specific data
from rag.vector_store import VectorStore

vector_store = VectorStore()
# Restore specific documents
vector_store.add_documents(backup_documents)
```

## Support Resources

### Documentation
- **User Guide**: `RAG_USER_GUIDE.md`
- **API Documentation**: `RAG_API_DOCS.md`
- **Developer Guide**: `RAG_DEVELOPER_GUIDE.md`

### Log Files
- **Application Logs**: `./logs/rag_pipeline.log`
- **Error Logs**: `./logs/errors.log`
- **Performance Logs**: `./logs/performance.log`
- **Debug Logs**: `debug.log`

### Test Scripts
```bash
# Run all tests
python test_rag_phase1.py
python test_rag_phase2.py
python test_rag_phase3.py
python test_rag_phase4.py
python test_rag_phase5.py
python test_rag_phase6.py

# Run integration tests
python -m pytest tests/test_integration.py -v
```

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the latest documentation
- **Examples**: Review example code and configurations

### Emergency Contacts
- **Critical Issues**: Create urgent GitHub issue
- **Security Issues**: Report via security contact
- **Performance Issues**: Use performance monitoring tools

---

## Quick Reference

### Common Commands
```bash
# System health check
python -c "from rag.integration import RAGAgent; print(RAGAgent().get_system_status())"

# Configuration check
python -c "from rag.config import get_config; print(get_config())"

# Clear cache
python -c "from rag.integration import RAGAgent; RAGAgent().cache_manager.clear_all()"

# Reset vector store
python -c "from rag.vector_store import VectorStore; VectorStore().reset_collection()"

# Start debug mode
python -c "from rag.integration import RAGAgent; RAGAgent().start_web_interface(debug=True)"
```

### Error Code Reference
- `CONFIG_INVALID`: Invalid configuration
- `DB_CONNECTION_FAILED`: Database connection failed
- `LLM_API_ERROR`: LLM API error
- `VECTOR_STORE_ERROR`: Vector store error
- `INTEGRATION_ERROR`: Integration error
- `SYNC_ERROR`: Synchronization error

### Performance Thresholds
- **Response Time**: < 2 seconds
- **Memory Usage**: < 80% of available RAM
- **CPU Usage**: < 70% under normal load
- **Cache Hit Rate**: > 80%
- **Success Rate**: > 95%

---

*This troubleshooting guide covers the most common issues and solutions for the RAG Pipeline. For additional support, refer to the documentation or create a GitHub issue.* 