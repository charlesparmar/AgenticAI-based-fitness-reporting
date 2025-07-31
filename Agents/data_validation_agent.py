import os
import json
import sqlite3
import requests
import sqlitecloud
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

# Import new modular components
from config.llm_config import llm_config
from utils.prompt_loader import prompt_loader

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
    
    def _remove_week_number_field(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove 'Week Number' field from fitness data"""
        if isinstance(data, dict):
            cleaned_data = data.copy()
            # Remove Week Number from measurements if it exists
            if 'fitness_data' in cleaned_data and 'measurements' in cleaned_data['fitness_data']:
                if 'Week Number' in cleaned_data['fitness_data']['measurements']:
                    del cleaned_data['fitness_data']['measurements']['Week Number']
                    print("🗑️ Removed 'Week Number' field from fitness data")
            return cleaned_data
        return data
    
    def _remove_week_number_from_historical_data(self, historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove 'Week Number' field from historical data"""
        cleaned_historical_data = []
        for entry in historical_data:
            cleaned_entry = entry.copy()
            if 'Week Number' in cleaned_entry:
                del cleaned_entry['Week Number']
            cleaned_historical_data.append(cleaned_entry)
        
        if historical_data and 'Week Number' in historical_data[0]:
            print("🗑️ Removed 'Week Number' field from historical data")
        
        return cleaned_historical_data

    def analyze_trends(self, new_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends using configured LLM with historical data"""
        try:
            # Get the model for this specific prompt
            model = prompt_loader.get_model_for_prompt("validation_prompt", temperature=0)
            
            # Load and format analysis prompt
            analysis_prompt = prompt_loader.format_prompt(
                "validation_prompt",
                new_data=json.dumps(new_data, indent=2),
                historical_data=json.dumps(historical_data, indent=2)
            )
            
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
            
            # Clean new data by removing 'Week Number'
            cleaned_new_data = self._remove_week_number_field(new_data)
            
            # Fetch historical data
            historical_data = self.fetch_historical_data()
            
            if not historical_data:
                print("❌ No historical data available for trend analysis. Validation requires historical data.")
                validation_result = {
                    "validation_status": "Validation Failed",
                    "reason": "No historical data available for trend analysis",
                    "confidence": 0.0
                }
            else:
                # Clean historical data by removing 'Week Number'
                cleaned_historical_data = self._remove_week_number_from_historical_data(historical_data)
                # Analyze trends with historical data
                validation_result = self.analyze_trends(cleaned_new_data, cleaned_historical_data)
            
            # Send notification
            notification_sent = self.send_pushover_notification(validation_result, cleaned_new_data)
            
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
    
    # Initialize the model using centralized configuration
    model = llm_config.get_model(temperature=0.7)
    
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