# Google Cloud Deployment Plan for Fitness Reporting Workflow

## Overview
This document outlines the complete deployment strategy for the AgenticAI-based Fitness Reporting System on Google Cloud Platform (GCP) with automated scheduling.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud Scheduler│    │  Cloud Functions│    │   Cloud Storage │
│   (Trigger)      │───▶│   (Workflow)    │───▶│   (Logs/Data)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Cloud SQL      │
                       │  (PostgreSQL)   │
                       └─────────────────┘
```

## Prerequisites

### 1. Google Cloud Project Setup
```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Initialize and authenticate
gcloud init
gcloud auth application-default login

# Set project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Required GCP Services
- **Cloud Functions** (v2) - For workflow execution
- **Cloud Scheduler** - For automated triggering
- **Cloud Storage** - For logs and temporary files
- **Secret Manager** - For secure credential storage
- **Cloud SQL** (Optional) - For database hosting
- **Cloud Logging** - For monitoring and debugging

## Deployment Steps

### Step 1: Environment Setup

#### 1.1 Create Cloud Storage Bucket
```bash
# Create bucket for logs and temporary files
gsutil mb gs://fitness-reporting-logs-YOUR_PROJECT_ID
gsutil mb gs://fitness-reporting-temp-YOUR_PROJECT_ID

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://fitness-reporting-logs-YOUR_PROJECT_ID
```

#### 1.2 Store Secrets in Secret Manager
```bash
# Store environment variables securely
echo -n "your_gmail_address@gmail.com" | gcloud secrets create gmail-address --data-file=-
echo -n "your_gmail_app_password" | gcloud secrets create gmail-app-password --data-file=-
echo -n "your_openai_api_key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your_supabase_email" | gcloud secrets create supabase-email --data-file=-
echo -n "your_supabase_password" | gcloud secrets create supabase-password --data-file=-
echo -n "your_pushover_user_key" | gcloud secrets create pushover-user-key --data-file=-
echo -n "your_pushover_token" | gcloud secrets create pushover-token --data-file=-
echo -n "your_sqlite_api_key" | gcloud secrets create sqlite-api-key --data-file=-
```

### Step 2: Prepare Application for Cloud Functions

#### 2.1 Create requirements.txt for Cloud Functions
```txt
# Cloud Functions requirements
functions-framework==3.*
google-cloud-storage==2.*
google-cloud-secret-manager==2.*
langgraph==0.5.4
langchain==0.3.27
langchain-openai==0.3.28
python-dotenv==1.1.1
requests==2.32.4
schedule==1.2.2
google-auth==2.40.3
google-auth-oauthlib==1.2.2
google-auth-httplib2==0.2.0
google-api-python-client==2.177.0
pandas==2.3.1
openpyxl==3.1.5
openai==1.97.1
selenium==4.34.2
sqlitecloud==0.0.84
mcp==1.12.2
websockets==15.0.1
aiohttp==3.12.15
asyncio-mqtt==0.16.2
```

#### 2.2 Create main.py for Cloud Functions
```python
import functions_framework
import os
import sys
import tempfile
from google.cloud import secretmanager
from google.cloud import storage

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_secret(secret_name):
    """Retrieve secret from Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.environ.get('GOOGLE_CLOUD_PROJECT')}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def set_environment_variables():
    """Set environment variables from Secret Manager"""
    secrets = {
        'GMAIL_ADDRESS': 'gmail-address',
        'GMAIL_APP_PASSWORD': 'gmail-app-password',
        'OPENAI_API_KEY': 'openai-api-key',
        'SUPABASE_EMAIL': 'supabase-email',
        'SUPABASE_PASSWORD': 'supabase-password',
        'PUSHOVER_USER_KEY': 'pushover-user-key',
        'PUSHOVER_TOKEN': 'pushover-token',
        'SQLITE_API_KEY': 'sqlite-api-key',
        'EMAIL_TO': 'coach@example.com',
        'SUPABASE_URL': 'https://charles-fitness-reporting.vercel.app/auth/login'
    }
    
    for env_var, secret_name in secrets.items():
        if not os.environ.get(env_var):
            try:
                os.environ[env_var] = get_secret(secret_name)
            except Exception as e:
                print(f"Warning: Could not load secret {secret_name}: {e}")

@functions_framework.http
def fitness_workflow_trigger(request):
    """Cloud Function entry point for fitness reporting workflow"""
    try:
        # Set environment variables
        set_environment_variables()
        
        # Import and run the workflow
        from orchestrated_workflow_with_feedback import run_orchestrated_workflow_with_feedback
        
        # Run the workflow
        run_orchestrated_workflow_with_feedback()
        
        return {
            'status': 'success',
            'message': 'Fitness reporting workflow completed successfully'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Workflow failed: {str(e)}'
        }, 500

@functions_framework.cloud_event
def fitness_workflow_scheduled(cloud_event):
    """Cloud Function entry point for scheduled execution"""
    try:
        # Set environment variables
        set_environment_variables()
        
        # Import and run the workflow
        from orchestrated_workflow_with_feedback import run_orchestrated_workflow_with_feedback
        
        # Run the workflow
        run_orchestrated_workflow_with_feedback()
        
        print("Scheduled fitness workflow completed successfully")
        
    except Exception as e:
        print(f"Scheduled fitness workflow failed: {str(e)}")
        raise
```

