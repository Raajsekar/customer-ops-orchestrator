
from pydantic import BaseModel

class VerificationResult(BaseModel):
    is_approved: bool
    final_answer: str
    reason: str

def verify_answer(title: str, description: str, draft_answer: str) -> VerificationResult:
    if not draft_answer or len(draft_answer.strip()) < 50:
        return VerificationResult(
            is_approved=False,
            final_answer="",
            reason="Draft answer is too short or empty.",
        )

    # Very naive safety check: you can replace with an LLM moderation call.
    lower = draft_answer.lower()
    if any(bad_word in lower for bad_word in ["stupid", "idiot"]):
        return VerificationResult(
            is_approved=False,
            final_answer="",
            reason="Draft contains unprofessional language.",
        )

    return VerificationResult(
        is_approved=True,
        final_answer=draft_answer,
        reason="Draft passes basic length and tone checks.",
    )
