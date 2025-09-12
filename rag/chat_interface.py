"""
Chat Interface Module for RAG Pipeline
Handles conversation management and chat functionality
"""

import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from .query_processor import QueryProcessor
from .retriever import Retriever
from .generator import ResponseGenerator
from .vector_store import VectorStore


@dataclass
class Message:
    """Represents a chat message"""
    id: str
    content: str
    sender: str  # 'user' or 'assistant'
    timestamp: datetime
    message_type: str  # 'text', 'error', 'system'
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class Conversation:
    """Represents a chat conversation"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Message]
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['messages'] = [msg.to_dict() for msg in self.messages]
        return data


class ChatInterface:
    """Manages chat conversations and interactions"""
    
    def __init__(self, vector_store: VectorStore, 
                 query_processor: QueryProcessor = None,
                 retriever: Retriever = None,
                 generator: ResponseGenerator = None):
        """
        Initialize chat interface
        
        Args:
            vector_store: Vector store instance
            query_processor: Query processor instance (optional)
            retriever: Retriever instance (optional)
            generator: Response generator instance (optional)
        """
        self.vector_store = vector_store
        self.query_processor = query_processor or QueryProcessor()
        self.retriever = retriever or Retriever(vector_store, query_processor)
        self.generator = generator or ResponseGenerator()
        
        # Conversation storage
        self.conversations: Dict[str, Conversation] = {}
        self.active_conversation_id: Optional[str] = None
    
    def create_conversation(self, title: str = None) -> str:
        """
        Create a new conversation with welcome message
        
        Args:
            title: Optional conversation title
            
        Returns:
            Conversation ID
        """
        try:
            conversation_id = str(uuid.uuid4())
            
            if not title:
                title = f"Fitness Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            conversation = Conversation(
                id=conversation_id,
                title=title,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                messages=[],
                metadata={}
            )
            
            # Add welcome message
            welcome_message = Message(
                id=str(uuid.uuid4()),
                content="Hello, Welcome to the world of Fitness Information for Charles Parmar. You can ask me questions about his fitness reports and I will happily provide answers to you.",
                sender="assistant",
                timestamp=datetime.now(),
                message_type="system",
                metadata={"is_welcome": True}
            )
            
            conversation.messages.append(welcome_message)
            
            # Store conversation
            self.conversations[conversation_id] = conversation
            self.active_conversation_id = conversation_id
            
            return conversation_id
            self.active_conversation_id = conversation_id
            
            print(f"✅ Created new conversation: {title}")
            return conversation_id
            
        except Exception as e:
            print(f"❌ Error creating conversation: {e}")
            return None
    
    def send_message(self, message: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Send a message and get response
        
        Args:
            message: User message
            conversation_id: Conversation ID (uses active if not provided)
            
        Returns:
            Response dictionary
        """
        try:
            # Get or create conversation
            if not conversation_id:
                conversation_id = self.active_conversation_id
                
            if not conversation_id:
                conversation_id = self.create_conversation()
                if not conversation_id:
                    return {"error": "Failed to create conversation"}
            
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                return {"error": "Conversation not found"}
            
            # Add user message
            user_message = Message(
                id=str(uuid.uuid4()),
                content=message,
                sender="user",
                timestamp=datetime.now(),
                message_type="text"
            )
            conversation.messages.append(user_message)
            
            # Process message and generate response
            response_data = self._process_message(message, conversation)
            
            # Add assistant response
            assistant_message = Message(
                id=str(uuid.uuid4()),
                content=response_data.get("response", "Sorry, I couldn't process your request."),
                sender="assistant",
                timestamp=datetime.now(),
                message_type="text",
                metadata=response_data
            )
            conversation.messages.append(assistant_message)
            
            # Update conversation
            conversation.updated_at = datetime.now()
            
            return {
                "conversation_id": conversation_id,
                "user_message": user_message.to_dict(),
                "assistant_message": assistant_message.to_dict(),
                "response_data": response_data
            }
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return {"error": str(e)}
    
    def _process_message(self, message: str, conversation: Conversation) -> Dict[str, Any]:
        """
        Process a message and generate response
        
        Args:
            message: User message
            conversation: Current conversation
            
        Returns:
            Response data
        """
        try:
            # Check for special commands
            if message.lower().startswith("/help"):
                return self.generator.generate_help_response()
            
            if message.lower().startswith("/summary"):
                # Get context for summary
                context = self.retriever.retrieve("summary", n_results=10)
                return self.generator.generate_summary_response(context)
            
            if message.lower().startswith("/new"):
                # Create new conversation
                new_id = self.create_conversation()
                return {
                    "response": f"Created new conversation. You can continue chatting here or switch to the new conversation.",
                    "new_conversation_id": new_id
                }
            
            # Process regular query
            # Step 1: Process query
            processed_query = self.query_processor.process_query(message)
            
            if "error" in processed_query:
                return self.generator._generate_error_response(message, processed_query["error"])
            
            # Step 2: Retrieve context
            context = self.retriever.retrieve(message, n_results=5)
            
            # Step 3: Generate response
            query_type = processed_query.get("query_type", "general")
            response = self.generator.generate_response(message, context, query_type)
            
            return response
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return self.generator._generate_error_response(message, str(e))
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation object or None
        """
        return self.conversations.get(conversation_id)
    
    def get_active_conversation(self) -> Optional[Conversation]:
        """
        Get the active conversation
        
        Returns:
            Active conversation or None
        """
        if self.active_conversation_id:
            return self.conversations.get(self.active_conversation_id)
        return None
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all conversations
        
        Returns:
            List of conversation summaries
        """
        try:
            conversations = []
            
            for conv_id, conversation in self.conversations.items():
                # Get last message for preview
                last_message = conversation.messages[-1].content if conversation.messages else "No messages"
                
                conv_summary = {
                    "id": conv_id,
                    "title": conversation.title,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                    "message_count": len(conversation.messages),
                    "last_message": last_message[:100] + "..." if len(last_message) > 100 else last_message,
                    "is_active": conv_id == self.active_conversation_id
                }
                
                conversations.append(conv_summary)
            
            # Sort by updated_at (most recent first)
            conversations.sort(key=lambda x: x["updated_at"], reverse=True)
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error listing conversations: {e}")
            return []
    
    def switch_conversation(self, conversation_id: str) -> bool:
        """
        Switch to a different conversation
        
        Args:
            conversation_id: Conversation ID to switch to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if conversation_id in self.conversations:
                self.active_conversation_id = conversation_id
                print(f"✅ Switched to conversation: {self.conversations[conversation_id].title}")
                return True
            else:
                print(f"❌ Conversation not found: {conversation_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error switching conversation: {e}")
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation
        
        Args:
            conversation_id: Conversation ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if conversation_id in self.conversations:
                deleted_conv = self.conversations.pop(conversation_id)
                
                # If this was the active conversation, clear it
                if conversation_id == self.active_conversation_id:
                    self.active_conversation_id = None
                    # Set another conversation as active if available
                    if self.conversations:
                        self.active_conversation_id = next(iter(self.conversations))
                
                print(f"✅ Deleted conversation: {deleted_conv.title}")
                return True
            else:
                print(f"❌ Conversation not found: {conversation_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting conversation: {e}")
            return False
    
    def rename_conversation(self, conversation_id: str, new_title: str) -> bool:
        """
        Rename a conversation
        
        Args:
            conversation_id: Conversation ID
            new_title: New title
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if conversation_id in self.conversations:
                self.conversations[conversation_id].title = new_title
                self.conversations[conversation_id].updated_at = datetime.now()
                print(f"✅ Renamed conversation to: {new_title}")
                return True
            else:
                print(f"❌ Conversation not found: {conversation_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error renaming conversation: {e}")
            return False
    
    def export_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Export a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Exported conversation data or None
        """
        try:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                return None
            
            export_data = {
                "conversation": conversation.to_dict(),
                "exported_at": datetime.now().isoformat(),
                "export_format": "json"
            }
            
            return export_data
            
        except Exception as e:
            print(f"❌ Error exporting conversation: {e}")
            return None
    
    def get_conversation_stats(self, conversation_id: str = None) -> Dict[str, Any]:
        """
        Get conversation statistics
        
        Args:
            conversation_id: Conversation ID (uses active if not provided)
            
        Returns:
            Statistics dictionary
        """
        try:
            if not conversation_id:
                conversation_id = self.active_conversation_id
            
            if not conversation_id or conversation_id not in self.conversations:
                return {"error": "No active conversation"}
            
            conversation = self.conversations[conversation_id]
            
            # Calculate statistics
            user_messages = [msg for msg in conversation.messages if msg.sender == "user"]
            assistant_messages = [msg for msg in conversation.messages if msg.sender == "assistant"]
            
            total_chars = sum(len(msg.content) for msg in conversation.messages)
            avg_message_length = total_chars / len(conversation.messages) if conversation.messages else 0
            
            stats = {
                "conversation_id": conversation_id,
                "title": conversation.title,
                "total_messages": len(conversation.messages),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "total_characters": total_chars,
                "average_message_length": round(avg_message_length, 2),
                "duration_minutes": round((conversation.updated_at - conversation.created_at).total_seconds() / 60, 2),
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat()
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting conversation stats: {e}")
            return {"error": str(e)}
    
    def clear_conversations(self) -> bool:
        """
        Clear all conversations
        
        Returns:
            True if successful, False otherwise
        """
        try:
            count = len(self.conversations)
            self.conversations.clear()
            self.active_conversation_id = None
            print(f"✅ Cleared {count} conversations")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing conversations: {e}")
            return False
    
    def get_chat_interface_info(self) -> Dict[str, Any]:
        """
        Get information about the chat interface
        
        Returns:
            Interface information
        """
        try:
            return {
                "total_conversations": len(self.conversations),
                "active_conversation_id": self.active_conversation_id,
                "components": {
                    "vector_store": self.vector_store is not None,
                    "query_processor": self.query_processor is not None,
                    "retriever": self.retriever is not None,
                    "generator": self.generator is not None
                },
                "available_commands": [
                    "/help - Get help information",
                    "/summary - Get fitness data summary",
                    "/new - Create new conversation",
                    "/list - List all conversations",
                    "/switch <id> - Switch to conversation",
                    "/delete <id> - Delete conversation",
                    "/rename <id> <title> - Rename conversation",
                    "/export <id> - Export conversation",
                    "/stats - Get conversation statistics",
                    "/clear - Clear all conversations"
                ]
            }
            
        except Exception as e:
            print(f"❌ Error getting chat interface info: {e}")
            return {"error": str(e)} 