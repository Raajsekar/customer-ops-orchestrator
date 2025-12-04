from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import os

# Load environment
from dotenv import load_dotenv
load_dotenv()

print(">>> Loaded ENV. DISABLE_AWS =", os.getenv("DISABLE_AWS"))

# Langfuse (correct modern API)
from langfuse.callback import CallbackHandler
langfuse_handler = CallbackHandler()

from ..models.ticket_state import TicketState
from ..graph.workflow import build_graph

app = FastAPI(
    title="Customer Operations Orchestrator",
    version="1.0.0",
    description="Multi-agent workflow: Classifier → Resolver → Verifier",
)

graph = build_graph()


class CreateTicketRequest(BaseModel):
    user_id: str | None = None
    title: str
    description: str


class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    category: str | None = None
    draft_answer: str | None = None
    final_answer: str | None = None
    metadata: dict | None = None
    trace_id: str | None = None


@app.get("/")
def root():
    return {
        "message": "Customer Ops Orchestrator is running!",
        "endpoints": ["/health", "/tickets", "/docs", "/redoc"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tickets", response_model=TicketResponse)
def create_ticket(req: CreateTicketRequest):
    trace_id = str(uuid.uuid4())

    # ---- START LANGFUSE TRACE ----
    langfuse_handler.create_trace(
        id=trace_id,
        name="ticket_flow",
        metadata={"user_id": req.user_id},
        input=req.model_dump(),
    )

    ticket = TicketState(
        ticket_id=str(uuid.uuid4()),
        user_id=req.user_id,
        title=req.title,
        description=req.description,
    )

    result = graph.invoke({"ticket": ticket})
    t = result["ticket"]

    # ---- END LANGFUSE TRACE ----
    langfuse_handler.end_trace(
        trace_id=trace_id,
        output=t.model_dump()
    )
    langfuse_handler.flush()

    return TicketResponse(
        ticket_id=t.ticket_id,
        status=t.status,
        category=t.category,
        draft_answer=t.draft_answer,
        final_answer=t.final_answer,
        metadata=t.metadata,
        trace_id=trace_id,
    )
