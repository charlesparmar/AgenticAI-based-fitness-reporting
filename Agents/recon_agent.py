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
    
    def update_database_entry(self, email_data: Dict[str, Any]) -> bool:
        """Update the database with email data (replace existing entry)"""
        try:
            if not self.sqlite_api_key:
                print("❌ SQLite API credentials not configured")
                return False
            
            print("🔄 Replacing database entry with email data...")
            
            # Connect to SQLite Cloud
            conn = sqlitecloud.connect(self.connection_string)
            cursor = conn.cursor()
            
            # First, delete the existing entry (if any)
            delete_query = """
            DELETE FROM fitness_data_new 
            WHERE week_number = ? AND entry_date = ?
            """
            
            week_number = email_data['fitness_data']['measurements'].get('Week Number')
            entry_date = email_data['fitness_data']['metadata'].get('entry_date')
            
            cursor.execute(delete_query, (week_number, entry_date))
            
            # Insert email data (excluding id which is auto-increment)
            insert_query = """
            INSERT INTO fitness_data_new (
                email_subject, email_sender, email_date, email_id, email_fetched_at,
                entry_date, submitted, processed_at,
                week_number, weight, fat_percentage, bmi, fat_weight, lean_weight,
                neck, shoulders, biceps, forearms, chest, above_navel, navel, waist, hips, thighs, calves,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Extract values from email JSON structure
            email_info = email_data['email_info']
            fitness_data = email_data['fitness_data']
            measurements = fitness_data['measurements']
            metadata = fitness_data['metadata']
            
            # Create values list with explicit handling of None values
            values = [
                email_info.get('subject'),
                email_info.get('sender'),
                email_info.get('date'),
                email_info.get('email_id'),
                email_info.get('fetched_at'),
                metadata.get('entry_date'),
                metadata.get('submitted'),
                email_data.get('processed_at'),
                measurements.get('Week Number'),
                measurements.get('Weight'),
                measurements.get('Fat Percentage'),
                measurements.get('Bmi'),
                measurements.get('Fat Weight'),
                measurements.get('Lean Weight'),
                measurements.get('Neck'),
                measurements.get('Shoulders'),
                measurements.get('Biceps'),
                measurements.get('Forearms'),
                measurements.get('Chest'),
                measurements.get('Above Navel'),
                measurements.get('Navel'),
                measurements.get('Waist'),
                measurements.get('Hips'),
                measurements.get('Thighs'),
                measurements.get('Calves'),
                datetime.now().isoformat(),  # created_at
                datetime.now().isoformat()   # updated_at
            ]
            
            cursor.execute(insert_query, values)
            conn.commit()
            
            print("✅ Database replaced with email data successfully")
            
            # Close connection
            conn.close()
            
            return True
                
        except Exception as e:
            print(f"❌ Error updating database: {e}")
            return False
    
    def reconcile_data(self, email_json: Dict[str, Any], database_json: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile email data with database data using LLM comparison"""
        try:
            print("🔄 Starting data reconciliation...")
            
            # Compare with LLM
            is_same_data = self.compare_data_with_llm(email_json, database_json)
            
            if is_same_data:
                # Send notification and end workflow
                self.send_push_notification("Fetched data already exist - the workflow would end here")
                return {
                    'success': True,
                    'data_exists': True,
                    'message': 'Data already exists in database',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # If data is different, replace database with email data
                if self.update_database_entry(email_json):
                    self.send_push_notification("Database replaced with email data - passing to validation agent")
                    return {
                        'success': True,
                        'data_exists': False,
                        'json_data': email_json,  # Pass email JSON to validation agent
                        'message': 'Database replaced with email data - ready for validation',
                        'timestamp': datetime.now().isoformat(),
                        'proceed_to_validation': True
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Failed to update database',
                        'timestamp': datetime.now().isoformat()
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
            if result.get('data_exists'):
                print("✅ Data already exists in database - workflow ended")
            else:
                print("✅ Successfully reconciled data and updated database:")
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
                
                # Check if workflow should proceed to validation
                if result.get('proceed_to_validation'):
                    print("🔄 Proceeding to validation agent with email JSON data...")
                    return result  # Return the full reconciliation result
                else:
                    print("✅ Workflow completed without validation")
                    return result
        else:
            print(f"❌ Error reconciling data: {result.get('error')}")
        
        return None
        
    except Exception as e:
        print(f"❌ Error running reconciliation agent: {e}")
        return None

if __name__ == "__main__":
    # Example usage - this would typically be called with data from other agents
    print("Reconciliation Agent - This agent requires email and database JSON data to be passed in")
    print("Use run_reconciliation_agent(email_json, database_json) to run the agent") 