# Dual Email Setup Guide

## Overview

The fitness reporting system now uses **two different email addresses** for different purposes:

1. **Email Fetching**: `charlesparmar@gmail.com` (IMAP + App Password)
2. **Email Sending**: `charles@parmarcharles.com` (OAuth 2.0)

## Setup Process

### 1. Gmail Fetcher Setup (charlesparmar@gmail.com)

This email is used by `fetcher_agent1_latestemail.py` to fetch fitness data emails.

**Requirements:**
- Gmail account: `charlesparmar@gmail.com`
- App Password (not regular password)

**Steps:**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already enabled
3. Generate an App Password:
   - Go to "App passwords"
   - Select "Mail" and your device
   - Copy the 16-character app password
4. Add to `.env` file:
   ```env
   GMAIL_FETCHER_ADDRESS=charlesparmar@gmail.com
   GMAIL_FETCHER_APP_PASSWORD=your_16_character_app_password
   ```

### 2. Gmail Sender Setup (charles@parmarcharles.com)

This email is used for sending final reports via OAuth 2.0.

**Requirements:**
- Gmail account or Google Workspace: `charles@parmarcharles.com`
- OAuth 2.0 credentials from Google Cloud Console

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select your project
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Application type: "Desktop application"
   - Name: "Fitness Reporting System"
   - Download the credentials as `credentials.json`
5. Place `credentials.json` in your project root
6. Run the token refresh script:
   ```bash
   python3 refresh_gmail_token.py
   ```
7. Complete OAuth flow in browser (authenticate with charles@parmarcharles.com)
8. Verify `token_sender.json` is created

### 3. Environment Variables

Your `.env` file should contain:

```env
# Gmail Fetcher Configuration (IMAP)
GMAIL_FETCHER_ADDRESS=charlesparmar@gmail.com
GMAIL_FETCHER_APP_PASSWORD=your_app_password_here

# Gmail Sender Configuration (OAuth 2.0)
GMAIL_ADDRESS=charles@parmarcharles.com

# Other configurations...
PUSHOVER_USER_KEY=your_pushover_key
PUSHOVER_TOKEN=your_pushover_token
```

### 4. File Structure

After setup, you should have:

```
project_root/
├── .env                    # Environment variables
├── credentials.json        # OAuth credentials for charles@parmarcharles.com
├── token_sender.json       # OAuth token for charles@parmarcharles.com
├── refresh_gmail_token.py  # Token refresh script
└── reporting_workflow.py   # Main workflow
```

## Workflow Process

1. **Fetch Email**: Uses `charlesparmar@gmail.com` (IMAP + App Password)
   - Fetches fitness data emails from inbox
   - Parses and extracts measurement data

2. **Process Data**: Modern API-only processing
   - Database reconciliation via SQLite Cloud API
   - AI-powered data validation
   - Supabase entry via REST API (no web automation)

3. **Generate Report**: Modern LLM-powered content generation
   - Baseline data retrieval from SQLite Cloud
   - AI-powered email body generation
   - Quality evaluation with feedback loop

4. **Send Report**: Uses `charles@parmarcharles.com` (OAuth 2.0)
   - Sends professional reports with Excel attachments
   - Gmail API integration (no SMTP)
   - Enterprise-grade delivery

## Troubleshooting

### Token Issues
- If `token_sender.json` is missing: Run `python3 refresh_gmail_token.py`
- If token expires: Workflow will auto-refresh or run refresh script manually
- If OAuth fails: Check credentials.json is for correct domain

### IMAP Issues
- If fetcher fails: Verify app password is correct
- If no emails found: Check subject line "Fitness Data Entry"
- If authentication fails: Generate new app password

### Permission Issues
- Gmail API not enabled: Enable in Google Cloud Console
- OAuth scope errors: Re-run refresh script
- Domain restrictions: Ensure charles@parmarcharles.com has proper access

## Verification

To verify setup:

1. Check environment variables:
   ```bash
   python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Fetcher:', os.getenv('GMAIL_FETCHER_ADDRESS')); print('Sender:', os.getenv('GMAIL_ADDRESS'))"
   ```

2. Test token:
   ```bash
   python3 refresh_gmail_token.py
   ```

3. Run workflow:
   ```bash
   python3 reporting_workflow.py
   ```

## Security Notes

- **App Password**: Only used for IMAP access, limited scope
- **OAuth Token**: Full Gmail API access, more secure than passwords
- **Credentials**: Store `credentials.json` securely, don't commit to git
- **Environment**: Keep `.env` file private and secure

## Benefits of Dual Email Setup

1. **Security**: Separation of concerns - reading vs writing
2. **Reliability**: Independent authentication methods
3. **Flexibility**: Different domains for different purposes
4. **Scalability**: Easier to manage different access levels

## v4.0.0 Modernization

**Legacy Components Removed:**
- ❌ Selenium web automation for Supabase login
- ❌ Browser-based report generation
- ❌ Legacy SUPABASE_URL, SUPABASE_EMAIL, SUPABASE_PASSWORD

**Modern API-Only Architecture:**
- ✅ Direct REST API calls to Supabase
- ✅ SQLite Cloud API for data retrieval
- ✅ LLM-powered content generation
- ✅ Clean, maintainable codebase
- ✅ Faster execution (no browser overhead)
- ✅ Better error handling and reliability
