"""
Environment Configuration Module
Handles environment-specific model configurations and switching capabilities
"""

import os
from typing import Dict, Any, Optional
from config.llm_config import llm_config, ModelProvider


class EnvironmentConfig:
    """Environment-specific configuration manager"""
    
    def __init__(self):
        self.current_environment = os.getenv("ENVIRONMENT", "development")
        self.configs = self._load_environment_configs()
    
    def _load_environment_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load environment-specific configurations"""
        return {
            "development": {
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini",
                "llm_temperature": 0.0,
                "debug_mode": True,
                "log_level": "DEBUG"
            },
            "staging": {
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "llm_temperature": 0.1,
                "debug_mode": True,
                "log_level": "INFO"
            },
            "production": {
                "llm_provider": "openai",
                "llm_model": "gpt-4o",
                "llm_temperature": 0.0,
                "debug_mode": False,
                "log_level": "WARNING"
            },
            "testing": {
                "llm_provider": "openai",
                "llm_model": "gpt-3.5-turbo",
                "llm_temperature": 0.0,
                "debug_mode": True,
                "log_level": "DEBUG"
            }
        }
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get configuration for current environment"""
        return self.configs.get(self.current_environment, self.configs["development"])
    
    def switch_model(self, provider: str, model: str, temperature: Optional[float] = None) -> bool:
        """
        Switch to a different model configuration
        
        Args:
            provider: Model provider (openai, anthropic, google)
            model: Specific model name
            temperature: Model temperature (optional)
        
        Returns:
            True if switch was successful, False otherwise
        """
        try:
            # Validate provider
            if provider.lower() == "openai":
                provider_enum = ModelProvider.OPENAI
            elif provider.lower() == "anthropic":
                provider_enum = ModelProvider.ANTHROPIC
            elif provider.lower() == "google":
                provider_enum = ModelProvider.GOOGLE
            else:
                print(f"❌ Invalid provider: {provider}")
                return False
            
            # Validate model
            if not llm_config.validate_model(provider_enum, model):
                print(f"❌ Invalid model {model} for provider {provider}")
                return False
            
            # Set environment variables
            os.environ["LLM_PROVIDER"] = provider.lower()
            os.environ["LLM_MODEL"] = model
            if temperature is not None:
                os.environ["LLM_TEMPERATURE"] = str(temperature)
            
            print(f"✅ Switched to {provider}/{model}")
            return True
            
        except Exception as e:
            print(f"❌ Error switching model: {e}")
            return False
    
    def reset_to_environment_default(self) -> bool:
        """Reset to environment default configuration"""
        try:
            config = self.get_current_config()
            return self.switch_model(
                config["llm_provider"],
                config["llm_model"],
                config["llm_temperature"]
            )
        except Exception as e:
            print(f"❌ Error resetting to default: {e}")
            return False
    
    def list_available_models(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """List available models for a provider"""
        if provider:
            if provider.lower() == "openai":
                provider_enum = ModelProvider.OPENAI
            elif provider.lower() == "anthropic":
                provider_enum = ModelProvider.ANTHROPIC
            elif provider.lower() == "google":
                provider_enum = ModelProvider.GOOGLE
            else:
                return {"error": f"Invalid provider: {provider}"}
            
            return {
                "provider": provider,
                "models": llm_config.get_available_models(provider_enum)
            }
        else:
            return {
                "openai": llm_config.get_available_models(ModelProvider.OPENAI),
                "anthropic": llm_config.get_available_models(ModelProvider.ANTHROPIC),
                "google": llm_config.get_available_models(ModelProvider.GOOGLE)
            }
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """Get information about current model configuration"""
        current_config = self.get_current_config()
        return {
            "environment": self.current_environment,
            "provider": os.getenv("LLM_PROVIDER", current_config["llm_provider"]),
            "model": os.getenv("LLM_MODEL", current_config["llm_model"]),
            "temperature": float(os.getenv("LLM_TEMPERATURE", str(current_config["llm_temperature"]))),
            "config": current_config
        }


# Global environment configuration instance
env_config = EnvironmentConfig()


def switch_to_model(provider: str, model: str, temperature: Optional[float] = None) -> bool:
    """Convenience function to switch models"""
    return env_config.switch_model(provider, model, temperature)


def get_current_model_info() -> Dict[str, Any]:
    """Convenience function to get current model info"""
    return env_config.get_current_model_info()


def list_models(provider: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to list available models"""
    return env_config.list_available_models(provider) 