#!/usr/bin/env python3
"""
Orchestrated workflow with feedback loop for fitness reporting system.
Includes Report Drafter and Email Evaluation agents with iterative improvement.
"""

import os
import sys
from typing import Dict, Any, TypedDict
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Charles-Fitness-report"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from Agents.fetcher_agent1_latestemail import run_latest_email_fetcher
from Agents.fetcher_agent2_database import run_database_fetcher
from Agents.recon_agent import run_reconciliation_agent
from Agents.data_validation_agent import DataValidationAgent
from Agents.supabase_api_agent import run_supabase_api_agent
from Agents.report_drafter_agent import run_report_drafter_agent
from Agents.evaluate_email_body_agent import run_evaluate_email_body_agent
from Agents.cleanup_agent import run_cleanup_agent
from Agents.model_config_validation_agent import run_model_config_validation_agent

# Gmail API scopes required for the fitness reporting system
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

def check_and_refresh_gmail_token():
    """Check if Gmail token is valid, refresh if needed"""
    try:
        print("🔍 Checking Gmail token status...")
        
        # Check if token.json exists
        token_path = "token.json"
        if not os.path.exists(token_path):
            print("❌ token.json not found!")
            print("Please run refresh_gmail_token.py first to create your token.")
            return False
        
        # Load existing token
        creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPES)
        
        # Check if token is expired or will expire soon (within 5 minutes)
        if creds.expired:
            print("🔄 Gmail token is expired, refreshing...")
            return refresh_gmail_token(creds)
        elif creds.expiry and (creds.expiry - datetime.now()).total_seconds() < 300:
            print("🔄 Gmail token expires soon (within 5 minutes), refreshing...")
            return refresh_gmail_token(creds)
        else:
            time_until_expiry = (creds.expiry - datetime.now()).total_seconds() if creds.expiry else None
            if time_until_expiry:
                minutes_left = int(time_until_expiry / 60)
                print(f"✅ Gmail token is valid (expires in {minutes_left} minutes)")
            else:
                print("✅ Gmail token is valid")
            return True
            
    except Exception as e:
        print(f"❌ Token check failed: {e}")
        return False

