from google.cloud import storage
import io
import logging
import os

from config.settings import settings
from storage.base import BaseStorage

logger = logging.getLogger(__name__)

class GCPStorage(BaseStorage):
    def __init__(self):
        self.bucket_name = settings.GCP_BUCKET_NAME
        self.project_id = settings.GCP_PROJECT_ID
        
        # If GOOGLE_APPLICATION_CREDENTIALS is set, the client will use it automatically.
        try:
            if self.project_id:
                self.client = storage.Client(project=self.project_id)
            else:
                 self.client = storage.Client()
                 
            self.bucket = self.client.bucket(self.bucket_name)
            if not self.bucket.exists():
                self.bucket = self.client.create_bucket(self.bucket_name)
                logger.info(f"Created GCP bucket: {self.bucket_name}")
                
        except Exception as e:
             logger.error(f"Failed to initialize GCP Storage: {e}")
             raise

    def upload_email(self, data: bytes, filename: str) -> str:
        try:
            blob = self.bucket.blob(filename)
            blob.upload_from_file(io.BytesIO(data))
            storage_key = f"gs://{self.bucket_name}/{filename}"
            logger.info(f"Uploaded email to {storage_key}")
            return storage_key
        except Exception as e:
            logger.error(f"GCP upload failed: {e}")
            raise
