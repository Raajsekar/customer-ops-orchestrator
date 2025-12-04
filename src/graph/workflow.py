from langgraph.graph import StateGraph, END
from typing import TypedDict

from ..models.ticket_state import TicketState
from ..agents.classifier import classify_ticket
from ..agents.resolver import resolve_ticket
from ..agents.verifier import verify_answer
from ..infra.dynamodb_client import save_ticket_state
from ..infra.s3_client import upload_text
from ..infra.sqs_client import send_message

MAX_RESOLVER_RETRIES = 2


class GraphState(TypedDict):
    ticket: TicketState


def classifier_node(state: GraphState) -> GraphState:
    t = state["ticket"]
    result = classify_ticket(t.title, t.description)
    t.category = result.category
    t.status = "CLASSIFIED"

    save_ticket_state(t.model_dump())
    send_message(
        {
            "type": "CLASSIFIED",
            "ticket_id": t.ticket_id,
            "category": t.category,
        }
    )
    return {"ticket": t}


def resolver_node(state: GraphState) -> GraphState:
    t = state["ticket"]

    if not t.category:
        t.status = "FAILED"
        t.metadata["error"] = "No category"
        save_ticket_state(t.model_dump())
        return {"ticket": t}

    out = resolve_ticket(t.title, t.description, t.category)
    t.draft_answer = out.draft_answer
    t.status = "IN_PROGRESS"
    t.retries += 1

    save_ticket_state(t.model_dump())
    send_message(
        {
            "type": "RESOLVED_DRAFT",
            "ticket_id": t.ticket_id,
            "category": t.category,
        }
    )
    return {"ticket": t}


def verifier_node(state: GraphState) -> GraphState:
    t = state["ticket"]

    v = verify_answer(t.title, t.description, t.draft_answer or "")
    t.status = "RESOLVED" if v.is_approved else "FAILED"
    t.final_answer = v.final_answer
    t.metadata["verification_reason"] = v.reason

    # Save transcript to S3
    history_key = f"tickets/{t.ticket_id}.txt"
    history_text = (
        f"Title: {t.title}\n\n"
        f"Description: {t.description}\n\n"
        f"Draft: {t.draft_answer}\n\n"
        f"Final: {t.final_answer}\n\n"
        f"Metadata: {t.metadata}\n"
    )
    upload_text(history_key, history_text)
    save_ticket_state(t.model_dump())

    send_message(
        {
            "type": "VERIFIED",
            "ticket_id": t.ticket_id,
            "status": t.status,
        }
    )

    return {"ticket": t}


def fallback_node(state: GraphState) -> GraphState:
    """Dapr-style fallback node after retries exhausted."""
    t = state["ticket"]
    t.status = "FAILED"
    t.metadata["fallback_reason"] = "Resolver failed after retries"

    save_ticket_state(t.model_dump())
    send_message(
        {
            "type": "FALLBACK",
            "ticket_id": t.ticket_id,
            "metadata": t.metadata,
        }
    )
    return {"ticket": t}


def resolver_condition(state: GraphState) -> str:
    t = state["ticket"]
    if t.status == "FAILED" and t.retries < MAX_RESOLVER_RETRIES:
        return "retry"
    elif t.status == "FAILED":
        return "fallback"
    return "ok"


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("classifier", classifier_node)
    graph.add_node("resolver", resolver_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("fallback", fallback_node)

    graph.set_entry_point("classifier")
    graph.add_edge("classifier", "resolver")

    graph.add_conditional_edges(
        "resolver",
        resolver_condition,
        {
            "ok": "verifier",
            "retry": "resolver",
            "fallback": "fallback",
        },
    )

    graph.add_edge("verifier", END)
    graph.add_edge("fallback", END)

    return graph.compile()
