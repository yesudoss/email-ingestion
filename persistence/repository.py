from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from config.settings import settings
from config.logging_config import setup_logging
from persistence.models import Base, ProcessedEmail, FailedEmail

logger = setup_logging()

class Repository:
    def __init__(self, db_path: str = settings.DB_PATH):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def is_processed(self, gmail_id: str) -> bool:
        session = self.Session()
        try:
            exists = session.query(ProcessedEmail).filter_by(gmail_id=gmail_id).first()
            return exists is not None
        finally:
            session.close()

    def mark_processed(self, gmail_id: str, storage_key: str):
        session = self.Session()
        try:
            processed = ProcessedEmail(gmail_id=gmail_id, storage_key=storage_key)
            session.add(processed)
            # If it was in failed table, remove it
            failed = session.query(FailedEmail).filter_by(gmail_id=gmail_id).first()
            if failed:
                session.delete(failed)
            session.commit()
            logger.info(f"Marked email {gmail_id} as processed.")
        except IntegrityError:
            session.rollback()
            logger.warning(f"Email {gmail_id} already processed.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error marking processed {gmail_id}: {e}")
            raise
        finally:
            session.close()

    def log_failure(self, gmail_id: str, error_message: str):
        session = self.Session()
        try:
            failed = session.query(FailedEmail).filter_by(gmail_id=gmail_id).first()
            if failed:
                failed.retry_count += 1
                failed.last_attempt = datetime.utcnow()
                failed.error_message = error_message
            else:
                failed = FailedEmail(
                    gmail_id=gmail_id,
                    error_message=error_message,
                    retry_count=1
                )
                session.add(failed)
            session.commit()
            logger.error(f"Logged failure for {gmail_id}: {error_message}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging failure for {gmail_id}: {e}")
            raise
        finally:
            session.close()

    def get_failed_emails(self) -> List[FailedEmail]:
        session = self.Session()
        try:
            return session.query(FailedEmail).all()
        finally:
            session.close()
