import boto3
from botocore.exceptions import ClientError
from typing import Optional
import io

from config.settings import settings
from config.logging_config import setup_logging
from storage.base import BaseStorage

logger = setup_logging()

class S3Storage(BaseStorage):
    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def upload_email(self, data: bytes, filename: str) -> str:
        try:
            self.s3.upload_fileobj(io.BytesIO(data), self.bucket, filename)
            storage_key = f"s3://{self.bucket}/{filename}"
            logger.info(f"Uploaded email to {storage_key}")
            return storage_key
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise
