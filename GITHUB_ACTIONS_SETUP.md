# GitHub Actions Setup Guide for Fitness Reporting System

## Overview

This guide will help you set up automated fitness reporting using GitHub Actions. The system will run on a schedule you configure and send fitness reports to configurable email recipients.

## Prerequisites

1. **GitHub Account**: You need a GitHub account
2. **Repository**: Your fitness reporting code must be in a GitHub repository
3. **Repository Visibility**: For free GitHub Actions, the repository must be public
4. **External Services**: All the services your workflow uses (Gmail, OpenAI, etc.)

## Step 1: Repository Setup

### 1.1 Make Repository Public (if using free plan)
```bash
# Navigate to your repository on GitHub
# Go to Settings > General > Danger Zone
# Click "Change repository visibility"
# Select "Make public"
# Confirm the change
```

**⚠️ Security Note**: Making the repository public will expose your code but NOT your secrets. All sensitive data will be stored securely in GitHub Secrets.

### 1.2 Repository Structure
Ensure your repository has the following structure:
```
fitness-reporting/
├── .github/
│   └── workflows/
│       └── fitness-reporting.yml
├── Agents/
├── config/
│   ├── email_config.py
│   └── email_recipients.json
├── requirements.txt
├── reporting_workflow.py
├── manage_email_recipients.py
└── README.md
```

## Step 2: GitHub Secrets Setup

Navigate to your repository on GitHub:
1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Add the following secrets:

### Required Secrets

```bash
# Gmail Configuration
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
GMAIL_CREDENTIALS={"web":{"client_id":"...","project_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_secret":"...","redirect_uris":["..."]}}
GMAIL_TOKEN={"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"...","scopes":["..."]}

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key

# Supabase Configuration
SUPABASE_EMAIL=your_supabase_email
SUPABASE_PASSWORD=your_supabase_password
SUPABASE_URL=https://your-supabase-project.vercel.app/auth/login

# Pushover Configuration (for notifications)
PUSHOVER_USER_KEY=your_pushover_user_key
PUSHOVER_TOKEN=your_pushover_app_token

# SQLite Cloud Configuration
SQLITE_API_KEY=your_sqlite_api_key

# Email Configuration
EMAIL_TO=coach@example.com
EMAIL_CC=assistant@example.com,nutritionist@example.com
EMAIL_SUBJECT_PREFIX=Charles Parmar : Progress Report
EMAIL_SEND_NOTIFICATIONS=true

# LangSmith Configuration (optional)
LANGSMITH_API_KEY=ls-your_langsmith_api_key
LANGSMITH_PROJECT=your_langsmith_project
```

### How to Get Gmail Credentials

1. **Create Gmail API Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Go to Credentials > Create Credentials > OAuth 2.0 Client IDs
   - Download the JSON file

2. **Generate Gmail Token**:
   - Run the `refresh_gmail_token.py` script locally
   - This will create `credentials.json` and `token.json` files
   - Copy the contents of these files to the GitHub secrets

## Step 3: Configure Workflow Frequency

The workflow is configured to run daily at 5:00 PM London time (UTC+0/UTC+1) by default. You can modify the schedule in `.github/workflows/fitness-reporting.yml`:

**⚠️ Important Note**: GitHub Actions uses UTC time for cron schedules. London time is UTC+0 during winter (GMT) and UTC+1 during summer (BST). The schedule below uses UTC time that corresponds to 5:00 PM London time.

### Common Schedule Examples

```yaml
# Daily at 5:00 PM London time (17:00 UTC)
- cron: '0 17 * * *'

# Weekdays only at 5:00 PM London time
- cron: '0 17 * * 1-5'

# Twice daily at 9:00 AM and 5:00 PM London time
- cron: '0 9,17 * * *'

# Every 6 hours
- cron: '0 */6 * * *'

# Every Monday at 5:00 PM London time
- cron: '0 17 * * 1'

# 1st and 15th of each month at 5:00 PM London time
- cron: '0 17 1,15 * *'

# Every 2 hours during business hours (9 AM - 6 PM London time, weekdays)
- cron: '0 9-18/2 * * 1-5'
```

### Cron Syntax Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

### Timezone Conversion Table

Since GitHub Actions uses UTC time, here's how the schedule translates to different timezones:

| UTC Time | London (GMT/BST) | New York (EST/EDT) | Los Angeles (PST/PDT) | Tokyo (JST) |
|----------|------------------|-------------------|----------------------|-------------|
| 17:00    | 17:00 (5:00 PM)  | 12:00 (12:00 PM)  | 09:00 (9:00 AM)      | 02:00 (2:00 AM) |
| 09:00    | 09:00 (9:00 AM)  | 04:00 (4:00 AM)   | 01:00 (1:00 AM)      | 18:00 (6:00 PM) |

