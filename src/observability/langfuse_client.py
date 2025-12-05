# src/observability/langfuse_client.py
from typing import Optional, Dict, Any
import os

try:
    import langfuse
    # Some versions expose a top-level Client/Api object, some provide helper functions.
    LF_AVAILABLE = True
except Exception:
    langfuse = None
    LF_AVAILABLE = False

class LangfuseStub:
    """Minimal safe wrapper. Does nothing if real Langfuse not present."""
    def __init__(self):
        self.enabled = LF_AVAILABLE and bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))

    def create_trace(self, id: str, name: str, metadata: Dict[str, Any] | None = None, input: Dict[str, Any] | None = None):
        # If real langfuse library exists and provides an API, hook here.
        # Keep this safe — swallow errors so the app doesn't crash.
        if not self.enabled:
            return None
        try:
            # Attempt a couple of likely APIs (best-effort)
            if hasattr(langfuse, "Client"):
                client = langfuse.Client(public_key=os.getenv("LANGFUSE_PUBLIC_KEY"), secret_key=os.getenv("LANGFUSE_SECRET_KEY"))
                return client.create_trace(id=id, name=name, metadata=metadata or {}, input=input or {})
            if hasattr(langfuse, "trace"):
                return langfuse.trace.create(id=id, name=name, metadata=metadata or {}, input=input or {})
        except Exception:
            return None
        return None

    def end_trace(self, trace_id: str, output: Dict[str, Any] | None = None):
        if not self.enabled:
            return None
        try:
            if hasattr(langfuse, "Client"):
                client = langfuse.Client(public_key=os.getenv("LANGFUSE_PUBLIC_KEY"), secret_key=os.getenv("LANGFUSE_SECRET_KEY"))
                return client.end_trace(id=trace_id, output=output or {})
            if hasattr(langfuse, "trace"):
                return langfuse.trace.end(trace_id, output or {})
        except Exception:
            return None
        return None

# single instance to import from other modules
langfuse_client = LangfuseStub()
