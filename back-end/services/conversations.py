from crud.conversations import ConversationCrud
from models.schema import Conversation

class ConversationService:
    def __init__(self):
       pass

    def get_coversation_by_id(self, user_id: str):
        """
        Fetch conversations by user ID.
        """
        try:
            converasation = ConversationCrud.get_conversation_by_id(self, user_id)
            if converasation:
                return converasation
            else:
                return None
        except Exception as e:
            raise ValueError(f"Error fetching conversations for user ID {user_id}: {str(e)}")
    

    def add_conversation(self, user_id: str):
        """
        Add a new conversation for a user.
        """
        try:
            if not user_id:
                return None
            
            result = ConversationCrud.add_conversation(self, user_id)
            if result:
                return result
            else:
                return False
        except Exception as e:
            raise ValueError(f"Error adding conversation for user ID {user_id}: {str(e)}")