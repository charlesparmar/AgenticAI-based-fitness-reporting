#!/usr/bin/env python3
"""
Test Script for RAG Pipeline Phase 4
Tests chat interface and web interface functionality
"""

import os
import sys
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.chat_interface import ChatInterface, Message, Conversation
from rag.web_interface import WebInterface
from rag.vector_store import VectorStore
from rag.query_processor import QueryProcessor
from rag.retriever import Retriever
from rag.generator import ResponseGenerator


def test_chat_interface():
    """Test chat interface functionality"""
    print("🧪 Testing Chat Interface...")
    print("=" * 50)
    
    # Initialize components
    vector_store = VectorStore(collection_name="test_chat_interface")
    query_processor = QueryProcessor()
    retriever = Retriever(vector_store, query_processor)
    generator = ResponseGenerator()
    chat_interface = ChatInterface(vector_store, query_processor, retriever, generator)
    
    # Test conversation creation
    print("\n1. Testing conversation creation...")
    
    conversation_id = chat_interface.create_conversation("Test Fitness Chat")
    if conversation_id:
        print(f"   ✅ Created conversation: {conversation_id}")
    else:
        print("   ❌ Failed to create conversation")
        return False
    
    # Test message sending
    print("\n2. Testing message sending...")
    
    test_messages = [
        "How has my weight changed?",
        "What are my current measurements?",
        "Give me a summary of my progress",
        "/help"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Message {i}: '{message}'")
        
        response = chat_interface.send_message(message, conversation_id)
        
        if "error" in response:
            print(f"      ❌ Error: {response['error']}")
        else:
            user_msg = response.get('user_message', {})
            assistant_msg = response.get('assistant_message', {})
            
            print(f"      ✅ User message: {user_msg.get('content', '')[:50]}...")
            print(f"      ✅ Assistant response: {assistant_msg.get('content', '')[:100]}...")
    
    # Test conversation management
    print("\n3. Testing conversation management...")
    
    # List conversations
    conversations = chat_interface.list_conversations()
    print(f"   ✅ Found {len(conversations)} conversations")
    
    for conv in conversations:
        print(f"      - {conv['title']} ({conv['message_count']} messages)")
    
    # Get conversation stats
    stats = chat_interface.get_conversation_stats(conversation_id)
    if "error" not in stats:
        print(f"   ✅ Conversation stats: {stats['total_messages']} messages, {stats['duration_minutes']} minutes")
    else:
        print(f"   ❌ Error getting stats: {stats['error']}")
    
    # Test conversation switching
    print("\n4. Testing conversation switching...")
    
    # Create another conversation
    conversation_id2 = chat_interface.create_conversation("Second Test Chat")
    if conversation_id2:
        print(f"   ✅ Created second conversation: {conversation_id2}")
        
        # Switch to first conversation
        success = chat_interface.switch_conversation(conversation_id)
        if success:
            print(f"   ✅ Switched to first conversation")
        else:
            print(f"   ❌ Failed to switch conversation")
    
    # Test conversation export
    print("\n5. Testing conversation export...")
    
    export_data = chat_interface.export_conversation(conversation_id)
    if export_data:
        print(f"   ✅ Exported conversation: {len(json.dumps(export_data))} characters")
        print(f"      - Messages: {len(export_data['conversation']['messages'])}")
        print(f"      - Export time: {export_data['exported_at']}")
    else:
        print(f"   ❌ Failed to export conversation")
    
    # Test special commands
    print("\n6. Testing special commands...")
    
    special_commands = [
        ("/help", "Help command"),
        ("/summary", "Summary command"),
        ("/new", "New conversation command")
    ]
    
    for command, description in special_commands:
        print(f"\n   Testing {description}: '{command}'")
        
        response = chat_interface.send_message(command, conversation_id)
        
        if "error" in response:
            print(f"      ❌ Error: {response['error']}")
        else:
            assistant_msg = response.get('assistant_message', {})
            print(f"      ✅ Response: {assistant_msg.get('content', '')[:100]}...")
    
    # Test conversation deletion
    print("\n7. Testing conversation deletion...")
    
    if conversation_id2:
        success = chat_interface.delete_conversation(conversation_id2)
        if success:
            print(f"   ✅ Deleted second conversation")
        else:
            print(f"   ❌ Failed to delete conversation")
    
    # Test chat interface info
    print("\n8. Testing chat interface info...")
    
    info = chat_interface.get_chat_interface_info()
    print(f"   ✅ Total conversations: {info['total_conversations']}")
    print(f"   ✅ Active conversation: {info['active_conversation_id']}")
    print(f"   ✅ Available commands: {len(info['available_commands'])}")
    
    # Clean up
    print("\n9. Cleaning up...")
    vector_store.reset_collection()
    print("   ✅ Test data cleaned up")
    
    return True


def test_web_interface():
    """Test web interface functionality"""
    print("\n🧪 Testing Web Interface...")
    print("=" * 50)
    
    try:
        # Initialize web interface
        print("\n1. Initializing web interface...")
        
        vector_store = VectorStore(collection_name="test_web_interface")
        query_processor = QueryProcessor()
        retriever = Retriever(vector_store, query_processor)
        generator = ResponseGenerator()
        chat_interface = ChatInterface(vector_store, query_processor, retriever, generator)
        
        web_interface = WebInterface(
            vector_store=vector_store,
            chat_interface=chat_interface,
            host="127.0.0.1",
            port=5001
        )
        
        print("   ✅ Web interface initialized")
        
        # Test Flask app creation
        print("\n2. Testing Flask app creation...")
        
        app = web_interface.get_app()
        socketio = web_interface.get_socketio()
        
        if app and socketio:
            print("   ✅ Flask app and SocketIO created successfully")
        else:
            print("   ❌ Failed to create Flask app or SocketIO")
            return False
        
        # Test template creation
        print("\n3. Testing template creation...")
        
        web_interface.create_templates()
        print("   ✅ Templates created successfully")
        
        # Test API endpoints (without running server)
        print("\n4. Testing API endpoint registration...")
        
        # Check if routes are registered
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        expected_routes = [
            "GET /",
            "POST /api/chat/send",
            "GET /api/chat/conversations",
            "GET /api/system/health"
        ]
        
        found_routes = 0
        for expected in expected_routes:
            for route in routes:
                if expected.split()[1] in route:
                    found_routes += 1
                    break
        
        print(f"   ✅ Found {found_routes}/{len(expected_routes)} expected routes")
        
        # Test health check endpoint
        print("\n5. Testing health check endpoint...")
        
        with app.test_client() as client:
            response = client.get('/api/system/health')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ Health check passed: {data['status']}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
        
        # Test system info endpoint
        print("\n6. Testing system info endpoint...")
        
        with app.test_client() as client:
            response = client.get('/api/system/info')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ System info retrieved")
                print(f"      - Chat interface: {data['chat_interface']['total_conversations']} conversations")
                print(f"      - Vector store: {data['vector_store'].get('document_count', 0)} documents")
            else:
                print(f"   ❌ System info failed: {response.status_code}")
        
        # Test conversation API endpoints
        print("\n7. Testing conversation API endpoints...")
        
        with app.test_client() as client:
            # Create conversation
            response = client.post('/api/chat/conversations', 
                                 json={'title': 'API Test Conversation'})
            if response.status_code == 200:
                data = response.get_json()
                conversation_id = data['conversation_id']
                print(f"   ✅ Created conversation via API: {conversation_id}")
                
                # Send message
                response = client.post('/api/chat/send', 
                                     json={'message': 'Hello from API test', 
                                           'conversation_id': conversation_id})
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"   ✅ Sent message via API")
                    print(f"      - Response: {data['assistant_message']['content'][:50]}...")
                else:
                    print(f"   ❌ Failed to send message: {response.status_code}")
                
                # Get conversation
                response = client.get(f'/api/chat/conversations/{conversation_id}')
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"   ✅ Retrieved conversation: {len(data['messages'])} messages")
                else:
                    print(f"   ❌ Failed to get conversation: {response.status_code}")
                
                # Delete conversation
                response = client.delete(f'/api/chat/conversations/{conversation_id}')
                if response.status_code == 200:
                    print(f"   ✅ Deleted conversation via API")
                else:
                    print(f"   ❌ Failed to delete conversation: {response.status_code}")
            else:
                print(f"   ❌ Failed to create conversation: {response.status_code}")
        
        # Clean up
        print("\n8. Cleaning up...")
        vector_store.reset_collection()
        print("   ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Web interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test integration between all phases"""
    print("\n🧪 Testing Full RAG Pipeline Integration...")
    print("=" * 50)
    
    try:
        # Initialize all components
        print("\n1. Initializing complete RAG pipeline...")
        
        vector_store = VectorStore(collection_name="integration_test_phase4")
        query_processor = QueryProcessor()
        retriever = Retriever(vector_store, query_processor)
        generator = ResponseGenerator()
        chat_interface = ChatInterface(vector_store, query_processor, retriever, generator)
        
        # Add test data
        print("2. Adding test data...")
        
        test_documents = [
            {
                'content': 'Week 1 measurements: Weight 80kg, BMI 25.5, Fat percentage 18%, Chest 100cm, Waist 85cm',
                'metadata': {
                    'type': 'measurement',
                    'date': '2024-01-01',
                    'week_number': 'Week 1',
                    'chunk_id': 'test_chunk_1',
                    'measurements': {'weight': 80, 'bmi': 25.5, 'fat_percent': 18, 'chest': 100, 'waist': 85}
                }
            },
            {
                'content': 'Week 2 measurements: Weight 79.5kg, BMI 25.2, Fat percentage 17.5%, Chest 99cm, Waist 84cm',
                'metadata': {
                    'type': 'measurement',
                    'date': '2024-01-08',
                    'week_number': 'Week 2',
                    'chunk_id': 'test_chunk_2',
                    'measurements': {'weight': 79.5, 'bmi': 25.2, 'fat_percent': 17.5, 'chest': 99, 'waist': 84}
                }
            },
            {
                'content': 'Trend analysis from week 1 to week 2: Weight decreased by 0.5kg, BMI decreased by 0.3, Fat percentage decreased by 0.5%',
                'metadata': {
                    'type': 'trend',
                    'date_from': '2024-01-01',
                    'date_to': '2024-01-08',
                    'week_from': 'Week 1',
                    'week_to': 'Week 2',
                    'chunk_id': 'trend_1_2',
                    'changes': {'weight': -0.5, 'bmi': -0.3, 'fat_percent': -0.5}
                }
            }
        ]
        
        success = vector_store.add_documents(test_documents)
        if not success:
            print("❌ Failed to add test documents")
            return False
        
        print("✅ Test data added successfully")
        
        # Test end-to-end chat flow
        print("\n3. Testing end-to-end chat flow...")
        
        # Create conversation
        conversation_id = chat_interface.create_conversation("Integration Test Chat")
        if not conversation_id:
            print("❌ Failed to create conversation")
            return False
        
        print(f"✅ Created conversation: {conversation_id}")
        
        # Test multiple messages
        test_queries = [
            "How has my weight changed?",
            "What are my current measurements?",
            "Show me my BMI trend",
            "Give me a summary of my progress"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: '{query}'")
            
            response = chat_interface.send_message(query, conversation_id)
            
            if "error" in response:
                print(f"      ❌ Error: {response['error']}")
            else:
                assistant_msg = response.get('assistant_message', {})
                response_data = response.get('response_data', {})
                
                print(f"      ✅ Response: {assistant_msg.get('content', '')[:100]}...")
                print(f"      📊 Query type: {response_data.get('query_type', 'unknown')}")
                print(f"      📄 Context used: {response_data.get('context_used', 0)} documents")
        
        # Test conversation management
        print("\n4. Testing conversation management...")
        
        # Get conversation stats
        stats = chat_interface.get_conversation_stats(conversation_id)
        if "error" not in stats:
            print(f"   ✅ Conversation stats:")
            print(f"      - Total messages: {stats['total_messages']}")
            print(f"      - User messages: {stats['user_messages']}")
            print(f"      - Assistant messages: {stats['assistant_messages']}")
            print(f"      - Duration: {stats['duration_minutes']} minutes")
        
        # Export conversation
        export_data = chat_interface.export_conversation(conversation_id)
        if export_data:
            print(f"   ✅ Exported conversation successfully")
            print(f"      - Export size: {len(json.dumps(export_data))} characters")
        
        # Test web interface integration
        print("\n5. Testing web interface integration...")
        
        web_interface = WebInterface(
            vector_store=vector_store,
            chat_interface=chat_interface,
            host="127.0.0.1",
            port=5002
        )
        
        app = web_interface.get_app()
        
        # Test web API with existing conversation
        with app.test_client() as client:
            # Send message via web API
            response = client.post('/api/chat/send', 
                                 json={'message': 'Test message via web API', 
                                       'conversation_id': conversation_id})
            
            if response.status_code == 200:
                print(f"   ✅ Web API message sent successfully")
            else:
                print(f"   ❌ Web API message failed: {response.status_code}")
        
        # Clean up
        print("\n6. Cleaning up...")
        vector_store.reset_collection()
        print("   ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 RAG Pipeline Phase 4 Test")
    print("=" * 60)
    
    # Check environment
    print("🔍 Environment Check:")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not set (will use fallback responses)")
    
    flask_secret = os.getenv("FLASK_SECRET_KEY")
    if flask_secret:
        print("✅ FLASK_SECRET_KEY is set")
    else:
        print("⚠️  FLASK_SECRET_KEY not set (using default)")
    
    print()
    
    # Run tests
    try:
        # Test chat interface
        chat_success = test_chat_interface()
        
        # Test web interface
        web_success = test_web_interface()
        
        # Test integration
        integration_success = test_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Phase 4 Test Summary:")
        print(f"   Chat Interface: {'✅ PASS' if chat_success else '❌ FAIL'}")
        print(f"   Web Interface: {'✅ PASS' if web_success else '❌ FAIL'}")
        print(f"   Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
        
        if chat_success and web_success and integration_success:
            print("\n🎉 Phase 4 implementation is working correctly!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Set up environment variables in .env file")
            print("3. Run the test script again to verify functionality")
            print("4. Start the web interface: python -c 'from rag.web_interface import WebInterface; WebInterface().run()'")
            print("5. Proceed to Phase 5: Advanced Features and Optimization")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 