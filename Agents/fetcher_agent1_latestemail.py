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
        print(f"🔍 DEBUG: Email body length: {len(email_body)}")
        print(f"🔍 DEBUG: Email body preview: {email_body[:500]}...")
        
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
        
        # Try multiple parsing strategies
        measurements_found = self._parse_measurements_strategy_1(body)
        if not measurements_found:
            measurements_found = self._parse_measurements_strategy_2(body)
        if not measurements_found:
            measurements_found = self._parse_measurements_strategy_3(body)
        if not measurements_found:
            measurements_found = self._parse_measurements_strategy_4(body)
        
        data['measurements'] = measurements_found
        
        print(f"🔍 DEBUG: Total measurements found: {len(measurements_found)}")
        if measurements_found:
            print(f"🔍 DEBUG: Measurements: {list(measurements_found.keys())}")
        
        # Additional validation for Navel and Above Navel
        if 'Above Navel' in data['measurements'] and 'Navel' in data['measurements']:
            above_navel = data['measurements']['Above Navel']
            navel = data['measurements']['Navel']
            if above_navel == navel:
                print(f"⚠️  WARNING: Above Navel ({above_navel}) and Navel ({navel}) have the same value!")
                print(f"🔍 This might indicate a parsing error. Please verify the email content.")
        
        return data
    
    def _parse_measurements_strategy_1(self, body: str) -> Dict[str, Any]:
        """Strategy 1: Standard colon-separated format with precise patterns"""
        print("🔍 DEBUG: Trying Strategy 1 - Standard colon format")
        
        measurement_patterns = {
            'Week Number': r'\bWeek\s+Number\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Weight': r'(?<!Fat\s)(?<!Lean\s)\bWeight\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Fat Percentage': r'\bFat\s+Percentage\b[\s\t]*[:=][\s\t]*(\.?\d+(?:\.\d+)?)',
            'Bmi': r'\bBmi\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Fat Weight': r'\bFat\s+Weight\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Lean Weight': r'\bLean\s+Weight\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Neck': r'\bNeck\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Shoulders': r'\bShoulders\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Biceps': r'\bBiceps\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Forearms': r'\bForearms\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Chest': r'\bChest\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Above Navel': r'\bAbove\s+Navel\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Navel': r'(?<!Above\s)\bNavel\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Waist': r'\bWaist\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Hips': r'\bHips\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Thighs': r'\bThighs\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)',
            'Calves': r'\bCalves\b[\s\t]*[:=][\s\t]*(\d+(?:\.\d+)?)'
        }
        
        return self._extract_measurements_with_patterns(body, measurement_patterns)
    
    def _parse_measurements_strategy_2(self, body: str) -> Dict[str, Any]:
        """Strategy 2: Table format with headers"""
        print("🔍 DEBUG: Trying Strategy 2 - Table format")
        
        # Look for table-like structure
        lines = body.split('\n')
        measurements = {}
        
        # Define measurement patterns in order of specificity (most specific first)
        measurement_specs = [
            ('Week Number', r'\bWeek\s+Number\b'),
            ('Fat Percentage', r'\bFat\s+Percentage\b'),
            ('Fat Weight', r'\bFat\s+Weight\b'),
            ('Lean Weight', r'\bLean\s+Weight\b'),
            ('Above Navel', r'\bAbove\s+Navel\b'),
            ('Weight', r'(?<!Fat\s)(?<!Lean\s)\bWeight\b'),  # Must come after Fat/Lean Weight
            ('Bmi', r'\bBmi\b'),
            ('Neck', r'\bNeck\b'),
            ('Shoulders', r'\bShoulders\b'),
            ('Biceps', r'\bBiceps\b'),
            ('Forearms', r'\bForearms\b'),
            ('Chest', r'\bChest\b'),
            ('Navel', r'(?<!Above\s)\bNavel\b'),  # Must come after Above Navel
            ('Waist', r'\bWaist\b'),
            ('Hips', r'\bHips\b'),
            ('Thighs', r'\bThighs\b'),
            ('Calves', r'\bCalves\b')
        ]
        
        # Find the measurements section
        in_measurements = False
        for line in lines:
            line = line.strip()
            if 'measurements' in line.lower() or 'measurement' in line.lower():
                in_measurements = True
                continue
            
            if in_measurements and line:
                # Try to parse each measurement in order of specificity
                for measurement_name, pattern in measurement_specs:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Extract value after the measurement name using flexible pattern
                        # Support both colon/equals and whitespace separators
                        value_pattern = rf'{pattern}[\s\t]*(?:[:=][\s\t]*|[\s\t]+)([\d.]+)'
                        value_match = re.search(value_pattern, line, re.IGNORECASE)
                        if value_match:
                            value = value_match.group(1)
                            try:
                                if '.' in value:
                                    measurements[measurement_name] = float(value)
                                else:
                                    measurements[measurement_name] = int(value)
                            except ValueError:
                                measurements[measurement_name] = value
                            break  # Stop after first match to avoid duplicate processing
        
        return measurements
    
    def _parse_measurements_strategy_3(self, body: str) -> Dict[str, Any]:
        """Strategy 3: HTML table format"""
        print("🔍 DEBUG: Trying Strategy 3 - HTML table format")
        
        # Look for HTML table structure
        measurements = {}
        
        # Define measurement specs in order of specificity (most specific first)
        measurement_specs = [
            ('Week Number', ['week number', 'weeknumber']),
            ('Fat Percentage', ['fat percentage', 'fatpercentage']),
            ('Fat Weight', ['fat weight', 'fatweight']),
            ('Lean Weight', ['lean weight', 'leanweight']),
            ('Above Navel', ['above navel', 'abovenavel']),
            ('Weight', ['weight']),  # Must come after Fat/Lean Weight
            ('Bmi', ['bmi', 'b.m.i']),
            ('Neck', ['neck']),
            ('Shoulders', ['shoulders']),
            ('Biceps', ['biceps']),
            ('Forearms', ['forearms']),
            ('Chest', ['chest']),
            ('Navel', ['navel']),  # Must come after Above Navel
            ('Waist', ['waist']),
            ('Hips', ['hips']),
            ('Thighs', ['thighs']),
            ('Calves', ['calves'])
        ]
        
        # Extract from HTML table rows
        table_row_pattern = r'<tr[^>]*>(.*?)</tr>'
        table_rows = re.findall(table_row_pattern, body, re.DOTALL | re.IGNORECASE)
        
        for row in table_rows:
            # Extract cells
            cell_pattern = r'<td[^>]*>(.*?)</td>'
            cells = re.findall(cell_pattern, row, re.DOTALL | re.IGNORECASE)
            
            if len(cells) >= 2:
                measurement_name = re.sub(r'<[^>]+>', '', cells[0]).strip().lower()
                value_text = re.sub(r'<[^>]+>', '', cells[1]).strip()
                
                # Check measurements in order of specificity
                for known_name, aliases in measurement_specs:
                    match_found = False
                    for alias in aliases:
                        if alias in measurement_name:
                            # Special handling for Weight to avoid Fat Weight/Lean Weight conflicts
                            if known_name == 'Weight':
                                if 'fat' in measurement_name or 'lean' in measurement_name:
                                    continue  # Skip, this should match Fat Weight or Lean Weight
                            
                            # Special handling for Navel to avoid Above Navel conflicts
                            if known_name == 'Navel':
                                if 'above' in measurement_name:
                                    continue  # Skip, this should match Above Navel
                            
                            # Extract numeric value
                            value_match = re.search(r'([\d.]+)', value_text)
                            if value_match:
                                value = value_match.group(1)
                                try:
                                    if '.' in value:
                                        measurements[known_name] = float(value)
                                    else:
                                        measurements[known_name] = int(value)
                                except ValueError:
                                    measurements[known_name] = value
                                match_found = True
                                break
                    
                    if match_found:
                        break  # Stop after first successful match
        
        return measurements
    
    def _parse_measurements_strategy_4(self, body: str) -> Dict[str, Any]:
        """Strategy 4: Unstructured text with flexible patterns"""
        print("🔍 DEBUG: Trying Strategy 4 - Unstructured text")
        
        measurements = {}
        
        # More flexible patterns in order of specificity (most specific first)
        flexible_patterns = {
            'Week Number': r'week\s+number[^\d]*(\d+(?:\.\d+)?)',
            'Fat Percentage': r'fat\s+percentage[^\d]*(\.?\d+(?:\.\d+)?)',
            'Fat Weight': r'fat\s+weight[^\d]*(\d+(?:\.\d+)?)',
            'Lean Weight': r'lean\s+weight[^\d]*(\d+(?:\.\d+)?)',
            'Above Navel': r'above\s+navel[^\d]*(\d+(?:\.\d+)?)',
            'Weight': r'(?<!fat\s)(?<!lean\s)weight[^\d]*(\d+(?:\.\d+)?)',  # Must come after Fat/Lean Weight
            'Bmi': r'bmi[^\d]*(\d+(?:\.\d+)?)',
            'Neck': r'neck[^\d]*(\d+(?:\.\d+)?)',
            'Shoulders': r'shoulders[^\d]*(\d+(?:\.\d+)?)',
            'Biceps': r'biceps[^\d]*(\d+(?:\.\d+)?)',
            'Forearms': r'forearms[^\d]*(\d+(?:\.\d+)?)',
            'Chest': r'chest[^\d]*(\d+(?:\.\d+)?)',
            'Navel': r'(?<!above\s)navel[^\d]*(\d+(?:\.\d+)?)',  # Must come after Above Navel
            'Waist': r'waist[^\d]*(\d+(?:\.\d+)?)',
            'Hips': r'hips[^\d]*(\d+(?:\.\d+)?)',
            'Thighs': r'thighs[^\d]*(\d+(?:\.\d+)?)',
            'Calves': r'calves[^\d]*(\d+(?:\.\d+)?)'
        }
        
        # Use improved extraction method that processes in order
        measurements = self._extract_measurements_with_ordered_patterns(body, flexible_patterns)
        
        # Fix Fat Percentage if it was parsed incorrectly
        if 'Fat Percentage' in measurements:
            fat_pct = measurements['Fat Percentage']
            if isinstance(fat_pct, int) and fat_pct > 100:
                # This is likely a decimal value that was parsed as integer
                measurements['Fat Percentage'] = fat_pct / 1000.0  # Convert 514 to 0.514
                print(f"🔍 DEBUG: Fixed Fat Percentage from {fat_pct} to {measurements['Fat Percentage']}")
        
        return measurements
    
    def _extract_measurements_with_ordered_patterns(self, body: str, patterns: Dict[str, str]) -> Dict[str, Any]:
        """Extract measurements using provided patterns in order (for Strategy 4)"""
        measurements = {}
        processed_body = body
        
        # Process patterns in the order they were defined
        for measurement_name, pattern in patterns.items():
            match = re.search(pattern, processed_body, re.IGNORECASE)
            if match:
                value = match.group(1)
                
                # Special handling for Fat Percentage to ensure proper decimal conversion
                if measurement_name == 'Fat Percentage' and value.startswith('.'):
                    value = '0' + value
                
                try:
                    if '.' in value:
                        measurements[measurement_name] = float(value)
                    else:
                        measurements[measurement_name] = int(value)
                except ValueError:
                    measurements[measurement_name] = value
                
                # Debug logging for critical measurements
                if measurement_name in ['Navel', 'Above Navel', 'Fat Percentage', 'Weight', 'Fat Weight', 'Lean Weight']:
                    print(f"🔍 DEBUG: Found {measurement_name} = {value} -> {measurements[measurement_name]}")
                
                # Remove the matched text to prevent re-matching
                processed_body = processed_body[:match.start()] + processed_body[match.end():]
        
        return measurements
    
    def _extract_measurements_with_patterns(self, body: str, patterns: Dict[str, str]) -> Dict[str, Any]:
        """Extract measurements using provided patterns"""
        measurements = {}
        processed_body = body
        
        for measurement_name, pattern in patterns.items():
            match = re.search(pattern, processed_body, re.IGNORECASE)
            if match:
                value = match.group(1)
                
                # Special handling for Fat Percentage to ensure proper decimal conversion
                if measurement_name == 'Fat Percentage' and value.startswith('.'):
                    value = '0' + value
                
                try:
                    if '.' in value:
                        measurements[measurement_name] = float(value)
                    else:
                        measurements[measurement_name] = int(value)
                except ValueError:
                    measurements[measurement_name] = value
                
                # Debug logging for critical measurements
                if measurement_name in ['Navel', 'Above Navel', 'Fat Percentage']:
                    print(f"🔍 DEBUG: Found {measurement_name} = {value} -> {measurements[measurement_name]}")
                
                # Remove the matched text to prevent re-matching
                processed_body = processed_body[:match.start()] + processed_body[match.end():]
        
        return measurements
    
    def validate_extracted_measurements(self, email_body: str, extracted_measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted measurements by re-parsing the email body with precise patterns.
        This serves as a quality check to catch parsing errors.
        """
        print("🔍 VALIDATION: Starting measurement validation...")
        
        # More precise validation patterns - designed to be very specific
        validation_patterns = {
            'Week Number': [
                r'Week\s+Number\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Week\s+Number\s+(\d+(?:\.\d+)?)',
                r'(?:Week|Wk)\s*#?\s*(\d+(?:\.\d+)?)'
            ],
            'Weight': [
                r'(?<!Fat\s)(?<!Lean\s)Weight\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'(?<!Fat\s)(?<!Lean\s)Weight\s+(\d+(?:\.\d+)?)',
                r'Body\s+Weight\s*[:=]?\s*(\d+(?:\.\d+)?)'
            ],
            'Fat Percentage': [
                r'Fat\s+Percentage\s*[:=]\s*(0?\.\d+|\d+\.\d+)',
                r'Fat\s+%\s*[:=]?\s*(0?\.\d+|\d+\.\d+)',
                r'Body\s+Fat\s*[:=]?\s*(0?\.\d+|\d+\.\d+)'
            ],
            'Bmi': [
                r'BMI\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'B\.?M\.?I\.?\s*[:=]?\s*(\d+(?:\.\d+)?)',
                r'Body\s+Mass\s+Index\s*[:=]?\s*(\d+(?:\.\d+)?)'
            ],
            'Fat Weight': [
                r'Fat\s+Weight\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Fat\s+Wt\s*[:=]?\s*(\d+(?:\.\d+)?)'
            ],
            'Lean Weight': [
                r'Lean\s+Weight\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Lean\s+Wt\s*[:=]?\s*(\d+(?:\.\d+)?)',
                r'Muscle\s+Weight\s*[:=]?\s*(\d+(?:\.\d+)?)'
            ],
            'Neck': [
                r'Neck\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Neck\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Shoulders': [
                r'Shoulders\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Shoulders\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Biceps': [
                r'Biceps\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Biceps\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Forearms': [
                r'Forearms\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Forearms\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Chest': [
                r'Chest\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Chest\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Above Navel': [
                r'Above\s+Navel\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Above\s+Navel\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Navel': [
                r'(?<!Above\s)Navel\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'(?<!Above\s)Navel\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?',
                r'Belly\s+Button\s*[:=]?\s*(\d+(?:\.\d+)?)'
            ],
            'Waist': [
                r'Waist\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Waist\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Hips': [
                r'Hips\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Hips\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Thighs': [
                r'Thighs\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Thighs\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ],
            'Calves': [
                r'Calves\s*[:=]\s*(\d+(?:\.\d+)?)',
                r'Calves\s+(\d+(?:\.\d+)?)\s*(?:cm|in|inches?)?'
            ]
        }
        
        validated_measurements = {}
        corrections_made = {}
        
        # Validate each measurement
        for measurement_name in extracted_measurements.keys():
            if measurement_name in validation_patterns:
                validated_value = None
                
                # Try each validation pattern for this measurement
                for pattern in validation_patterns[measurement_name]:
                    match = re.search(pattern, email_body, re.IGNORECASE)
                    if match:
                        raw_value = match.group(1)
                        
                        # Convert to appropriate type
                        try:
                            if '.' in raw_value:
                                validated_value = float(raw_value)
                            else:
                                validated_value = int(raw_value)
                            break  # Use first successful match
                        except ValueError:
                            continue
                
                if validated_value is not None:
                    validated_measurements[measurement_name] = validated_value
                    
                    # Check for discrepancies
                    extracted_value = extracted_measurements[measurement_name]
                    if extracted_value != validated_value:
                        corrections_made[measurement_name] = {
                            'extracted': extracted_value,
                            'validated': validated_value
                        }
                        print(f"⚠️  VALIDATION: Correcting {measurement_name}: {extracted_value} → {validated_value}")
                else:
                    # If validation failed, keep the extracted value
                    validated_measurements[measurement_name] = extracted_measurements[measurement_name]
                    print(f"ℹ️  VALIDATION: Could not validate {measurement_name}, keeping extracted value: {extracted_measurements[measurement_name]}")
            else:
                # Keep measurements that don't have validation patterns
                validated_measurements[measurement_name] = extracted_measurements[measurement_name]
        
        # Additional range validation for specific measurements
        validated_measurements = self._apply_range_validation(validated_measurements, corrections_made)
        
        # Log validation summary
        if corrections_made:
            print(f"🔧 VALIDATION: Made {len(corrections_made)} corrections:")
            for measurement, correction in corrections_made.items():
                print(f"   • {measurement}: {correction['extracted']} → {correction['validated']}")
        else:
            print("✅ VALIDATION: All measurements validated successfully, no corrections needed")
        
        return validated_measurements
    
    def _apply_range_validation(self, measurements: Dict[str, Any], corrections_made: Dict[str, Any]) -> Dict[str, Any]:
        """Apply additional range validation for measurements"""
        # Define reasonable ranges for measurements
        ranges = {
            'Fat Percentage': (0.05, 0.60),  # 5% to 60%
            'Bmi': (10.0, 60.0),  # BMI between 10 and 60
            'Weight': (30.0, 500.0),  # Weight between 30 and 500 lbs/kg
            'Week Number': (1, 104)  # Week 1 to 104 (2 years)
        }
        
        for measurement_name, (min_val, max_val) in ranges.items():
            if measurement_name in measurements:
                value = measurements[measurement_name]
                if not (min_val <= value <= max_val):
                    print(f"⚠️  RANGE WARNING: {measurement_name} value {value} is outside expected range [{min_val}, {max_val}]")
                    
                    # Special handling for Fat Percentage
                    if measurement_name == 'Fat Percentage' and value > 1.0:
                        # Might be a percentage instead of decimal (e.g., 25.4 instead of 0.254)
                        corrected_value = value / 100.0
                        if min_val <= corrected_value <= max_val:
                            measurements[measurement_name] = corrected_value
                            corrections_made[measurement_name] = {
                                'extracted': value,
                                'validated': corrected_value,
                                'reason': 'Range validation - converted percentage to decimal'
                            }
                            print(f"🔧 RANGE CORRECTION: {measurement_name}: {value} → {corrected_value} (converted % to decimal)")
        
        return measurements
    
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
            
            # Validate the extracted measurements
            if fitness_data.get('measurements'):
                print("\n🔍 VALIDATION: Validating extracted measurements...")
                validated_measurements = self.validate_extracted_measurements(body, fitness_data['measurements'])
                fitness_data['measurements'] = validated_measurements
                print("✅ VALIDATION: Measurement validation completed\n")
            
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
        """Extract email body from email message with enhanced format handling"""
        body = ""
        
        print(f"🔍 DEBUG: Email content type: {email_message.get_content_type()}")
        print(f"🔍 DEBUG: Email is multipart: {email_message.is_multipart()}")
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                print(f"🔍 DEBUG: Part content type: {content_type}")
                print(f"🔍 DEBUG: Part disposition: {content_disposition}")
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text content (prefer plain text over HTML)
                if content_type == "text/plain":
                    try:
                        part_body = part.get_payload(decode=True).decode()
                        if part_body.strip():  # If we found plain text content, use it
                            body = part_body
                            print(f"🔍 DEBUG: Found plain text content, length: {len(body)}")
                            break
                    except Exception as e:
                        print(f"🔍 DEBUG: Error decoding plain text: {e}")
                        continue
                elif content_type == "text/html" and not body:
                    # Fall back to HTML if no plain text found
                    try:
                        html_body = part.get_payload(decode=True).decode()
                        print(f"🔍 DEBUG: Found HTML content, length: {len(html_body)}")
                        
                        # Enhanced HTML to text conversion
                        import re
                        
                        # Remove script and style tags
                        html_body = re.sub(r'<script[^>]*>.*?</script>', '', html_body, flags=re.DOTALL | re.IGNORECASE)
                        html_body = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL | re.IGNORECASE)
                        
                        # Convert common HTML entities
                        html_body = html_body.replace('&nbsp;', ' ')
                        html_body = html_body.replace('&amp;', '&')
                        html_body = html_body.replace('&lt;', '<')
                        html_body = html_body.replace('&gt;', '>')
                        html_body = html_body.replace('&quot;', '"')
                        
                        # Remove HTML tags but preserve line breaks
                        html_body = re.sub(r'<br[^>]*>', '\n', html_body, flags=re.IGNORECASE)
                        html_body = re.sub(r'</p>', '\n', html_body, flags=re.IGNORECASE)
                        html_body = re.sub(r'<[^>]+>', '', html_body)
                        
                        # Clean up whitespace
                        html_body = re.sub(r'\s+', ' ', html_body)
                        html_body = re.sub(r'\n\s*\n', '\n', html_body)
                        
                        body = html_body.strip()
                        print(f"🔍 DEBUG: Converted HTML to text, length: {len(body)}")
                    except Exception as e:
                        print(f"🔍 DEBUG: Error processing HTML: {e}")
                        continue
        else:
            # Not multipart
            try:
                body = email_message.get_payload(decode=True).decode()
                print(f"🔍 DEBUG: Single part email, length: {len(body)}")
            except Exception as e:
                print(f"🔍 DEBUG: Error decoding single part: {e}")
                body = "Could not decode email body"
        
        # If still no body, try to get any available content
        if not body.strip():
            print("🔍 DEBUG: No body found, trying alternative extraction methods")
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
                                    print(f"🔍 DEBUG: Found alternative content, length: {len(body)}")
                                    break
                            except:
                                continue
                else:
                    body = str(payload)
                    print(f"🔍 DEBUG: Using raw payload, length: {len(body)}")
            except Exception as e:
                print(f"🔍 DEBUG: Error in alternative extraction: {e}")
                body = "Could not extract email body"
        
        final_body = body.strip() if body else "No readable content found"
        print(f"🔍 DEBUG: Final body length: {len(final_body)}")
        return final_body

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