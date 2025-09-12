#!/usr/bin/env python3
"""
Service Account Authentication for Gmail API
This script uses service account credentials for Gmail API access.
"""

import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API scopes required for the fitness reporting system
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

def create_service_account_credentials():
    """Create service account credentials for Gmail API"""
    
    print("🔐 Service Account Authentication Setup")
    print("=" * 50)
    
    # Check if service account file exists
    service_account_file = "service-account.json"
    if not os.path.exists(service_account_file):
        print(f"❌ Error: {service_account_file} not found!")
        print("Please download your service account JSON file from Google Cloud Console:")
        print("1. Go to IAM & Admin > Service Accounts")
        print("2. Click on your service account")
        print("3. Go to Keys tab > Add Key > Create new key > JSON")
        print("4. Save it as 'service-account.json' in this directory")
        return None
    
    try:
        # Get the user email to impersonate (from environment or prompt)
        user_email = os.getenv("GMAIL_ADDRESS")
        if not user_email:
            print("❌ Error: GMAIL_ADDRESS not found in environment variables")
            print("Please set GMAIL_ADDRESS in your .env file")
            return None
        
        print(f"📧 Creating credentials for: {user_email}")
        
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES
        )
        
        # Create delegated credentials (impersonate the user)
        delegated_credentials = credentials.with_subject(user_email)
        
        # Test the credentials
        print("🔍 Testing credentials...")
        delegated_credentials.refresh(Request())
        
        print("✅ Service account authentication successful!")
        print(f"📊 Scopes: {', '.join(SCOPES)}")
        print(f"👤 Impersonating: {user_email}")
        print(f"⏰ Token expires: {delegated_credentials.expiry}")
        
        return delegated_credentials
        
    except Exception as e:
        print(f"❌ Error creating service account credentials: {e}")
        return None

def save_credentials_as_token(credentials):
    """Save service account credentials in token.json format for compatibility"""
    
    if not credentials:
        return False
    
    try:
        # Create a token-like structure for compatibility
        token_data = {
            "token": credentials.token,
            "refresh_token": None,  # Service accounts don't use refresh tokens
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": None,
            "client_secret": None,
            "scopes": SCOPES,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            "type": "service_account"
        }
        
        with open("token.json", 'w') as token_file:
            json.dump(token_data, token_file, indent=2)
        
        print("💾 Credentials saved to token.json (service account format)")
        return True
        
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False

def main():
    """Main function"""
    print("Gmail API Service Account Authentication")
    print("This tool sets up service account authentication for Gmail API.")
    print()
    
    credentials = create_service_account_credentials()
    
    if credentials:
        success = save_credentials_as_token(credentials)
        if success:
            print("\n🎉 Service account setup completed successfully!")
            print("You can now run your fitness reporting workflow with service account auth.")
        else:
            print("\n❌ Failed to save credentials!")
    else:
        print("\n❌ Service account setup failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
