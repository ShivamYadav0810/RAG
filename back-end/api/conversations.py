from fastapi import APIRouter, HTTPException

from models.schema import User
from services.conversations import ConversationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])
conversation_process = ConversationService()


@router.get("/all-conversations", response_model=dict)
def get_all_Conversations(user_id: str = None):
    """
    Get all conversations or a specific user by ID.
    """
    if user_id:
        conversations = conversation_process.get_coversation_by_id(user_id)
        return {"conversations": conversations if conversations else []}
    else:
        raise HTTPException(status_code=422, detail="User ID is required to fetch a specific Conversations.")

@router.post("/new-conversation", response_model=bool)
def add_conversations(user_id: str):
    """
    Add a new conversation.
    """
    try:
        conversations = conversation_process.add_conversation(user_id)
        return conversations
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        raise HTTPException(status_code=400, detail="User already exists or invalid data provided.")