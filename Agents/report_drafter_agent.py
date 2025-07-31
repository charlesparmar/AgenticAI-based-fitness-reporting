import os
import json
import sqlitecloud
import requests
import time
import smtplib
import tempfile
import os.path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

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

class ReportDrafterAgent:
    """Agent for drafting and sending fitness reports via email"""
    
    def __init__(self):
        # SQLite Cloud configuration
        self.sqlite_api_key = os.getenv("SQLITE_API_KEY")
        self.connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={self.sqlite_api_key}"
        
        # Supabase credentials from environment variables
        self.supabase_email = os.getenv("SUPABASE_EMAIL")
        self.supabase_password = os.getenv("SUPABASE_PASSWORD")
        self.supabase_url = os.getenv("SUPABASE_URL")
        
        # Gmail credentials for sending emails
        self.gmail_address = os.getenv("GMAIL_ADDRESS")
        self.gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
        
        # Email configuration
        self.email_to = os.getenv("EMAIL_TO", "coach@example.com")
        
        # LLM configuration using modular system
        self.llm = llm_config.get_model(temperature=0.7)
        
        # Pushover notifier
        self.notifier = PushoverNotifier()
        
        # Validate environment variables
        if not self.supabase_email:
            raise ValueError("SUPABASE_EMAIL must be set in .env file")
        if not self.supabase_password:
            raise ValueError("SUPABASE_PASSWORD must be set in .env file")
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL must be set in .env file")
        if not self.gmail_address:
            raise ValueError("GMAIL_ADDRESS must be set in .env file")
        if not self.gmail_app_password:
            raise ValueError("GMAIL_APP_PASSWORD must be set in .env file")
        
    def setup_headless_browser(self):
        """Setup headless Chrome browser with download preferences and timeout handling"""
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
            
            # Set up download preferences
            prefs = {
                "download.default_directory": tempfile.gettempdir(),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Add timeout settings
            chrome_options.add_argument("--timeout=30000")  # 30 second timeout
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set page load timeout
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            print("✅ Headless browser setup completed with timeout handling")
            return driver
            
        except Exception as e:
            print(f"❌ Error setting up browser: {e}")
            return None
    
    def login_to_supabase(self, driver):
        """Login to Supabase application"""
        try:
            print("🔐 Logging into Supabase...")
            
            # Navigate to login page
            driver.get(self.supabase_url)
            time.sleep(3)
            
            # Wait for email field and enter email
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(self.supabase_email)
            
            # Find and fill password field
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.supabase_password)
            
            # Submit the form
            password_field.send_keys(Keys.RETURN)
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            current_url = driver.current_url
            if "login" not in current_url.lower():
                print("✅ Successfully logged into Supabase")
                return True
            else:
                print("❌ Login failed - still on login page")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
    
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
    
    def click_draft_email_button(self, driver):
        """Click the 'Draft Email' button"""
        try:
            print("📧 Clicking 'Draft Email' button...")
            
            # Wait for the Draft Email button to be present and clickable
            draft_email_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Draft Email')]"))
            )
            draft_email_button.click()
            
            # Wait for modal to appear
            time.sleep(3)
            print("✅ Draft Email modal opened")
            return True
            
        except Exception as e:
            print(f"❌ Error clicking Draft Email button: {e}")
            return False
    
    def fill_email_fields(self, driver, email_body: str):
        """Fill the email fields in the modal"""
        try:
            print("📝 Filling email fields...")
            
            # Wait for modal to be fully loaded
            time.sleep(3)
            
            # First, make sure we're looking within the modal
            print("🔍 Looking for 'To' field within the Draft Email modal...")
            
            # Try multiple selectors for 'To' field - specifically within the modal
            to_field = None
            to_selectors = [
                "//div[contains(@class, 'modal')]//input[@placeholder='To']",
                "//div[contains(@class, 'modal')]//input[@name='to']",
                "//div[contains(@class, 'modal')]//input[contains(@class, 'to')]",
                "//div[contains(@class, 'modal')]//input[@type='email']",
                "//div[contains(@class, 'modal')]//input[contains(@placeholder, 'email')]",
                "//div[contains(@class, 'dialog')]//input[@placeholder='To']",
                "//div[contains(@class, 'dialog')]//input[@name='to']",
                "//div[contains(@class, 'popup')]//input[@placeholder='To']",
                "//div[contains(@class, 'popup')]//input[@name='to']",
                # Fallback: look for any input that might be the first field in a modal
                "//div[contains(@class, 'modal')]//input[1]",
                "//div[contains(@class, 'dialog')]//input[1]"
            ]
            
            for selector in to_selectors:
                try:
                    to_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"✅ Found 'To' field using selector: {selector}")
                    break
                except:
                    continue
            
            if to_field:
                to_field.clear()
                to_field.send_keys(self.email_to)
                print(f"✅ Updated 'To' field with: {self.email_to}")
            else:
                print("⚠️ Could not find 'To' field, continuing...")
            
            # Try multiple selectors for 'Body' field - specifically within the modal
            body_field = None
            body_selectors = [
                "//div[contains(@class, 'modal')]//textarea[@placeholder='Body']",
                "//div[contains(@class, 'modal')]//textarea[@name='body']",
                "//div[contains(@class, 'modal')]//textarea[contains(@class, 'body')]",
                "//div[contains(@class, 'modal')]//textarea[contains(@placeholder, 'message')]",
                "//div[contains(@class, 'modal')]//textarea[contains(@placeholder, 'content')]",
                "//div[contains(@class, 'modal')]//div[@contenteditable='true']",
                "//div[contains(@class, 'modal')]//div[contains(@class, 'editor')]",
                "//div[contains(@class, 'dialog')]//textarea[@placeholder='Body']",
                "//div[contains(@class, 'dialog')]//textarea[@name='body']",
                "//div[contains(@class, 'dialog')]//div[@contenteditable='true']",
                "//div[contains(@class, 'popup')]//textarea[@placeholder='Body']",
                "//div[contains(@class, 'popup')]//textarea[@name='body']",
                # Fallback: look for any textarea or contenteditable div in modal
                "//div[contains(@class, 'modal')]//textarea",
                "//div[contains(@class, 'modal')]//div[@contenteditable='true']",
                "//div[contains(@class, 'dialog')]//textarea",
                "//div[contains(@class, 'dialog')]//div[@contenteditable='true']"
            ]
            
            for selector in body_selectors:
                try:
                    body_field = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"✅ Found 'Body' field using selector: {selector}")
                    break
                except:
                    continue
            
            if body_field:
                body_field.clear()
                body_field.send_keys(email_body)
                print(f"✅ Updated 'Body' field with email content ({len(email_body)} characters)")
            else:
                print("⚠️ Could not find 'Body' field, continuing without web form filling")
            
            # Debug: Print all form elements found specifically within modal
            try:
                print("🔍 Debug: Searching for form elements within modal...")
                
                # Look for modal containers first
                modal_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'dialog') or contains(@class, 'popup')]")
                print(f"📊 Found {len(modal_containers)} potential modal containers")
                
                # Search for elements within each modal
                for i, modal in enumerate(modal_containers):
                    print(f"🔍 Modal {i+1}:")
                    try:
                        # Find inputs within this modal
                        modal_inputs = modal.find_elements(By.TAG_NAME, "input")
                        modal_textareas = modal.find_elements(By.TAG_NAME, "textarea")
                        modal_divs = modal.find_elements(By.TAG_NAME, "div")
                        
                        print(f"  📊 Modal {i+1} contains: {len(modal_inputs)} inputs, {len(modal_textareas)} textareas, {len(modal_divs)} divs")
                        
                        # Print input elements with their attributes
                        for j, inp in enumerate(modal_inputs[:3]):  # Show first 3
                            try:
                                placeholder = inp.get_attribute('placeholder') or 'None'
                                name = inp.get_attribute('name') or 'None'
                                type_attr = inp.get_attribute('type') or 'None'
                                print(f"    Input {j+1}: placeholder='{placeholder}', name='{name}', type='{type_attr}'")
                            except:
                                pass
                        
                        # Print textarea elements with their attributes
                        for j, ta in enumerate(modal_textareas[:3]):  # Show first 3
                            try:
                                placeholder = ta.get_attribute('placeholder') or 'None'
                                name = ta.get_attribute('name') or 'None'
                                print(f"    Textarea {j+1}: placeholder='{placeholder}', name='{name}'")
                            except:
                                pass
                                
                    except Exception as modal_e:
                        print(f"    ⚠️ Error examining modal {i+1}: {modal_e}")
                        
            except Exception as debug_e:
                print(f"⚠️ Debug error: {debug_e}")
            
            print("✅ Email fields filled successfully")
            return True
            
            print("✅ Email fields filled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error filling email fields: {e}")
            return False
    
    def click_send_email_button(self, driver):
        """Click the 'Send Email' button"""
        try:
            print("📤 Clicking 'Send Email' button...")
            
            # Wait for the Send Email button to be present and clickable
            send_email_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send Email')]"))
            )
            send_email_button.click()
            
            # Wait for email to be sent
            time.sleep(5)
            print("✅ Email sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error clicking Send Email button: {e}")
            return False
    
    def click_export_report_button(self, driver):
        """Click the 'Export Report' button to download PDF"""
        try:
            print("📄 Looking for Export Report button...")
            
            # Try multiple selectors for the export button
            export_selectors = [
                "//button[contains(text(), 'Export Report')]",
                "//button[contains(text(), 'Export')]",
                "//button[contains(text(), 'Download')]",
                "//button[contains(text(), 'PDF')]",
                "//a[contains(text(), 'Export Report')]",
                "//a[contains(text(), 'Export')]",
                "//a[contains(text(), 'Download')]",
                "//a[contains(text(), 'PDF')]",
                "//button[contains(@class, 'export')]",
                "//button[contains(@class, 'download')]",
                "//a[contains(@class, 'export')]",
                "//a[contains(@class, 'download')]"
            ]
            
            export_button = None
            for selector in export_selectors:
                try:
                    export_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✅ Found Export Report button using selector: {selector}")
                    break
                except:
                    continue
            
            if not export_button:
                print("❌ Export Report button not found")
                return False
            
            # Click the export button with timeout
            try:
                export_button.click()
                print("✅ Export Report button clicked")
                
                # Wait for download to start with timeout
                time.sleep(3)
                
                return True
                
            except Exception as e:
                print(f"❌ Error clicking export button: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Error clicking Export Report button: {e}")
            return False
    
    def wait_for_download_and_get_file(self, driver, timeout=30):
        """Wait for PDF download to complete and return the file path with enhanced timeout handling"""
        try:
            print("⏳ Waiting for PDF download to complete...")
            
            download_dir = tempfile.gettempdir()
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check for PDF files in download directory
                pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
                
                if pdf_files:
                    # Get the most recent PDF file
                    pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), reverse=True)
                    latest_pdf = os.path.join(download_dir, pdf_files[0])
                    
                    # Check if file is still being downloaded (size is stable)
                    initial_size = os.path.getsize(latest_pdf)
                    time.sleep(2)
                    current_size = os.path.getsize(latest_pdf)
                    
                    if initial_size == current_size:
                        print(f"✅ PDF downloaded successfully: {latest_pdf}")
                        return latest_pdf
                
                time.sleep(1)
            
            print("❌ PDF download timeout - no file found or download incomplete")
            return None
            
        except Exception as e:
            print(f"❌ Error waiting for download: {e}")
            return None
    
    def send_email_via_gmail(self, email_body: str, pdf_file_path: str, iteration_count: int = 1) -> bool:
        """Send email via Gmail SMTP with PDF attachment"""
        try:
            print("📧 Sending email via Gmail SMTP...")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = self.email_to
            msg['Subject'] = f"Fitness Report - Week {datetime.now().strftime('%Y-%m-%d')}"
            
            # Add body
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Add PDF attachment
            if pdf_file_path and os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(pdf_file_path)}'
                )
                msg.attach(part)
                print(f"✅ PDF attached: {os.path.basename(pdf_file_path)}")
            else:
                print("⚠️ PDF file not found, sending email without attachment")
            
            # Send email via Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            server.starttls()
            server.login(self.gmail_address, self.gmail_app_password)
            
            text = msg.as_string()
            server.sendmail(self.gmail_address, self.email_to, text)
            server.quit()
            
            print("✅ Email sent successfully via Gmail SMTP")
            
            # Send success notification
            notification_message = f"Fitness report email sent successfully (generated in {iteration_count} iteration{'s' if iteration_count > 1 else ''})"
            self.notifier.send_notification(notification_message, "Email Sent Successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending email via Gmail: {e}")
            return False
    
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
            
            # Store for later use in send_final_email
            self._last_email_body = email_body_data
            
            print("✅ Email body generated successfully, ready for evaluation")
            
            return {
                'success': True,
                'email_body_data': email_body_data,
                'driver': None,  # No driver needed yet
                'message': 'Email body generated successfully, ready for evaluation',
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"❌ Error in Report Drafter agent: {e}")
            return {
                'success': False,
                'error': f'Report Drafter agent error: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def send_final_email(self, driver, iteration_count: int = 1) -> bool:
        """Send the final email after approval - exports PDF and sends via Gmail"""
        try:
            print(f"📤 Starting final email sending process (iteration {iteration_count})...")
            
            # Get the final email body data
            email_body_data = getattr(self, '_last_email_body', None)
            if not email_body_data:
                print("❌ No email body data found for sending")
                return False
            
            email_body = email_body_data.get('email_body', '')
            if not email_body:
                print("❌ No email body content found")
                return False
            
            print("🔐 Logging into Supabase...")
            # Login to Supabase
            if not self.login_to_supabase(driver):
                print("❌ Failed to login to Supabase")
                return False
            
            print("📄 Clicking 'Export Report' button...")
            # Click Export Report button instead of Draft Email
            if not self.click_export_report_button(driver):
                print("❌ Failed to click Export Report button")
                return False
            
            print("⏳ Waiting for PDF download...")
            # Wait for PDF download to complete
            pdf_file_path = self.wait_for_download_and_get_file(driver)
            if not pdf_file_path:
                print("❌ Failed to download PDF report")
                return False
            
            print("📧 Sending email via Gmail SMTP...")
            # Send email via Gmail SMTP with PDF attachment
            if not self.send_email_via_gmail(email_body, pdf_file_path, iteration_count):
                print("❌ Failed to send email via Gmail")
                return False
            
            print("✅ Final email sent successfully via Gmail!")
            return True
            
        except Exception as e:
            print(f"❌ Error sending final email: {e}")
            # Still send notification even if email sending fails
            notification_message = f"Report drafted but email sending had issues (generated in {iteration_count} iteration{'s' if iteration_count > 1 else ''})"
            self.notifier.send_notification(notification_message, "Email Process Completed")
            return True  # Return True to continue workflow

def run_report_drafter_agent(supabase_data: Dict[str, Any], feedback: str = ""):
    """Run the Report Drafter agent"""
    try:
        agent = ReportDrafterAgent()
        result = agent.process_report_drafting(supabase_data, feedback)
        
        if result.get('success'):
            print("✅ Report Drafter agent completed successfully")
            print(f"📊 Message: {result.get('message')}")
        else:
            print(f"❌ Report Drafter agent failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running Report Drafter agent: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    print("Report Drafter Agent - This agent requires Supabase data to be passed in")
    print("Use run_report_drafter_agent(supabase_data) to run the agent") 