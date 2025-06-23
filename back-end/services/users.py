from fastapi import HTTPException
from crud.users import UsersCrud
from typing import List
from models.schema import User

class UserService:
    def __init__(self):
        pass

    def add_user(self, user: User) -> User:
        try:
            if not user.email or not user.username:
                raise HTTPException(status_code=422, detail="Email and username are required to add a user.")
            fetched_user = UsersCrud.get_user_by_email(self, user.email)
            if fetched_user:
                return fetched_user[0][0]
            return UsersCrud.add_user(self, user)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error adding user: {str(e)}")