### Step 3: Deploy Cloud Function

#### 3.1 Create deployment directory structure
```bash
mkdir -p cloud-deployment
cd cloud-deployment

# Copy application files
cp -r ../Agents .
cp ../orchestrated_workflow_with_feedback.py .
cp ../requirements.txt .
cp ../main.py .
cp ../credentials.json .
cp ../token.json .

# Create .gcloudignore
cat > .gcloudignore << EOF
.gcloudignore
.git
.gitignore
__pycache__/
*.pyc
.env
.venv/
venv/
*.md
test_*
EOF
```

#### 3.2 Deploy Cloud Function
```bash
# Deploy the function
gcloud functions deploy fitness-reporting-workflow \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=fitness_workflow_scheduled \
    --trigger-topic=fitness-workflow-trigger \
    --memory=2GB \
    --timeout=540s \
    --max-instances=1 \
    --set-env-vars=GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID

# Deploy HTTP trigger version (for manual testing)
gcloud functions deploy fitness-reporting-workflow-http \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=fitness_workflow_trigger \
    --trigger-http \
    --memory=2GB \
    --timeout=540s \
    --max-instances=1 \
    --set-env-vars=GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
    --allow-unauthenticated
```

### Step 4: Set Up Cloud Scheduler

#### 4.1 Create Pub/Sub Topic
```bash
# Create topic for workflow triggering
gcloud pubsub topics create fitness-workflow-trigger
```

#### 4.2 Create Scheduled Jobs

##### Daily at 9:00 AM
```bash
gcloud scheduler jobs create pubsub daily-fitness-workflow \
    --schedule="0 9 * * *" \
    --topic=fitness-workflow-trigger \
    --message-body='{"trigger": "daily", "time": "09:00"}' \
    --location=us-central1 \
    --description="Daily fitness reporting workflow at 9:00 AM"
```

##### Every 6 hours
```bash
gcloud scheduler jobs create pubsub hourly-fitness-workflow \
    --schedule="0 */6 * * *" \
    --topic=fitness-workflow-trigger \
    --message-body='{"trigger": "hourly", "interval": "6"}' \
    --location=us-central1 \
    --description="Fitness reporting workflow every 6 hours"
```

##### Weekly on Monday at 8:00 AM
```bash
gcloud scheduler jobs create pubsub weekly-fitness-workflow \
    --schedule="0 8 * * 1" \
    --topic=fitness-workflow-trigger \
    --message-body='{"trigger": "weekly", "day": "monday", "time": "08:00"}' \
    --location=us-central1 \
    --description="Weekly fitness reporting workflow on Monday at 8:00 AM"
```

### Step 5: Monitoring and Logging

#### 5.1 Set up Cloud Monitoring
```bash
# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=dashboard-config.json
```

#### 5.2 Create dashboard-config.json
```json
{
  "displayName": "Fitness Reporting Workflow Dashboard",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Function Execution Count",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\"",
                  "aggregation": {
                    "perSeriesAligner": "ALIGN_RATE",
                    "crossSeriesReducer": "REDUCE_SUM"
                  }
                }
              }
            }
          ]
        }
      },
      {
        "title": "Function Execution Time",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_time\"",
                  "aggregation": {
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }
          ]
        }
      }
    ]
  }
}
```

#### 5.3 Set up Alerting
```bash
# Create alerting policy
gcloud alpha monitoring policies create --policy-from-file=alert-policy.json
```

#### 5.4 Create alert-policy.json
```json
{
  "displayName": "Fitness Workflow Error Alert",
  "conditions": [
    {
      "displayName": "Function execution errors",
      "conditionThreshold": {
        "filter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" AND resource.labels.function_name=\"fitness-reporting-workflow\"",
        "comparison": "COMPARISON_GREATER_THAN",
        "thresholdValue": 0,
        "duration": "300s"
      }
    }
  ],
  "notificationChannels": ["projects/YOUR_PROJECT_ID/notificationChannels/YOUR_CHANNEL_ID"]
}
```

### Step 6: Testing and Validation

