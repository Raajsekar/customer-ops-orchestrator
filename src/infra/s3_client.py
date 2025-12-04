"""S3 client used to store ticket history (transcripts)."""
import os

DISABLE_AWS = os.getenv("DISABLE_AWS", "true").lower() == "true"

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None  # type: ignore

DEFAULT_BUCKET = os.getenv("S3_BUCKET", "ticket-history-dev")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def upload_text(key: str, text: str, bucket: str | None = None):
    if DISABLE_AWS or boto3 is None:
        return
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.put_object(Bucket=bucket or DEFAULT_BUCKET, Key=key, Body=text.encode("utf-8"))
