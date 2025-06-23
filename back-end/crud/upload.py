from utils.helper import execute_fetch_query, execute_insert_or_update_query
import uuid
class FileCrud():
    def __init__(self):
        pass
    def add_file(self, file_id, file_name, file_type, file_path, user_id):
        """
        Add a new file to the database.
        """
        try:
            file_id = str(uuid.uuid4())
            query = "INSERT INTO file_uploads (id, user_id, file_name, file_token, file_type, file_path) VALUES (?, ?, ?, ?, ?, ?)"
            params = (file_id, user_id, file_name, 0, file_type, str(file_path))
            result = execute_insert_or_update_query(query, params)
            
            return True if result else False
        except Exception as e:
            raise ValueError(f"Error adding file {file_name}: {str(e)}")
    @staticmethod
    def get_files_by_userid(user_id):
        """
        Fetch files by user ID.
        """
        try:
            query = "SELECT * FROM file_uploads WHERE user_id = ?"
            params = (user_id,)
            result = execute_fetch_query(query, params)
            
            return result if result else []
        except Exception as e:
            raise ValueError(f"Error fetching files for user ID {user_id}: {str(e)}")
    
    def delete_file(self, file_id):
        """
        Delete a file by its ID.
        """
        try:
            query = "DELETE FROM file_uploads WHERE id = ?"
            params = (file_id,)
            result = execute_insert_or_update_query(query, params)
            
            return True if result else False
        except Exception as e:
            raise ValueError(f"Error deleting file with ID {file_id}: {str(e)}")
        
    def get_user_id_by_file_id(self, file_id):
        """
        Get user ID by file ID.
        """
        try:
            query = "SELECT user_id FROM file_uploads WHERE id = ?"
            params = (file_id,)
            result = execute_fetch_query(query, params)
            
            return result[0][0] if result else None
        except Exception as e:
            raise ValueError(f"Error fetching user ID for file ID {file_id}: {str(e)}")