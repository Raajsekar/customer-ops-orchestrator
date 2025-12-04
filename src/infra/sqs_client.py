"""SQS client for A2A JSON messages between agents."""
import os
import json

DISABLE_AWS = os.getenv("DISABLE_AWS", "true").lower() == "true"

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None  # type: ignore

QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def send_message(payload: dict):
    if DISABLE_AWS or boto3 is None or not QUEUE_URL:
        return
    sqs = boto3.client("sqs", region_name=AWS_REGION)
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(payload))
