# LLM Modularization System

This document explains the new modular LLM system that allows easy switching between different AI models and prompt management.

## Overview

The system has been modularized to support:
- **Multiple LLM Providers**: OpenAI, Anthropic (Claude), Google (Gemini)
- **External Prompt Management**: All prompts stored in separate files
- **Environment-based Configuration**: Different settings for dev/staging/production
- **Easy Model Switching**: Simple commands to change models

## Architecture

### 1. Configuration Structure (`config/`)
- `llm_config.py`: Centralized model configuration and provider management
- `environment.py`: Environment-specific settings and model switching

### 2. Prompt Management (`prompts/`)
- `reconciliation_prompt.txt`: Data comparison prompts
- `validation_prompt.txt`: Data validation with historical data
- `validation_single_prompt.txt`: Single data point validation
- `report_drafting_prompt.txt`: Email body generation
- `email_evaluation_prompt.txt`: Email quality evaluation

### 3. Utility System (`utils/`)
- `prompt_loader.py`: Loads and formats prompts from files

## Usage

### Environment Variables

Set these in your `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=openai          # openai, anthropic, google
LLM_MODEL=gpt-4o-mini        # Specific model name
LLM_TEMPERATURE=0.0          # Model temperature

# Environment
ENVIRONMENT=development       # development, staging, production, testing
```

### Model Management

Use the `manage_models.py` script to manage models:

```bash
# List all available models
python manage_models.py list

# Check current configuration
python manage_models.py current

# Switch to a different model
python manage_models.py switch --provider openai --model gpt-4o --temperature 0.1

# Switch to Claude
python manage_models.py switch --provider anthropic --model claude-3-5-sonnet

# Switch to Gemini
python manage_models.py switch --provider google --model gemini-1.5-pro

# Reset to environment default
python manage_models.py reset
```

### Available Models

#### OpenAI
- `gpt-4o`: GPT-4 Omni
- `gpt-4o-mini`: GPT-4 Omni Mini
- `gpt-4-turbo`: GPT-4 Turbo
- `gpt-3.5-turbo`: GPT-3.5 Turbo

#### Anthropic (Claude)
- `claude-3-5-sonnet`: Claude 3.5 Sonnet
- `claude-3-opus`: Claude 3 Opus
- `claude-3-sonnet`: Claude 3 Sonnet
- `claude-3-haiku`: Claude 3 Haiku

#### Google (Gemini)
- `gemini-1.5-pro`: Gemini 1.5 Pro
- `gemini-1.5-flash`: Gemini 1.5 Flash
- `gemini-pro`: Gemini Pro

### Environment Configurations

#### Development
- Provider: OpenAI
- Model: GPT-4o-mini
- Temperature: 0.0
- Debug: Enabled
- Log Level: DEBUG

#### Staging
- Provider: OpenAI
- Model: GPT-4o
- Temperature: 0.1
- Debug: Enabled
- Log Level: INFO

#### Production
- Provider: OpenAI
- Model: GPT-4o
- Temperature: 0.0
- Debug: Disabled
- Log Level: WARNING

#### Testing
- Provider: OpenAI
- Model: GPT-3.5-turbo
- Temperature: 0.0
- Debug: Enabled
- Log Level: DEBUG

## Prompt Management

### Editing Prompts

All prompts are stored in the `prompts/` directory as `.txt` files. You can edit them directly:

```bash
# Edit reconciliation prompt
nano prompts/reconciliation_prompt.txt

# Edit email evaluation prompt
nano prompts/email_evaluation_prompt.txt
```

### Prompt Variables

Prompts support variable substitution using Python's `.format()` method:

```python
# In prompt file
Email body to evaluate: {email_body}
Baseline data: {baseline_data}

# In code
prompt = prompt_loader.format_prompt(
    "email_evaluation_prompt",
    email_body=email_content,
    baseline_data=json.dumps(data, indent=2)
)
```

## Code Integration

### Using the New System

The agents have been updated to use the modular system:

```python
# Old way (hardcoded)
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# New way (modular)
from config.llm_config import llm_config
from utils.prompt_loader import prompt_loader

model = llm_config.get_model(temperature=0)
prompt = prompt_loader.format_prompt("prompt_name", **variables)
```

### Adding New Prompts

1. Create a new `.txt` file in `prompts/`
2. Add your prompt template with variables
3. Use `prompt_loader.format_prompt()` in your code

### Adding New Models

1. Add the model to `MODEL_MAPPINGS` in `config/llm_config.py`
2. Add the corresponding LangChain import
3. Update the `get_model()` method if needed

## Migration Guide

### From Hardcoded to Modular

The system automatically handles the migration. All agents now use:
- `llm_config.get_model()` instead of hardcoded `ChatOpenAI`
- `prompt_loader.format_prompt()` instead of hardcoded prompts

### Backward Compatibility

The system maintains backward compatibility:
- Default configuration matches the original setup
- All existing functionality preserved
- Gradual migration possible

## Troubleshooting

### Common Issues

1. **Model not found**: Check available models with `python manage_models.py list`
2. **Prompt not found**: Ensure prompt file exists in `prompts/` directory
3. **API key missing**: Set appropriate API key for the provider (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)

### Debug Mode

Enable debug mode for detailed logging:

```bash
export ENVIRONMENT=development
```

### Testing

Test the system with:

```bash
# Test model switching
python manage_models.py switch --provider openai --model gpt-4o-mini

# Test prompt loading
python -c "from utils.prompt_loader import prompt_loader; print(prompt_loader.load_prompt('reconciliation_prompt'))"
```

## Benefits

1. **Flexibility**: Easy switching between different AI providers
2. **Maintainability**: Prompts stored separately from code
3. **Scalability**: Easy to add new models and prompts
4. **Environment Management**: Different configurations for different environments
5. **Cost Optimization**: Use cheaper models for development/testing
6. **Reliability**: Fallback options if one provider is unavailable 