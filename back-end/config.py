from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Chatbot API"
    APP_DESCRIPTION: str = "A modular chatbot API built with FastAPI"
    APP_VERSION: str = "1.0.0"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database settings (for future use)
    DATABASE_URL: str = "database.db"
    GEMINI_KEY: str = ""
    GEMINI_EMBEDDING_MODEL:str = "models/text-embedding-004"
    SPARSE_EMBEDDING_MODEL:str = "Qdrant/bm25"
    UPLOAD_DIR:str = "data"

    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"


settings = Settings()