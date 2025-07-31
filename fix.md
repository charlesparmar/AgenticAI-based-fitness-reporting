# Model Configuration System Fix

## Problem
The orchestrated workflow is showing `gpt-4o-mini` in LangSmith instead of the configured model because the model configuration system is not properly loading from config files and falling back to hardcoded defaults.

## Root Causes
1. Environment variables `LLM_PROVIDER`, `LLM_MODEL`, `LLM_TEMPERATURE` are not set
2. LLM config instance is created once at import time and doesn't reload dynamically
3. Model switching doesn't persist across shell sessions
4. Hardcoded defaults override config-driven values

## Precise Steps to Fix

### Step 1: Fix LLM Config Initialization
- Modify `config/llm_config.py` to reload configuration dynamically instead of once at import
- Change the `_load_from_env()` method to be called each time `get_model()` is invoked
- Remove the hardcoded defaults in `__init__()` method

### Step 2: Update Environment Config Loading
- Modify `config/environment.py` to ensure environment config is loaded before LLM config
- Update `get_current_model_info()` to always read from current environment config, not cached values
- Remove fallback to hardcoded defaults in environment config

### Step 3: Fix Model Configuration Persistence
- Add environment variable persistence in `manage_models.py switch` command
- Write model configuration to `.env` file when switching models
- Ensure `.env` file is loaded before LLM config initialization

### Step 4: Update Orchestrated Workflow
- Modify `reporting_workflow.py` to reload LLM config before each agent execution
- Ensure each agent uses fresh model configuration, not cached values
- Add model configuration logging to verify correct model is being used

### Step 5: Remove Hardcoded Defaults
- Remove all hardcoded `"gpt-4o-mini"` references from config files
- Replace with environment-driven configuration loading
- Update all agent files to use `llm_config.get_model()` consistently

### Step 6: Add Configuration Validation
- Add validation to ensure model configuration is properly loaded
- Add debug logging to show which model is being used in each agent
- Verify LangSmith traces show correct model name

### Step 7: Test Configuration Flow
- Test model switching with `manage_models.py switch`
- Verify configuration persists across shell sessions
- Confirm orchestrated workflow uses switched model in LangSmith

## Files to Modify
1. `config/llm_config.py`
2. `config/environment.py`
3. `manage_models.py`
4. `reporting_workflow.py`
5. All agent files in `Agents/` directory

## Expected Result
- Model configuration loads from environment config files
- Model switching persists across sessions
- LangSmith shows the correct configured model instead of hardcoded `gpt-4o-mini`
- All agents use the centralized model configuration system 