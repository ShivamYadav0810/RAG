from crud.chats import ChatCrud
from utils.rag_pipeline import query_with_gemini_generation_stream, prompt_expansion, create_chat_name, query_with_gemini_generation
import json

class ChatService:
    def __init__(self):
        self.chats = []

    def get_chats_by_id(self, conversation_id: str):
        try:
            chats_history = ChatCrud.get_chats_by_id(self, conversation_id)
            if not chats_history:
                return []
            return chats_history
        except Exception as e:
            raise ValueError(f"Error fetching chats for conversation ID {conversation_id}: {str(e)}")

    def add_chat_and_generate_response_stream(self, conversation_id: str, message: str):
        """Generator function that yields streaming response chunks."""
        try:
            chat_history = ChatCrud.get_chats_by_id(self, conversation_id)
            print("chat_history:", chat_history)
            og_message = message
            
            if chat_history:
                conversation_name = create_chat_name(chat_history)
                message = prompt_expansion(message, chat_history)
                print(f"Expanded message: {message}")
                ChatCrud.update_conversation_name(self, conversation_id, conversation_name)

            user_id = ChatCrud.get_user_id_by_conversation_id(self, conversation_id)
            collection_name = f"{user_id}_collection"
            print(f"Using collection: {collection_name} for user ID: {user_id}*************")
            
            # Stream the response
            full_response = ""
            for chunk in query_with_gemini_generation_stream(message, collection_name):
                if chunk.get("content"):
                    full_response += chunk["content"]
                yield chunk
            
            # Save the complete response to database
            if full_response:
                ChatCrud.add_chat(self, conversation_id, og_message, full_response)
                
        except Exception as e:
            yield {"error": f"Error adding chat for conversation ID {conversation_id}: {str(e)}"}

    # Keep original method for compatibility
    def add_chat_and_generate_response(self, conversation_id: str, message: str):
        try:
            chat_history = ChatCrud.get_chats_by_id(self, conversation_id)
            print("chat_history:", chat_history)
            og_message = message
            if chat_history:
                conversation_name = create_chat_name(chat_history)
                message = prompt_expansion(message, chat_history)
                print(f"Expanded message: {message}")
                ChatCrud.update_conversation_name(self, conversation_id, conversation_name)

            user_id = ChatCrud.get_user_id_by_conversation_id(self, conversation_id)
            collection_name = f"{user_id}_collection"
            print(f"Using collection: {collection_name} for user ID: {user_id}*************")
            
            resp = query_with_gemini_generation(message, collection_name)
            print(f"Generated response: {resp}")
            if ChatCrud.add_chat(self, conversation_id, og_message, resp.get("generated_response")):
                return resp.get("generated_response")
            return None
        except Exception as e:
            raise ValueError(f"Error adding chat for conversation ID {conversation_id}: {str(e)}")
