from config.settings import settings
from storage.base import BaseStorage
from storage.s3 import S3Storage
from storage.azure import AzureStorage
from storage.gcp import GCPStorage
from config.logging_config import setup_logging

logger = setup_logging()

class StorageFactory:
    @staticmethod
    def get_storage() -> BaseStorage:
        provider = settings.STORAGE_PROVIDER.lower()
        if provider == "aws":
            logger.info("Using AWS S3 Storage")
            return S3Storage()
        elif provider == "azure":
            logger.info("Using Azure Storage")
            return AzureStorage()
        elif provider == "gcp":
            logger.info("Using GCP Storage")
            return GCPStorage()
        else:
            raise ValueError(f"Unknown storage provider: {provider}")
