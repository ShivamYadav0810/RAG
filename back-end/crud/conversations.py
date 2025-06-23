from utils.helper import execute_fetch_query, execute_insert_or_update_query
import uuid

class ConversationCrud:
    def __init__(self):
        pass

    def get_conversation_by_id(self, user_id: str):
        """
        Fetch conversations by user ID.
        """
        try:
            query = "SELECT * FROM conversations WHERE user_id = ?"
            params = (user_id,)
            result = execute_fetch_query(query, params)
            if result:
                return result
            else:
                return None
        except Exception as e:
            raise ValueError(f"Error fetching conversations for user ID {user_id}: {str(e)}")

    def add_conversation(self, user_id: str):
        """
        Add a new conversation for a user.
        """
        try:
            conversation_id = str(uuid.uuid4())
            query = "Insert into conversations (id, user_id, title) VALUES (?, ?, ?)"
            params = (conversation_id, user_id, "New Chat")
            result = execute_insert_or_update_query(query, params)
            if result:
                return True
            else:
                None
        except Exception as e:
            raise ValueError(f"Error adding conversation for user ID {user_id}: {str(e)}")