def refresh_gmail_token(creds=None):
    """Refresh Gmail token with correct scopes"""
    try:
        # Check if credentials.json exists
        credentials_path = "credentials.json"
        if not os.path.exists(credentials_path):
            print(f"❌ Error: {credentials_path} not found!")
            print("Please download your Gmail API credentials from Google Cloud Console.")
            return False
        
        # If no creds provided, try to load from file
        if not creds:
            token_path = "token.json"
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPES)
        
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
                for scope in GMAIL_SCOPES:
                    print(f"   • {scope}")
                print()
                
                # Create flow instance
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, GMAIL_SCOPES)
                
                # Run the local server for OAuth2 authentication
                print("🌐 Opening browser for authentication...")
                print("Please complete the authentication in your browser.")
                print("The server will automatically close after authentication.")
                print()
                
                creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        print("💾 Saving new token to token.json...")
        with open("token.json", 'w') as token:
            token.write(creds.to_json())
        
        print("✅ Token successfully refreshed and saved!")
        
        # Verify scopes
        print("🔍 Verifying scopes:")
        for scope in GMAIL_SCOPES:
            if scope in creds.scopes:
                print(f"   ✅ {scope}")
            else:
                print(f"   ❌ {scope} (MISSING)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return False

# State for the orchestrated workflow with feedback
class WorkflowState(TypedDict):
    model_config_validation_result: Dict[str, Any]
    email_data: Dict[str, Any]
    database_data: Dict[str, Any]
    reconciliation_result: Dict[str, Any]
    validation_result: Dict[str, Any]
    supabase_result: Dict[str, Any]
    report_drafter_result: Dict[str, Any]
    email_evaluation_result: Dict[str, Any]
    feedback: str
    iteration_count: int
    max_iterations: int
    final_email_sent: bool
    cleanup_result: Dict[str, Any]
    error: str
    timestamp: str

# Tools for the orchestrated workflow
@tool
def model_config_validation_tool() -> Dict[str, Any]:
    """Validate model configuration before workflow execution"""
    success = run_model_config_validation_agent()
    return {
        "success": success,
        "timestamp": datetime.now().isoformat()
    }

@tool
def fetch_email_tool(email_address: str, app_password: str) -> Dict[str, Any]:
    """Fetch latest fitness email and create JSON"""
    result = run_latest_email_fetcher(email_address, app_password)
    return result

@tool
def fetch_database_tool() -> Dict[str, Any]:
    """Fetch latest database entry and create JSON"""
    result = run_database_fetcher()
    return result

@tool
def reconcile_data_tool(email_json: Dict[str, Any], database_json: Dict[str, Any]) -> Dict[str, Any]:
    """Reconcile email data with database data using LLM"""
    result = run_reconciliation_agent(email_json, database_json)
    return result

@tool
def validate_fitness_data_tool(new_data_file: str) -> Dict[str, Any]:
    """Validate fitness data against historical trends"""
    agent = DataValidationAgent()
    result = agent.validate_fitness_data(new_data_file)
    return result

@tool
def supabase_entry_tool(new_email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enter fitness data into Supabase application via REST API"""
    result = run_supabase_api_agent(new_email_data)
    return result

@tool
def report_drafter_tool(supabase_data: Dict[str, Any], feedback: str = "") -> Dict[str, Any]:
    """Draft fitness report email using LLM and web automation"""
    result = run_report_drafter_agent(supabase_data, feedback)
    return result

@tool
def evaluate_email_body_tool(email_body_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate email body quality and provide feedback"""
    result = run_evaluate_email_body_agent(email_body_data)
    return result

@tool
def cleanup_tool() -> Dict[str, Any]:
    """Clean up browser sessions and system resources"""
    result = run_cleanup_agent()
    return result

def create_reporting_workflow():
    """Create the orchestrated workflow with feedback loop using LangGraph"""
    
    # Create the graph
    workflow = StateGraph(WorkflowState)
    
    # Define node functions
    def model_config_validation_node(state):
        """Model configuration validation node - runs first"""
        print("🔍 Starting model configuration validation...")
        
        result = model_config_validation_tool.invoke({})
        
        if not result.get('success'):
            print("❌ Model configuration validation failed - terminating workflow")
            return {
                **state,
                "model_config_validation_result": result,
                "error": "Model configuration validation failed"
            }
        
        print("✅ Model configuration validation passed")
        return {
            **state,
            "model_config_validation_result": result
        }
    
    def fetch_email_node(state):
        """Fetch email node"""
        email_address = os.getenv("GMAIL_ADDRESS")
        app_password = os.getenv("GMAIL_APP_PASSWORD")
        
        result = fetch_email_tool.invoke({
            "email_address": email_address,
            "app_password": app_password
        })
        
        return {
            **state,
            "email_data": result
        }
    
    def fetch_database_node(state):
        """Fetch database node"""
        result = fetch_database_tool.invoke({})
        
        return {
            **state,
            "database_data": result
        }
    
    def reconcile_data_node(state):
        """Reconcile data node"""
        email_data = state.get("email_data")
        database_data = state.get("database_data")
        
        if email_data and database_data:
            result = reconcile_data_tool.invoke({
                "email_json": email_data,
                "database_json": database_data
            })
            
            return {
                **state,
                "reconciliation_result": result
            }
        else:
            print("❌ Missing email or database data for reconciliation")
            return state
    
    def validate_data_node(state):
        """Validate data node - only runs if reconciliation was successful"""
        reconciliation_result = state.get("reconciliation_result")
        email_data = state.get("email_data")
        
        if reconciliation_result and not reconciliation_result.get('data_exists') and email_data:
            print("🔄 Starting data validation process...")
            
            # Create a temporary file with the email data using tempfile
            import tempfile
            import json
            
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(email_data, temp_file, indent=2)
                    temp_file_path = temp_file.name
                
                result = validate_fitness_data_tool.invoke({
                    "new_data_file": temp_file_path
                })
                
                # Clean up temporary file
                os.unlink(temp_file_path)
                
                return {
                    **state,
                    "validation_result": result
                }
                
            except Exception as e:
                print(f"❌ Error in validation: {e}")
                # Clean up temp file if it exists
                try:
                    if 'temp_file_path' in locals():
                        os.unlink(temp_file_path)
                except:
                    pass
                return state
        else:
            print("❌ Validation skipped - data already exists or reconciliation failed")
            return state
    
    def supabase_entry_node(state):
        """Supabase entry node - only runs if validation was successful"""
        validation_result = state.get("validation_result")
        
        if validation_result and validation_result.get('validation_result', {}).get('validation_status') == 'Validation Success':
            print("🔄 Starting Supabase entry process...")
            
            # Get the email data for Supabase entry
            email_data = state.get("email_data")
            if email_data:
                result = supabase_entry_tool.invoke({
                    "new_email_data": email_data
                })
                
                print(f"✅ Supabase entry completed, result keys: {list(result.keys()) if result else 'None'}")
                
                return {
                    **state,
                    "supabase_result": result
                }
            else:
                print("❌ No email data found for Supabase entry")
        else:
            print("❌ Supabase entry skipped - validation was not successful")
        return state
    
    def report_drafter_node(state):
        """Report Drafter node - only runs if Supabase entry was successful"""
        supabase_result = state.get("supabase_result")
        feedback = state.get("feedback", "")
        
        if supabase_result and supabase_result.get('success'):
            print(f"🔄 Starting Report Drafter process (iteration {state.get('iteration_count', 1)})...")
            
            # Get the email data for report drafting
            email_data = state.get("email_data")
            if email_data:
                result = report_drafter_tool.invoke({
                    "supabase_data": email_data,
                    "feedback": feedback
                })
                
                print(f"✅ Report Drafter completed, result keys: {list(result.keys()) if result else 'None'}")
                
                return {
                    **state,
                    "report_drafter_result": result
                }
            else:
                print("❌ No email data found for Report Drafter")
        else:
            print("❌ Report Drafter skipped - Supabase entry was not successful")
        return state
    
    def email_evaluation_node(state):
        """Email Evaluation node - only runs if Report Drafter was successful"""
        report_drafter_result = state.get("report_drafter_result")
        
        if report_drafter_result and report_drafter_result.get('success'):
            print("🔄 Starting Email Evaluation process...")
            
            # Get the email body data for evaluation
            email_body_data = report_drafter_result.get('email_body_data')
            if email_body_data:
                result = evaluate_email_body_tool.invoke({
                    "email_body_data": email_body_data
                })
                
                print(f"✅ Email Evaluation completed, result keys: {list(result.keys()) if result else 'None'}")
                
                return {
                    **state,
                    "email_evaluation_result": result
                }
            else:
                print("❌ No email body data found for evaluation")
        else:
            print("❌ Email Evaluation skipped - Report Drafter was not successful")
        return state
    
    def feedback_decision_node(state):
        """Feedback decision node - decides whether to continue feedback loop or send final email"""
        email_evaluation_result = state.get("email_evaluation_result")
        iteration_count = state.get("iteration_count", 1)
        max_iterations = state.get("max_iterations", 3)  # Changed from 5 to 3
        
        if not email_evaluation_result:
            print("❌ No email evaluation result found")
            return {
                **state,
                "next_step": "end_workflow"
            }
        
        # Check if email is approved
        if email_evaluation_result.get('approved', False):
            print("✅ Email body approved! Proceeding to send final email")
            return {
                **state,
                "next_step": "send_final_email"
            }
        
        # Check if we've reached maximum iterations
        if iteration_count >= max_iterations:
            print(f"✅ Maximum iterations ({max_iterations}) reached. Forcing approval and proceeding to send email.")
            return {
                **state,
                "next_step": "send_final_email"
            }
        
        # Continue feedback loop
        print(f"🔄 Email needs revision. Starting iteration {iteration_count + 1}...")
        return {
            **state,
            "next_step": "feedback_loop"
        }
    
    def feedback_loop_node(state):
        """Feedback loop node - updates feedback and iteration count"""
        email_evaluation_result = state.get("email_evaluation_result")
        iteration_count = state.get("iteration_count", 1)
        
        feedback = email_evaluation_result.get('feedback', '') if email_evaluation_result else ''
        
        return {
            **state,
            "feedback": feedback,
            "iteration_count": iteration_count + 1,
            "report_drafter_result": {},  # Clear previous result
            "email_evaluation_result": {}  # Clear previous result
        }
    
    def send_final_email_node(state):
        """Final Email Send node - sends the approved email using Final Email Agent"""
        report_drafter_result = state.get("report_drafter_result")
        iteration_count = state.get("iteration_count", 1)
        
        if not report_drafter_result:
            print("❌ No report drafter result found for sending email")
            return {
                **state,
                "final_email_sent": False,
                "error": "No report drafter result found"
            }
        
        # Get email body data from the report drafter result
        email_body_data = report_drafter_result.get('email_body_data', {})
        email_body = email_body_data.get('email_body', '')
        
        if not email_body:
            print("❌ No email body found in report drafter result")
            return {
                **state,
                "final_email_sent": False,
                "error": "No email body found"
            }
        
        print(f"✅ Sending final approved email via Final Email Agent (after {iteration_count} iteration{'s' if iteration_count > 1 else ''})...")
        
        try:
            # Import and use the Final Email Agent
            from Agents.final_email_agent import run_final_email_agent
            
            # Send email using Final Email Agent
            result = run_final_email_agent(email_body_data, iteration_count)
            
            if result.get('success'):
                print("✅ Final email sent successfully via Final Email Agent!")
                return {
                    **state,
                    "final_email_sent": True,
                    "message": f"Email sent successfully via Final Email Agent after {iteration_count} iteration{'s' if iteration_count > 1 else ''}",
                    "final_email_result": result
                }
            else:
                print(f"❌ Failed to send final email via Final Email Agent: {result.get('error')}")
                return {
                    **state,
                    "final_email_sent": False,
                    "error": f"Final Email Agent error: {result.get('error')}",
                    "final_email_result": result
                }
                        
        except Exception as e:
            print(f"❌ Error sending final email via Final Email Agent: {e}")
            return {
                **state,
                "final_email_sent": False,
                "error": f"Error sending final email via Final Email Agent: {e}"
            }
    
    def cleanup_node(state):
        """Cleanup node - runs after email sending to clean up resources"""
        print("🧹 Starting post-email cleanup...")
        
        try:
            result = run_cleanup_agent()
            
            if result.get("success", False):
                print("✅ Cleanup completed successfully")
            else:
                print("⚠️ Cleanup completed with warnings")
            
            return {
                **state,
                "cleanup_result": result
            }
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return {
                **state,
                "cleanup_result": {
                    "success": False,
                    "message": f"Error during cleanup: {e}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
    
    def end_workflow_node(state):
        """End workflow node - handles workflow termination"""
        print("🏁 Workflow ended")
        return state
    
    # Add nodes
    workflow.add_node("model_config_validation", model_config_validation_node)
    workflow.add_node("fetch_email", fetch_email_node)
    workflow.add_node("fetch_database", fetch_database_node)
    workflow.add_node("reconcile_data", reconcile_data_node)
    workflow.add_node("validate_data", validate_data_node)
    workflow.add_node("supabase_entry", supabase_entry_node)
    workflow.add_node("report_drafter", report_drafter_node)
    workflow.add_node("email_evaluation", email_evaluation_node)
    workflow.add_node("feedback_decision", feedback_decision_node)
    workflow.add_node("feedback_loop", feedback_loop_node)
    workflow.add_node("send_final_email", send_final_email_node)
    workflow.add_node("cleanup", cleanup_node)
    workflow.add_node("end_workflow", end_workflow_node)
    
    # Set entry point
    workflow.set_entry_point("model_config_validation")
    
    # Add edges with conditional logic for model config validation
    workflow.add_conditional_edges(
        "model_config_validation",
        lambda x: "end_workflow" if x.get("error") else "fetch_email",
        {
            "fetch_email": "fetch_email",
            "end_workflow": "end_workflow"
        }
    )
    
    workflow.add_edge("fetch_email", "fetch_database")
    workflow.add_edge("fetch_database", "reconcile_data")
    workflow.add_edge("reconcile_data", "validate_data")
    workflow.add_edge("validate_data", "supabase_entry")
    workflow.add_edge("supabase_entry", "report_drafter")
    workflow.add_edge("report_drafter", "email_evaluation")
    workflow.add_edge("email_evaluation", "feedback_decision")
    
    # Conditional edges from feedback_decision
    workflow.add_conditional_edges(
        "feedback_decision",
        lambda x: x["next_step"],
        {
            "feedback_loop": "feedback_loop",
            "send_final_email": "send_final_email",
            "end_workflow": "end_workflow"
        }
    )
    
    workflow.add_edge("feedback_loop", "report_drafter")
    workflow.add_edge("send_final_email", "cleanup")
    workflow.add_edge("cleanup", "end_workflow")
    
    # Set finish point
    workflow.set_finish_point("end_workflow")
    
    # Compile the graph
    app = workflow.compile()
    
    return app

def run_reporting_workflow():
    """Run the complete orchestrated workflow with feedback loop"""
    print("🤖 Running Orchestrated Fitness Data Workflow with Feedback Loop")
    print("=" * 70)
    
    # Step 0: Check and refresh Gmail token if needed
    print("🔍 Step 0: Checking Gmail token status...")
    if not check_and_refresh_gmail_token():
        print("❌ Gmail token check/refresh failed. Please check your credentials.")
        return
    
    # Check credentials
    email_address = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not email_address or not app_password:
        print("❌ Gmail credentials not found")
        return
    
    print(f"🔍 Step 1: Validating model configuration")
    print(f"📧 Step 2: Fetching fitness email from {email_address}")
    print(f"🗄️ Step 3: Fetching latest database entry")
    print(f"🔄 Step 4: Reconciling data with LLM")
    print(f"🔍 Step 5: Validating data against historical trends")
    print(f"📱 Step 6: Entering data into Supabase")
    print(f"📝 Step 7: Drafting email report (with feedback loop)")
    print(f"🔍 Step 8: Evaluating email body quality")
    print(f"📤 Step 9: Sending final email via Final Email Agent (if approved)")
    print(f"🧹 Step 10: Post-cleanup (clean up resources)")
    print("-" * 70)
    
    try:
        # Create and run the LangGraph workflow
        app = create_reporting_workflow()
        
        # Initialize state
        initial_state = {
            "model_config_validation_result": {},
            "email_data": {},
            "database_data": {},
            "reconciliation_result": {},
            "validation_result": {},
            "supabase_result": {},
            "report_drafter_result": {},
            "email_evaluation_result": {},
            "feedback": "",
            "iteration_count": 1,
            "max_iterations": 3,  # Changed from 5 to 3
            "final_email_sent": False,
            "cleanup_result": {},
            "error": "",
            "timestamp": datetime.now().isoformat()
        }
        
        # Run the workflow
        result = app.invoke({
            "model_config_validation_result": {},
            "email_data": {},
            "database_data": {},
            "reconciliation_result": {},
            "validation_result": {},
            "supabase_result": {},
            "report_drafter_result": {},
            "email_evaluation_result": {},
            "feedback": "",
            "iteration_count": 1,
            "max_iterations": 3,  # Changed from 5 to 3
            "final_email_sent": False,
            "cleanup_result": {},
            "error": "",
            "timestamp": datetime.now().isoformat()
        })
        
        # Extract results
        print("📊 Workflow Results:")
        print(f"Result keys: {list(result.keys())}")
        
        # Check if we have the expected data
        if 'email_data' in result:
            email_result = result['email_data']
            if email_result:
                print("✅ Email fetched successfully!")
                
                # Check database data
                if 'database_data' in result:
                    database_result = result['database_data']
                    if database_result:
                        print("✅ Database entry fetched successfully!")
                        
                        # Check reconciliation result
                        if 'reconciliation_result' in result:
                            reconciliation_result = result['reconciliation_result']
                            if reconciliation_result:
                                if reconciliation_result.get('data_exists'):
                                    print("✅ Data already exists - workflow ended")
                                else:
                                    print("✅ Data reconciled and database updated!")
                                    
                                    # Check validation result
                                    if 'validation_result' in result:
                                        validation_result = result['validation_result']
                                        if validation_result:
                                            status = validation_result.get('validation_result', {}).get('validation_status', 'Unknown')
                                            reason = validation_result.get('validation_result', {}).get('reason', 'No reason provided')
                                            confidence = validation_result.get('validation_result', {}).get('confidence', 0.0)
                                            
                                            print(f"✅ Validation completed: {status}")
                                            print(f"📈 Confidence: {confidence:.2f}")
                                            print(f"🔍 Reason: {reason}")
                                            
                                            if validation_result.get('notification_sent'):
                                                print("✅ Pushover notification sent!")
                                            else:
                                                print("❌ Pushover notification failed")
                                            
                                            # Check Supabase result
                                            if 'supabase_result' in result:
                                                supabase_result = result['supabase_result']
                                                if supabase_result and supabase_result.get('success'):
                                                    print("✅ Supabase entry completed successfully!")
                                                    if supabase_result.get('notification_sent'):
                                                        print("✅ Supabase notification sent!")
                                                    if supabase_result.get('db_saved'):
                                                        print("✅ Supabase confirmation saved to database!")
                                                    
                                                    # Check Report Drafter result
                                                    if 'report_drafter_result' in result:
                                                        report_drafter_result = result['report_drafter_result']
                                                        if report_drafter_result and report_drafter_result.get('success'):
                                                            print("✅ Report Drafter completed successfully!")
                                                            
                                                            # Check Email Evaluation result
                                                            if 'email_evaluation_result' in result:
                                                                email_evaluation_result = result['email_evaluation_result']
                                                                if email_evaluation_result and email_evaluation_result.get('success'):
                                                                    if email_evaluation_result.get('approved'):
                                                                        print("✅ Email body approved!")
                                                                        print(f"📊 Evaluation score: {email_evaluation_result.get('score', 'N/A')}")
                                                                        
                                                                        # Check final email sending
                                                                        if result.get('final_email_sent'):
                                                                            print("✅ Final email sent successfully!")
                                                                            
                                                                            # Check cleanup results
                                                                            if 'cleanup_result' in result:
                                                                                cleanup = result['cleanup_result']
                                                                                if cleanup and cleanup.get('success'):
                                                                                    print("✅ Post-cleanup completed successfully!")
                                                                                else:
                                                                                    print("⚠️ Post-cleanup completed with warnings")
                                                                        else:
                                                                            print("❌ Final email sending failed")
                                                                    else:
                                                                        print("❌ Email body needs revision")
                                                                        print(f"📊 Feedback: {email_evaluation_result.get('feedback', 'No feedback')}")
                                                                        print(f"📊 Iteration count: {result.get('iteration_count', 'N/A')}")
                                                                else:
                                                                    print("❌ Email evaluation failed")
                                                            else:
                                                                print("❌ Email evaluation result not found")
                                                        else:
                                                            print("❌ Report Drafter failed")
                                                    else:
                                                        print("❌ Report Drafter result not found")
                                                else:
                                                    print("❌ Supabase entry failed")
                                            else:
                                                print("✅ Workflow completed without Supabase entry")
                                        else:
                                            print("❌ Validation failed")
                                    else:
                                        print("✅ Workflow completed without validation")
                            else:
                                print(f"❌ Reconciliation failed: {reconciliation_result.get('error') if reconciliation_result else 'No result'}")
                        else:
                            print("❌ Reconciliation step not found in workflow result")
                    else:
                        print("❌ Database fetching failed")
                else:
                    print("❌ Database data not found in workflow result")
            else:
                print(f"❌ Email fetching failed: {email_result.get('error') if email_result else 'No result'}")
        else:
            print("❌ Email data not found in workflow result")
            print(f"Available keys: {list(result.keys())}")
        
        print(f"\n🔍 Check your LangSmith dashboard to see the traces!")
        print(f"Project: Charles-Fitness-report")
        print(f"URL: https://smith.langchain.com/")
        
    except Exception as e:
        print(f"❌ Error running orchestrated workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_reporting_workflow() 