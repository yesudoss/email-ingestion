from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from botocore.exceptions import ClientError
from typing import Optional

from config.settings import settings
from config.logging_config import setup_logging
from email_service.gmail import GmailService
from storage.factory import StorageFactory
from persistence.repository import Repository

logger = setup_logging()

class EmailProcessor:
    def __init__(self):
        self.gmail_service = GmailService()
        self.storage_service = StorageFactory.get_storage()
        self.repository = Repository()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ClientError, IOError)),
        reraise=True
    )
    def _upload_with_retry(self, content: bytes, filename: str) -> str:
        return self.storage_service.upload_email(content, filename)

    def process_emails(self):
        logger.info("Starting email processing job...")
        
        try:
            # Fetch emails from the last X minutes
            messages = self.gmail_service.fetch_emails(minutes=settings.SCHEDULE_INTERVAL_MINUTES)
            
            for msg in messages:
                gmail_id = msg['id']
                
                # Idempotency check
                if self.repository.is_processed(gmail_id):
                    logger.info(f"Skipping {gmail_id} - already processed.")
                    continue

                logger.info(f"Processing email {gmail_id}...")
                
                try:
                    # Download content
                    content = self.gmail_service.download_email_content(gmail_id)
                    if not content:
                        logger.warning(f"Empty content for {gmail_id}, skipping.")
                        continue

                    # Construct filename/key
                    filename = f"{gmail_id}.eml"
                    
                    # Upload to storage (with retry)
                    storage_key = self._upload_with_retry(content, filename)
                    
                    # Mark as processed
                    self.repository.mark_processed(gmail_id, storage_key)
                    logger.info(f"Successfully processed {gmail_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to process {gmail_id}: {e}")
                    self.repository.log_failure(gmail_id, str(e))
        
        except Exception as e:
            logger.critical(f"Critical failure in process_emails: {e}")
        
        logger.info("Email processing job finished.")
