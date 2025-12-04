# src/llm/bedrock_client.py
from typing import Optional
import os
import json

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None  # type: ignore

BEDROCK_REGION = os.getenv("AWS_REGION", "us-east-1")
DISABLE_AWS = os.getenv("DISABLE_AWS", "true").lower() == "true"


def _get_client():
    if boto3 is None:
        raise RuntimeError("boto3 not installed")
    return boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def call_mistral_large(prompt: str) -> str:
    """
    Call Bedrock mistral-large (replace model ID with actual one from your account).
    For local dev (DISABLE_AWS=true) this just returns a fake answer.
    """
    if DISABLE_AWS or boto3 is None:
        return f"[LOCAL_FAKE_MISTRAL_OUTPUT] {prompt[:200]}"

    client = _get_client()
    body = {
        "inputText": prompt,
        # TODO: adapt to real Mistral schema
    }
    resp = client.invoke_model(
        modelId=os.getenv("BEDROCK_MISTRAL_MODEL_ID", "mistral.mxxx"),
        body=json.dumps(body).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )
    out = resp["body"].read().decode("utf-8")
    return out  # parse as needed


def call_titan_summarize(text: str) -> str:
    """
    Example Titan text summarization call.
    """
    if DISABLE_AWS or boto3 is None:
        return f"[LOCAL_SUMMARY] {text[:200]}"

    client = _get_client()
    body = {"inputText": text}
    resp = client.invoke_model(
        modelId=os.getenv("BEDROCK_TITAN_MODEL_ID", "amazon.titan-text-lite-v1"),
        body=json.dumps(body).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )
    out = resp["body"].read().decode("utf-8")
    return out  # parse as needed
