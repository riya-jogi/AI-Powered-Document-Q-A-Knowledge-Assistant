"""
Application configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/document_qa_db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "document_qa_db"
    DB_USER: str = "your_db_user"
    DB_PASSWORD: str = "your_db_password"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2:7b"
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_FILE_TYPES: str = "pdf,docx,txt"
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"  # or 'cuda' if GPU is available
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()