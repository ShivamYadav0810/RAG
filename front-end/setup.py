import streamlit as st
import requests
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import time
import sseclient  # pip install sseclient-py

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your actual API URL

class ChatbotAPI:
    """API client for the chatbot backend"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health/health-check")
            return response.status_code == 200
        except:
            return False
    
    def login_user(self, user_data: Dict) -> Optional[Dict]:
        """Login or create a user"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/users/login",
                json=user_data
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return None
    
    def get_conversations(self, user_id: str) -> Optional[List]:
        """Get all conversations for a user"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/conversations/all-conversations",
                params={"user_id": user_id}
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.error(f"Error fetching conversations: {str(e)}")
            return []
    
    def create_conversation(self, user_id: str) -> bool:
        """Create a new conversation"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/conversations/new-conversation",
                params={"user_id": user_id}
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error creating conversation: {str(e)}")
            return False
    
    def get_chats(self, conversation_id: str) -> Optional[List]:
        """Get all chats in a conversation"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/chat/all-chats",
                params={"conversation_id": conversation_id}
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.error(f"Error fetching chats: {str(e)}")
            return []
    
    def send_message_stream(self, conversation_id: str, message: str):
        """Send a message and get streaming response"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/chat/new-chat-stream",
                params={"conversation_id": conversation_id, "message": message},
                stream=True,
                headers={"Accept": "text/event-stream"}
            )
            
            if response.status_code == 200:
                client = sseclient.SSEClient(response)
                for event in client.events():
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            yield data
                        except json.JSONDecodeError:
                            continue
            else:
                yield {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            yield {"error": f"Error sending message: {str(e)}"}
    
    def send_message(self, conversation_id: str, message: str) -> Optional[str]:
        """Send a message and get response (non-streaming fallback)"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/chat/new-chat",
                params={"conversation_id": conversation_id, "message": message}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Error sending message: {str(e)}")
            return None
    
    def upload_file(self, user_id: str, file) -> bool:
        """Upload a file"""
        try:
            files = {"file": (file.name, file, file.type)}
            response = requests.post(
                f"{self.base_url}/api/v1/uploads/file-upload",
                params={"user_id": user_id},
                files=files
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
            return False
    
    def get_files(self, user_id: str) -> Optional[List]:
        """Get all files for a user"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/uploads/files",
                params={"user_id": user_id}
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.error(f"Error fetching files: {str(e)}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/uploads/file/{file_id}"
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error deleting file: {str(e)}")
            return False

def initialize_session_state():
    """Initialize session state variables"""
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None 
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "api_client" not in st.session_state:
        st.session_state.api_client = ChatbotAPI(API_BASE_URL)
    if "streaming_enabled" not in st.session_state:
        st.session_state.streaming_enabled = True

def login_page():
    """Display login page"""
    st.title("🤖 Chatbot Login")
    
    # Check API health
    if not st.session_state.api_client.health_check():
        st.error("⚠️ API is not available. Please check if the backend is running.")
        st.info(f"Expected API URL: {API_BASE_URL}")
        return
    
    st.success("✅ API is healthy and ready!")
    
    with st.form("login_form"):
        st.subheader("Login or Register")
        
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", placeholder="Enter your username")
        
        with col2:
            email = st.text_input("Email", placeholder="your.email@example.com")
        
        submit_button = st.form_submit_button("Login / Register")
        
        if submit_button and username and email:
            user_data = {
                "id": "",
                "username": username,
                "email": email if email else None
            }
            
            with st.spinner("Logging in..."):
                result = st.session_state.api_client.login_user(user_data)
                
                if result:
                    st.session_state.username = username
                    st.session_state.user_id = result.get("user_id")
                    st.success(f"Welcome, {username}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Login failed. Please try again.")

def sidebar():
    """Display sidebar with conversations and file management"""
    with st.sidebar:
        st.title("💬 Conversations")
        
        # User info
        if st.session_state.user_id:
            st.info(f"👤 {st.session_state.username}")
            
            # Streaming toggle
            st.session_state.streaming_enabled = st.checkbox(
                "🔄 Enable Streaming", 
                value=st.session_state.streaming_enabled,
                help="Enable real-time streaming responses"
            )
            
            if st.button("🚪 Logout"):
                st.session_state.user_id = None
                st.session_state.conversation_id = None
                st.rerun()
        
        st.divider()
        
        # New conversation button
        if st.button("➕ New Conversation"):
            user_id = st.session_state.user_id
            if st.session_state.api_client.create_conversation(user_id):
                st.success("New conversation created!")
                load_conversations()
                st.rerun()
        
        # Load and display conversations
        load_conversations()
        
        # Display conversations
        if st.session_state.conversations:
            st.subheader("Your Conversations")
            for i, conv in enumerate(st.session_state.conversations.get('conversations', [])):
                conv_id = conv[0]
                conv_title = conv[2]
                
                if st.button(f"💬 {conv_title}", key=f"conv_{conv_id}"):
                    st.session_state.current_conversation_id = conv_id
                    load_chat_history()
                    st.rerun()
        
        st.divider()
        
        # File management section
        st.subheader("📁 File Management")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload a file",
            type=['txt', 'pdf', 'doc', 'docx', 'csv', 'json', 'py', 'md']
        )
        
        if uploaded_file and st.button("Upload File"):
            user_id = st.session_state.user_id
            if st.session_state.api_client.upload_file(user_id, uploaded_file):
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                st.rerun()
        
        # Display uploaded files
        user_id = st.session_state.user_id
        files = st.session_state.api_client.get_files(user_id)
        
        if files:
            st.subheader("Your Files")
            for file in files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"📄 {file.get('file_name', 'Unknown')}")
                with col2:
                    if st.button("🗑️", key=f"delete_{file.get('id')}"):
                        if st.session_state.api_client.delete_file(file.get('id')):
                            st.success("File deleted!")
                            st.rerun()

