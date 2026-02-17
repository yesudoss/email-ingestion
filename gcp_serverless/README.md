# Google Serverless Email Ingestion

This directory contains a standalone script designed to run on **Google Cloud Functions** or **Google Cloud Run**.

It fetches emails from Gmail and uploads them to a Google Cloud Storage (GCS) bucket.

## Prerequisites

1.  **Google Cloud Storage Bucket**:
    *   Ensure a bucket named `email-ingestion-bucket` exists (or update `BUCKET_NAME` in `main.py`).
2.  **Gmail Credentials (`token.json`)**:
    *   Since serverless environments cannot pop up a browser for login, you **must** generate a `token.json` file locally and bundle it with this script.
    *   The script expects `token.json` to be present in the same directory.
3.  **GCS Permissions**:
    *   The runtime Service Account (e.g., App Engine default service account) must have `Storage Object Creator` or `Storage Admin` role on the bucket.

## Deployment

### Cloud Functions (Gen 2)

```bash
gcloud functions deploy email-ingester \
  --gen2 \
  --runtime=python310 \
  --region=us-central1 \
  --source=. \
  --entry-point=ingest_emails \
  --trigger-http \
  --memory=512MB
```

### Cloud Run

```bash
gcloud run deploy email-ingester --source .
```

## Local Testing

You can run the script locally to test, provided you have `token.json` in this folder and have authenticated `gcloud` for GCS access.

```bash
pip install -r requirements.txt
python main.py
```
