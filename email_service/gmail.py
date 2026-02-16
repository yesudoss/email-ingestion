import os.path
import base64
import email
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.logging_config import setup_logging
from config.settings import settings

logger = setup_logging()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing token: {e}")
                    self.creds = None

            if not self.creds:
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())
                else:
                    logger.error("credentials.json not found. Cannot authenticate.")
                    raise FileNotFoundError("credentials.json not found.")

        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise

    def fetch_emails(self, minutes: int = 15) -> List[Dict[str, Any]]:
        """
        Fetch emails from the last `minutes`.
        """
        try:
            # Calculate timestamp for query
            cutoff = datetime.now() - timedelta(minutes=minutes)
            timestamp = int(cutoff.timestamp())
            query = f"after:{timestamp}"
            
            logger.info(f"Fetching emails with query: {query}")
            
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            logger.info(f"Found {len(messages)} emails.")
            return messages
        except HttpError as error:
            logger.error(f"An error occurred fetching emails: {error}")
            return []

    def download_email_content(self, msg_id: str) -> Optional[bytes]:
        """
        Download the raw email content (RFC822).
        """
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
            msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
            return msg_str
        except HttpError as error:
            logger.error(f"An error occurred downloading email {msg_id}: {error}")
            return None
