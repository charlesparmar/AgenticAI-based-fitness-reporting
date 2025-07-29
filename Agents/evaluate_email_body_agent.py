import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

class EvaluateEmailBodyAgent:
    """Agent for evaluating email body quality and providing feedback"""
    
    def __init__(self):
        # OpenAI configuration using LangChain
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY must be set in .env file")
    
    def evaluate_email_body(self, email_body: str, baseline_data: Dict[str, Any], current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate email body quality using OpenAI GPT-4o-mini"""
        try:
            print("🔍 Evaluating email body quality...")
            
            # Prepare the evaluation prompt
            prompt = f"""You are a quality control personnel evaluating a fitness update email. Please evaluate the following email body based on these criteria:

1. **Greeting**: Please check if the greeting is present. 
2. **Week Comparison**: Must be for two weeks (first and last weeks data). Please be lenient with this. As long as there is some comparison. This criteria is met. 
3. **Online Link**: Must include the link "https://viewonlyfitnessreport.vercel.app/" only once and not repeated. Sometimes this can be twice like [https://viewonlyfitnessreport.vercel.app/](https://viewonlyfitnessreport.vercel.app/). In this case give feedback to correct it to https://viewonlyfitnessreport.vercel.app/ and make sure there is no brackets etc around the link. If it is stated like [this link](https://viewonlyfitnessreport.vercel.app/), then again give feedback that it must show only like https://viewonlyfitnessreport.vercel.app/. This is very important. 
4. **Signature**: Must have appropriate signature section




Email body to evaluate:
{email_body}

First week's data (baseline): {json.dumps(baseline_data, indent=2)}
Last week's data (current): {json.dumps(current_data, indent=2)}

Please provide your evaluation in the following JSON format:
{{
    "approved": true/false,
    "feedback": "Detailed feedback on what needs to be improved (if not approved)",
    "score": 1-10,
    "issues": ["list of specific issues found"],
    "strengths": ["list of strengths"]
}}

If approved, set "approved" to true and provide positive feedback. If not approved, set "approved" to false and provide specific feedback on what needs to be changed."""
            
            # Make API call to OpenAI using LangChain
            messages = [
                SystemMessage(content="You are a quality control expert evaluating fitness update emails. Provide detailed, constructive feedback."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
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