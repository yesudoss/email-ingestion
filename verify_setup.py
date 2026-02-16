import sys
import os
import traceback

try:
    print("Verifying imports...")
    from config.settings import settings
    from config.logging_config import setup_logging
    
    # Import one by one
    print("Importing models...")
    from persistence.models import ProcessedEmail, FailedEmail
    print("Importing repository...")
    from persistence.repository import Repository
    print("Importing storage...")
    from storage.base import BaseStorage
    from storage.s3 import S3Storage
    from storage.azure import AzureStorage
    from storage.gcp import GCPStorage
    from storage.factory import StorageFactory
    print("Imports successful.")

    print("Verifying configuration...")
    if not settings.EMAIL_PROVIDER:
        raise ValueError("EMAIL_PROVIDER not set")
    print(f"EMAIL_PROVIDER: {settings.EMAIL_PROVIDER}")
    print(f"STORAGE_PROVIDER: {settings.STORAGE_PROVIDER}")
    
    print("Configuration verified.")

    print(f"Verifying storage factory for provider '{settings.STORAGE_PROVIDER}'...")
    try:
        storage = StorageFactory.get_storage()
        storage_type = type(storage).__name__
        print(f"Storage backend initialized: {storage_type}")
        
        expected_map = {
            "gcp": "GCPStorage",
            "aws": "S3Storage",
            "azure": "AzureStorage"
        }
        
        expected_type = expected_map.get(settings.STORAGE_PROVIDER.lower())
        if expected_type and storage_type != expected_type:
            print(f"ERROR: Expected {expected_type} but got {storage_type}")
        elif not expected_type:
             print(f"ERROR: Unknown provider {settings.STORAGE_PROVIDER}")
        else:
            print("Storage provider matches configuration.")
            
    except Exception as e:
        print(f"Storage factory warning: {e}")

    print("Setup verification complete.")

except Exception:
    traceback.print_exc()
    sys.exit(1)
