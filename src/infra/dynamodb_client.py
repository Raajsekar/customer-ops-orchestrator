"""DynamoDB wrapper for ticket state.

By default, DISABLE_AWS defaults to true so local dev never hits AWS
unless you explicitly set DISABLE_AWS=false.
"""
import os

DISABLE_AWS = os.getenv("DISABLE_AWS", "true").lower() == "true"

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None  # type: ignore

TABLE_NAME = os.getenv("DDB_TICKET_TABLE", "tickets-dev")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def _get_table():
    if boto3 is None:
        raise RuntimeError("boto3 not installed")
    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return ddb.Table(TABLE_NAME)


def save_ticket_state(ticket_dict: dict) -> None:
    if DISABLE_AWS or boto3 is None:
        return
    table = _get_table()
    table.put_item(Item=ticket_dict)


def load_ticket_state(ticket_id: str):
    if DISABLE_AWS or boto3 is None:
        return None
    table = _get_table()
    resp = table.get_item(Key={"ticket_id": ticket_id})
    return resp.get("Item")
