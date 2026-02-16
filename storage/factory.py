import logging

from config.settings import settings
from storage.base import BaseStorage
from storage.s3 import S3Storage
from storage.azure import AzureStorage
from storage.gcp import GCPStorage

logger = logging.getLogger(__name__)

class StorageFactory:
    @staticmethod
    def get_storage() -> BaseStorage:
        provider = settings.STORAGE_PROVIDER.lower()
        
        logger.info(f"Initializing storage provider: {provider}")

        if provider == "aws":
            return S3Storage()
        elif provider == "azure":
            return AzureStorage()
        elif provider == "gcp":
             return GCPStorage()
        else:
             raise ValueError(f"Unknown storage provider: {provider}. Valid options are 'aws', 'azure', 'gcp'.")
