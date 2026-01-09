import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_STR: str = "/api"
    PROJECT_NAME: str = "Prediction Point API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pais.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        case_sensitive = True

settings = Settings()
