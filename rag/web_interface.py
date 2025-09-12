"""
Web Interface Module for RAG Pipeline
Flask-based web application for chat interface
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from .chat_interface import ChatInterface
from .vector_store import VectorStore
from .query_processor import QueryProcessor
from .retriever import Retriever
from .generator import ResponseGenerator


class WebInterface:
    """Flask web application for RAG chat interface"""
    
    def __init__(self, vector_store: VectorStore = None, 
                 chat_interface: ChatInterface = None,
                 host: str = "0.0.0.0", port: int = 8080):
        """
        Initialize web interface
        
        Args:
            vector_store: Vector store instance (optional)
            chat_interface: Chat interface instance (optional)
            host: Host to bind to
            port: Port to bind to
        """
        self.host = host
        self.port = port
        
        # Initialize components
        if not vector_store:
            vector_store = VectorStore()
        
        if not chat_interface:
            query_processor = QueryProcessor()
            retriever = Retriever(vector_store, query_processor)
            generator = ResponseGenerator()
            chat_interface = ChatInterface(vector_store, query_processor, retriever, generator)
        
        self.vector_store = vector_store
        self.chat_interface = chat_interface
        
        # Initialize Flask app
        self.app = Flask(__name__, 
                        template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
                        static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
        self.app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Register routes
        self._register_routes()
        self._register_socket_events()
        
        # Create templates if they don't exist
        self.create_templates()
    
    def _register_routes(self):
        """Register Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main chat interface page"""
            try:
                return render_template('chat.html')
            except Exception as e:
                print(f"❌ Template error: {e}")
                print(f"📁 Current working directory: {os.getcwd()}")
                print(f"📁 Template folder: {self.app.template_folder}")
                print(f"📁 Template exists: {os.path.exists(os.path.join(self.app.template_folder, 'chat.html'))}")
                return f"Template error: {e}", 500
        
        @self.app.route('/api/chat/send', methods=['POST'])
        def send_message():
            """Send a message via REST API"""
            try:
                data = request.get_json()
                message = data.get('message', '').strip()
                conversation_id = data.get('conversation_id')
                
                if not message:
                    return jsonify({"error": "Message cannot be empty"}), 400
                
                # Send message
                response = self.chat_interface.send_message(message, conversation_id)
                
                if "error" in response:
                    return jsonify(response), 400
                
                return jsonify(response)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/conversations', methods=['GET'])
        def list_conversations():
            """List all conversations"""
            try:
                conversations = self.chat_interface.list_conversations()
                return jsonify({"conversations": conversations})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/conversations/<conversation_id>', methods=['GET'])
        def get_conversation(conversation_id):
            """Get a specific conversation"""
            try:
                conversation = self.chat_interface.get_conversation(conversation_id)
                if not conversation:
                    return jsonify({"error": "Conversation not found"}), 404
                
                return jsonify(conversation.to_dict())
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/conversations', methods=['POST'])
        def create_conversation():
            """Create a new conversation"""
            try:
                data = request.get_json()
                title = data.get('title')
                
                conversation_id = self.chat_interface.create_conversation(title)
                
                if not conversation_id:
                    return jsonify({"error": "Failed to create conversation"}), 500
                
                return jsonify({
                    "conversation_id": conversation_id,
                    "message": "Conversation created successfully"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/conversations/<conversation_id>', methods=['DELETE'])
        def delete_conversation(conversation_id):
            """Delete a conversation"""
            try:
                success = self.chat_interface.delete_conversation(conversation_id)
                
                if not success:
                    return jsonify({"error": "Failed to delete conversation"}), 400
                
                return jsonify({"message": "Conversation deleted successfully"})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/conversations/<conversation_id>/rename', methods=['PUT'])
        def rename_conversation(conversation_id):
            """Rename a conversation"""
            try:
                data = request.get_json()
                new_title = data.get('title', '').strip()
                
                if not new_title:
                    return jsonify({"error": "Title cannot be empty"}), 400
                
                success = self.chat_interface.rename_conversation(conversation_id, new_title)
                
                if not success:
                    return jsonify({"error": "Failed to rename conversation"}), 400
                
                return jsonify({"message": "Conversation renamed successfully"})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/conversations/<conversation_id>/export', methods=['GET'])
        def export_conversation(conversation_id):
            """Export a conversation"""
            try:
                export_data = self.chat_interface.export_conversation(conversation_id)
                
                if not export_data:
                    return jsonify({"error": "Failed to export conversation"}), 400
                
                return jsonify(export_data)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/conversations/<conversation_id>/stats', methods=['GET'])
        def get_conversation_stats(conversation_id):
            """Get conversation statistics"""
            try:
                stats = self.chat_interface.get_conversation_stats(conversation_id)
                
                if "error" in stats:
                    return jsonify(stats), 400
                
                return jsonify(stats)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/switch/<conversation_id>', methods=['POST'])
        def switch_conversation(conversation_id):
            """Switch to a different conversation"""
            try:
                success = self.chat_interface.switch_conversation(conversation_id)
                
                if not success:
                    return jsonify({"error": "Failed to switch conversation"}), 400
                
                return jsonify({"message": "Switched conversation successfully"})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/chat/clear', methods=['DELETE'])
        def clear_conversations():
            """Clear all conversations"""
            try:
                success = self.chat_interface.clear_conversations()
                
                if not success:
                    return jsonify({"error": "Failed to clear conversations"}), 500
                
                return jsonify({"message": "All conversations cleared successfully"})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/system/info', methods=['GET'])
        def get_system_info():
            """Get system information"""
            try:
                chat_info = self.chat_interface.get_chat_interface_info()
                vector_info = self.vector_store.get_collection_info()
                data_context = self._get_data_context()
                
                return jsonify({
                    "chat_interface": chat_info,
                    "vector_store": vector_info,
                    "data_context": data_context,
                    "server_time": datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/system/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            try:
                return jsonify({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "components": {
                        "vector_store": self.vector_store is not None,
                        "chat_interface": self.chat_interface is not None
                    }
                })
                
            except Exception as e:
                return jsonify({
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }), 500
    
    def _register_socket_events(self):
        """Register Socket.IO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            print(f"Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to fitness chat server'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('join_conversation')
        def handle_join_conversation(data):
            """Join a conversation room"""
            conversation_id = data.get('conversation_id')
            if conversation_id:
                join_room(conversation_id)
                emit('joined_conversation', {'conversation_id': conversation_id})
        
        @self.socketio.on('leave_conversation')
        def handle_leave_conversation(data):
            """Leave a conversation room"""
            conversation_id = data.get('conversation_id')
            if conversation_id:
                leave_room(conversation_id)
                emit('left_conversation', {'conversation_id': conversation_id})
        
        @self.socketio.on('send_message')
        def handle_send_message(data):
            """Handle real-time message sending"""
            try:
                message = data.get('message', '').strip()
                conversation_id = data.get('conversation_id')
                
                if not message:
                    emit('error', {'error': 'Message cannot be empty'})
                    return
                
                # Send message
                response = self.chat_interface.send_message(message, conversation_id)
                
                if "error" in response:
                    emit('error', response)
                else:
                    # Emit to the conversation room
                    if conversation_id:
                        emit('message_received', response, room=conversation_id)
                    else:
                        emit('message_received', response)
                
            except Exception as e:
                emit('error', {'error': str(e)})
        
        @self.socketio.on('typing_start')
        def handle_typing_start(data):
            """Handle typing indicator start"""
            conversation_id = data.get('conversation_id')
            if conversation_id:
                emit('user_typing', {'user_id': request.sid}, room=conversation_id, include_self=False)
        
        @self.socketio.on('typing_stop')
        def handle_typing_stop(data):
            """Handle typing indicator stop"""
            conversation_id = data.get('conversation_id')
            if conversation_id:
                emit('user_stopped_typing', {'user_id': request.sid}, room=conversation_id, include_self=False)
    
    def _get_data_context(self) -> Dict[str, Any]:
        """
        Get data context information for display
        
        Returns:
            Data context information
        """
        try:
            # Get collection info
            collection_info = self.vector_store.get_collection_info()
            
            # Get sample data for analysis
            sample_data = []
            try:
                # Get a few sample documents to analyze
                sample_results = self.chat_interface.retriever.retrieve("fitness data", n_results=10)
                if sample_results:
                    # Extract fitness data from sample results
                    from .utils.calculations import FitnessCalculations
                    calculations = FitnessCalculations()
                    
                    fitness_data = []
                    for result in sample_results:
                        if 'content' in result:
                            # Try to extract structured data
                            extracted = self._extract_fitness_data_from_content(result['content'])
                            if extracted:
                                fitness_data.append(extracted)
                    
                    if fitness_data:
                        # Perform basic analytics
                        validation_result = calculations.validate_data_consistency(fitness_data)
                        total_loss_result = calculations.calculate_total_weight_loss(fitness_data)
                        weeks_count = calculations.count_actual_weeks_of_data(fitness_data)
                        
                        data_context = {
                            "total_records": collection_info.get('count', 0),
                            "data_quality": {
                                "valid": validation_result.get('valid', False),
                                "issues": validation_result.get('issues', []),
                                "warnings": validation_result.get('warnings', [])
                            },
                            "analytics_summary": {
                                "total_weight_loss": total_loss_result.value if total_loss_result else 0,
                                "weeks_of_data": weeks_count,
                                "date_range": validation_result.get('date_range', {}),
                                "confidence": total_loss_result.confidence if total_loss_result else 0
                            },
                            "available_measurements": self._get_available_measurements(fitness_data),
                            "system_capabilities": [
                                "Weight loss calculations and analysis",
                                "Time-based query processing",
                                "Data validation and consistency checks",
                                "Trend analysis and insights",
                                "Date range filtering",
                                "Statistical calculations"
                            ],
                            "query_examples": [
                                "What is my current weight?",
                                "How much weight have I lost in total?",
                                "Show me my weight loss until end of June",
                                "How many weeks of data do I have?",
                                "What was my weight on 2024-01-15?",
                                "Calculate my average weight loss per week"
                            ]
                        }
                    else:
                        data_context = {
                            "total_records": collection_info.get('count', 0),
                            "data_quality": {"valid": False, "issues": ["No structured fitness data found"]},
                            "analytics_summary": {},
                            "available_measurements": [],
                            "system_capabilities": [
                                "Weight loss calculations and analysis",
                                "Time-based query processing",
                                "Data validation and consistency checks",
                                "Trend analysis and insights",
                                "Date range filtering",
                                "Statistical calculations"
                            ],
                            "query_examples": [
                                "What is my current weight?",
                                "How much weight have I lost in total?",
                                "Show me my weight loss until end of June",
                                "How many weeks of data do I have?",
                                "What was my weight on 2024-01-15?",
                                "Calculate my average weight loss per week"
                            ]
                        }
                else:
                    data_context = {
                        "total_records": collection_info.get('count', 0),
                        "data_quality": {"valid": False, "issues": ["No data available"]},
                        "analytics_summary": {},
                        "available_measurements": [],
                        "system_capabilities": [
                            "Weight loss calculations and analysis",
                            "Time-based query processing",
                            "Data validation and consistency checks",
                            "Trend analysis and insights",
                            "Date range filtering",
                            "Statistical calculations"
                        ],
                        "query_examples": [
                            "What is my current weight?",
                            "How much weight have I lost in total?",
                            "Show me my weight loss until end of June",
                            "How many weeks of data do I have?",
                            "What was my weight on 2024-01-15?",
                            "Calculate my average weight loss per week"
                        ]
                    }
            except Exception as e:
                print(f"Error analyzing data context: {e}")
                data_context = {
                    "total_records": collection_info.get('count', 0),
                    "data_quality": {"valid": False, "issues": [f"Analysis error: {str(e)}"]},
                    "analytics_summary": {},
                    "available_measurements": [],
                    "system_capabilities": [
                        "Weight loss calculations and analysis",
                        "Time-based query processing",
                        "Data validation and consistency checks",
                        "Trend analysis and insights",
                        "Date range filtering",
                        "Statistical calculations"
                    ],
                    "query_examples": [
                        "What is my current weight?",
                        "How much weight have I lost in total?",
                        "Show me my weight loss until end of June",
                        "How many weeks of data do I have?",
                        "What was my weight on 2024-01-15?",
                        "Calculate my average weight loss per week"
                    ]
                }
            
            return data_context
            
        except Exception as e:
            print(f"Error getting data context: {e}")
            return {
                "error": str(e),
                "system_capabilities": [
                    "Weight loss calculations and analysis",
                    "Time-based query processing",
                    "Data validation and consistency checks",
                    "Trend analysis and insights",
                    "Date range filtering",
                    "Statistical calculations"
                ],
                "query_examples": [
                    "What is my current weight?",
                    "How much weight have I lost in total?",
                    "Show me my weight loss until end of June",
                    "How many weeks of data do I have?",
                    "What was my weight on 2024-01-15?",
                    "Calculate my average weight loss per week"
                ]
            }
    
    def _extract_fitness_data_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract fitness data from content string
        
        Args:
            content: Content string
            
        Returns:
            Extracted fitness data or None
        """
        try:
            import re
            from datetime import datetime
            
            # Look for date patterns
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            date_match = re.search(date_pattern, content)
            
            if not date_match:
                return None
            
            date_str = date_match.group(1)
            
            # Look for weight patterns
            weight_pattern = r'weight[:\s]*(\d+\.?\d*)'
            weight_match = re.search(weight_pattern, content, re.IGNORECASE)
            
            data = {'date': date_str}
            
            if weight_match:
                data['weight'] = float(weight_match.group(1))
            
            # Look for other measurements
            measurements = ['bmi', 'fat_percent', 'chest', 'waist', 'arms', 'legs']
            for measurement in measurements:
                pattern = rf'{measurement}[:\s]*(\d+\.?\d*)'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    data[measurement] = float(match.group(1))
            
            return data if len(data) > 1 else None  # Must have at least date and one measurement
            
        except Exception as e:
            print(f"Error extracting fitness data: {e}")
            return None
    
    def _get_available_measurements(self, fitness_data: List[Dict[str, Any]]) -> List[str]:
        """
        Get list of available measurements from fitness data
        
        Args:
            fitness_data: List of fitness measurements
            
        Returns:
            List of available measurement types
        """
        try:
            if not fitness_data:
                return []
            
            available_measurements = set()
            
            for record in fitness_data:
                for key in record.keys():
                    if key != 'date':
                        available_measurements.add(key)
            
            return list(available_measurements)
            
        except Exception as e:
            print(f"Error getting available measurements: {e}")
            return []

    def create_templates(self):
        """Create basic HTML templates"""
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create chat.html template
        chat_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fitness Data Chat</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-header {
            background: #007bff;
            color: white;
            padding: 15px;
            text-align: center;
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 15px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .message.user {
            background: #e3f2fd;
            margin-left: 20%;
        }
        .message.assistant {
            background: #f5f5f5;
            margin-right: 20%;
        }
        .message-input {
            display: flex;
            padding: 15px;
            border-top: 1px solid #eee;
        }
        .message-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-right: 10px;
        }
        .message-input button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .message-input button:hover {
            background: #0056b3;
        }
        .typing-indicator {
            color: #666;
            font-style: italic;
            padding: 5px 15px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>Fitness Data Assistant</h2>
            <p>Ask me anything about your fitness data!</p>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message assistant">
                <strong>Assistant:</strong> Hello! I'm your fitness data assistant. I can help you analyze your fitness measurements, track trends, and provide insights. Try asking me questions like:
                <ul>
                    <li>"How has my weight changed?"</li>
                    <li>"Show me my BMI trends"</li>
                    <li>"Give me a summary of my progress"</li>
                    <li>"What are my current measurements?"</li>
                </ul>
            </div>
        </div>
        <div class="typing-indicator" id="typing" style="display: none;">
            Assistant is typing...
        </div>
        <div class="message-input">
            <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const socket = io();
        const messagesDiv = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const typingDiv = document.getElementById('typing');

        socket.on('connected', function(data) {
            console.log('Connected to server');
        });

        socket.on('message_received', function(data) {
            addMessage('assistant', data.assistant_message.content);
        });

        socket.on('user_typing', function(data) {
            typingDiv.style.display = 'block';
        });

        socket.on('user_stopped_typing', function(data) {
            typingDiv.style.display = 'none';
        });

        socket.on('error', function(data) {
            addMessage('assistant', 'Error: ' + data.error);
        });

        function sendMessage() {
            const message = messageInput.value.trim();
            if (message) {
                addMessage('user', message);
                socket.emit('send_message', {message: message});
                messageInput.value = '';
            }
        }

        function addMessage(sender, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'Assistant'}:</strong> ${content}`;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Typing indicator
        let typingTimer;
        messageInput.addEventListener('input', function() {
            socket.emit('typing_start', {});
            clearTimeout(typingTimer);
            typingTimer = setTimeout(function() {
                socket.emit('typing_stop', {});
            }, 1000);
        });
    </script>
</body>
</html>'''
        
        with open(os.path.join(templates_dir, 'chat.html'), 'w') as f:
            f.write(chat_template)
        
        print(f"✅ Created templates in {templates_dir}")
    
    def run(self, debug: bool = False):
        """
        Run the web interface
        
        Args:
            debug: Enable debug mode
        """
        try:
            # Create templates if they don't exist
            self.create_templates()
            
            print(f"🚀 Starting Fitness Chat Web Interface")
            print(f"📍 URL: http://{self.host}:{self.port}")
            print(f"🔧 Debug mode: {debug}")
            
            # Run the application
            self.socketio.run(self.app, host=self.host, port=self.port, debug=debug)
            
        except Exception as e:
            print(f"❌ Error starting web interface: {e}")
    
    def get_app(self):
        """Get the Flask app instance"""
        return self.app
    
    def get_socketio(self):
        """Get the SocketIO instance"""
        return self.socketio 