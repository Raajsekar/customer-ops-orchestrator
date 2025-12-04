# src/api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import os

from dotenv import load_dotenv
load_dotenv()

print(">>> Loaded ENV. DISABLE_AWS =", os.getenv("DISABLE_AWS"))

# Correct Langfuse import
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
)

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
        "endpoints": ["/health", "/tickets", "/docs"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tickets", response_model=TicketResponse)
def create_ticket(req: CreateTicketRequest):

    # Create trace correctly
    trace = langfuse.trace(
        name="ticket_flow",
        input=req.model_dump(),
        metadata={"user_id": req.user_id}
    )

    ticket = TicketState(
        ticket_id=str(uuid.uuid4()),
        user_id=req.user_id,
        title=req.title,
        description=req.description,
    )

    # Run LangGraph workflow
    result = graph.invoke({"ticket": ticket})
    t = result["ticket"]

    # Record workflow result step
    trace.generation(
        name="workflow_output",
        model="orchestrator",
        input=ticket.model_dump(),
        output=t.model_dump()
    )

    # End trace
    trace.end(output=t.model_dump())

    return TicketResponse(
        ticket_id=t.ticket_id,
        status=t.status,
        category=t.category,
        draft_answer=t.draft_answer,
        final_answer=t.final_answer,
        metadata=t.metadata,
        trace_id=trace.id
    )
