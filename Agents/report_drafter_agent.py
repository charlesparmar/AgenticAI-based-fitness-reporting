#!/usr/bin/env python3
"""
Modern Report Drafter Agent - LLM-powered email content generation
This agent focuses solely on generating email content using AI, without legacy web automation.
"""

import os
import json
import sqlitecloud
import requests
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Import modular components
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

class ModernReportDrafterAgent:
    """Modern Report Drafter Agent - LLM-powered email content generation only"""
    
    def __init__(self):
        # SQLite Cloud connection
        self.sqlite_api_key = os.getenv("SQLITE_API_KEY")
        if not self.sqlite_api_key:
            raise ValueError("SQLITE_API_KEY must be set in .env file")
        
        self.connection_string = f"sqlitecloud://clyqxnxkk001q08kz0ojs9eae.sqlite.cloud:8860/fitness?apikey={self.sqlite_api_key}"
        
        # Pushover notifier
        self.notifier = PushoverNotifier()
        
    def get_baseline_data(self) -> Dict[str, Any]:
        """Get baseline data (week 0) from SQLite database"""
        try:
            print("📊 Fetching baseline data from SQLite...")
            
            # Connect to SQLite Cloud
            connection = sqlitecloud.connect(self.connection_string)
            cursor = connection.cursor()
            
            # Get week 0 data (baseline)
            cursor.execute("""
                SELECT * FROM fitness_measurements 
                WHERE week_number = 0 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                # Get column names
                columns = [description[0] for description in cursor.description]
                baseline_data = dict(zip(columns, result))
                print("✅ Baseline data retrieved successfully")
                return baseline_data
            else:
                print("❌ No baseline data found")
                return {}
                
        except Exception as e:
            print(f"❌ Error fetching baseline data: {e}")
            return {}
        finally:
            if 'connection' in locals():
                connection.close()
    
    def create_email_body(self, baseline_data: Dict[str, Any], current_data: Dict[str, Any], feedback: str = "") -> str:
        """Create email body using configured LLM"""
        try:
            print("✍️ Generating email body with LLM...")
            
            # Prepare feedback section
            feedback_section = f"Previous feedback to address: {feedback}" if feedback else ""
            
            # Get the model for this specific prompt
            model = prompt_loader.get_model_for_prompt("report_drafting_prompt", temperature=0.7)
            
            # Load and format the prompt
            prompt = prompt_loader.format_prompt(
                "report_drafting_prompt",
                feedback_section=feedback_section,
                baseline_data=json.dumps(baseline_data, indent=2),
                current_data=json.dumps(current_data, indent=2)
            )
            
            # Make API call using LangChain
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content="You are a helpful assistant that writes professional fitness update emails."),
                HumanMessage(content=prompt)
            ]
            
            response = model.invoke(messages)
            
            email_body = response.content.strip()
            print("✅ Email body generated successfully")
            return email_body
            
        except Exception as e:
            print(f"❌ Error generating email body: {e}")
            return ""
    
    def process_report_drafting(self, supabase_data: Dict[str, Any], feedback: str = "") -> Dict[str, Any]:
        """Main function to process report drafting - generates email body only"""
        try:
            print("🤖 Starting Report Drafter Agent...")
            
            # Get baseline data from SQLite
            baseline_data = self.get_baseline_data()
            if not baseline_data:
                return {
                    'success': False,
                    'error': 'Failed to get baseline data',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Create email body using LLM (with feedback if provided)
            email_body = self.create_email_body(baseline_data, supabase_data, feedback)
            if not email_body:
                return {
                    'success': False,
                    'error': 'Failed to generate email body',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Store email body for evaluation
            email_body_data = {
                'email_body': email_body,
                'baseline_data': baseline_data,
                'current_data': supabase_data,
                'timestamp': datetime.now().isoformat()
            }
            
            print("✅ Email body generated successfully, ready for evaluation")
            
            return {
                'success': True,
                'email_body_data': email_body_data,
                'message': 'Email body generated successfully, ready for evaluation',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error in report drafting process: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

def run_report_drafter_agent(supabase_data: Dict[str, Any], feedback: str = ""):
    """Run the Modern Report Drafter agent"""
    try:
        agent = ModernReportDrafterAgent()
        result = agent.process_report_drafting(supabase_data, feedback)
        
        if result.get('success'):
            print("✅ Report Drafter agent completed successfully")
            print(f"📊 Message: {result.get('message')}")
        else:
            print(f"❌ Report Drafter agent failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running Report Drafter agent: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Example usage
    print("Modern Report Drafter Agent - LLM-powered email content generation")
    print("This agent requires Supabase data to be passed in")