**Note**: London time varies between GMT (UTC+0) and BST (UTC+1) due to daylight saving time.

## Step 4: Email Recipients Configuration

### 4.1 Using the Management Script

The system includes a utility script to manage email recipients:

```bash
# List all recipients
python manage_email_recipients.py list

# Add a new recipient
python manage_email_recipients.py add coach@example.com --name "Primary Coach" --role coach

# Add CC recipient
python manage_email_recipients.py add assistant@example.com --name "Assistant" --role cc

# Remove a recipient
python manage_email_recipients.py remove assistant@example.com

# Update recipient
python manage_email_recipients.py update coach@example.com --active false

# Set primary recipient
python manage_email_recipients.py set-primary coach@example.com

# Show configuration
python manage_email_recipients.py config
```

### 4.2 Manual Configuration

You can also manually edit `config/email_recipients.json`:

```json
{
  "recipients": [
    {
      "email": "coach@example.com",
      "name": "Primary Coach",
      "role": "coach",
      "active": true
    },
    {
      "email": "assistant@example.com",
      "name": "Assistant Coach",
      "role": "cc",
      "active": true
    }
  ],
  "config": {
    "primary_recipient": "coach@example.com",
    "cc_recipients": ["assistant@example.com"],
    "bcc_recipients": [],
    "subject_prefix": "[Fitness Report]",
    "reply_to": null,
    "send_notifications": true
  }
}
```

## Step 5: Manual Workflow Execution

You can manually trigger the workflow with custom parameters:

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Fitness Reporting Workflow**
4. Click **Run workflow**
5. Configure the inputs:
   - **Test Mode**: Skip actual email sending
   - **Custom Email To**: Override primary recipient
   - **Custom Email CC**: Override CC recipients
   - **Skip Notifications**: Skip push notifications

## Step 6: Monitoring and Troubleshooting

### 6.1 View Workflow Runs

1. Go to **Actions** tab in your repository
2. Click on **Fitness Reporting Workflow**
3. View recent runs and their status

### 6.2 Download Logs

1. Click on a specific workflow run
2. Scroll down to **Artifacts**
3. Download `workflow-logs-[run-id]` to get detailed logs

### 6.3 Common Issues

**Workflow Fails to Start**:
- Check if repository is public (for free plan)
- Verify all required secrets are set
- Check cron syntax in workflow file

**Email Sending Fails**:
- Verify Gmail credentials and token
- Check if Gmail API is enabled
- Ensure email addresses are valid

**Authentication Errors**:
- Regenerate Gmail token using `refresh_gmail_token.py`
- Update `GMAIL_TOKEN` secret with new token

**Missing Dependencies**:
- Check `requirements.txt` is up to date
- Verify all Python packages are listed

## Step 7: Advanced Configuration

### 7.1 Environment-Specific Configuration

You can create different workflows for different environments:

```yaml
# .github/workflows/fitness-reporting-dev.yml
name: Fitness Reporting (Development)

on:
  workflow_dispatch:
    inputs:
      test_mode:
        description: 'Run in test mode'
        required: false
        default: true
        type: boolean

env:
  ENVIRONMENT: development
  EMAIL_SEND_NOTIFICATIONS: false
```

### 7.2 Conditional Execution

Add conditions to your workflow:

```yaml
- name: Run fitness reporting workflow
  if: github.event_name == 'schedule' || github.event.inputs.test_mode == 'false'
  run: |
    python3 reporting_workflow.py
```

### 7.3 Notifications

Add notifications for workflow status:

```yaml
- name: Notify on failure
  if: failure()
  run: |
    # Send notification about workflow failure
    echo "Workflow failed!"
```

## Security Best Practices

1. **Never commit secrets to code**
2. **Use environment-specific secrets**
3. **Regularly rotate API keys**
4. **Monitor workflow logs for sensitive data**
5. **Use least privilege principle for API keys**

## Cost Considerations

- **GitHub Actions**: Free tier includes 2,000 minutes/month for public repositories
- **OpenAI API**: Pay per token usage
- **Gmail API**: Free with quotas
- **Other services**: Check individual pricing

## Support

If you encounter issues:

1. Check the workflow logs in GitHub Actions
2. Verify all secrets are correctly set
3. Test the workflow manually first
4. Check the troubleshooting section above

For additional help, refer to:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Syntax Reference](https://crontab.guru/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
