import os
import json
import sqlite3
import requests
import sqlitecloud
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataValidationAgent:
    """Agent for validating fitness data against historical trends"""
    
    def __init__(self):
        self.sqlite_api_key = os.getenv("SQLITE_API_KEY")
        self.sqlite_db_url = os.getenv("SQLITE_DB_URL")
        self.sqlite_table_name = os.getenv("SQLITE_TABLE_NAME", "fitness_measurements")
        self.pushover_token = os.getenv("PUSHOVER_TOKEN")
        self.pushover_user_key = os.getenv("PUSHOVER_USER_KEY")
        
        # SQLite Cloud connection string - using fitness_data.db database
        self.connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={self.sqlite_api_key}"
        
        # Validation results table name
        self.validation_table_name = "validation_results"
        
    def fetch_historical_data(self) -> Optional[List[Dict[str, Any]]]:
        """Fetch last 4 data entries from SQLite cloud database using Python library"""
        try:
            if not self.sqlite_api_key:
                print("❌ SQLite API credentials not configured")
                return None
            
            print("🔄 Connecting to SQLite Cloud...")
            
            # Connect to SQLite Cloud using the Python library
            conn = sqlitecloud.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Query to get last 4 entries
            query = f"""
            SELECT * FROM {self.sqlite_table_name} 
            ORDER BY date DESC 
            LIMIT 4
            """
            
            print(f"🔄 Executing query: {query}")
            cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Convert to list of dictionaries
            historical_data = []
            for row in results:
                row_dict = dict(zip(column_names, row))
                historical_data.append(row_dict)
            
            print(f"✅ Fetched {len(historical_data)} historical entries")
            
            # Close connection
            conn.close()
            
            return historical_data
                
        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
            return None
    
    def analyze_trends(self, new_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends using GPT-4o-mini with historical data"""
        try:
            # Initialize the model
            model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Prepare data for analysis
            analysis_prompt = self._create_analysis_prompt(new_data, historical_data)
            
            # Get model response
            response = model.invoke(analysis_prompt)
            
            # Parse the response
            analysis_result = self._parse_analysis_response(response.content)
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Error analyzing trends: {e}")
            return {
                "validation_status": "Validation Failed",
                "reason": f"Analysis error: {e}",
                "confidence": 0.0
            }
    
    def analyze_single_data_point(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze single data point using GPT-4o-mini without historical data"""
        try:
            # Initialize the model
            model = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Prepare data for analysis
            analysis_prompt = self._create_single_data_analysis_prompt(new_data)
            
            # Get model response
            response = model.invoke(analysis_prompt)
            
            # Parse the response
            analysis_result = self._parse_analysis_response(response.content)
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Error analyzing single data point: {e}")
            return {
                "validation_status": "Validation Failed",
                "reason": f"Analysis error: {e}",
                "confidence": 0.0
            }
    
    def _create_analysis_prompt(self, new_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> str:
        """Create analysis prompt for the LLM"""
        
        prompt = f"""
You are a fitness data validation expert. Analyze the new fitness data against historical trends.

IMPORTANT: Ignore week numbers and dates when comparing data. Focus only on the actual fitness measurements and body metrics.

HISTORICAL DATA (Last 4 entries):
{json.dumps(historical_data, indent=2)}

NEW DATA TO VALIDATE:
{json.dumps(new_data, indent=2)}

ANALYSIS TASK:
1. Compare the new data with historical trends (IGNORE week numbers and focus only on weight metrics and body measurements)
2. Check if measurements are within reasonable ranges
3. Look for any anomalies or sudden changes in body measurements
4. Determine if the data follows expected patterns for fitness progress

VALIDATION CRITERIA:
- Weight changes should be gradual (not more than 5kg in one entry)
- Body measurements should be consistent and allow for some variation
- Fat percentage should follow logical patterns but allow for some variation
- All measurements should be within humanly possible ranges but allow for some variation
- Focus on: weight, fat_percentage, bmi, body measurements (neck, shoulders, biceps, etc.)
- IGNORE: week numbers, dates, and any metadata fields

RESPONSE FORMAT (JSON):
{{
    "validation_status": "Validation Success" or "Validation Failed",
    "reason": "Detailed explanation of the validation result (focus on measurements, not week numbers)",
    "confidence": 0.0 to 1.0,
    "anomalies": ["list of any anomalies found in measurements only"],
    "trend_analysis": "Brief trend analysis of fitness measurements"
}}

Provide your analysis in valid JSON format only.
"""
        return prompt
    
    def _create_single_data_analysis_prompt(self, new_data: Dict[str, Any]) -> str:
        """Create analysis prompt for single data point without historical data"""
        
        prompt = f"""
You are a fitness data validation expert. Analyze the new fitness data for reasonableness and potential issues.

NEW DATA TO VALIDATE:
{json.dumps(new_data, indent=2)}

ANALYSIS TASK:
1. Check if measurements are within reasonable human ranges
2. Look for any obvious anomalies or impossible values
3. Verify data consistency within the entry
4. Assess the overall quality and plausibility of the data

VALIDATION CRITERIA:
- Weight should be between 30-300 kg (reasonable human range)
- Body measurements should be proportional and realistic
- Fat percentage should be between 2-50% (reasonable range)
- All measurements should be positive numbers
- BMI should be calculated correctly (weight in kg / height in m²)
- Measurements should be consistent (e.g., waist should be smaller than hips)

RESPONSE FORMAT (JSON):
{{
    "validation_status": "Validation Success" or "Validation Failed",
    "reason": "Detailed explanation of the validation result",
    "confidence": 0.0 to 1.0,
    "anomalies": ["list of any anomalies found"],
    "data_quality": "Assessment of data quality"
}}

Provide your analysis in valid JSON format only.
"""
        return prompt
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM analysis response"""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                return result
            else:
                # Fallback parsing
                return {
                    "validation_status": "Validation Failed",
                    "reason": "Could not parse analysis response",
                    "confidence": 0.0
                }
        except Exception as e:
            return {
                "validation_status": "Validation Failed",
                "reason": f"Response parsing error: {e}",
                "confidence": 0.0
            }
    
    def send_pushover_notification(self, validation_result: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Send notification via Pushover"""
        try:
            if not self.pushover_token or not self.pushover_user_key:
                print("❌ Pushover credentials not configured")
                return False
            
            # Create notification message
            status = validation_result.get("validation_status", "Unknown")
            reason = validation_result.get("reason", "No reason provided")
            confidence = validation_result.get("confidence", 0.0)
            
            message = f"""
🏋️ Fitness Data Validation: {status}

📊 New Entry Date: {new_data.get('fitness_data', {}).get('metadata', {}).get('entry_date', 'Unknown')}
📈 Confidence: {confidence:.2f}

🔍 Analysis: {reason}

📱 Sent by Data Validation Agent
"""
            
            # Send via Pushover
            pushover_data = {
                "token": self.pushover_token,
                "user": self.pushover_user_key,
                "message": message.strip(),
                "title": f"Fitness Validation: {status}",
                "priority": 1 if status == "Validation Failed" else 0
            }
            
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data=pushover_data
            )
            
            if response.status_code == 200:
                print(f"✅ Pushover notification sent: {status}")
                return True
            else:
                print(f"❌ Failed to send Pushover notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Pushover notification: {e}")
            return False
    
    def save_validation_result_to_db(self, validation_data: Dict[str, Any]) -> bool:
        """Save validation result to database"""
        try:
            if not self.sqlite_api_key:
                print("❌ SQLite API credentials not configured")
                return False
            
            print("🔄 Saving validation result to database...")
            
            # Connect to SQLite Cloud
            conn = sqlitecloud.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Extract validation result data
            validation_result = validation_data.get('validation_result', {})
            
            # Prepare the insert query
            insert_query = f"""
            INSERT INTO {self.validation_table_name} (
                validation_timestamp,
                new_data_file,
                validation_status,
                reason,
                confidence,
                anomalies,
                trend_analysis,
                notification_sent,
                historical_data_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Prepare the data
            insert_data = (
                validation_data.get('validation_timestamp'),
                validation_data.get('new_data_file'),
                validation_result.get('validation_status'),
                validation_result.get('reason'),
                validation_result.get('confidence'),
                json.dumps(validation_result.get('anomalies', [])),  # Convert list to JSON string
                validation_result.get('trend_analysis'),
                1 if validation_data.get('notification_sent') else 0,  # Convert boolean to integer
                validation_data.get('historical_data_count', 0)
            )
            
            # Execute the insert
            cursor.execute(insert_query, insert_data)
            conn.commit()
            
            print(f"✅ Validation result saved to database with ID: {cursor.lastrowid}")
            
            # Close connection
            conn.close()
            
            return True
                
        except Exception as e:
            print(f"❌ Error saving validation result to database: {e}")
            return False
    
    def validate_fitness_data(self, new_data_file: str) -> Dict[str, Any]:
        """Main validation function"""
        try:
            print(f"🔍 Starting validation for: {new_data_file}")
            
            # Load new data
            with open(new_data_file, 'r') as f:
                new_data = json.load(f)
            
            # Fetch historical data
            historical_data = self.fetch_historical_data()
            
            if not historical_data:
                print("⚠️ No historical data available, using LLM analysis for single data point")
                validation_result = self.analyze_single_data_point(new_data)
            else:
                # Analyze trends with historical data
                validation_result = self.analyze_trends(new_data, historical_data)
            
            # Send notification
            notification_sent = self.send_pushover_notification(validation_result, new_data)
            
            # Prepare validation data
            validation_data = {
                "validation_timestamp": datetime.now().isoformat(),
                "new_data_file": new_data_file,
                "validation_result": validation_result,
                "notification_sent": notification_sent,
                "historical_data_count": len(historical_data) if historical_data else 0
            }
            
            # Save validation result to database
            db_saved = self.save_validation_result_to_db(validation_data)
            
            if db_saved:
                print("✅ Validation result saved to database")
            else:
                print("❌ Failed to save validation result to database")
            
            return validation_data
            
        except Exception as e:
            print(f"❌ Error in validation process: {e}")
            return {
                "validation_status": "Validation Failed",
                "reason": f"Validation error: {e}",
                "timestamp": datetime.now().isoformat()
            }

# LangGraph State
class ValidationState:
    """State for the data validation agent"""
    def __init__(self, validation_result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.validation_result = validation_result
        self.error = error
        self.timestamp = datetime.now().isoformat()

# Tools for LangGraph
@tool
def validate_fitness_data_tool(new_data_file: str) -> Dict[str, Any]:
    """Validate fitness data against historical trends"""
    agent = DataValidationAgent()
    result = agent.validate_fitness_data(new_data_file)
    return result

# LangGraph Agent
def create_data_validation_agent():
    """Create the data validation agent using LangGraph"""
    
    # Initialize the model
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create the graph
    workflow = StateGraph(ValidationState)
    
    # Add nodes
    workflow.add_node("validate_data", ToolNode([validate_fitness_data_tool]))
    
    # Set entry point
    workflow.set_entry_point("validate_data")
    
    # Add edges
    workflow.add_edge("validate_data", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

# Main execution function
def run_data_validation_agent(new_data_file: str):
    """Run the data validation agent"""
    try:
        # Create and run the agent
        agent = create_data_validation_agent()
        
        # Initialize state
        initial_state = ValidationState()
        
        # Run the agent
        result = agent.invoke({
            "validate_data": {"new_data_file": new_data_file}
        })
        
        # Extract the result
        if 'validate_data' in result:
            validation_result = result['validate_data']
            
            if validation_result.get('validation_result', {}).get('validation_status'):
                status = validation_result['validation_result']['validation_status']
                print(f"✅ Validation completed: {status}")
                print(f"📄 Result file: validation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            else:
                print("❌ Validation failed")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running data validation agent: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        new_data_file = sys.argv[1]
        run_data_validation_agent(new_data_file)
    else:
        print("Usage: python data_validation_agent.py <new_data_file.json>") 