"""Tiny Langfuse helper (optional)."""
from typing import Optional
from ..config.settings import get_settings

try:
    from langfuse import Langfuse
except ImportError:  # pragma: no cover
    Langfuse = None  # type: ignore

_settings = get_settings()
_client: Optional["Langfuse"] = None

if (
    Langfuse
    and _settings.langfuse_public_key
    and _settings.langfuse_secret_key
    and _settings.langfuse_host
):
    _client = Langfuse(
        public_key=_settings.langfuse_public_key,
        secret_key=_settings.langfuse_secret_key,
        host=_settings.langfuse_host,
    )


def get_langfuse() -> Optional["Langfuse"]:
    return _client
