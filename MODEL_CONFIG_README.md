# Model Configuration System

This system allows you to assign different LLM models to different prompts by editing a simple text file.

## Overview

The model configuration system consists of:
- `prompts/model_config.txt` - Configuration file where you assign models to prompts
- Updated `utils/prompt_loader.py` - Enhanced prompt loader that reads the configuration
- `example_model_usage.py` - Example script demonstrating usage

## Model Definitions

The system supports three model assignments:

- **Model 1** = `gpt-4o-mini` (OpenAI)
- **Model 2** = `claude-3-5-sonnet-20241022` (Anthropic)
- **Model 3** = `gemini-1.5-flash` (Google)

## Configuration File

Edit `prompts/model_config.txt` to assign models to prompts:

```txt
# Model Configuration for Prompts
# This file maps each prompt to a specific model
# Update the model assignments below to change which model is used for each prompt

# Model Definitions:
# Model 1 = gpt-4o-mini
# Model 2 = claude-3-5-sonnet-20241022
# Model 3 = gemini-1.5-flash

# Prompt to Model Mappings:
email_evaluation_prompt = Model 1
validation_prompt = Model 2
validation_single_prompt = Model 1
report_drafting_prompt = Model 3
reconciliation_prompt = Model 1
```

## Usage in Code

### Basic Usage

```python
from utils.prompt_loader import prompt_loader

# Get the appropriate model for a specific prompt
model = prompt_loader.get_model_for_prompt("email_evaluation_prompt", temperature=0.7)

# Load the prompt content
prompt_content = prompt_loader.load_prompt("email_evaluation_prompt")

# Use the model and prompt together
response = model.invoke(prompt_content)
```

### Advanced Usage

```python
# Get model with custom temperature
model = prompt_loader.get_model_for_prompt("report_drafting_prompt", temperature=0.9)

# Format prompt with variables
formatted_prompt = prompt_loader.format_prompt("validation_prompt", data=data, threshold=0.8)

# Get all available prompts
available_prompts = prompt_loader.get_available_prompts()

# Check current model assignments
for prompt_name in available_prompts:
    if prompt_name != "model_config":
        model_assignment = prompt_loader.model_config.get(prompt_name, "Model 1 (default)")
        print(f"{prompt_name}: {model_assignment}")
```

## Changing Model Assignments

To change which model is used for a prompt:

1. Edit `prompts/model_config.txt`
2. Change the model assignment for the desired prompt
3. Save the file
4. The changes take effect immediately when you restart your application

### Example Changes

```txt
# Change email evaluation to use Claude
email_evaluation_prompt = Model 2

# Change report drafting to use GPT-4o-mini
report_drafting_prompt = Model 1

# Change validation to use Gemini
validation_prompt = Model 3
```

## Environment Variables

Make sure you have the appropriate API keys set in your environment:

```bash
# For OpenAI (Model 1)
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic (Model 2)
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For Google (Model 3)
export GOOGLE_API_KEY="your-google-api-key"
```

## Testing

Run the example script to test the configuration:

```bash
python3 example_model_usage.py
```

This will show:
- Available prompts
- Current model assignments
- Example of getting a model for a specific prompt
- Example of loading prompt content

## Error Handling

The system includes robust error handling:

- If `model_config.txt` is missing, all prompts default to Model 1
- If a prompt is not found in the config, it defaults to Model 1
- If an unknown model assignment is used, it defaults to Model 1
- All errors are logged with warnings but don't crash the application

## Integration with Existing Code

The new functionality is backward compatible. Existing code that uses `prompt_loader.load_prompt()` will continue to work unchanged. The new `get_model_for_prompt()` method is an additional feature that can be used when you need the appropriate model for a specific prompt. 