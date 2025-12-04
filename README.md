
# Customer Operations Orchestrator (Project 2)

Multi‑agent customer support workflow using LangGraph (Classifier → Resolver → Verifier).

## Features

- Classifies tickets into **HR / TECH / FINANCE**
- Runs a simple **RAG-style resolver** over a JSON knowledge base
- Verifier approves / rejects draft answers
- Exposes a **FastAPI** endpoint: `POST /tickets`

## Quick start (local, no AWS required)

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
# or
source .venv/bin/activate  # macOS / Linux

pip install -r requirements.txt

uvicorn src.api.main:app --reload
```

Then open: http://127.0.0.1:8000/docs and try `POST /tickets`.

Example payload:

```json
{
  "user_id": "u123",
  "title": "VPN not working",
  "description": "I can't connect to the company VPN from home on Windows."
}
```

## Notes

- This repo is **framework-complete** but uses very simple logic so it can run without paid services.
- You can later plug in:
  - Bedrock / other LLMs inside agents
  - DynamoDB & S3 clients in `src/infra/*`
  - Langfuse / LangSmith in `src/observability/*`