def load_conversations():
    """Load conversations for the current user"""
    if st.session_state.user_id:
        user_id = st.session_state.user_id
        conversations = st.session_state.api_client.get_conversations(user_id)
        if conversations:
            st.session_state.conversations = conversations

def load_chat_history():
    """Load chat history for the current conversation"""
    if st.session_state.current_conversation_id:
        chats = st.session_state.api_client.get_chats(st.session_state.current_conversation_id)
        if chats:
            st.session_state.chat_history = chats.get('chats', [])

def chat_interface():
    """Display main chat interface with streaming support"""
    st.title("🤖 AI Chatbot")
    
    # Display current conversation info
    if st.session_state.current_conversation_id:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"💬 Current Conversation: {st.session_state.current_conversation_id}")
        with col2:
            streaming_status = "🔄 Streaming ON" if st.session_state.streaming_enabled else "⏸️ Streaming OFF"
            st.info(streaming_status)
    else:
        st.warning("Please select or create a conversation from the sidebar.")
        return
    
    # Chat history container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        if st.session_state.chat_history:
            for chat in st.session_state.chat_history:
                # User message
                chat = json.loads(chat[2])
                if chat.get('HumanMessage'):
                    with st.chat_message("user"):
                        st.write(chat['HumanMessage'])
                
                # Bot response
                if chat.get('AIResponse'):
                    with st.chat_message("assistant"):
                        st.write(chat['AIResponse'])
        else:
            st.info("No messages yet. Start a conversation!")
    
    # Chat input
    if message := st.chat_input("Type your message here..."):
        # Add user message to chat
        with st.chat_message("user"):
            st.write(message)
        
        # Generate response
        with st.chat_message("assistant"):
            if st.session_state.streaming_enabled:
                # Streaming response
                response_placeholder = st.empty()
                full_response = ""
                
                try:
                    for chunk in st.session_state.api_client.send_message_stream(
                        st.session_state.current_conversation_id, 
                        message
                    ):
                        if chunk.get("error"):
                            st.error(chunk["error"])
                            break
                        elif chunk.get("content"):
                            full_response += chunk["content"]
                            response_placeholder.write(full_response + "▊")  # Cursor effect
                        elif chunk.get("done"):
                            response_placeholder.write(full_response)
                            break
                    
                    # Reload chat history after completion
                    if full_response:
                        time.sleep(0.5)  # Small delay for database update
                        load_chat_history()
                        
                except Exception as e:
                    st.error(f"Streaming error: {str(e)}")
                    # Fallback to non-streaming
                    with st.spinner("Thinking..."):
                        response = st.session_state.api_client.send_message(
                            st.session_state.current_conversation_id, 
                            message
                        )
                        if response:
                            st.write(response)
                            load_chat_history()
                        else:
                            st.error("Failed to get response from the chatbot.")
            else:
                # Non-streaming response
                with st.spinner("Thinking..."):
                    response = st.session_state.api_client.send_message(
                        st.session_state.current_conversation_id, 
                        message
                    )
                    
                    if response:
                        st.write(response)
                        load_chat_history()
                    else:
                        st.error("Failed to get response from the chatbot.")

def main():
    """Main application function"""
    st.set_page_config(
        page_title="AI Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Check if user is logged in
    if not st.session_state.user_id:
        login_page()
    else:
        # Display sidebar
        sidebar()
        
        # Display main chat interface
        chat_interface()

if __name__ == "__main__":
    main()