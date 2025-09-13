#!/usr/bin/env python3
"""
Script to create the report_sent table in SQLite Cloud database.
This table will store metadata and content of all sent fitness reports.
"""

import os
import sqlitecloud
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_report_sent_table():
    """Create the report_sent table in SQLite Cloud database"""
    try:
        # Get SQLite Cloud credentials
        sqlite_api_key = os.getenv("SQLITE_API_KEY")
        if not sqlite_api_key:
            print("❌ SQLite API key not found in environment variables")
            return False
        
        # Connection string
        connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={sqlite_api_key}"
        
        print("🔄 Connecting to SQLite Cloud...")
        conn = sqlitecloud.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='report_sent'
        """)
        
        if cursor.fetchone():
            print("⚠️ Table 'report_sent' already exists")
            response = input("Do you want to drop and recreate it? (y/N): ")
            if response.lower() == 'y':
                cursor.execute("DROP TABLE report_sent")
                print("✅ Existing table dropped")
            else:
                print("❌ Table creation cancelled")
                conn.close()
                return False
        
        # Create the table
        create_table_query = """
        CREATE TABLE report_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_sent DATE NOT NULL,
            from_email VARCHAR(255) NOT NULL,
            to_email VARCHAR(255) NOT NULL,
            cc_emails TEXT,
            sent_datetime TIMESTAMP NOT NULL,
            email_body TEXT NOT NULL,
            subject VARCHAR(500),
            message_id VARCHAR(255),
            excel_attached BOOLEAN DEFAULT FALSE,
            iteration_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_query)
        print("✅ Table 'report_sent' created successfully")
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_report_sent_date_sent ON report_sent(date_sent)")
        cursor.execute("CREATE INDEX idx_report_sent_to_email ON report_sent(to_email)")
        print("✅ Indexes created successfully")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("🎉 Report Sent table setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating report_sent table: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Creating Report Sent table...")
    success = create_report_sent_table()
    
    if success:
        print("\n✅ Database setup completed!")
        print("📋 Table 'report_sent' is ready to store email reports")
        print("🔧 You can now run the final_email_agent and it will automatically save reports")
    else:
        print("\n❌ Database setup failed!")
        print("🔧 Please check your SQLite credentials and try again")
