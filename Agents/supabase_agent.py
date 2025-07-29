import os
import json
import sqlitecloud
import requests
import time
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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

class SupabaseAgent:
    """Agent for entering fitness data into Supabase application"""
    
    def __init__(self):
        # SQLite Cloud configuration
        self.sqlite_api_key = os.getenv("SQLITE_API_KEY")
        self.connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={self.sqlite_api_key}"
        
        # Supabase credentials from environment variables
        self.supabase_email = os.getenv("SUPABASE_EMAIL")
        self.supabase_password = os.getenv("SUPABASE_PASSWORD")
        self.supabase_url = os.getenv("SUPABASE_URL")
        
        # Validate environment variables
        if not self.supabase_email:
            raise ValueError("SUPABASE_EMAIL must be set in .env file")
        if not self.supabase_password:
            raise ValueError("SUPABASE_PASSWORD must be set in .env file")
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL must be set in .env file")
        
        # Pushover notifier
        self.notifier = PushoverNotifier()
        
    def setup_headless_browser(self):
        """Setup headless Chrome browser"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
            
        except Exception as e:
            print(f"❌ Error setting up browser: {e}")
            return None
    
    def login_to_supabase(self, driver):
        """Login to Supabase application"""
        try:
            print("🔄 Navigating to Supabase login page...")
            driver.get(self.supabase_url)
            
            # Wait for page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print("🔄 Entering login credentials...")
            
            # Find and fill email field
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(self.supabase_email)
            
            # Find and fill password field
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.supabase_password)
            
            # Find and click login button
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(driver, 15).until(
                EC.url_changes(self.supabase_url)
            )
            
            print("✅ Successfully logged into Supabase")
            return True
            
        except TimeoutException:
            print("❌ Timeout waiting for login elements")
            return False
        except NoSuchElementException as e:
            print(f"❌ Element not found during login: {e}")
            return False
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
    
    def extract_formatted_data(self, new_email_data):
        """Extract and format data according to the table headers"""
        try:
            measurements = new_email_data.get('fitness_data', {}).get('measurements', {})
            metadata = new_email_data.get('fitness_data', {}).get('metadata', {})
            
            # Extract date from metadata
            entry_date = metadata.get('entry_date', '')
            # Convert date format from "28/07/2025" to "2025-07-28"
            if entry_date:
                try:
                    day, month, year = entry_date.split('/')
                    formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    formatted_date = entry_date
            else:
                formatted_date = datetime.now().strftime("%Y-%m-%d")
            
            # Format data according to the table headers
            formatted_data = {
                'week_numbi': measurements.get('Week Number', ''),
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
            
            print("📊 Formatted data for Supabase:")
            for key, value in formatted_data.items():
                print(f"   {key}: {value}")
            
            return formatted_data
            
        except Exception as e:
            print(f"❌ Error extracting formatted data: {e}")
            return {}
    
    def find_form_field(self, driver, field_name, value):
        """Find and fill a form field with multiple selector strategies"""
        try:
            # Multiple selector strategies for each field
            field_selectors = [
                # Direct name/id selectors
                f"input[name='{field_name}']",
                f"input[id='{field_name}']",
                f"input[data-testid='{field_name}']",
                # Placeholder-based selectors
                f"input[placeholder*='{field_name.replace('_', ' ')}']",
                f"input[placeholder*='{field_name.title().replace('_', ' ')}']",
                # Label-based selectors
                f"input[aria-label*='{field_name.replace('_', ' ')}']",
                # Generic input selectors
                "input[type='text']",
                "input[type='number']",
                "input[type='date']"
            ]
            
            for selector in field_selectors:
                try:
                    # Wait for element to be present and visible
                    field = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    # Check if field is visible and enabled
                    if field.is_displayed() and field.is_enabled():
                        # Clear and fill the field
                        field.clear()
                        field.send_keys(str(value))
                        print(f"✅ Filled {field_name}: {value} using selector: {selector}")
                        return True
                        
                except (TimeoutException, NoSuchElementException):
                    continue
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {e}")
                    continue
            
            print(f"⚠️ Could not find field for {field_name}")
            return False
            
        except Exception as e:
            print(f"❌ Error filling {field_name}: {e}")
            return False
    
    def enter_fitness_data(self, driver, new_email_data):
        """Enter fitness data into the application"""
        try:
            print("🔄 Looking for Add Entry button...")
            
            # Wait for the page to load after login
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for Add Entry button (updated selector based on debug results)
            add_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Entry')]"))
            )
            
            print("🔄 Clicking Add Entry button...")
            add_button.click()
            
            # Wait for modal to appear with longer timeout
            print("🔄 Waiting for modal to appear...")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Add New Entry')]"))
            )
            
            # Additional wait for modal to fully load
            time.sleep(3)
            
            print("🔄 Modal opened, entering fitness data...")
            
            # Extract and format data
            formatted_data = self.extract_formatted_data(new_email_data)
            
            # Map of field names to their corresponding form field names
            field_mappings = {
                'week_numbi': 'week_numbi',
                'date': 'date',
                'weight': 'weight',
                'fat_percent': 'fat_percent',
                'bmi': 'bmi',
                'fat_weight': 'fat_weight',
                'lean_weight': 'lean_weight',
                'neck': 'neck',
                'shoulders': 'shoulders',
                'biceps': 'biceps',
                'forearms': 'forearms',
                'chest': 'chest',
                'above_navel': 'above_navel',
                'navel': 'navel',
                'waist': 'waist',
                'hips': 'hips',
                'thighs': 'thighs',
                'calves': 'calves'
            }
            
            # Fill in each field
            fields_filled = 0
            for field_name, form_field_name in field_mappings.items():
                value = formatted_data.get(field_name, '')
                if value:
                    if self.find_form_field(driver, form_field_name, value):
                        fields_filled += 1
            
            print(f"📊 Filled {fields_filled} out of {len(field_mappings)} fields")
            
            # Look for Save Entry button with multiple strategies
            save_button_selectors = [
                (By.XPATH, "//button[contains(text(), 'Save Entry')]"),
                (By.XPATH, "//button[contains(text(), 'Save')]"),
                (By.XPATH, "//button[contains(text(), 'Submit')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']")
            ]
            
            save_button = None
            for selector_type, selector in save_button_selectors:
                try:
                    save_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    print(f"✅ Found save button using: {selector_type} = {selector}")
                    break
                except:
                    continue
            
            if not save_button:
                print("❌ Could not find save button")
                return False
            
            print("🔄 Clicking Save Entry button...")
            
            # Scroll to the button first
            driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            time.sleep(2)
            
            # Click the button using JavaScript to avoid click interception
            driver.execute_script("arguments[0].click();", save_button)
            
            # Wait for success message or modal to close
            print("🔄 Waiting for save to complete...")
            WebDriverWait(driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Success') or contains(text(), 'Added') or contains(text(), 'saved')]")),
                    EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Add New Entry')]"))
                )
            )
            
            print("✅ Successfully entered fitness data into Supabase")
            return True
            
        except TimeoutException:
            print("❌ Timeout waiting for form elements")
            return False
        except NoSuchElementException as e:
            print(f"❌ Element not found during data entry: {e}")
            return False
        except Exception as e:
            print(f"❌ Error during data entry: {e}")
            return False
    
    def save_confirmation_to_db(self, message: str) -> bool:
        """Save confirmation message to SQLite Cloud database"""
        try:
            if not self.sqlite_api_key:
                print("❌ SQLite API credentials not configured")
                return False
            
            print("🔄 Saving confirmation to database...")
            
            # Connect to SQLite Cloud
            conn = sqlitecloud.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Insert confirmation message
            insert_query = """
            INSERT INTO "supabase entry confirmation" (
                "Entry Confirmation",
                "created_date&time"
            ) VALUES (?, ?)
            """
            
            current_time = datetime.now().timestamp()  # Unix timestamp as REAL
            
            cursor.execute(insert_query, (message, current_time))
            conn.commit()
            
            print(f"✅ Confirmation saved to database with ID: {cursor.lastrowid}")
            
            # Close connection
            conn.close()
            
            return True
                
        except Exception as e:
            print(f"❌ Error saving confirmation to database: {e}")
            return False
    
    def process_supabase_entry(self, new_email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main function to process Supabase entry"""
        driver = None
        try:
            print("🤖 Starting Supabase Agent...")
            
            # Setup headless browser
            driver = self.setup_headless_browser()
            if not driver:
                # Send failure notification
                self.notifier.send_notification("Entry to Supabase failed - Please send report manually", "Supabase Entry Failed")
                return {
                    'success': False,
                    'error': 'Failed to setup browser',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Login to Supabase
            if not self.login_to_supabase(driver):
                # Send failure notification
                self.notifier.send_notification("Entry to Supabase failed - Please send report manually", "Supabase Entry Failed")
                return {
                    'success': False,
                    'error': 'Failed to login to Supabase',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Enter fitness data
            if not self.enter_fitness_data(driver, new_email_data):
                # Send failure notification
                self.notifier.send_notification("Entry to Supabase failed - Please send report manually", "Supabase Entry Failed")
                return {
                    'success': False,
                    'error': 'Failed to enter fitness data',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Send success notification
            notification_message = "new entry made in supabase"
            self.notifier.send_notification(notification_message, "Supabase Entry Success")
            
            # Save confirmation to database
            db_saved = self.save_confirmation_to_db(notification_message)
            
            if db_saved:
                print("✅ Confirmation saved to database")
            else:
                print("❌ Failed to save confirmation to database")
            
            return {
                'success': True,
                'message': 'Successfully entered data into Supabase',
                'notification_sent': True,
                'db_saved': db_saved,
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"❌ Error in Supabase agent: {e}")
            # Send failure notification
            self.notifier.send_notification("Entry to Supabase failed - Please send report manually", "Supabase Entry Failed")
            return {
                'success': False,
                'error': f'Supabase agent error: {e}',
                'timestamp': datetime.now().isoformat()
            }
        finally:
            # Always close the browser
            if driver:
                try:
                    print("🔄 Closing browser...")
                    driver.quit()
                    print("✅ Browser closed successfully")
                except Exception as e:
                    print(f"⚠️ Error closing browser: {e}")

def run_supabase_agent(new_email_data: Dict[str, Any]):
    """Run the Supabase agent"""
    try:
        agent = SupabaseAgent()
        result = agent.process_supabase_entry(new_email_data)
        
        if result.get('success'):
            print("✅ Supabase agent completed successfully")
            print(f"📊 Message: {result.get('message')}")
            print(f"📊 Notification sent: {result.get('notification_sent')}")
            print(f"📊 Database saved: {result.get('db_saved')}")
        else:
            print(f"❌ Supabase agent failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running Supabase agent: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    print("Supabase Agent - This agent requires email JSON data to be passed in")
    print("Use run_supabase_agent(new_email_data) to run the agent") 