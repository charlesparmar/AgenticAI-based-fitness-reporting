# Plan for Modularizing LLM Prompts and Model Configuration

## Phase 1: Create Configuration Structure
**File to create:** `config/llm_config.py`
- Create a centralized configuration file for LLM models
- Define model mappings (OpenAI, Claude, Gemini)
- Create a model selection mechanism

## Phase 2: Create Prompts Directory Structure
**Files to create:** `prompts/` directory with individual prompt files
- `prompts/reconciliation_prompt.txt`
- `prompts/validation_prompt.txt`
- `prompts/report_drafting_prompt.txt`
- `prompts/email_evaluation_prompt.txt`
- `prompts/email_body_prompt.txt`

## Phase 3: Create Prompt Loader Utility
**File to create:** `utils/prompt_loader.py`
- Create a utility class to load prompts from files
- Add error handling for missing prompt files
- Create a standardized prompt loading interface

## Phase 4: Update Reconciliation Agent
**File to modify:** `Agents/recon_agent.py`
- Replace hardcoded prompt with prompt loader
- Replace hardcoded model with config-based model
- Test the agent functionality

## Phase 5: Update Data Validation Agent
**File to modify:** `Agents/data_validation_agent.py`
- Replace hardcoded prompt with prompt loader
- Replace hardcoded model with config-based model
- Test the agent functionality

## Phase 6: Update Report Drafter Agent
**File to modify:** `Agents/report_drafter_agent.py`
- Replace hardcoded prompt with prompt loader
- Replace hardcoded model with config-based model
- Test the agent functionality

## Phase 7: Update Email Evaluation Agent
**File to modify:** `Agents/evaluate_email_body_agent.py`
- Replace hardcoded prompt with prompt loader
- Replace hardcoded model with config-based model
- Test the agent functionality

## Phase 8: Update Final Email Agent
**File to modify:** `Agents/final_email_agent.py`
- Replace hardcoded prompt with prompt loader
- Replace hardcoded model with config-based model
- Test the agent functionality

## Phase 9: Update Main Workflow
**File to modify:** `reporting_workflow.py`
- Import and initialize the new configuration system
- Ensure all agents use the new prompt and model system
- Test the complete workflow

## Phase 10: Create Environment Configuration
**File to create:** `config/environment.py`
- Create environment-specific model configurations
- Add model switching capabilities
- Create a simple interface to change models

Each phase can be completed independently, and the code will remain functional after each phase. This allows you to test incrementally and rollback if needed. 