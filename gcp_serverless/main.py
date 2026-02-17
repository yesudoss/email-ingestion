import os
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import storage

# --- Configuration ---
# Hardcoded configuration for "straight forward" execution
BUCKET_NAME = "email-ingestion-bucket"  # REPLACE WITH YOUR BUCKET NAME
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.json'  # Expected to be bundled with the function

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_gmail_service():
    """
    Authenticates with Gmail using a bundled token.json.
    Serverless environments cannot perform interactive login, so token.json must be present.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, GMAIL_SCOPES)
    
    # If there are no (valid) credentials available, we can try to refresh if possible,
    # but we cannot start a new 'InstalledAppFlow' (interactive) in a serverless function.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Refreshed expired token.")
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                raise RuntimeError("Gmail token is expired and could not be refreshed.")
        else:
            logger.error(f"{TOKEN_FILE} not found or invalid. Cannot authenticate Gmail non-interactively.")
            raise FileNotFoundError(f"Missing {TOKEN_FILE}. Please generate it locally and bundle it.")

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        logger.error(f"An error occurred building Gmail service: {error}")
        raise

def get_gcs_bucket():
    """
    Returns the GCS bucket object using Application Default Credentials (ADC).
    This works automatically in Cloud Functions/Run.
    """
    try:
        # Client() automatically looks for credentials in the environment
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        return bucket
    except Exception as e:
        logger.error(f"Error getting GCS bucket: {e}")
        raise

def fetch_emails(service, minutes: int = 15) -> List[Dict[str, Any]]:
    """Fetch emails from the last `minutes`."""
    try:
        cutoff = datetime.now() - timedelta(minutes=minutes)
        timestamp = int(cutoff.timestamp())
        query = f"after:{timestamp}"
        
        logger.info(f"Fetching emails with query: {query}")
        
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        logger.info(f"Found {len(messages)} emails.")
        return messages
    except HttpError as error:
        logger.error(f"An error occurred fetching emails: {error}")
        return []

def download_and_upload_email(gmail_service, bucket, msg_id: str):
    """Downloads raw email and uploads to GCS."""
    try:
        # 1. Download from Gmail
        message = gmail_service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        raw_content = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        
        # 2. Upload to GCS
        filename = f"emails/{msg_id}.eml"
        blob = bucket.blob(filename)
        blob.upload_from_string(raw_content, content_type='message/rfc822')
        
        logger.info(f"Successfully processed email {msg_id} -> gs://{BUCKET_NAME}/{filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to process email {msg_id}: {e}")
        return False

def ingest_emails(event, context=None):
    """
    Cloud Function Entry Point.
    Args:
        event (dict): Event payload (for Pub/Sub) or Request (for HTTP).
        context (google.cloud.functions.Context): Metadata for the event.
    """
    try:
        logger.info("Starting email ingestion (Serverless)...")
        
        # Initialize services
        gmail_service = get_gmail_service()
        bucket = get_gcs_bucket()
        
        # Fetch and Process
        messages = fetch_emails(gmail_service, minutes=15)
        
        count = 0
        for msg in messages:
            if download_and_upload_email(gmail_service, bucket, msg['id']):
                count += 1
                
        return f"Processed {count} emails successfully."
    except Exception as e:
        logger.error(f"Function failed: {e}")
        # Re-raise to signal failure to Cloud Functions runtime (triggers retry if configured)
        raise

# Local testing block
if __name__ == "__main__":
    try:
        print("Running locally...")
        ingest_emails({}, None)
    except Exception as e:
        print(f"Execution failed: {e}")
