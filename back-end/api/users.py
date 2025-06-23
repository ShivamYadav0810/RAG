from fastapi import APIRouter, HTTPException
from typing import List
from models.schema import User
from services.users import UserService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["User"])
user_process = UserService()

@router.post("/login", response_model=dict)
def perform_login(user: User):
    """
    Login/Add a new user.
    """
    try:
        new_user_id = user_process.add_user(user)
        return {"user_id": new_user_id}
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        raise HTTPException(status_code=400, detail="User already exists or invalid data provided.")