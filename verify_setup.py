import sys
import os
import traceback

try:
    print("Verifying imports...")
    from config.settings import settings
    from config.logging_config import setup_logging
    # from persistence.models import ProcessedEmail, FailedEmail
    # from persistence.repository import Repository
    # from storage.base import BaseStorage
    # from storage.s3 import S3Storage
    # from storage.factory import StorageFactory
    # from email_service.gmail import GmailService
    # from processor.email_processor import EmailProcessor
    # from scheduler.job_runner import JobRunner
    
    # Import one by one
    print("Importing models...")
    from persistence.models import ProcessedEmail, FailedEmail
    print("Importing repository...")
    from persistence.repository import Repository
    print("Importing storage...")
    from storage.base import BaseStorage
    from storage.s3 import S3Storage
    from storage.factory import StorageFactory
    print("Importing email service...")
    from email_service.gmail import GmailService
    print("Importing processor...")
    from processor.email_processor import EmailProcessor
    print("Importing scheduler...")
    from scheduler.job_runner import JobRunner
    print("Imports successful.")

    print("Verifying configuration...")
    if not settings.EMAIL_PROVIDER:
        raise ValueError("EMAIL_PROVIDER not set")
    print(f"EMAIL_PROVIDER: {settings.EMAIL_PROVIDER}")
    print(f"STORAGE_PROVIDER: {settings.STORAGE_PROVIDER}")
    print("Configuration verified.")

    print("Verifying persistence layer...")
    repo = Repository()
    print("Repository initialized and DB created.")

    print("Verifying storage factory...")
    try:
        storage = StorageFactory.get_storage()
        print(f"Storage backend initialized: {type(storage).__name__}")
    except Exception as e:
        print(f"Storage factory warning (expected if no credentials): {e}")

    print("Setup verification complete.")

except Exception:
    traceback.print_exc()
    sys.exit(1)
