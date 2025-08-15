#!/usr/bin/env python3
"""
Gmail Token Refresh Script
This script helps refresh Gmail API tokens with the correct scopes for the fitness reporting system.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API scopes required for the fitness reporting system
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

def refresh_gmail_token():
    """Refresh Gmail API token with correct scopes"""
    
    print("🔄 Gmail Token Refresh Script")
    print("=" * 50)
    
    # Check if credentials.json exists
    credentials_path = "credentials.json"
    if not os.path.exists(credentials_path):
        print(f"❌ Error: {credentials_path} not found!")
        print("Please download your Gmail API credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to APIs & Services > Credentials")
        print("4. Download the OAuth 2.0 Client ID as 'credentials.json'")
        print("5. Place it in this directory")
        return False
    
    try:
        # Load existing token if it exists
        token_path = "token.json"
        creds = None
        
        if os.path.exists(token_path):
            print("📁 Found existing token.json")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ Failed to refresh token: {e}")
                    print("🔄 Starting new authentication flow...")
                    creds = None
            
            if not creds:
                print("🔄 Starting new authentication flow...")
                print("📋 Required scopes:")
                for scope in SCOPES:
                    print(f"   • {scope}")
                print()
                
                # Create flow instance
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                
                # Run the local server for OAuth2 authentication
                print("🌐 Opening browser for authentication...")
                print("Please complete the authentication in your browser.")
                print("The server will automatically close after authentication.")
                print()
                
                creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        print("💾 Saving new token to token.json...")
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print("✅ Token successfully refreshed and saved!")
        print(f"📁 Token saved to: {os.path.abspath(token_path)}")
        print(f"⏰ Token expires: {creds.expiry}")
        
        # Verify scopes
        print("\n🔍 Verifying scopes:")
        for scope in SCOPES:
            if scope in creds.scopes:
                print(f"   ✅ {scope}")
            else:
                print(f"   ❌ {scope} (MISSING)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return False

def main():
    """Main function"""
    print("Gmail API Token Refresh Tool")
    print("This tool will refresh your Gmail API token with the correct scopes.")
    print()
    
    success = refresh_gmail_token()
    
    if success:
        print("\n🎉 Token refresh completed successfully!")
        print("You can now run your fitness reporting workflow.")
    else:
        print("\n❌ Token refresh failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
