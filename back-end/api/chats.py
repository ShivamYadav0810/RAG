from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from models.schema import Chat
from services.chats import ChatService
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])
chat_process = ChatService()

@router.get("/all-chats", response_model=dict)
def get_all_chats(conversation_id: str = None):
    """Get all chat of a specific conversation by ID."""
    if conversation_id:
        chats = chat_process.get_chats_by_id(conversation_id)
        return {"chats": chats if chats else []}
    else:
        return HTTPException(status_code=422, detail="Conversation ID is required to fetch a specific chat.")

@router.post("/new-chat-stream")
def add_conversations_stream(conversation_id: str, message: str):
    """Generate streaming response to chat."""
    try:
        def generate():
            for chunk in chat_process.add_chat_and_generate_response_stream(conversation_id, message):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error adding chat: {e}")
        raise HTTPException(status_code=400, detail="Chat format is not correct.")

# Keep the original non-streaming endpoint for compatibility
@router.post("/new-chat", response_model=str)
def add_conversations(conversation_id: str, message: str):
    """Generate response to chat."""
    try:
        chat_resp = chat_process.add_chat_and_generate_response(conversation_id, message)
        return chat_resp
    except Exception as e:
        logger.error(f"Error adding chat: {e}")
        raise HTTPException(status_code=400, detail="Chat format is not correct.")