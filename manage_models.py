#!/usr/bin/env python3
"""
Model Management Script
Simple command-line interface for managing and switching between different LLM models
"""

import sys
import argparse
from config.environment import env_config, switch_to_model, get_current_model_info, list_models


def main():
    parser = argparse.ArgumentParser(description="Manage LLM models for the fitness reporting system")
    parser.add_argument("command", choices=["list", "switch", "current", "reset"], 
                       help="Command to execute")
    parser.add_argument("--provider", choices=["openai", "anthropic", "google"],
                       help="Model provider (for switch command)")
    parser.add_argument("--model", help="Model name (for switch command)")
    parser.add_argument("--temperature", type=float, help="Model temperature (for switch command)")
    
    args = parser.parse_args()
    
    if args.command == "list":
        print("📋 Available Models:")
        print("=" * 50)
        
        models = list_models()
        for provider, provider_models in models.items():
            print(f"\n🔹 {provider.upper()}:")
            for model_name, model_id in provider_models.items():
                print(f"   - {model_name}: {model_id}")
    
    elif args.command == "current":
        print("🔍 Current Model Configuration:")
        print("=" * 50)
        
        info = get_current_model_info()
        print(f"Environment: {info['environment']}")
        print(f"Provider: {info['provider']}")
        print(f"Model: {info['model']}")
        print(f"Temperature: {info['temperature']}")
        print(f"Debug Mode: {info['config']['debug_mode']}")
        print(f"Log Level: {info['config']['log_level']}")
    
    elif args.command == "switch":
        if not args.provider or not args.model:
            print("❌ Error: --provider and --model are required for switch command")
            sys.exit(1)
        
        print(f"🔄 Switching to {args.provider}/{args.model}...")
        success = switch_to_model(args.provider, args.model, args.temperature)
        
        if success:
            print("✅ Model switched successfully!")
            print("\nNew configuration:")
            info = get_current_model_info()
            print(f"Provider: {info['provider']}")
            print(f"Model: {info['model']}")
            print(f"Temperature: {info['temperature']}")
        else:
            print("❌ Failed to switch model")
            sys.exit(1)
    
    elif args.command == "reset":
        print("🔄 Resetting to environment default...")
        success = env_config.reset_to_environment_default()
        
        if success:
            print("✅ Reset to environment default successfully!")
            print("\nCurrent configuration:")
            info = get_current_model_info()
            print(f"Provider: {info['provider']}")
            print(f"Model: {info['model']}")
            print(f"Temperature: {info['temperature']}")
        else:
            print("❌ Failed to reset to default")
            sys.exit(1)


if __name__ == "__main__":
    main() 