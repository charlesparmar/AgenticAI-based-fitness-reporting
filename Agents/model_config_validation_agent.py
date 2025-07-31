#!/usr/bin/env python3
"""
Model Configuration Validation Agent
Validates that all required models are properly configured before workflow execution
"""

import os
import json
import requests
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ModelConfigValidationAgent:
    """Agent for validating model configuration before workflow execution"""
    
    def __init__(self):
        self.pushover_token = os.getenv("PUSHOVER_TOKEN")
        self.pushover_user_key = os.getenv("PUSHOVER_USER_KEY")
        
    def validate_model_configuration(self) -> Dict[str, Any]:
        """Validate that all required models are properly configured"""
        try:
            print("🔍 Starting Model Configuration Validation...")
            
            # Check if model_config.txt exists
            model_config_path = "prompts/model_config.txt"
            if not os.path.exists(model_config_path):
                error_msg = "Model configuration file (prompts/model_config.txt) not found"
                self._send_error_notification(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Load and parse model_config.txt
            model_config = self._load_model_config(model_config_path)
            if not model_config:
                error_msg = "Failed to load model configuration from prompts/model_config.txt"
                self._send_error_notification(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check if all required prompts have model assignments
            required_prompts = [
                "email_evaluation_prompt",
                "validation_prompt", 
                "report_drafting_prompt",
                "reconciliation_prompt"
            ]
            
            missing_prompts = []
            for prompt in required_prompts:
                if prompt not in model_config:
                    missing_prompts.append(prompt)
            
            if missing_prompts:
                error_msg = f"Missing model assignments for prompts: {', '.join(missing_prompts)}"
                self._send_error_notification(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate that all model assignments are valid
            valid_models = ["Model 1", "Model 2", "Model 3"]
            invalid_assignments = []
            
            for prompt, assignment in model_config.items():
                if assignment not in valid_models:
                    invalid_assignments.append(f"{prompt}: {assignment}")
            
            if invalid_assignments:
                error_msg = f"Invalid model assignments: {', '.join(invalid_assignments)}"
                self._send_error_notification(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check if environment variables for models are set
            missing_env_vars = []
            for i in range(1, 4):
                provider_key = f"LLM_PROVIDER_{i}"
                model_key = f"LLM_MODEL_{i}"
                if not os.getenv(provider_key) or not os.getenv(model_key):
                    missing_env_vars.append(f"Model {i} ({provider_key}, {model_key})")
            
            if missing_env_vars:
                error_msg = f"Missing environment variables for: {', '.join(missing_env_vars)}"
                self._send_error_notification(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }
            
            # All validations passed
            print("✅ Model configuration validation passed")
            print("📊 Model assignments:")
            for prompt, assignment in model_config.items():
                print(f"  {prompt}: {assignment}")
            
            return {
                "success": True,
                "model_config": model_config,
                "message": "All model configurations are properly set",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error during model configuration validation: {e}"
            self._send_error_notification(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _load_model_config(self, config_path: str) -> Dict[str, str]:
        """Load model configuration from file"""
        try:
            model_config = {}
            with open(config_path, 'r', encoding='utf-8') as f:
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
            print(f"❌ Error loading model config: {e}")
            return {}
    
    def _send_error_notification(self, error_msg: str) -> bool:
        """Send error notification via Pushover"""
        try:
            if not self.pushover_token or not self.pushover_user_key:
                print("❌ Pushover credentials not configured")
                print(f"Token: {self.pushover_token}")
                print(f"User: {self.pushover_user_key}")
                return False
            
            # Create a simpler message to avoid formatting issues
            message = f"🚨 LLM Model Configuration Error\n\n❌ {error_msg}\n\n🛑 Workflow terminated due to configuration issues.\n\n📱 Sent by Model Configuration Validation Agent"
            
            pushover_data = {
                "token": self.pushover_token,
                "user": self.pushover_user_key,
                "message": message,
                "title": "LLM Models Need to be Defined",
                "priority": 1,  # High priority (but not emergency)
                "sound": "siren"  # Alert sound
            }
            
            print(f"🔍 Sending Pushover notification with data: {pushover_data}")
            
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data=pushover_data,
                timeout=10
            )
            
            print(f"🔍 Pushover response status: {response.status_code}")
            print(f"🔍 Pushover response text: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Pushover notification sent: LLM Models Need to be Defined")
                return True
            else:
                print(f"❌ Failed to send Pushover notification: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
            import traceback
            traceback.print_exc()
            return False

# Main execution function
def run_model_config_validation_agent():
    """Run the model configuration validation agent"""
    try:
        agent = ModelConfigValidationAgent()
        result = agent.validate_model_configuration()
        
        if not result.get('success'):
            print(f"❌ Model configuration validation failed: {result.get('error')}")
            return False
        
        print("✅ Model configuration validation completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running model configuration validation: {e}")
        return False

if __name__ == "__main__":
    success = run_model_config_validation_agent()
    exit(0 if success else 1) 