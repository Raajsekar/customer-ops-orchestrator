
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel

TicketStatus = Literal["NEW", "CLASSIFIED", "IN_PROGRESS", "RESOLVED", "FAILED"]

class TicketState(BaseModel):
    ticket_id: str
    user_id: Optional[str] = None
    title: str
    description: str
    category: Optional[Literal["HR", "TECH", "FINANCE"]] = None
    status: TicketStatus = "NEW"
    draft_answer: Optional[str] = None
    final_answer: Optional[str] = None
    metadata: Dict[str, Any] = {}
    retries: int = 0
