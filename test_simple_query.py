#!/usr/bin/env python3
"""
Simple test to verify RAG system fixes
"""

import requests
import json

def test_simple_queries():
    """Test simple queries via the web interface"""
    
    print("🧪 Testing Simple Queries")
    print("=" * 40)
    
    # Test queries
    test_queries = [
        "what is my current weight?",
        "what was my weight in the start?",
        "show me my weight data"
    ]
    
    base_url = "http://localhost:8080"
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        try:
            # Send query to the web interface
            response = requests.post(
                f"{base_url}/api/chat/send",
                json={"message": query, "conversation_id": "test"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data.get('response', 'No response')}")
                
                # Check if response contains weight data
                response_text = data.get('response', '').lower()
                if 'no data' in response_text or 'no weight' in response_text:
                    print("⚠️ Response indicates no data available")
                elif 'weight' in response_text:
                    print("✅ Response contains weight information")
                else:
                    print("ℹ️ Response received but no weight info found")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_queries() 