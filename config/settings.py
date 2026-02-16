import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    EMAIL_PROVIDER: str = "gmail"
    
    # Storage Selection
    # Options: "aws", "azure", "gcp"
    STORAGE_PROVIDER: str = "gcp" 
    
    SCHEDULE_INTERVAL_MINUTES: int = 15
    
    # GCP - Primary
    # Defaults to local dummy file if not set
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = "gcp_credentials.json"
    GCP_BUCKET_NAME: str = "email-ingestion-bucket"
    GCP_PROJECT_ID: Optional[str] = None # Optional, client can infer from creds
    
    # AWS - Optional
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = "project-email-ingestion"
    
    # Azure - Optional
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_CONTAINER_NAME: Optional[str] = "email-ingestion-container"
    
    # SQLite
    DB_PATH: str = "metadata.db"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
