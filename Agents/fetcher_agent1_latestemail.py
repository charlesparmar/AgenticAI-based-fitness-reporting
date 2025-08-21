import os
import email
import imaplib
import json
import re
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from email.header import decode_header
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

class LatestEmailFetcher:
    """Agent for fetching the latest fitness data email from Gmail using IMAP"""
    
    def __init__(self):
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.connection = None
        
        # Pushover notifier
        self.notifier = PushoverNotifier()
        
    def send_push_notification(self, message: str, title: str = "Fitness Data Report"):
        """Send push notification"""
        return self.notifier.send_notification(message, title, priority=0, sound="pushover")
        
    def authenticate_imap(self, email_address: str, app_password: str) -> bool:
        """Authenticate with Gmail using IMAP and app password"""
        try:
            # Connect to Gmail IMAP server
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # Login with email and app password
            self.connection.login(email_address, app_password)
            
            print("✅ IMAP authentication successful!")
            return True
            
        except Exception as e:
            print(f"❌ IMAP authentication failed: {e}")
            return False
    
    def parse_fitness_data(self, email_body: str) -> Dict[str, Any]:
        """Parse fitness data from email body and create JSON structure"""
        # Clean up the HTML content
        body = re.sub(r'body\s*\{[^}]*\}', '', email_body)
        body = re.sub(r'\.[a-zA-Z-]+\s*\{[^}]*\}', '', body)
        
        # Extract key information
        data = {
            'metadata': {},
            'measurements': {}
        }
        
        # Extract date
        date_match = re.search(r'Fitness Data Entry Date:\s*(\d{2}/\d{2}/\d{4})', body)
        if date_match:
            data['metadata']['entry_date'] = date_match.group(1)
        
        # Extract submission time
        time_match = re.search(r'Submitted:\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', body)
        if time_match:
            data['metadata']['submitted'] = time_match.group(1)
        
        # Extract measurements with more precise regex patterns
        # Handle the specific case of "Above Navel" vs "Navel" carefully
        
        # First, extract all measurements with a more sophisticated approach
        measurement_patterns = {
            'Week Number': r'\bWeek Number\b\s*:\s*(\d+(?:\.\d+)?)',
            'Weight': r'\bWeight\b\s*:\s*(\d+(?:\.\d+)?)',
            'Fat Percentage': r'\bFat Percentage\b\s*:\s*(\.?\d+(?:\.\d+)?)',
            'Bmi': r'\bBmi\b\s*:\s*(\d+(?:\.\d+)?)',
            'Fat Weight': r'\bFat Weight\b\s*:\s*(\d+(?:\.\d+)?)',
            'Lean Weight': r'\bLean Weight\b\s*:\s*(\d+(?:\.\d+)?)',
            'Neck': r'\bNeck\b\s*:\s*(\d+(?:\.\d+)?)',
            'Shoulders': r'\bShoulders\b\s*:\s*(\d+(?:\.\d+)?)',
            'Biceps': r'\bBiceps\b\s*:\s*(\d+(?:\.\d+)?)',
            'Forearms': r'\bForearms\b\s*:\s*(\d+(?:\.\d+)?)',
            'Chest': r'\bChest\b\s*:\s*(\d+(?:\.\d+)?)',
            'Above Navel': r'\bAbove Navel\b\s*:\s*(\d+(?:\.\d+)?)',
            'Navel': r'\bNavel\b\s*:\s*(\d+(?:\.\d+)?)',
            'Waist': r'\bWaist\b\s*:\s*(\d+(?:\.\d+)?)',
            'Hips': r'\bHips\b\s*:\s*(\d+(?:\.\d+)?)',
            'Thighs': r'\bThighs\b\s*:\s*(\d+(?:\.\d+)?)',
            'Calves': r'\bCalves\b\s*:\s*(\d+(?:\.\d+)?)'
        }
        
        # Create a copy of the body for processing
        processed_body = body
        
        for measurement_name, pattern in measurement_patterns.items():
            match = re.search(pattern, processed_body, re.IGNORECASE)
            if match:
                value = match.group(1)
                # Convert to float if it has decimal, otherwise keep as string
                try:
                    if '.' in value:
                        data['measurements'][measurement_name] = float(value)
                    else:
                        data['measurements'][measurement_name] = int(value)
                except ValueError:
                    data['measurements'][measurement_name] = value
                
                # Debug logging for critical measurements only
                if measurement_name in ['Navel', 'Above Navel']:
                    print(f"🔍 DEBUG: Found {measurement_name} = {value}")
                
                # Remove the matched text to prevent re-matching
                processed_body = processed_body[:match.start()] + processed_body[match.end():]
        
        # Additional validation for Navel and Above Navel
        if 'Above Navel' in data['measurements'] and 'Navel' in data['measurements']:
            above_navel = data['measurements']['Above Navel']
            navel = data['measurements']['Navel']
            if above_navel == navel:
                print(f"⚠️  WARNING: Above Navel ({above_navel}) and Navel ({navel}) have the same value!")
                print(f"🔍 This might indicate a parsing error. Please verify the email content.")
        
        return data
    
    def create_fitness_json(self, fitness_data: Dict[str, Any], email_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a JSON structure with fitness data (not saved locally)"""
        # Create comprehensive JSON structure
        json_data = {
            'email_info': {
                'subject': email_info.get('subject'),
                'sender': email_info.get('sender'),
                'date': email_info.get('date'),
                'email_id': email_info.get('email_id'),
                'fetched_at': email_info.get('timestamp')
            },
            'fitness_data': fitness_data,
            'processed_at': datetime.now().isoformat()
        }
        
        print(f"✅ Created JSON data structure")
        return json_data
    
    def fetch_latest_fitness_email(self, email_address: str, app_password: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest email with subject 'Fitness Data Entry' using IMAP"""
        try:
            # Send initial notification
            self.send_push_notification("Data analysis and Fitness Data reporting initiated")
            
            # Authenticate
            if not self.authenticate_imap(email_address, app_password):
                return None
            
            # Select the INBOX
            self.connection.select('INBOX')
            
            # Search for emails with specific subject
            search_criteria = 'SUBJECT "Fitness Data Entry"'
            status, message_numbers = self.connection.search(None, search_criteria)
            
            if status != 'OK':
                return {
                    'success': False,
                    'error': 'Failed to search emails',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get the latest email (last in the list)
            email_list = message_numbers[0].split()
            
            if not email_list:
                return {
                    'success': False,
                    'error': 'No emails found with subject "Fitness Data Entry"',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get the latest email (last message number)
            latest_email_num = email_list[-1]
            
            # Fetch the email
            status, message_data = self.connection.fetch(latest_email_num, '(RFC822)')
            
            if status != 'OK':
                return {
                    'success': False,
                    'error': 'Failed to fetch email',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Parse the email
            raw_email = message_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract email details
            subject = self._decode_header(email_message['subject'])
            sender = self._decode_header(email_message['from'])
            date = self._decode_header(email_message['date'])
            
            # Extract email body
            body = self._extract_email_body(email_message)
            
            # Close connection
            self.connection.close()
            self.connection.logout()
            
            # Parse fitness data from body
            fitness_data = self.parse_fitness_data(body)
            
            # Create JSON structure (not saved locally)
            json_data = self.create_fitness_json(fitness_data, {
                'subject': subject,
                'sender': sender,
                'date': date,
                'email_id': latest_email_num.decode(),
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'json_data': json_data,
                'message': 'Latest fitness email fetched and JSON created',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            if self.connection:
                try:
                    self.connection.close()
                    self.connection.logout()
                except:
                    pass
            
            return {
                'success': False,
                'error': f'Unexpected error: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _decode_header(self, header_value: str) -> str:
        """Decode email header values"""
        if not header_value:
            return "Unknown"
        
        decoded_parts = decode_header(header_value)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_string += part.decode(encoding)
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += str(part)
        
        return decoded_string
    
    def _extract_email_body(self, email_message) -> str:
        """Extract email body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text content (prefer plain text over HTML)
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        if body.strip():  # If we found plain text content, use it
                            break
                    except:
                        continue
                elif content_type == "text/html" and not body:
                    # Fall back to HTML if no plain text found
                    try:
                        html_body = part.get_payload(decode=True).decode()
                        # Simple HTML to text conversion
                        import re
                        # Remove HTML tags
                        body = re.sub(r'<[^>]+>', '', html_body)
                        # Remove extra whitespace
                        body = re.sub(r'\s+', ' ', body).strip()
                    except:
                        continue
        else:
            # Not multipart
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                body = "Could not decode email body"
        
        # If still no body, try to get any available content
        if not body.strip():
            try:
                # Try to get the raw payload
                payload = email_message.get_payload()
                if isinstance(payload, list):
                    for part in payload:
                        if hasattr(part, 'get_payload'):
                            try:
                                part_body = part.get_payload(decode=True).decode()
                                if part_body.strip():
                                    body = part_body
                                    break
                            except:
                                continue
                else:
                    body = str(payload)
            except:
                body = "Could not extract email body"
        
        return body.strip() if body else "No readable content found"

def run_latest_email_fetcher(email_address: str, app_password: str):
    """Run the latest email fetcher agent"""
    try:
        fetcher = LatestEmailFetcher()
        result = fetcher.fetch_latest_fitness_email(email_address, app_password)
        
        if result.get('success'):
            print("✅ Successfully fetched latest fitness email:")
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
                
            return json_data  # Return JSON data for next agent
        else:
            print(f"❌ Error fetching email: {result.get('error')}")
        
        return None
        
    except Exception as e:
        print(f"❌ Error running latest email fetcher agent: {e}")
        return None

if __name__ == "__main__":
    # Example usage with environment variables
    email_address = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if email_address and app_password:
        run_latest_email_fetcher(email_address, app_password)
    else:
        print("Please set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in your .env file") 