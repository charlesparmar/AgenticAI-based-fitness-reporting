"""
Prompt Loader Utility
Loads prompts from external files with error handling and formatting
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from config.llm_config import llm_config, ModelProvider


class PromptLoader:
    """Utility class for loading and formatting prompts from files"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        """
        Initialize the prompt loader
        
        Args:
            prompts_dir: Directory containing prompt files
        """
        self.prompts_dir = Path(prompts_dir)
        
        # Ensure prompts directory exists
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self.prompts_dir}")
        
        # Load model configuration
        self.model_config = self._load_model_config()
    
    def _load_model_config(self) -> Dict[str, str]:
        """
        Load model configuration from model_config.txt
        
        Returns:
            Dictionary mapping prompt names to model assignments
        """
        config_file = self.prompts_dir / "model_config.txt"
        
        if not config_file.exists():
            print(f"Warning: Model config file not found: {config_file}")
            return {}
        
        try:
            model_config = {}
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line.startswith('#') or not line or '=' not in line:
                        continue
                    
                    # Parse prompt = model assignment
                    if '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            prompt_name = parts[0].strip()
                            model_assignment = parts[1].strip()
                            model_config[prompt_name] = model_assignment
            
            return model_config
        except Exception as e:
            print(f"Warning: Error loading model config: {e}")
            return {}
    
    def _get_model_from_assignment(self, model_assignment: str) -> tuple[ModelProvider, str]:
        """
        Convert model assignment (Model 1, Model 2, Model 3) to provider and model name
        
        Args:
            model_assignment: String like "Model 1", "Model 2", "Model 3"
        
        Returns:
            Tuple of (ModelProvider, model_name)
        """
        # Get model number from assignment (e.g., "Model 1" -> "1")
        if not model_assignment.startswith("Model "):
            raise ValueError(f"Invalid model assignment format: {model_assignment}")
        
        model_number = model_assignment.split(" ")[1]
        
        # Get provider and model from environment variables
        provider_key = f"LLM_PROVIDER_{model_number}"
        model_key = f"LLM_MODEL_{model_number}"
        
        provider_str = os.getenv(provider_key)
        model_name = os.getenv(model_key)
        
        if not provider_str or not model_name:
            raise ValueError(f"Environment variables not set for {model_assignment}: {provider_key}={provider_str}, {model_key}={model_name}")
        
        # Convert provider string to ModelProvider enum
        if provider_str.lower() == "openai":
            provider = ModelProvider.OPENAI
        elif provider_str.lower() == "anthropic":
            provider = ModelProvider.ANTHROPIC
        elif provider_str.lower() == "google":
            provider = ModelProvider.GOOGLE
        else:
            raise ValueError(f"Invalid provider '{provider_str}' for {model_assignment}")
        
        return (provider, model_name)
    
    def get_model_for_prompt(self, prompt_name: str, temperature: Optional[float] = None) -> Any:
        """
        Get the appropriate LLM model for a specific prompt
        
        Args:
            prompt_name: Name of the prompt file (without extension)
            temperature: Optional temperature override
        
        Returns:
            LangChain LLM instance configured for the prompt
        """
        # Get model assignment for this prompt
        if prompt_name not in self.model_config:
            raise ValueError(f"No model assignment found for prompt '{prompt_name}' in model_config.txt")
        
        model_assignment = self.model_config[prompt_name]
        
        # Convert assignment to provider and model
        provider, model_name = self._get_model_from_assignment(model_assignment)
        
        print(f"🔧 Using {provider.value}/{model_name} for prompt '{prompt_name}'")
        
        # Get the model instance
        return llm_config.get_model(provider=provider, model_name=model_name, temperature=temperature)
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt from file
        
        Args:
            prompt_name: Name of the prompt file (without extension)
        
        Returns:
            Prompt content as string
        
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            raise IOError(f"Error reading prompt file {prompt_file}: {e}")
    
    def format_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Load and format a prompt with variables
        
        Args:
            prompt_name: Name of the prompt file (without extension)
            **kwargs: Variables to format into the prompt
        
        Returns:
            Formatted prompt string
        """
        prompt_template = self.load_prompt(prompt_name)
        
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable in prompt {prompt_name}: {e}")
        except Exception as e:
            raise ValueError(f"Error formatting prompt {prompt_name}: {e}")
    
    def get_available_prompts(self) -> list:
        """Get list of available prompt files"""
        try:
            return [f.stem for f in self.prompts_dir.glob("*.txt")]
        except Exception as e:
            print(f"Warning: Error listing prompts: {e}")
            return []
    
    def validate_prompt(self, prompt_name: str) -> bool:
        """Check if a prompt file exists"""
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        return prompt_file.exists()


# Global prompt loader instance
prompt_loader = PromptLoader() 