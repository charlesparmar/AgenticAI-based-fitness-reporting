import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

# Import new modular components
from config.llm_config import llm_config
from utils.prompt_loader import prompt_loader

# Load environment variables
load_dotenv()

class EvaluateEmailBodyAgent:
    """Agent for evaluating email body quality and providing feedback"""
    
    def __init__(self):
        # LLM configuration using modular system
        self.llm = llm_config.get_model(temperature=0.3)
    
    def evaluate_email_body(self, email_body: str, baseline_data: Dict[str, Any], current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate email body quality using configured LLM"""
        try:
            print("🔍 Evaluating email body quality...")
            
            # Get the model for this specific prompt
            model = prompt_loader.get_model_for_prompt("email_evaluation_prompt", temperature=0.3)
            
            # Load and format the evaluation prompt
            prompt = prompt_loader.format_prompt(
                "email_evaluation_prompt",
                email_body=email_body,
                baseline_data=json.dumps(baseline_data, indent=2),
                current_data=json.dumps(current_data, indent=2)
            )
            
            # Make API call to OpenAI using LangChain
            messages = [
                SystemMessage(content="You are a quality control expert evaluating fitness update emails. Provide detailed, constructive feedback."),
                HumanMessage(content=prompt)
            ]
            
            response = model.invoke(messages)
            
            evaluation_text = response.content.strip()
            
            # Try to parse JSON response
            try:
                evaluation = json.loads(evaluation_text)
                print("✅ Email body evaluation completed")
                return {
                    'success': True,
                    'evaluation': evaluation,
                    'timestamp': datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                print("⚠️ JSON parsing failed, creating structured response")
                return {
                    'success': True,
                    'evaluation': {
                        'approved': False,
                        'feedback': 'Failed to parse evaluation response. Please regenerate the email body.',
                        'score': 5,
                        'issues': ['Evaluation response parsing error'],
                        'strengths': []
                    },
                    'raw_response': evaluation_text,
                    'timestamp': datetime.now().isoformat()
                }
            
        except Exception as e:
            print(f"❌ Error evaluating email body: {e}")
            return {
                'success': False,
                'error': f'Email evaluation error: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def process_email_evaluation(self, email_body_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main function to process email evaluation"""
        try:
            print("🤖 Starting Email Body Evaluation Agent...")
            
            # Extract data from email_body_data
            email_body = email_body_data.get('email_body', '')
            baseline_data = email_body_data.get('baseline_data', {})
            current_data = email_body_data.get('current_data', {})
            
            if not email_body:
                return {
                    'success': False,
                    'error': 'No email body provided for evaluation',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Evaluate the email body
            evaluation_result = self.evaluate_email_body(email_body, baseline_data, current_data)
            
            if evaluation_result.get('success'):
                evaluation = evaluation_result.get('evaluation', {})
                
                if evaluation.get('approved', False):
                    print("✅ Email body approved!")
                    return {
                        'success': True,
                        'approved': True,
                        'feedback': evaluation.get('feedback', 'Email body meets all quality standards'),
                        'score': evaluation.get('score', 10),
                        'message': 'Email body approved for sending',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print("❌ Email body needs revision")
                    return {
                        'success': True,
                        'approved': False,
                        'feedback': evaluation.get('feedback', 'Email body needs improvement'),
                        'score': evaluation.get('score', 0),
                        'issues': evaluation.get('issues', []),
                        'strengths': evaluation.get('strengths', []),
                        'message': 'Email body needs revision based on feedback',
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                return {
                    'success': False,
                    'error': evaluation_result.get('error', 'Evaluation failed'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error in Email Body Evaluation agent: {e}")
            return {
                'success': False,
                'error': f'Email Body Evaluation agent error: {e}',
                'timestamp': datetime.now().isoformat()
            }

def run_evaluate_email_body_agent(email_body_data: Dict[str, Any]):
    """Run the Email Body Evaluation agent"""
    try:
        agent = EvaluateEmailBodyAgent()
        result = agent.process_email_evaluation(email_body_data)
        
        if result.get('success'):
            if result.get('approved'):
                print("✅ Email Body Evaluation agent completed successfully - APPROVED")
                print(f"📊 Score: {result.get('score')}")
                print(f"📊 Feedback: {result.get('feedback')}")
            else:
                print("✅ Email Body Evaluation agent completed - NEEDS REVISION")
                print(f"📊 Score: {result.get('score')}")
                print(f"📊 Feedback: {result.get('feedback')}")
                if result.get('issues'):
                    print(f"📊 Issues: {', '.join(result.get('issues'))}")
        else:
            print(f"❌ Email Body Evaluation agent failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running Email Body Evaluation agent: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    print("Email Body Evaluation Agent - This agent requires email body data to be passed in")
    print("Use run_evaluate_email_body_agent(email_body_data) to run the agent") 