
from .kb_loader import load_kb

def simple_retriever(query: str, category: str):
    """Very small fake retriever.

    - Filters docs by category
    - Does a naive keyword check to slightly re-order them
    """
    kb = load_kb()
    docs = [d for d in kb if d.get("category") == category]

    # Sort: docs that contain some query token first.
    tokens = [t for t in query.lower().split() if len(t) > 3]
    def score(doc):
        text = doc.get("content", "").lower()
        return sum(token in text for token in tokens)

    docs.sort(key=score, reverse=True)
    return docs[:3]
