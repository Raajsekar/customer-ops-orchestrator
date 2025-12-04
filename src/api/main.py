from fastapi import FastAPI, Response
from pydantic import BaseModel
import uuid

from ..models.ticket_state import TicketState
from ..graph.workflow import build_graph
from ..observability.langfuse_client import get_langfuse
from ..observability.langsmith_client import get_langsmith
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Customer Operations Orchestrator",
    version="0.1.0",
    description="Multi-agent ticket workflow: Classifier → Resolver → Verifier",
)

graph = build_graph()
langfuse = get_langfuse()
langsmith = get_langsmith()


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
def create_ticket(req: CreateTicketRequest, response: Response):
    trace_id = str(uuid.uuid4())

    lf_trace = None
    ls_run = None

    if langfuse:
        lf_trace = langfuse.trace(
            name="ticket_flow",
            id=trace_id,
            input=req.model_dump(),
        )

    if langsmith:
        ls_run = langsmith.create_run(
            name="ticket_flow",
            run_type="chain",
            inputs=req.model_dump(),
            id=trace_id,
        )

    ticket = TicketState(
        ticket_id=str(uuid.uuid4()),
        user_id=req.user_id,
        title=req.title,
        description=req.description,
    )

    # Run through LangGraph
    result = graph.invoke({"ticket": ticket})
    t = result["ticket"]

    if lf_trace:
        lf_trace.update(output=t.model_dump())
    if ls_run:
        ls_run.end(outputs=t.model_dump())

    response.headers["X-Trace-Id"] = trace_id

    return TicketResponse(
        ticket_id=t.ticket_id,
        status=t.status,
        category=t.category,
        draft_answer=t.draft_answer,
        final_answer=t.final_answer,
        metadata=t.metadata,
        trace_id=trace_id,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/")
def root():
    return {
        "message": "Customer Ops Orchestrator is running!",
        "endpoints": ["/health", "/tickets", "/docs"]
    }
