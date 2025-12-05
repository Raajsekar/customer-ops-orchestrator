"""DynamoDB wrapper for ticket state."""
import os

DISABLE_AWS = os.getenv("DISABLE_AWS", "true").lower() == "true"

try:
    import boto3
except ImportError:
    boto3 = None

TABLE_NAME = os.getenv("DDB_TICKET_TABLE", "tickets-dev")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def _get_table():
    """Return DynamoDB table only when AWS is enabled"""
    if DISABLE_AWS or boto3 is None:
        return None  # IMPORTANT FIX

    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return ddb.Table(TABLE_NAME)


def save_ticket_state(ticket_dict: dict) -> None:
    table = _get_table()
    if table is None:
        return
    table.put_item(Item=ticket_dict)


def load_ticket_state(ticket_id: str):
    table = _get_table()
    if table is None:
        return None
    resp = table.get_item(Key={"ticket_id": ticket_id})
    return resp.get("Item")
