import os
import sqlitecloud
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseFetcher:
    """Agent for fetching the latest entry from SQLite cloud database"""
    
    def __init__(self):
        # SQLite Cloud configuration
        self.sqlite_api_key = os.getenv("SQLITE_API_KEY")
        self.sqlite_db_url = os.getenv("SQLITE_DB_URL")
        self.connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={self.sqlite_api_key}"
        
    def fetch_latest_db_entry(self) -> Optional[Dict[str, Any]]:
        """Fetch the latest entry from SQLite cloud database"""
        try:
            if not self.sqlite_api_key:
                print("❌ SQLite API credentials not configured")
                return None
            
            print("🔄 Connecting to SQLite Cloud...")
            
            # Connect to SQLite Cloud using the Python library
            conn = sqlitecloud.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Query to get the latest entry from fitness_measurements table
            query = """
            SELECT * FROM fitness_measurements 
            ORDER BY created_at DESC 
            LIMIT 1
            """
            
            print(f"🔄 Executing query: {query}")
            cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            
            if not results:
                print("✅ No existing data found in database")
                conn.close()
                return None
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Convert to dictionary
            latest_entry = dict(zip(column_names, results[0]))
            
            print(f"✅ Fetched latest database entry")
            
            # Close connection
            conn.close()
            
            return latest_entry
                
        except Exception as e:
            print(f"❌ Error fetching database entry: {e}")
            return None
    
    def create_database_json(self, db_entry: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a JSON structure from database entry or blank values if no entry"""
        if db_entry is None:
            # Create JSON with blank values when no existing data
            json_data = {
                'database_info': {
                    'id': None,
                    'created_at': None,
                    'updated_at': None
                },
                'email_info': {
                    'subject': None,
                    'sender': None,
                    'date': None,
                    'email_id': None,
                    'fetched_at': None
                },
                'fitness_data': {
                    'metadata': {
                        'entry_date': None,
                        'submitted': None,
                        'processed_at': None
                    },
                    'measurements': {
                        'Week Number': None,
                        'Weight': None,
                        'Fat Percentage': None,
                        'Bmi': None,
                        'Fat Weight': None,
                        'Lean Weight': None,
                        'Neck': None,
                        'Shoulders': None,
                        'Biceps': None,
                        'Forearms': None,
                        'Chest': None,
                        'Above Navel': None,
                        'Navel': None,
                        'Waist': None,
                        'Hips': None,
                        'Thighs': None,
                        'Calves': None
                    }
                },
                'processed_at': datetime.now().isoformat()
            }
            print(f"✅ Created database JSON structure with blank values (no existing data)")
            return json_data
        else:
            # Create comprehensive JSON structure from existing data
            json_data = {
                'database_info': {
                    'id': db_entry.get('id'),
                    'created_at': db_entry.get('created_at'),
                    'updated_at': db_entry.get('updated_at')
                },
                'email_info': {
                    'subject': db_entry.get('email_subject'),
                    'sender': db_entry.get('email_sender'),
                    'date': db_entry.get('email_date'),
                    'email_id': db_entry.get('email_id'),
                    'fetched_at': db_entry.get('email_fetched_at')
                },
                'fitness_data': {
                    'metadata': {
                        'entry_date': db_entry.get('entry_date'),
                        'submitted': db_entry.get('submitted'),
                        'processed_at': db_entry.get('processed_at')
                    },
                    'measurements': {
                        'Week Number': db_entry.get('week_number'),
                        'Weight': db_entry.get('weight'),
                        'Fat Percentage': db_entry.get('fat_percentage'),
                        'Bmi': db_entry.get('bmi'),
                        'Fat Weight': db_entry.get('fat_weight'),
                        'Lean Weight': db_entry.get('lean_weight'),
                        'Neck': db_entry.get('neck'),
                        'Shoulders': db_entry.get('shoulders'),
                        'Biceps': db_entry.get('biceps'),
                        'Forearms': db_entry.get('forearms'),
                        'Chest': db_entry.get('chest'),
                        'Above Navel': db_entry.get('above_navel'),
                        'Navel': db_entry.get('navel'),
                        'Waist': db_entry.get('waist'),
                        'Hips': db_entry.get('hips'),
                        'Thighs': db_entry.get('thighs'),
                        'Calves': db_entry.get('calves')
                    }
                },
                'processed_at': datetime.now().isoformat()
            }
            
            # Debug logging for critical measurements
            above_navel = db_entry.get('above_navel')
            navel = db_entry.get('navel')
            print(f"🔍 DEBUG: Database - Above Navel: {above_navel}, Navel: {navel}")
            
            if above_navel == navel and above_navel is not None:
                print(f"⚠️  WARNING: Database shows Above Navel ({above_navel}) and Navel ({navel}) have the same value!")
                print(f"🔍 This might indicate a data storage issue in the database.")
            
            print(f"✅ Created database JSON structure")
            return json_data

def run_database_fetcher():
    """Run the database fetcher agent"""
    try:
        fetcher = DatabaseFetcher()
        db_entry = fetcher.fetch_latest_db_entry()
        
        if db_entry:
            print("✅ Successfully fetched latest database entry:")
            print(f"Week number: {db_entry.get('week_number')}")
            print(f"Weight: {db_entry.get('weight')}")
            print(f"Fat percentage: {db_entry.get('fat_percentage')}")
            print(f"BMI: {db_entry.get('bmi')}")
            print(f"Created at: {db_entry.get('created_at')}")
            
            # Create JSON structure from existing data
            json_data = fetcher.create_database_json(db_entry)
            
            # Display fitness data summary
            fitness_data = json_data.get('fitness_data', {})
            if fitness_data:
                print(f"\n📊 Database Fitness Data Summary:")
                print(f"Entry Date: {fitness_data.get('metadata', {}).get('entry_date')}")
                print(f"Measurements: {len(fitness_data.get('measurements', {}))}")
                
            return json_data  # Return JSON data for next agent
        else:
            print("✅ No existing data found - creating blank JSON structure")
            
            # Create JSON structure with blank values
            json_data = fetcher.create_database_json(None)
            
            print(f"📊 Blank Database JSON Summary:")
            print(f"Entry Date: None (no existing data)")
            print(f"Measurements: {len(json_data.get('fitness_data', {}).get('measurements', {}))} (all blank)")
            
            return json_data  # Return blank JSON data for next agent
        
    except Exception as e:
        print(f"❌ Error running database fetcher agent: {e}")
        return None
        
    except Exception as e:
        print(f"❌ Error running database fetcher agent: {e}")
        return None

if __name__ == "__main__":
    run_database_fetcher() 