#### 6.1 Test Manual Execution
```bash
# Test the HTTP trigger
curl -X POST https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/fitness-reporting-workflow-http

# Test the scheduled trigger
gcloud pubsub topics publish fitness-workflow-trigger --message='{"test": "manual"}'
```

#### 6.2 Monitor Execution
```bash
# View function logs
gcloud functions logs read fitness-reporting-workflow --limit=50

# View scheduler job status
gcloud scheduler jobs list

# Test scheduler job
gcloud scheduler jobs run daily-fitness-workflow
```

## Configuration Options

### Scheduling Frequencies

#### Daily Execution
```bash
# Every day at 9:00 AM
--schedule="0 9 * * *"

# Every day at 6:00 PM
--schedule="0 18 * * *"
```

#### Weekly Execution
```bash
# Every Monday at 8:00 AM
--schedule="0 8 * * 1"

# Every Friday at 5:00 PM
--schedule="0 17 * * 5"
```

#### Custom Intervals
```bash
# Every 4 hours
--schedule="0 */4 * * *"

# Every 12 hours
--schedule="0 */12 * * *"

# Twice daily (9 AM and 6 PM)
--schedule="0 9,18 * * *"
```

### Resource Configuration

#### Memory Options
- **512MB** - Light workloads
- **1GB** - Standard workloads
- **2GB** - Heavy workloads (recommended for this application)
- **4GB** - Very heavy workloads

#### Timeout Options
- **300s** (5 minutes) - Quick workflows
- **540s** (9 minutes) - Standard workflows (recommended)
- **900s** (15 minutes) - Long-running workflows

## Cost Optimization

### 1. Function Configuration
```bash
# Optimize for cost
gcloud functions deploy fitness-reporting-workflow \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=fitness_workflow_scheduled \
    --trigger-topic=fitness-workflow-trigger \
    --memory=1GB \
    --timeout=300s \
    --max-instances=1 \
    --min-instances=0
```

### 2. Scheduling Optimization
- Use appropriate intervals to avoid unnecessary executions
- Monitor execution logs to optimize frequency
- Consider timezone differences for optimal scheduling

## Security Considerations

### 1. IAM Permissions
```bash
# Create service account for the function
gcloud iam service-accounts create fitness-workflow-sa \
    --display-name="Fitness Workflow Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:fitness-workflow-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:fitness-workflow-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

### 2. Network Security
```bash
# Restrict function to VPC (if needed)
gcloud functions deploy fitness-reporting-workflow \
    --vpc-connector=projects/YOUR_PROJECT_ID/locations/us-central1/connectors/fitness-vpc-connector \
    --vpc-connector-egress-settings=PRIVATE_RANGES_ONLY
```

## Maintenance and Updates

### 1. Update Function
```bash
# Deploy updated function
gcloud functions deploy fitness-reporting-workflow \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=fitness_workflow_scheduled \
    --trigger-topic=fitness-workflow-trigger
```

### 2. Update Secrets
```bash
# Update secret values
echo -n "new_secret_value" | gcloud secrets versions add secret-name --data-file=-
```

### 3. Monitor and Scale
```bash
# View function metrics
gcloud functions describe fitness-reporting-workflow --region=us-central1

# Adjust resources based on usage
gcloud functions deploy fitness-reporting-workflow --memory=4GB --timeout=900s
```

## Troubleshooting

### Common Issues

#### 1. Function Timeout
- Increase timeout value
- Optimize workflow performance
- Check for infinite loops

#### 2. Memory Issues
- Increase memory allocation
- Optimize data processing
- Use streaming for large datasets

#### 3. Authentication Errors
- Verify service account permissions
- Check secret manager access
- Validate API keys

#### 4. Scheduling Issues
- Verify cron syntax
- Check timezone settings
- Monitor scheduler logs

### Debug Commands
```bash
# View function logs
gcloud functions logs read fitness-reporting-workflow --limit=100

# Check scheduler status
gcloud scheduler jobs describe daily-fitness-workflow

# Test function manually
gcloud functions call fitness-reporting-workflow-http --data='{"test": "debug"}'

# View project quotas
gcloud compute regions describe us-central1
```

## Estimated Costs

### Monthly Cost Breakdown (US Central)
- **Cloud Functions**: ~$5-15/month (depending on execution frequency)
- **Cloud Scheduler**: ~$0.10/month
- **Secret Manager**: ~$0.06/month
- **Cloud Storage**: ~$0.02/month
- **Cloud Logging**: ~$0.50/month

**Total Estimated Cost**: $5-16/month

## Next Steps

1. **Deploy the function** using the provided commands
2. **Test the deployment** with manual triggers
3. **Set up monitoring** and alerting
4. **Configure scheduling** based on your requirements
5. **Monitor performance** and optimize as needed
6. **Set up backup and disaster recovery** procedures

## Support and Resources

- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator) 