from azure.storage.blob import BlobServiceClient
from typing import Optional
import io
import logging

from config.settings import settings
from storage.base import BaseStorage

logger = logging.getLogger(__name__)

class AzureStorage(BaseStorage):
    def __init__(self):
        self.container_name = settings.AZURE_CONTAINER_NAME
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set")
            
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            if not self.container_client.exists():
                 self.container_client.create_container()
                 logger.info(f"Created Azure container: {self.container_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage: {e}")
            raise

    def upload_email(self, data: bytes, filename: str) -> str:
        try:
            blob_client = self.container_client.get_blob_client(filename)
            blob_client.upload_blob(io.BytesIO(data), overwrite=True)
            storage_key = f"azure://{self.container_name}/{filename}"
            logger.info(f"Uploaded email to {storage_key}")
            return storage_key
        except Exception as e:
            logger.error(f"Azure upload failed: {e}")
            raise
