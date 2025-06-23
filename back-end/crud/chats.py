from utils.helper import execute_fetch_query, execute_insert_or_update_query
from datetime import datetime
import uuid
import json

class ChatCrud:
    def get_chats_by_id(self, conversation_id: str):
        try:
        # fetching chat history from a database
            query = "SELECT * FROM chats WHERE conversation_id = ? order by updated_at"
            params = (conversation_id,)
            result = execute_fetch_query(query, params)
            if not result:
                return []
            return result
        except Exception as e:
            raise ValueError(f"Error fetching chats for conversation {conversation_id}: {str(e)}")

    def add_chat(self, conversation_id: str, message: str, response: str):
        # adding a chat to a database
        try:
            chat_id = str(uuid.uuid4())
            query = "INSERT INTO chats (id, conversation_id, content, updated_at) VALUES (?, ?, ?, ?)"
            params = (chat_id, conversation_id, json.dumps({"HumanMessage": message, "AIResponse": response}), datetime.now())
            if execute_insert_or_update_query(query, params):
                return True
            return False
        except Exception as e:
            raise ValueError(f"Error adding chat for conversation {conversation_id}: {str(e)}")
    
    def get_user_id_by_conversation_id(self, conversation_id: str):
        # fetching user ID by conversation ID from a database
        try:
            query = "SELECT user_id FROM conversations WHERE id = ?"
            params = (conversation_id,)
            result = execute_fetch_query(query, params)
            if not result:
                raise ValueError(f"No user found for conversation ID {conversation_id}")
            return result[0][0]
        except Exception as e:
            raise ValueError(f"Error fetching user ID for conversation {conversation_id}: {str(e)}")
    
    def update_conversation_name(self, conversation_id, conversation_name):
        # updating conversation name in a database
        try:
            query = "UPDATE conversations SET title = ? WHERE id = ?"
            params = (conversation_name, conversation_id)
            if execute_insert_or_update_query(query, params):
                return True
            return False
        except Exception as e:
            raise ValueError(f"Error updating conversation name for {conversation_id}: {str(e)}")