
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_create_ticket_flow():
    payload = {
        "user_id": "u1",
        "title": "VPN not working",
        "description": "I cannot connect to company VPN from home."
    }
    resp = client.post("/tickets", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("RESOLVED", "FAILED")
    assert body["ticket_id"]
