import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    class Config:
        env_file = ".env"
        extra = "ignore"

api_settings = Settings()
