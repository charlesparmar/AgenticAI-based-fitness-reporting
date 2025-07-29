#!/usr/bin/env python3
"""
Final Email Agent for sending approved fitness reports with Excel attachments.
This agent takes control after email evaluation approval and handles the final email formatting and sending.
"""

import os
import json
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import tempfile

# Load environment variables
load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

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
                print(f"✅ Push notification sent: {message}")
                return True
            else:
                print(f"❌ Failed to send push notification: {result.get('errors', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending push notification: {e}")
            return False

class FinalEmailAgent:
    """Final Email Agent for sending approved fitness reports"""
    
    def __init__(self):
        """Initialize the Final Email Agent"""
        self.service = None
        self.credentials_path = os.getenv('GMAIL_API_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = os.getenv('GMAIL_API_TOKEN_PATH', 'token.json')
        self.email_address = os.getenv('GMAIL_ADDRESS')
        self.coach_email = os.getenv('EMAIL_TO', 'coach@example.com')
        
        if not self.email_address:
            raise ValueError("GMAIL_ADDRESS not found in environment variables")
        
        # Initialize Pushover notifier
        try:
            self.notifier = PushoverNotifier()
        except ValueError:
            print("⚠️ Pushover credentials not configured - push notifications will be skipped")
            self.notifier = None
        
        # Initialize Gmail service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Gmail API service with authentication"""
        try:
            creds = None
            
            # Load existing token if available
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            
            # If no valid credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=8080)
                
                # Save the credentials for the next run
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Final Email Agent Gmail service initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Final Email Agent Gmail service: {e}")
            raise
    
    def fetch_supabase_data(self):
        """Fetch all fitness data from fitness_measurements table via SQLite Cloud"""
        try:
            import sqlitecloud
            
            # SQLite Cloud configuration
            sqlite_api_key = os.getenv("SQLITE_API_KEY")
            if not sqlite_api_key:
                print("❌ SQLite API credentials not configured")
                return None
            
            # Connect to SQLite Cloud using the connection string format
            connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={sqlite_api_key}"
            conn = sqlitecloud.connect(connection_string)
            
            # Query all fitness data from fitness_measurements table, excluding id, week_number, and created_at
            query = """
                SELECT date, weight, fat_percent, bmi, fat_weight, lean_weight, 
                       neck, shoulders, biceps, forearms, chest, above_navel, 
                       navel, waist, hips, thighs, calves
                FROM fitness_measurements 
                ORDER BY date DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            print(f"✅ Fetched {len(df)} records from fitness_measurements table")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching fitness_measurements data: {e}")
            return None
    
    def create_excel_file(self, data_df):
        """Create Excel file with fitness data"""
        try:
            if data_df is None or data_df.empty:
                print("❌ No data available for Excel file")
                return None
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            excel_path = temp_file.name
            temp_file.close()
            
            # Create Excel file
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                data_df.to_excel(writer, sheet_name='Fitness Data', index=False)
            
            print(f"✅ Excel file created: {excel_path}")
            return excel_path
            
        except Exception as e:
            print(f"❌ Error creating Excel file: {e}")
            return None
    
    def create_final_email_body(self, original_body):
        """Create final email body with feedback request"""
        try:
            # Add feedback request line before the closing
            feedback_line = "\nPlease kindly let me know your feedback and tell me how I did?\n"
            
            # Find the closing section and insert feedback line before it
            if "Warm Regards," in original_body:
                parts = original_body.split("Warm Regards,")
                final_body = parts[0] + feedback_line + "Warm Regards," + parts[1]
            else:
                # If no specific closing found, add at the end
                final_body = original_body + feedback_line
            
            return final_body
            
        except Exception as e:
            print(f"❌ Error creating final email body: {e}")
            return original_body
    
    def create_message_with_attachment(self, to_email, subject, body, attachment_path=None):
        """Create a Gmail message with optional attachment"""
        try:
            message = MIMEMultipart()
            message['to'] = to_email
            message['from'] = self.email_address
            message['subject'] = subject
            
            # Add body
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                message.attach(part)
                print(f"✅ Attachment added: {os.path.basename(attachment_path)}")
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            return {'raw': raw_message}
            
        except Exception as e:
            print(f"❌ Error creating message with attachment: {e}")
            raise
    
    def send_final_email(self, email_body_data, iteration_count=1):
        """Send final approved email with Excel attachment"""
        try:
            # Get current date for subject
            current_date = datetime.now().strftime("%d/%m/%Y")
            subject = f"Progress Report : Charles Parmar : {current_date}"
            
            # Create final email body
            original_body = email_body_data.get('email_body', '')
            final_body = self.create_final_email_body(original_body)
            
            # Fetch Supabase data and create Excel file
            print("📊 Fetching Supabase data for Excel attachment...")
            data_df = self.fetch_supabase_data()
            excel_path = self.create_excel_file(data_df)
            
            # Create message with attachment
            message = self.create_message_with_attachment(
                to_email=self.coach_email,
                subject=subject,
                body=final_body,
                attachment_path=excel_path
            )
            
            # Send the message
            sent_message = self.service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            # Clean up temporary file
            if excel_path and os.path.exists(excel_path):
                os.unlink(excel_path)
                print("✅ Temporary Excel file cleaned up")
            
            print(f"✅ Final email sent successfully!")
            print(f"   To: {self.coach_email}")
            print(f"   Subject: {subject}")
            print(f"   Message ID: {sent_message['id']}")
            print(f"   Excel attachment: {'Yes' if excel_path else 'No'}")
            
            # Send push notification after successful email
            try:
                pushover_token = os.getenv("PUSHOVER_TOKEN")
                pushover_user_key = os.getenv("PUSHOVER_USER_KEY")
                
                if pushover_token and pushover_user_key:
                    # Create message with iteration count
                    iteration_text = f" after {iteration_count} feedback loop{'s' if iteration_count > 1 else ''}" if iteration_count > 1 else ""
                    pushover_data = {
                        "token": pushover_token,
                        "user": pushover_user_key,
                        "message": f"Your report has been sent successfully{iteration_text}",
                        "title": "Fitness Report Sent",
                        "priority": 0,
                        "sound": "pushover"
                    }
                    
                    response = requests.post(
                        "https://api.pushover.net/1/messages.json",
                        data=pushover_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("status") == 1:
                            iteration_text = f" after {iteration_count} feedback loop{'s' if iteration_count > 1 else ''}" if iteration_count > 1 else ""
                            print(f"✅ Push notification sent: Your report has been sent successfully{iteration_text}")
                        else:
                            print(f"❌ Failed to send push notification: {result.get('errors', 'Unknown error')}")
                    else:
                        print(f"❌ Failed to send push notification: {response.status_code}")
                else:
                    print("⚠️ Push notification skipped - credentials not configured")
            except Exception as e:
                print(f"⚠️ Failed to send push notification: {e}")
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'to_email': self.coach_email,
                'subject': subject,
                'excel_attached': excel_path is not None,
                'timestamp': datetime.now().isoformat()
            }
            
        except HttpError as error:
            print(f"❌ Error sending final email: {error}")
            return {
                'success': False,
                'error': str(error),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Unexpected error sending final email: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

def run_final_email_agent(email_body_data, iteration_count=1):
    """Run the Final Email Agent to send approved fitness report"""
    print("🤖 Starting Final Email Agent...")
    
    try:
        # Initialize the agent
        agent = FinalEmailAgent()
        
        # Extract email body from the data
        email_body = email_body_data.get('email_body', '')
        if not email_body:
            print("❌ No email body found in email_body_data")
            return {
                'success': False,
                'error': 'No email body found',
                'timestamp': datetime.now().isoformat()
            }
        
        # Send the final email
        result = agent.send_final_email(email_body_data, iteration_count)
        
        print("✅ Final Email Agent completed successfully")
        return result
        
    except Exception as e:
        print(f"❌ Error running Final Email Agent: {e}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Test the Final Email Agent
    test_email_body = {
        'email_body': 'This is a test fitness report email with Excel attachment.'
    }
    
    result = run_final_email_agent(test_email_body, 1)
    print(f"Test result: {result}") 