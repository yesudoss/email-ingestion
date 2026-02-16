# Email Ingestion & Cloud Storage Service

A production-ready Python application that pulls emails from Gmail, uploads them to cloud storage (AWS S3), and ensures idempotency using SQLite.

## Features
- **Configurable Interval**: Pulls emails every X minutes.
- **Multiple Storage Providers**: AWS S3 implemented, extensible for Azure/GCP.
- **Idempotency**: Prevents duplicate processing using SQLite.
- **Retry Mechanism**: Exponential backoff using `tenacity`.
- **Structured Logging**: JSON formatted logs for observability.
- **Dead-letter Queue**: Failed records persist in the database.

## Prerequisites
- Python 3.9+
- AWS Account (for S3)
- Google Cloud Project (for Gmail API) enabled

## Setup

1. **Clone the repository**
2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Configure Environment Variables**:
    Copy `.env.example` to `.env` and fill in the values.
    ```bash
    cp .env.example .env
    ```
    - `EMAIL_PROVIDER`: `gmail`
    - `STORAGE_PROVIDER`: `aws` (or `azure`, `gcp` when implemented)
    - `AWS_ACCESS_KEY_ID`: Your AWS Access Key
    - `AWS_SECRET_ACCESS_KEY`: Your AWS Secret Key
    - `S3_BUCKET_NAME`: Target S3 bucket
    - `SCHEDULE_INTERVAL_MINUTES`: Interval in minutes (default: 15)

4. **Gmail Credentials**:
    Place your `credentials.json` (OAuth 2.0 Client ID) in the root directory.
    On first run, it will open a browser to authenticate and save `token.json`.

## Usage

Run the service:
```bash
python main.py
```

## Architecture
- **Scheduler**: APScheduler triggers the job.
- **Email Service**: Fetches emails via Gmail API.
- **Processor**: Orchestrates download, idempotency check, and upload.
- **Storage**: Abstracted layer uploads to S3.
- **Persistence**: SQLite tracks processed IDs and failures.
