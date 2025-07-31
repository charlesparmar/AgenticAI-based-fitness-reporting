"""
LLM Configuration Module
Centralized configuration for different LLM models and their settings
"""

import os
from typing import Dict, Any, Optional
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI


class ModelProvider(Enum):
    """Enum for different LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class LLMConfig:
    """Configuration class for LLM models"""
    
    # Model mappings for different providers
    MODEL_MAPPINGS = {
        ModelProvider.OPENAI: {
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini",
            "gpt-4-turbo": "gpt-4-turbo",
            "gpt-3.5-turbo": "gpt-3.5-turbo"
        },
        ModelProvider.ANTHROPIC: {
            "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-sonnet-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307"
        },
        ModelProvider.GOOGLE: {
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-pro": "gemini-pro"
        }
    }
    
    def __init__(self):
        # Default configuration
        self.default_provider = ModelProvider.OPENAI
        self.default_model = "gpt-4o-mini"
        self.default_temperature = 0.0
        
        # Load from environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables and environment config"""
        # First try to load from environment variables
        provider_str = os.getenv("LLM_PROVIDER")
        env_model = os.getenv("LLM_MODEL")
        env_temp = os.getenv("LLM_TEMPERATURE")
        
        # If environment variables are not set, load from environment configuration
        if not provider_str or not env_model:
            try:
                from config.environment import env_config
                current_config = env_config.get_current_config()
                if not provider_str:
                    provider_str = current_config["llm_provider"]
                if not env_model:
                    env_model = current_config["llm_model"]
                if not env_temp:
                    env_temp = str(current_config["llm_temperature"])
            except ImportError:
                pass
        
        # Set provider
        if provider_str:
            provider_str = provider_str.lower()
            if provider_str == "anthropic":
                self.default_provider = ModelProvider.ANTHROPIC
            elif provider_str == "google":
                self.default_provider = ModelProvider.GOOGLE
            else:
                self.default_provider = ModelProvider.OPENAI
        
        # Set model
        if env_model:
            self.default_model = env_model
        
        # Set temperature
        if env_temp:
            try:
                self.default_temperature = float(env_temp)
            except ValueError:
                pass
    
    def get_model(self, 
                  provider: Optional[ModelProvider] = None, 
                  model_name: Optional[str] = None,
                  temperature: Optional[float] = None) -> Any:
        """
        Get an LLM model instance based on configuration
        
        Args:
            provider: Model provider (defaults to configured default)
            model_name: Specific model name (defaults to configured default)
            temperature: Model temperature (defaults to configured default)
        
        Returns:
            LangChain LLM instance
        """
        provider = provider or self.default_provider
        model_name = model_name or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        
        if provider == ModelProvider.OPENAI:
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif provider == ModelProvider.ANTHROPIC:
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        elif provider == ModelProvider.GOOGLE:
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                api_key=os.getenv("GOOGLE_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def get_available_models(self, provider: Optional[ModelProvider] = None) -> Dict[str, str]:
        """Get available models for a provider"""
        provider = provider or self.default_provider
        return self.MODEL_MAPPINGS.get(provider, {})
    
    def validate_model(self, provider: ModelProvider, model_name: str) -> bool:
        """Validate if a model exists for a provider"""
        available_models = self.get_available_models(provider)
        return model_name in available_models


# Global configuration instance
llm_config = LLMConfig() 