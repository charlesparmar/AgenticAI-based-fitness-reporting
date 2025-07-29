# AgenticAI-based Fitness Reporting System

A comprehensive automated fitness data processing and reporting system using LangGraph orchestration with multiple AI agents.

## Overview

This system automatically:
1. Fetches fitness data from Gmail emails
2. Validates data against historical trends
3. Enters data into Supabase application
4. Generates progress reports with iterative improvement
5. Sends final reports via email

## Project Structure

```
AgenticAI-based-fitness-reporting/
├── orchestrated_workflow_with_feedback.py  # Main workflow orchestration
├── requirements.txt                        # Python dependencies
├── .env                                   # Environment variables (create from env.example)
├── env.example                            # Environment variables template
├── token.json                             # Gmail API token
├── Agents/                                # AI Agent modules
│   ├── fetcher_agent1_latestemail.py      # Email fetching agent
│   ├── fetcher_agent2_database.py         # Database fetching agent
│   ├── recon_agent.py                     # Data reconciliation agent
│   ├── data_validation_agent.py           # Data validation agent
│   ├── supabase_agent.py                  # Supabase entry agent
│   ├── report_drafter_agent.py            # Report drafting agent
│   ├── evaluate_email_body_agent.py       # Email evaluation agent
│   ├── final_email_agent.py               # Final email sending agent
│   └── cleanup_agent.py                   # System cleanup agent
└── .venv/                                 # Virtual environment
```

## Setup

1. **Install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

3. **Run the workflow:**
   ```bash
   source .venv/bin/activate
   python orchestrated_workflow_with_feedback.py
   ```

## Workflow Steps

1. **Email Fetching** - Retrieves latest fitness data from Gmail
2. **Database Operations** - Fetches and reconciles with existing data
3. **Data Validation** - Validates against historical trends
4. **Supabase Entry** - Enters validated data into Supabase application
5. **Report Generation** - Creates progress reports with feedback loop
6. **Email Evaluation** - Evaluates report quality (up to 3 iterations)
7. **Final Email Sending** - Sends approved report via Gmail API
8. **Cleanup** - Cleans up system resources

## Features

- **LangGraph Orchestration** - Complex workflow management
- **Iterative Improvement** - Email quality feedback loop
- **Data Validation** - Historical trend analysis
- **Automated Web Interaction** - Selenium-based Supabase entry
- **Gmail API Integration** - Automated email sending
- **LangSmith Tracing** - Workflow monitoring and debugging

## Environment Variables

Required environment variables (see `env.example`):
- `GMAIL_ADDRESS` - Gmail account for fetching/sending
- `GMAIL_APP_PASSWORD` - Gmail app password
- `OPENAI_API_KEY` - OpenAI API key for LLM operations
- `SUPABASE_EMAIL` - Supabase login email
- `SUPABASE_PASSWORD` - Supabase login password
- `SUPABASE_URL` - Supabase application URL
- `PUSHOVER_USER_KEY` - Pushover notification user key
- `PUSHOVER_TOKEN` - Pushover notification app token
- `SQLITE_API_KEY` - SQLite Cloud API key
- `EMAIL_TO` - Recipient email for reports

## Monitoring

The system uses LangSmith for tracing and monitoring:
- Project: Charles-Fitness-report
- Dashboard: https://smith.langchain.com/ 