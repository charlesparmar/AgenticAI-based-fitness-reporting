import os
import json
import requests
import sqlitecloud
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Import new modular components
from config.llm_config import llm_config
from utils.prompt_loader import prompt_loader

# Load environment variables
load_dotenv()

class PushoverNotifier:
    """Handles push notifications via Pushover"""
    
    def __init__(self):
        self.user_key = os.getenv("PUSHOVER_USER_KEY")
        self.app_token = os.getenv("PUSHOVER_TOKEN")
        self.api_url = "https://api.pushover.net/1/messages.json"
        
        if not self.user_key or not self.app_token:
            raise ValueError("PUSHOVER_USER_KEY and PUSHOVER_TOKEN must be set in .env file")
    
    def send_notification(self, message, title=None, priority=0, sound=None):
        """Send a push notification"""
        payload = {
            "token": self.app_token,
            "user": self.user_key,
            "message": message,
            "priority": priority
        }
        
        if title:
            payload["title"] = title
        if sound:
            payload["sound"] = sound
        
        try:
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("status") == 1:
                print(f"✅ Notification sent: {message}")
                return True
            else:
                print(f"❌ Failed to send notification: {result.get('errors', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending notification: {e}")
            return False

class ReconciliationAgent:
    """Agent for comparing email data with database data using LLM"""
    
    def __init__(self):
        # SQLite Cloud configuration
        self.sqlite_api_key = os.getenv("SQLITE_API_KEY")
        self.connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={self.sqlite_api_key}"
        
        # Pushover notifier
        self.notifier = PushoverNotifier()
        
    def send_push_notification(self, message: str, title: str = "Fitness Data Report"):
        """Send push notification"""
        return self.notifier.send_notification(message, title, priority=0, sound="pushover")
    
    def compare_data_with_llm(self, new_data: Dict[str, Any], db_data: Dict[str, Any]) -> bool:
        """Compare new data with database data using configured LLM"""
        try:
            # Get the model for this specific prompt
            model = prompt_loader.get_model_for_prompt("reconciliation_prompt", temperature=0)
            
            # Load and format comparison prompt
            comparison_prompt = prompt_loader.format_prompt(
                "reconciliation_prompt",
                new_data=json.dumps(new_data, indent=2),
                db_data=json.dumps(db_data, indent=2)
            )
            
            # Get model response
            response = model.invoke(comparison_prompt)
            
            # Parse the response
            result = response.content.strip().upper()
            
            print(f"🔄 LLM comparison result: {result}")
            
            return result == "SAME"
            
        except Exception as e:
            print(f"❌ Error comparing data with LLM: {e}")
            return False
    
    def reconcile_data(self, email_json: Dict[str, Any], database_json: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile email data with database data using LLM comparison"""
        try:
            print("🔄 Starting data reconciliation...")
            
            # Compare with LLM
            is_same_data = self.compare_data_with_llm(email_json, database_json)
            
            if is_same_data:
                # Data is identical - workflow can continue
                self.send_push_notification("Reconciliation successful - both fetchers extracted identical data. Workflow proceeding.")
                return {
                    'success': True,
                    'data_matches': True,
                    'json_data': email_json,  # Pass email JSON to next agent
                    'message': 'Reconciliation successful - both fetchers extracted identical data',
                    'timestamp': datetime.now().isoformat(),
                    'proceed_to_validation': True
                }
            else:
                # Data is different - this indicates an error, terminate workflow
                self.send_push_notification("Reconciliation failed - fetcher agents extracted different data. Workflow terminated.")
                return {
                    'success': False,
                    'data_matches': False,
                    'error': 'Reconciliation failed - fetcher agents extracted different data',
                    'message': 'Fetcher agents must extract identical data. Difference detected indicates an error.',
                    'timestamp': datetime.now().isoformat(),
                    'proceed_to_validation': False
                }
                    
        except Exception as e:
            print(f"❌ Error in data reconciliation: {e}")
            return {
                'success': False,
                'error': f'Reconciliation error: {e}',
                'timestamp': datetime.now().isoformat()
            }

def run_reconciliation_agent(email_json: Dict[str, Any], database_json: Dict[str, Any]):
    """Run the reconciliation agent"""
    try:
        agent = ReconciliationAgent()
        result = agent.reconcile_data(email_json, database_json)
        
        if result.get('success'):
            if result.get('data_matches'):
                print("✅ Reconciliation successful - both fetchers extracted identical data")
                json_data = result.get('json_data', {})
                print(f"Subject: {json_data.get('email_info', {}).get('subject')}")
                print(f"From: {json_data.get('email_info', {}).get('sender')}")
                print(f"Date: {json_data.get('email_info', {}).get('date')}")
                
                # Display fitness data summary
                fitness_data = json_data.get('fitness_data', {})
                if fitness_data:
                    print(f"\n📊 Fitness Data Summary:")
                    print(f"Entry Date: {fitness_data.get('metadata', {}).get('entry_date')}")
                    print(f"Measurements: {len(fitness_data.get('measurements', {}))}")
                
                # Workflow proceeds to validation
                if result.get('proceed_to_validation'):
                    print("🔄 Proceeding to validation agent with reconciled data...")
                    return result  # Return the full reconciliation result
                else:
                    print("✅ Reconciliation completed - ready for next agent")
                    return result
        else:
            print(f"❌ Reconciliation failed: {result.get('error')}")
            print("🛑 Workflow terminated due to data mismatch between fetchers")
        
        return None
        
    except Exception as e:
        print(f"❌ Error running reconciliation agent: {e}")
        return None

if __name__ == "__main__":
    # Example usage - this would typically be called with data from other agents
    print("Reconciliation Agent - This agent requires email and database JSON data to be passed in")
    print("Use run_reconciliation_agent(email_json, database_json) to run the agent") 