import shutil
import uuid
from crud.upload import FileCrud
from pathlib import Path
from models.schema import FileUpload

from utils.data_indexing_pipeline import add_data_to_vector_store

UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)

class FileUploadService():
    def __init__(self):
        pass

    def add_file(self, file, user_id):
        """
        adding a file to the database.
        """
        try:
            if not file or not user_id:
                return False
            
            file_location = UPLOAD_DIR / user_id
            if not file_location.exists():
                file_location.mkdir(parents=True, exist_ok=True)
            
            file_location = file_location / file.filename

            print(f"File location: {file_location}")
            contents = file.read()
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            print(f"File saved at: {file_location}")
            
            file_id = str(uuid.uuid4())
            if FileCrud.add_file(self, file_id, file.filename, file.content_type, file_location, user_id):
                add_data_to_vector_store(user_id)
                return True
            print("Crud was also successful")
            return False
        except Exception as e:
            raise ValueError(f"Error adding file {file.filename}: {str(e)}")

    def get_files_by_user_id(self, user_id):
        """
        fetching files by user ID.
        """
        try:
            if not user_id:
                return []

            files = FileCrud.get_files_by_userid(user_id)
            if files:
                files = [
                    FileUpload(
                        id=file[0],
                        user_id=file[1],
                        file_name=file[2],
                        file_token=file[3],
                        file_type=file[4],
                        file_path=file[5]
                    ) 
                    for file in files
                ]
            return files if files else []
        except Exception as e:
            raise ValueError(f"Error fetching files for user ID {user_id}: {str(e)}")

    def delete_file(self, file_id):
        """
        deleting a file by its ID.
        """
        try:
            if not file_id:
                return False

            if FileCrud.delete_file(self, file_id):
                user_id = FileCrud.get_user_id_by_file_id(self, file_id)
                add_data_to_vector_store(user_id)
                return True
            return False
        except Exception as e:
            raise ValueError(f"Error deleting file with ID {file_id}: {str(e)}")