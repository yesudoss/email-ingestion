import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    EMAIL_PROVIDER: str = "gmail"
    STORAGE_PROVIDER: str = "aws"
    SCHEDULE_INTERVAL_MINUTES: int = 15
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "project-email-ingestion"
    
    # Gmail
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # SQLite
    DB_PATH: str = "metadata.db"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
