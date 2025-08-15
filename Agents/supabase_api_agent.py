#!/usr/bin/env python3
"""
Supabase API Agent for entering fitness data using REST API instead of Selenium.
This replaces the web automation approach with direct API calls.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

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

class SupabaseAPIAgent:
    """Agent for entering fitness data into Supabase using REST API"""
    
    def __init__(self):
        # Supabase API configuration
        self.supabase_url = os.getenv("SUPABASE_API_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Validate environment variables
        if not self.supabase_url:
            raise ValueError("SUPABASE_API_URL must be set in .env file")
        if not self.supabase_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY must be set in .env file")
        
        # API headers
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # Pushover notifier
        try:
            self.notifier = PushoverNotifier()
        except ValueError:
            print("⚠️ Pushover credentials not configured - notifications will be skipped")
            self.notifier = None
    
    def parse_and_format_date(self, entry_date):
        """Parse and format date with robust error handling"""
        try:
            if not entry_date:
                # Use current date if no date provided
                return datetime.now().strftime("%Y-%m-%d")
            
            # Clean the date string
            entry_date = str(entry_date).strip()
            
            # Check if it's already in YYYY-MM-DD format
            if len(entry_date) == 10 and entry_date.count('-') == 2:
                try:
                    # Validate the date format
                    datetime.strptime(entry_date, "%Y-%m-%d")
                    return entry_date
                except ValueError:
                    pass
            
            # Handle DD/MM/YYYY format
            if entry_date.count('/') == 2:
                parts = entry_date.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    
                    # Validate parts are numeric
                    if day.isdigit() and month.isdigit() and year.isdigit():
                        # Ensure year is 4 digits
                        if len(year) == 2:
                            year = '20' + year
                        elif len(year) != 4:
                            raise ValueError(f"Invalid year format: {year}")
                        
                        # Validate day and month ranges
                        day_int = int(day)
                        month_int = int(month)
                        year_int = int(year)
                        
                        if not (1 <= day_int <= 31 and 1 <= month_int <= 12 and 2000 <= year_int <= 2100):
                            raise ValueError(f"Invalid date values: {day}/{month}/{year}")
                        
                        formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        
                        # Final validation
                        datetime.strptime(formatted_date, "%Y-%m-%d")
                        return formatted_date
            
            # If all parsing attempts fail, use current date
            print(f"⚠️ Could not parse date '{entry_date}', using current date")
            return datetime.now().strftime("%Y-%m-%d")
            
        except Exception as e:
            print(f"❌ Error parsing date '{entry_date}': {e}")
            print(f"🔄 Using current date as fallback")
            return datetime.now().strftime("%Y-%m-%d")
    
    def extract_formatted_data(self, new_email_data):
        """Extract and format data for Supabase API"""
        try:
            measurements = new_email_data.get('fitness_data', {}).get('measurements', {})
            metadata = new_email_data.get('fitness_data', {}).get('metadata', {})
            
            # Extract date from metadata with improved parsing
            entry_date = metadata.get('entry_date', '')
            formatted_date = self.parse_and_format_date(entry_date)
            
            # Format data for Supabase API (matching table column names)
            formatted_data = {
                'week_number': measurements.get('Week Number', ''),
                'date': formatted_date,
                'weight': measurements.get('Weight', ''),
                'fat_percent': measurements.get('Fat Percentage', ''),
                'bmi': measurements.get('Bmi', ''),
                'fat_weight': measurements.get('Fat Weight', ''),
                'lean_weight': measurements.get('Lean Weight', ''),
                'neck': measurements.get('Neck', ''),
                'shoulders': measurements.get('Shoulders', ''),
                'biceps': measurements.get('Biceps', ''),
                'forearms': measurements.get('Forearms', ''),
                'chest': measurements.get('Chest', ''),
                'above_navel': measurements.get('Above Navel', ''),
                'navel': measurements.get('Navel', ''),
                'waist': measurements.get('Waist', ''),
                'hips': measurements.get('Hips', ''),
                'thighs': measurements.get('Thighs', ''),
                'calves': measurements.get('Calves', '')
            }
            
            # Remove empty values to avoid API issues
            formatted_data = {k: v for k, v in formatted_data.items() if v != ''}
            
            print("📊 Formatted data for Supabase API:")
            for key, value in formatted_data.items():
                print(f"   {key}: {value}")
            
            return formatted_data
            
        except Exception as e:
            print(f"❌ Error extracting formatted data: {e}")
            return {}
    
    def insert_fitness_data(self, formatted_data):
        """Insert fitness data into Supabase using REST API"""
        try:
            # API endpoint for the progress_reports table
            api_endpoint = f"{self.supabase_url}/rest/v1/progress_reports"
            
            print(f"🔄 Inserting data into Supabase API: {api_endpoint}")
            print(f"📊 Data to insert: {json.dumps(formatted_data, indent=2)}")
            
            # Make the API request
            response = requests.post(
                api_endpoint,
                headers=self.headers,
                json=formatted_data
            )
            
            # Check response
            if response.status_code == 201:
                print(f"✅ Successfully inserted data into Supabase (Status: {response.status_code})")
                try:
                    if response.text.strip():
                        result = response.json()
                        print(f"📊 Response: {result}")
                    else:
                        result = {"message": "Data inserted successfully"}
                        print(f"📊 Empty response (normal with return=minimal)")
                except json.JSONDecodeError:
                    # Handle any JSON parsing issues
                    result = {"message": "Data inserted successfully"}
                    print(f"📊 Response parsing issue, but insertion was successful")
                return {
                    'success': True,
                    'data': result,
                    'status_code': response.status_code
                }
            else:
                print(f"❌ Failed to insert data: {response.status_code}")
                print(f"📊 Error response: {response.text}")
                return {
                    'success': False,
                    'error': f"API request failed: {response.status_code}",
                    'response_text': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            print(f"❌ Error inserting data via API: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_confirmation_to_db(self, message: str) -> bool:
        """Save confirmation message to SQLite Cloud database"""
        try:
            sqlite_api_key = os.getenv("SQLITE_API_KEY")
            if not sqlite_api_key:
                print("❌ SQLite API credentials not configured")
                return False
            
            print("🔄 Saving confirmation to database...")
            
            # Connect to SQLite Cloud
            import sqlitecloud
            connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={sqlite_api_key}"
            conn = sqlitecloud.connect(connection_string)
            cursor = conn.cursor()
            
            # Insert confirmation message
            insert_query = """
            INSERT INTO "supabase entry confirmation" (
                "Entry Confirmation",
                "created_date&time"
            ) VALUES (?, ?)
            """
            
            current_time = datetime.now().timestamp()
            cursor.execute(insert_query, (message, current_time))
            conn.commit()
            
            print(f"✅ Confirmation saved to database with ID: {cursor.lastrowid}")
            conn.close()
            
            return True
                
        except Exception as e:
            print(f"❌ Error saving confirmation to database: {e}")
            return False
    
    def process_supabase_entry(self, new_email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main function to process Supabase entry via API"""
        try:
            print("🤖 Starting Supabase API Agent...")
            
            # Extract and format data
            formatted_data = self.extract_formatted_data(new_email_data)
            
            if not formatted_data:
                if self.notifier:
                    self.notifier.send_notification("Entry to Supabase failed - No data to insert", "Supabase Entry Failed")
                return {
                    'success': False,
                    'error': 'No data to insert',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Insert data via API
            api_result = self.insert_fitness_data(formatted_data)
            
            if not api_result.get('success'):
                if self.notifier:
                    self.notifier.send_notification("Entry to Supabase failed - API error", "Supabase Entry Failed")
                return {
                    'success': False,
                    'error': api_result.get('error', 'Unknown API error'),
                    'timestamp': datetime.now().isoformat()
                }
            
            # Send success notification
            notification_message = "new entry made in supabase via API"
            if self.notifier:
                self.notifier.send_notification(notification_message, "Supabase Entry Success")
            
            # Save confirmation to database
            db_saved = self.save_confirmation_to_db(notification_message)
            
            if db_saved:
                print("✅ Confirmation saved to database")
            else:
                print("❌ Failed to save confirmation to database")
            
            return {
                'success': True,
                'message': 'Successfully entered data into Supabase via API',
                'notification_sent': True,
                'db_saved': db_saved,
                'api_response': api_result.get('data'),
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"❌ Error in Supabase API agent: {e}")
            if self.notifier:
                self.notifier.send_notification("Entry to Supabase failed - Please send report manually", "Supabase Entry Failed")
            return {
                'success': False,
                'error': f'Supabase API agent error: {e}',
                'timestamp': datetime.now().isoformat()
            }

def run_supabase_api_agent(new_email_data: Dict[str, Any]):
    """Run the Supabase API agent"""
    try:
        agent = SupabaseAPIAgent()
        result = agent.process_supabase_entry(new_email_data)
        
        if result.get('success'):
            print("✅ Supabase API agent completed successfully")
            print(f"📊 Message: {result.get('message')}")
            print(f"📊 Notification sent: {result.get('notification_sent')}")
            print(f"📊 Database saved: {result.get('db_saved')}")
        else:
            print(f"❌ Supabase API agent failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running Supabase API agent: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    print("Supabase API Agent - This agent requires email JSON data to be passed in")
    print("Use run_supabase_api_agent(new_email_data) to run the agent")
