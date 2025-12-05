from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

from langfuse import Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

from ..models.ticket_state import TicketState
from ..graph.workflow import build_graph

app = FastAPI(title="Customer Ops Orchestrator")
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


@app.post("/tickets", response_model=TicketResponse)
def create_ticket(req: CreateTicketRequest):

    # -------- CREATE LANGFUSE TRACE --------
    trace = langfuse.trace.create(
        name="ticket_flow",
        input=req.model_dump(),
        metadata={"user_id": req.user_id},
    )

    ticket = TicketState(
        ticket_id=str(uuid.uuid4()),
        user_id=req.user_id,
        title=req.title,
        description=req.description,
    )

    result = graph.invoke({"ticket": ticket})
    t = result["ticket"]

    # ---- UPDATE TRACE ----
    trace.update(output=t.model_dump())

    return TicketResponse(
        ticket_id=t.ticket_id,
        status=t.status,
        category=t.category,
        draft_answer=t.draft_answer,
        final_answer=t.final_answer,
        metadata=t.metadata,
        trace_id=trace.id
    )
