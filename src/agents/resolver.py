from pydantic import BaseModel
from ..rag.retriever import simple_retriever
import os

from ..llm.bedrock_client import call_titan_summarize


class ResolverOutput(BaseModel):
    draft_answer: str
    used_docs: list


USE_BEDROCK_RESOLVER = os.getenv("USE_BEDROCK_RESOLVER", "false").lower() == "true"


def resolve_ticket(title: str, description: str, category: str) -> ResolverOutput:
    docs = simple_retriever(description, category)

    if not docs:
        draft = (
            "I could not find a matching article in the knowledge base. "
            "Please forward this ticket to a human agent."
        )
        return ResolverOutput(draft_answer=draft, used_docs=[])

    context = "\n".join([d["content"] for d in docs])

    if USE_BEDROCK_RESOLVER:
        prompt = (
            "You are a customer support agent. Use the context to answer the ticket.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"TICKET TITLE: {title}\n"
            f"TICKET DESCRIPTION: {description}\n\n"
            "Provide a clear, polite answer."
        )
        answer = call_titan_summarize(prompt)
        return ResolverOutput(draft_answer=answer, used_docs=docs)

    # Fallback: format docs directly
    bullets = "\n".join([f"- {d['content']}" for d in docs])
    draft = (
        f"Here is a suggested answer based on internal knowledge base articles for category '{category}':\n\n"
        f"{bullets}\n\n"
        "If this does not fully solve the issue, please contact the support team."
    )
    return ResolverOutput(draft_answer=draft, used_docs=docs)
