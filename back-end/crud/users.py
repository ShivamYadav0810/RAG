from utils.helper import execute_fetch_query, execute_insert_or_update_query
import uuid

class UsersCrud():
    def __init__(self):
        pass
    def get_user_by_email(self, user_email):
        """
        Fetch all users or a specific user by ID.
        """
        try:
            if user_email:
                query = "SELECT * from users WHERE email = ?"
                params = (user_email,)
                result = execute_fetch_query(query, params)
                if result:
                    return result
                else:
                    return None
        except Exception as e:
            raise ValueError(f"Error fetching user by email {user_email}: {str(e)}")
        
    def add_user(self, user):
        """
        Add a new user.
        """
        try:
            user_id = str(uuid.uuid4()) if not user.id else user.id
            query = "INSERT INTO users (id, username, email) VALUES (?, ?, ?)"
            params = (user_id, user.username, user.email)
            result = execute_insert_or_update_query(query, params)
            
            return user_id if result else None
        except Exception as e:
            raise ValueError(f"Error adding user {user.username}: {str(e)}")