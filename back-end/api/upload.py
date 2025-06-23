from fastapi import APIRouter, HTTPException, File, UploadFile
from models.schema import FileUpload
from services.upload import FileUploadService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/uploads", tags=["Uploads"])
file_management_process = FileUploadService()


@router.post("/file-upload", response_model=bool)
def add_file(user_id: str, file: UploadFile = File(...)):
    """
    Upload a file.
    """
    try:
        result = file_management_process.add_file(file, user_id)
        if result:
            return True
        else:
            raise HTTPException(status_code=400, detail="File upload failed.")
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during file upload.")
    
@router.get("/files", response_model=list[FileUpload])
def get_files(user_id: str):
    """
    Get all files uploaded by a specific user.
    """
    try:
        files = file_management_process.get_files_by_user_id(user_id)
        if files:
            return files
        else:
            return []
    except Exception as e:
        logger.error(f"Error fetching files: {e}")
        raise HTTPException(status_code=404, detail="Files not found for the given user ID.")

@router.delete("/file/{file_id}", response_model=bool)
def delete_file(file_id: str):
    """
    Delete a file by its ID.
    """
    try:
        result = file_management_process.delete_file(file_id)
        if result:
            return True
        else:
            raise HTTPException(status_code=404, detail="File not found or deletion failed.")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during file deletion.")

