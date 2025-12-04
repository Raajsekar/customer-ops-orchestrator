from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import os

# ENV
from dotenv import load_dotenv
load_dotenv()

print(">>> Loaded ENV. DISABLE_AWS =", os.getenv("DISABLE_AWS"))

# --- Langfuse (CORRECT USAGE) ---
from langfuse import Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL")
)

# --- Internal Modules ---
from ..models.ticket_state import TicketState
from ..graph.workflow import build_graph

# FastAPI App
app = FastAPI(
    title="Customer Operations Orchestrator",
    version="1.0.0",
    description="Multi-agent workflow: Classifier → Resolver → Verifier",
)

graph = build_graph()


# -------------------------------
# MODELS
# -------------------------------
class CreateTicketRequest(BaseModel):
    user_id: str | None = None
    title: str
    description: str

class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    category: str | None
    draft_answer: str | None
    final_answer: str | None
    metadata: dict | None
    trace_id: str | None


# -------------------------------
@app.get("/")
def root():
    return {
        "message": "Customer Ops Orchestrator is running!",
        "endpoints": ["/health", "/tickets", "/docs"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------------
# MAIN WORKFLOW
# -------------------------------
@app.post("/tickets", response_model=TicketResponse)
def create_ticket(req: CreateTicketRequest):

    # Create trace properly
    trace_id = str(uuid.uuid4())
    trace = langfuse.trace.create(
        id=trace_id,
        name="ticket_flow",
        input=req.model_dump(),
        metadata={"user_id": req.user_id}
    )

    # Build ticket object
    ticket = TicketState(
        ticket_id=str(uuid.uuid4()),
        user_id=req.user_id,
        title=req.title,
        description=req.description,
    )

    # Run graph
    result = graph.invoke({"ticket": ticket})
    t = result["ticket"]

    # End trace
    trace.update(output=t.model_dump())
    langfuse.flush()

    return TicketResponse(
        ticket_id=t.ticket_id,
        status=t.status,
        category=t.category,
        draft_answer=t.draft_answer,
        final_answer=t.final_answer,
        metadata=t.metadata,
        trace_id=trace_id
    )
