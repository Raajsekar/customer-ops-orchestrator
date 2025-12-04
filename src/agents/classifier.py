from pydantic import BaseModel
from typing import Optional
import os

from ..llm.bedrock_client import call_mistral_large

ALLOWED_CATEGORIES = ["HR", "TECH", "FINANCE"]

USE_BEDROCK = os.getenv("USE_BEDROCK_CLASSIFIER", "false").lower() == "true"


class ClassificationResult(BaseModel):
    category: str
    reasoning: str


def classify_ticket(title: str, description: str) -> ClassificationResult:
    text = (title + " " + description).lower()

    if USE_BEDROCK:
        prompt = (
            "You are a classifier for support tickets. "
            "Return only one word: HR, TECH, or FINANCE.\n\n"
            f"Title: {title}\nDescription: {description}\n"
        )
        raw = call_mistral_large(prompt)

        cat = "TECH"
        for c in ALLOWED_CATEGORIES:
            if c.lower() in raw.lower():
                cat = c
                break

        return ClassificationResult(
            category=cat,
            reasoning=f"Bedrock Mistral output: {raw[:200]}",
        )

    # Fallback: keyword-based (works with no Bedrock)
    if any(k in text for k in ["salary", "leave", "vacation", "policy", "offer letter"]):
        cat = "HR"
    elif any(k in text for k in ["invoice", "payment", "refund", "bill", "reimbursement"]):
        cat = "FINANCE"
    else:
        cat = "TECH"

    return ClassificationResult(
        category=cat,
        reasoning="Simple keyword-based classifier.",
    )
