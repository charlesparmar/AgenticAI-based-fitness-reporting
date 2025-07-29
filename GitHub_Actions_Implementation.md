# GitHub Actions Implementation for Fitness Reporting Workflow

## Overview
This document outlines the implementation of the AgenticAI-based Fitness Reporting System using GitHub Actions for automated daily execution. This approach provides a cost-effective solution with secure secret management.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Actions│    │  Workflow Runner│    │   External APIs │
│   (Cron Trigger)│───▶│   (Ubuntu VM)   │───▶│   (Gmail, etc.) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  SQLite Cloud   │
                       │  (Database)     │
                       └─────────────────┘
```

## Prerequisites

### 1. GitHub Repository Setup
- GitHub account
- Repository with fitness reporting code
- Repository must be public for free GitHub Actions

### 2. Required External Services
- OpenAI API account
- SQLite Cloud account
- Gmail account with OAuth2.0 setup
- Supabase account
- Pushover account
- LangSmith account (optional)

## Implementation Steps

### Step 1: Repository Preparation

#### 1.1 Make Repository Public
```bash
# Navigate to your repository on GitHub
# Go to Settings > General > Danger Zone
# Click "Change repository visibility"
# Select "Make public"
# Confirm the change
```

**⚠️ Security Note**: Making the repository public will expose your code but NOT your secrets. All sensitive data will be stored securely in GitHub Secrets.

#### 1.2 Repository Structure
```
fitness-reporting/
├── .github/
│   └── workflows/
│       └── daily-workflow.yml
├── Agents/
│   ├── __init__.py
│   ├── fetcher_agent1_latestemail.py
│   ├── data_validation_agent.py
│   ├── evaluate_email_body_agent.py
│   ├── final_email_agent.py
│   ├── recon_agent.py
│   ├── report_drafter_agent.py
│   └── supabase_agent.py
├── requirements.txt
├── orchestrated_workflow_with_feedback.py
├── credentials.json
├── token.json
├── README.md
└── setup_instructions.md
```

### Step 2: Secure Secret Management

#### 2.1 GitHub Secrets Setup
Navigate to your repository on GitHub:
1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Add the following secrets:

```bash
# Required Secrets (Add these one by one)
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
OPENAI_API_KEY=sk-your_openai_api_key
SUPABASE_EMAIL=your_supabase_email
SUPABASE_PASSWORD=your_supabase_password
PUSHOVER_USER_KEY=your_pushover_user_key
PUSHOVER_TOKEN=your_pushover_token
SQLITE_API_KEY=your_sqlite_api_key
EMAIL_TO=coach@example.com
SUPABASE_URL=https://your-supabase-project.vercel.app/auth/login
LANGSMITH_API_KEY=ls-your_langsmith_api_key (optional)
LANGSMITH_PROJECT=your_langsmith_project (optional)
```

#### 2.2 Secret Security Best Practices
- **Never commit secrets to code**
- **Use environment-specific secrets**
- **Rotate secrets regularly**
- **Use least privilege principle**
- **Monitor secret usage**

#### 2.3 Encrypted Files Setup
For files that contain sensitive data (credentials.json, token.json):

```bash
# Install git-crypt (for additional security)
# On macOS: brew install git-crypt
# On Ubuntu: sudo apt-get install git-crypt

# Initialize git-crypt
git-crypt init

# Create .gitattributes file
echo "credentials.json filter=git-crypt diff=git-crypt" >> .gitattributes
echo "token.json filter=git-crypt diff=git-crypt" >> .gitattributes

# Commit encrypted files
git add .gitattributes credentials.json token.json
git commit -m "Add encrypted credential files"
```

### Step 3: GitHub Actions Workflow

#### 3.1 Create Workflow File
Create `.github/workflows/daily-workflow.yml`:

```yaml
name: Daily Fitness Reporting Workflow

on:
  schedule:
    # Run daily at 9:00 AM UTC
    - cron: '0 9 * * *'
  workflow_dispatch:
    # Allow manual triggering

