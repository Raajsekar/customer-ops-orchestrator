"""Tiny LangSmith helper (optional)."""
from typing import Optional
import os

try:
    from langsmith import Client
except ImportError:  # pragma: no cover
    Client = None  # type: ignore

_api_key = os.getenv("LANGSMITH_API_KEY")
_client: Optional["Client"] = Client(api_key=_api_key) if (Client and _api_key) else None


def get_langsmith() -> Optional["Client"]:
    return _client
