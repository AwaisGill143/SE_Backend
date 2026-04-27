"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True)
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:VIfBrmBrRE7r8Bxg@db.vhahbxcmnktadgtcadmx.supabase.co:5432/postgres"
    SQLALCHEMY_ECHO: bool = False
    
    # JWT/Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    YOUTUBE_API_KEY: str = ""
    JUDGE0_API_KEY: str = ""
    JUDGE0_API_URL: str = "https://judge0-ce.p.rapidapi.com"
    
    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east1-gcp"
    PINECONE_INDEX_NAME: str = "careerlaunch-embeddings"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "careerlaunch-uploads"
    
    # Email
    EMAIL_FROM: str = "noreply@careerlaunch.ai"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # CORS - defaults to a list
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

# Initialize settings
settings = Settings()