jobs:
  fitness-reporting:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        # If using git-crypt, uncomment the following:
        # token: ${{ secrets.GIT_CRYPT_KEY }}
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Create credentials files
      run: |
        # Create credentials.json from secret
        echo '${{ secrets.GMAIL_CREDENTIALS }}' > credentials.json
        
        # Create token.json from secret
        echo '${{ secrets.GMAIL_TOKEN }}' > token.json
        
        # Verify files exist
        ls -la credentials.json token.json
    
    - name: Set environment variables
      run: |
        echo "GMAIL_ADDRESS=${{ secrets.GMAIL_ADDRESS }}" >> $GITHUB_ENV
        echo "GMAIL_APP_PASSWORD=${{ secrets.GMAIL_APP_PASSWORD }}" >> $GITHUB_ENV
        echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> $GITHUB_ENV
        echo "SUPABASE_EMAIL=${{ secrets.SUPABASE_EMAIL }}" >> $GITHUB_ENV
        echo "SUPABASE_PASSWORD=${{ secrets.SUPABASE_PASSWORD }}" >> $GITHUB_ENV
        echo "PUSHOVER_USER_KEY=${{ secrets.PUSHOVER_USER_KEY }}" >> $GITHUB_ENV
        echo "PUSHOVER_TOKEN=${{ secrets.PUSHOVER_TOKEN }}" >> $GITHUB_ENV
        echo "SQLITE_API_KEY=${{ secrets.SQLITE_API_KEY }}" >> $GITHUB_ENV
        echo "EMAIL_TO=${{ secrets.EMAIL_TO }}" >> $GITHUB_ENV
        echo "SUPABASE_URL=${{ secrets.SUPABASE_URL }}" >> $GITHUB_ENV
        echo "LANGSMITH_API_KEY=${{ secrets.LANGSMITH_API_KEY }}" >> $GITHUB_ENV
        echo "LANGSMITH_PROJECT=${{ secrets.LANGSMITH_PROJECT }}" >> $GITHUB_ENV
    
    - name: Run fitness reporting workflow
      run: |
        python orchestrated_workflow_with_feedback.py
    
    - name: Upload workflow logs
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: workflow-logs
        path: |
          *.log
          fitness_data_*.json
          validation_result_*.json
    
    - name: Cleanup sensitive files
      if: always()
      run: |
        rm -f credentials.json token.json
        echo "Sensitive files cleaned up"
```

#### 3.2 Alternative: Manual Trigger Workflow
Create `.github/workflows/manual-workflow.yml` for testing:

```yaml
name: Manual Fitness Reporting Workflow

on:
  workflow_dispatch:
    inputs:
      test_mode:
        description: 'Run in test mode'
        required: false
        default: 'false'
        type: boolean

jobs:
  fitness-reporting:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Create credentials files
      run: |
        echo '${{ secrets.GMAIL_CREDENTIALS }}' > credentials.json
        echo '${{ secrets.GMAIL_TOKEN }}' > token.json
    
    - name: Set environment variables
      run: |
        echo "GMAIL_ADDRESS=${{ secrets.GMAIL_ADDRESS }}" >> $GITHUB_ENV
        echo "GMAIL_APP_PASSWORD=${{ secrets.GMAIL_APP_PASSWORD }}" >> $GITHUB_ENV
        echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> $GITHUB_ENV
        echo "SUPABASE_EMAIL=${{ secrets.SUPABASE_EMAIL }}" >> $GITHUB_ENV
        echo "SUPABASE_PASSWORD=${{ secrets.SUPABASE_PASSWORD }}" >> $GITHUB_ENV
        echo "PUSHOVER_USER_KEY=${{ secrets.PUSHOVER_USER_KEY }}" >> $GITHUB_ENV
        echo "PUSHOVER_TOKEN=${{ secrets.PUSHOVER_TOKEN }}" >> $GITHUB_ENV
        echo "SQLITE_API_KEY=${{ secrets.SQLITE_API_KEY }}" >> $GITHUB_ENV
        echo "EMAIL_TO=${{ secrets.EMAIL_TO }}" >> $GITHUB_ENV
        echo "SUPABASE_URL=${{ secrets.SUPABASE_URL }}" >> $GITHUB_ENV
        echo "LANGSMITH_API_KEY=${{ secrets.LANGSMITH_API_KEY }}" >> $GITHUB_ENV
        echo "LANGSMITH_PROJECT=${{ secrets.LANGSMITH_PROJECT }}" >> $GITHUB_ENV
    
    - name: Run fitness reporting workflow
      run: |
        if [ "${{ github.event.inputs.test_mode }}" = "true" ]; then
          echo "Running in test mode"
          python -c "print('Test mode - workflow would run here')"
        else
          python orchestrated_workflow_with_feedback.py
        fi
    
    - name: Cleanup sensitive files
      if: always()
      run: |
        rm -f credentials.json token.json
