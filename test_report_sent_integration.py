#!/usr/bin/env python3
"""
Test script to verify the report_sent table integration with final_email_agent.
This script tests the database connection and save_email_report functionality.
"""

import os
import sys
import sqlitecloud
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test SQLite Cloud database connection"""
    try:
        sqlite_api_key = os.getenv("SQLITE_API_KEY")
        if not sqlite_api_key:
            print("❌ SQLite API key not found")
            return False
        
        connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={sqlite_api_key}"
        
        print("🔄 Testing database connection...")
        conn = sqlitecloud.connect(connection_string)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='report_sent'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Database connection successful - report_sent table exists")
            conn.close()
            return True
        else:
            print("❌ report_sent table not found - please run create_report_sent_table.py first")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_save_email_report():
    """Test the save_email_report functionality"""
    try:
        from Agents.final_email_agent import FinalEmailAgent
        
        print("🔄 Testing save_email_report functionality...")
        
        # Create test agent (this will test initialization)
        agent = FinalEmailAgent()
        
        # Test data
        test_email_data = {
            'from_email': 'test@example.com',
            'to_email': 'coach@example.com',
            'cc_emails': ['cc@example.com'],
            'email_body': 'This is a test fitness report email body for database integration testing.',
            'subject': 'Test Report: Database Integration',
            'message_id': f'test_message_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'excel_attached': True,
            'iteration_count': 1
        }
        
        # Test saving to database
        success = agent.save_email_report(test_email_data)
        
        if success:
            print("✅ save_email_report test successful")
            return True
        else:
            print("❌ save_email_report test failed")
            return False
            
    except Exception as e:
        print(f"❌ save_email_report test failed: {e}")
        return False

def verify_test_data():
    """Verify that test data was saved correctly"""
    try:
        sqlite_api_key = os.getenv("SQLITE_API_KEY")
        connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={sqlite_api_key}"
        
        print("🔄 Verifying test data in database...")
        conn = sqlitecloud.connect(connection_string)
        cursor = conn.cursor()
        
        # Query for test records
        cursor.execute("""
            SELECT id, date_sent, from_email, to_email, subject, excel_attached, iteration_count, created_at
            FROM report_sent 
            WHERE subject LIKE 'Test Report: Database Integration%'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if result:
            print("✅ Test data found in database:")
            print(f"   ID: {result[0]}")
            print(f"   Date Sent: {result[1]}")
            print(f"   From: {result[2]}")
            print(f"   To: {result[3]}")
            print(f"   Subject: {result[4]}")
            print(f"   Excel Attached: {result[5]}")
            print(f"   Iteration Count: {result[6]}")
            print(f"   Created At: {result[7]}")
            conn.close()
            return True
        else:
            print("❌ No test data found in database")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error verifying test data: {e}")
        return False

def cleanup_test_data():
    """Clean up test data from database"""
    try:
        sqlite_api_key = os.getenv("SQLITE_API_KEY")
        connection_string = f"sqlitecloud://ccbfw4dwnk.g3.sqlite.cloud:8860/fitness_data.db?apikey={sqlite_api_key}"
        
        print("🔄 Cleaning up test data...")
        conn = sqlitecloud.connect(connection_string)
        cursor = conn.cursor()
        
        # Delete test records
        cursor.execute("""
            DELETE FROM report_sent 
            WHERE subject LIKE 'Test Report: Database Integration%'
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"✅ Cleaned up {deleted_count} test record(s)")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up test data: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🤖 Testing Report Sent Table Integration")
    print("=" * 50)
    
    # Test 1: Database connection
    if not test_database_connection():
        print("\n❌ Database connection test failed - stopping tests")
        return False
    
    # Test 2: Save email report functionality
    if not test_save_email_report():
        print("\n❌ Save email report test failed")
        return False
    
    # Test 3: Verify data was saved
    if not verify_test_data():
        print("\n❌ Data verification test failed")
        return False
    
    # Test 4: Cleanup test data
    if not cleanup_test_data():
        print("\n⚠️ Cleanup failed - you may need to manually remove test data")
    
    print("\n🎉 All integration tests passed!")
    print("✅ The final_email_agent is ready to save email reports to the database")
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n📋 Summary:")
        print("✅ Database connection: Working")
        print("✅ Email report saving: Working")
        print("✅ Data verification: Working")
        print("✅ Integration: Complete")
    else:
        print("\n📋 Summary:")
        print("❌ Integration tests failed")
        print("🔧 Please check the error messages above and resolve any issues")
