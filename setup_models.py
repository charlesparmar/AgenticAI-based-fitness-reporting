#!/usr/bin/env python3
"""
Model Configuration Setup Script
Helps set up environment variables for 3 different model configurations
"""

import os
import sys
from dotenv import load_dotenv

def setup_model_config():
    """Set up environment variables for model configurations"""
    
    print("🤖 Model Configuration Setup")
    print("=" * 50)
    print("This script will help you set up 3 different model configurations.")
    print("Temperature will be hardcoded to 0.0 for all models.")
    print()
    
    # Load existing .env file if it exists
    load_dotenv()
    
    # Model configurations
    models = {}
    
    print("📋 Available Models:")
    print("🔹 OPENAI: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo")
    print("🔹 ANTHROPIC: claude-3-5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku")
    print("🔹 GOOGLE: gemini-1.5-pro, gemini-1.5-flash, gemini-pro")
    print()
    
    # Get Model 1 configuration
    print("🎯 Model 1 Configuration:")
    print("-" * 30)
    provider1 = input("Enter provider for Model 1 (openai/anthropic/google): ").lower().strip()
    
    if provider1 == "openai":
        model1 = input("Enter OpenAI model (gpt-4o/gpt-4o-mini/gpt-4-turbo/gpt-3.5-turbo): ").strip()
    elif provider1 == "anthropic":
        model1 = input("Enter Anthropic model (claude-3-5-sonnet/claude-3-opus/claude-3-sonnet/claude-3-haiku): ").strip()
    elif provider1 == "google":
        model1 = input("Enter Google model (gemini-1.5-pro/gemini-1.5-flash/gemini-pro): ").strip()
    else:
        print("❌ Invalid provider. Please use: openai, anthropic, or google")
        return
    
    models["model1"] = {"provider": provider1, "model": model1, "temperature": 0.0}
    
    print()
    
    # Get Model 2 configuration
    print("🎯 Model 2 Configuration:")
    print("-" * 30)
    provider2 = input("Enter provider for Model 2 (openai/anthropic/google): ").lower().strip()
    
    if provider2 == "openai":
        model2 = input("Enter OpenAI model (gpt-4o/gpt-4o-mini/gpt-4-turbo/gpt-3.5-turbo): ").strip()
    elif provider2 == "anthropic":
        model2 = input("Enter Anthropic model (claude-3-5-sonnet/claude-3-opus/claude-3-sonnet/claude-3-haiku): ").strip()
    elif provider2 == "google":
        model2 = input("Enter Google model (gemini-1.5-pro/gemini-1.5-flash/gemini-pro): ").strip()
    else:
        print("❌ Invalid provider. Please use: openai, anthropic, or google")
        return
    
    models["model2"] = {"provider": provider2, "model": model2, "temperature": 0.0}
    
    print()
    
    # Get Model 3 configuration
    print("🎯 Model 3 Configuration:")
    print("-" * 30)
    provider3 = input("Enter provider for Model 3 (openai/anthropic/google): ").lower().strip()
    
    if provider3 == "openai":
        model3 = input("Enter OpenAI model (gpt-4o/gpt-4o-mini/gpt-4-turbo/gpt-3.5-turbo): ").strip()
    elif provider3 == "anthropic":
        model3 = input("Enter Anthropic model (claude-3-5-sonnet/claude-3-opus/claude-3-sonnet/claude-3-haiku): ").strip()
    elif provider3 == "google":
        model3 = input("Enter Google model (gemini-1.5-pro/gemini-1.5-flash/gemini-pro): ").strip()
    else:
        print("❌ Invalid provider. Please use: openai, anthropic, or google")
        return
    
    models["model3"] = {"provider": provider3, "model": model3, "temperature": 0.0}
    
    print()
    
    # Show summary
    print("📊 Configuration Summary:")
    print("=" * 50)
    for i, (key, config) in enumerate(models.items(), 1):
        print(f"Model {i}: {config['provider']}/{config['model']} (temp: {config['temperature']})")
    
    print()
    
    # Ask which model to set as default
    default_model = input("Which model should be the default? (1/2/3): ").strip()
    
    if default_model not in ["1", "2", "3"]:
        print("❌ Invalid choice. Using Model 1 as default.")
        default_model = "1"
    
    default_key = f"model{default_model}"
    default_config = models[default_key]
    
    # Set environment variables
    os.environ["LLM_PROVIDER"] = default_config["provider"]
    os.environ["LLM_MODEL"] = default_config["model"]
    os.environ["LLM_TEMPERATURE"] = str(default_config["temperature"])
    
    # Set model-specific environment variables
    for i, (key, config) in enumerate(models.items(), 1):
        os.environ[f"LLM_PROVIDER_{i}"] = config["provider"]
        os.environ[f"LLM_MODEL_{i}"] = config["model"]
        os.environ[f"LLM_TEMPERATURE_{i}"] = str(config["temperature"])
    
    print()
    print("✅ Environment variables set successfully!")
    print(f"Default model: {default_config['provider']}/{default_config['model']}")
    print()
    
    # Show current environment variables
    print("🔍 Current Environment Variables:")
    print("-" * 40)
    print(f"LLM_PROVIDER: {os.environ.get('LLM_PROVIDER', 'Not set')}")
    print(f"LLM_MODEL: {os.environ.get('LLM_MODEL', 'Not set')}")
    print(f"LLM_TEMPERATURE: {os.environ.get('LLM_TEMPERATURE', 'Not set')}")
    print()
    
    for i in range(1, 4):
        print(f"Model {i}:")
        print(f"  LLM_PROVIDER_{i}: {os.environ.get(f'LLM_PROVIDER_{i}', 'Not set')}")
        print(f"  LLM_MODEL_{i}: {os.environ.get(f'LLM_MODEL_{i}', 'Not set')}")
        print(f"  LLM_TEMPERATURE_{i}: {os.environ.get(f'LLM_TEMPERATURE_{i}', 'Not set')}")
    
    print()
    print("💡 To make these permanent, add them to your .env file.")
    print("💡 You can switch between models using: python3 manage_models.py switch")

if __name__ == "__main__":
    setup_model_config() 