```

### Step 4: Monitoring and Notifications

#### 4.1 Workflow Notifications
Add to your workflow:

```yaml
    - name: Notify on success
      if: success()
      run: |
        echo "✅ Workflow completed successfully"
        # Add custom success notification logic here
    
    - name: Notify on failure
      if: failure()
      run: |
        echo "❌ Workflow failed"
        # Add custom failure notification logic here
```

#### 4.2 GitHub Actions Monitoring
- **Workflow History**: View in Actions tab
- **Logs**: Available for each run
- **Artifacts**: Download workflow outputs
- **Notifications**: Email notifications for failures

## Generic Setup Instructions for New Users

### Prerequisites for New Users

#### 1. Basic Requirements
- Python 3.11+
- Git
- GitHub account
- Text editor (VS Code recommended)

#### 2. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-username/fitness-reporting.git
cd fitness-reporting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### External Service Setup

#### 1. OpenAI API Setup
1. **Create OpenAI Account**
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Sign up for an account
   - Add payment method

2. **Generate API Key**
   - Go to API Keys section
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

3. **Set Environment Variable**
   ```bash
   export OPENAI_API_KEY="sk-your_api_key_here"
   ```

#### 2. SQLite Cloud Setup
1. **Create SQLite Cloud Account**
   - Visit [SQLite Cloud](https://sqlitecloud.io/)
   - Sign up for free account
   - Create a new database

2. **Get Connection Details**
   - Note your database URL
   - Generate API key
   - Save connection string format

3. **Set Environment Variable**
   ```bash
   export SQLITE_API_KEY="your_sqlite_api_key"
   ```

#### 3. Gmail OAuth2.0 Setup
1. **Create Google Cloud Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project
   - Enable Gmail API

2. **Create OAuth2.0 Credentials**
   - Go to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Download credentials.json

3. **Generate Access Token**
   ```bash
   # Run the Gmail setup script
   python setup_gmail_oauth.py
   ```

#### 4. Supabase Setup
1. **Create Supabase Account**
   - Visit [Supabase](https://supabase.com/)
   - Sign up and create project
   - Note project URL and API keys

2. **Create Database Tables**
   ```sql
   -- Create fitness_measurements table
   CREATE TABLE fitness_measurements (
       id SERIAL PRIMARY KEY,
       date DATE NOT NULL,
       weight DECIMAL(5,2),
       fat_percent DECIMAL(4,2),
       bmi DECIMAL(4,2),
       fat_weight DECIMAL(5,2),
       lean_weight DECIMAL(5,2),
       neck DECIMAL(4,1),
       shoulders DECIMAL(4,1),
       biceps DECIMAL(4,1),
       forearms DECIMAL(4,1),
       chest DECIMAL(4,1),
       above_navel DECIMAL(4,1),
       navel DECIMAL(4,1),
       waist DECIMAL(4,1),
       hips DECIMAL(4,1),
       thighs DECIMAL(4,1),
       calves DECIMAL(4,1),
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```

3. **Set Environment Variables**
   ```bash
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_ANON_KEY="your_anon_key"
   export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"
   ```

#### 5. Pushover Setup
1. **Create Pushover Account**
   - Visit [Pushover](https://pushover.net/)
   - Sign up for account
   - Install mobile app

2. **Get API Credentials**
   - Note your User Key
   - Create new application
   - Copy API Token

3. **Set Environment Variables**
   ```bash
   export PUSHOVER_USER_KEY="your_user_key"
   export PUSHOVER_TOKEN="your_api_token"
   ```

#### 6. LangSmith Setup (Optional)
1. **Create LangSmith Account**
   - Visit [LangSmith](https://smith.langchain.com/)
   - Sign up for account
   - Create new project

2. **Get API Key**
   - Go to API Keys section
   - Create new API key
   - Copy the key (starts with `ls_`)

3. **Set Environment Variables**
   ```bash
   export LANGSMITH_API_KEY="ls_your_api_key"
   export LANGSMITH_PROJECT="your_project_name"
   ```

### Configuration Files

#### 1. Environment File (.env)
Create `.env` file in project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key

# Gmail Configuration
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# SQLite Cloud Configuration
SQLITE_API_KEY=your_sqlite_api_key

# Supabase Configuration
SUPABASE_EMAIL=your_supabase_email
SUPABASE_PASSWORD=your_supabase_password
SUPABASE_URL=https://your-project.vercel.app/auth/login

# Pushover Configuration
PUSHOVER_USER_KEY=your_pushover_user_key
PUSHOVER_TOKEN=your_pushover_token

# Email Configuration
EMAIL_TO=coach@example.com

# LangSmith Configuration (Optional)
LANGSMITH_API_KEY=ls_your_langsmith_api_key
LANGSMITH_PROJECT=your_langsmith_project
```

#### 2. Gmail Credentials
Place `credentials.json` and `token.json` in project root:
- `credentials.json` - OAuth2.0 client credentials
- `token.json` - Generated access token

### Testing the Setup

#### 1. Test Individual Components
```bash
# Test OpenAI API
python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('OpenAI API working')"

# Test SQLite Cloud connection
python -c "import sqlitecloud; print('SQLite Cloud module available')"

# Test Gmail credentials
python -c "import json; json.load(open('credentials.json')); print('Gmail credentials valid')"
```

#### 2. Test Complete Workflow
```bash
# Run the workflow manually
python orchestrated_workflow_with_feedback.py
```

## Security Best Practices

### 1. Repository Security
- **Never commit secrets** to version control
- **Use .gitignore** for sensitive files
- **Regular security audits** of dependencies
- **Keep dependencies updated**

### 2. Secret Management
- **Use GitHub Secrets** for all sensitive data
- **Rotate secrets regularly**
- **Use environment-specific secrets**
- **Monitor secret usage**

### 3. Access Control
- **Limit repository access**
- **Use branch protection rules**
- **Require code reviews**
- **Monitor workflow access**

## Troubleshooting

### Common Issues

#### 1. Workflow Failures
```bash
# Check workflow logs
# Go to Actions tab > Select workflow run > View logs

# Common causes:
# - Missing secrets
# - Invalid API keys
# - Network connectivity issues
# - Python dependency conflicts
```

#### 2. Secret Issues
```bash
# Verify secrets are set correctly
# Go to Settings > Secrets and variables > Actions
# Check that all required secrets are present

# Test secret access in workflow
echo "Testing secret access..."
```

#### 3. Environment Issues
```bash
# Check Python version
python --version

# Verify dependencies
pip list

# Test imports
python -c "import langchain, openai, sqlitecloud; print('All imports successful')"
```

## Cost Analysis

### GitHub Actions Pricing
- **Public repositories**: Free (unlimited minutes)
- **Private repositories**: $4/month (3,000 minutes)
- **Additional minutes**: $0.008 per minute

### Estimated Usage
- **Daily execution**: ~5-10 minutes per run
- **Monthly minutes**: ~150-300 minutes
- **Cost for private repo**: $4/month (well within free tier)

## Next Steps

1. **Set up GitHub repository** and make it public
2. **Configure all external services** (OpenAI, SQLite Cloud, etc.)
3. **Add secrets to GitHub** repository
4. **Create workflow files** in `.github/workflows/`
5. **Test the workflow** manually
6. **Monitor daily execution** and logs
7. **Set up notifications** for failures
8. **Optimize workflow** based on performance

## Support Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [SQLite Cloud Documentation](https://sqlitecloud.io/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Pushover API Documentation](https://pushover.net/api) 