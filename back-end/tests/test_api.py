import pytest
from fastapi.testclient import TestClient

import app as app_module


@pytest.fixture
def client(monkeypatch):
    """Create a test client with a real Orchestrator (no LLM)."""
    from tests.helpers import OrchestratorNoLLM

    monkeypatch.setattr(app_module, "Orchestrator", OrchestratorNoLLM)
    from app import app
    with TestClient(app) as c:
        yield c


def test_get_route(client):
    resp = client.get("/api/route", params={"start": "Siam", "end": "Asok"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "route"
    assert data["data"]["from"] == "Siam (CEN)"
    assert data["data"]["to"] == "Asok (E4)"


def test_get_route_invalid(client):
    resp = client.get("/api/route", params={"start": "Narnia", "end": "Siam"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "error"


def test_get_stations(client):
    resp = client.get("/api/stations")
    assert resp.status_code == 200
    stations = resp.json()
    assert len(stations) > 0
    assert all("name" in s and "lines" in s for s in stations)


def test_get_attractions(client):
    resp = client.get("/api/attractions")
    assert resp.status_code == 200
    attractions = resp.json()
    assert len(attractions) > 0
    assert all("name" in a and "station" in a for a in attractions)


def test_post_query(auth_client, auth_headers, db_session):
    """POST /api/query requires auth and a valid conversation_id."""
    from tests.helpers import StubLLM
    from db import crud
    from auth.jwt import decode_token

    # Get user from the auth_headers token
    token = auth_headers["Authorization"].split(" ")[1]
    payload = decode_token(token, expected_type="access")
    user_id = payload["sub"]

    # Create a conversation
    conv = crud.create_conversation(db_session, user_id, "Test Chat")

    # Stub the LLM on the test app's orchestrator
    auth_client.app.state.orchestrator.llm = StubLLM(
        ("find_route", {"start": "Siam", "end": "Asok"})
    )

    resp = auth_client.post(
        "/api/query",
        json={"message": "route from Siam to Asok", "conversation_id": conv.id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "route"
    assert data["data"]["from"] == "Siam (CEN)"

    # Verify messages were persisted
    messages = crud.get_messages_for_conversation(db_session, conv.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "model"


def test_post_query_unauthenticated(client):
    resp = client.post("/api/query", json={"message": "hello", "conversation_id": 1})
    assert resp.status_code in (401, 403)

def test_get_route_missing_start(client):
    resp = client.get("/api/route", params={"end": "Asok"})
    assert resp.status_code in (400, 422)

def test_get_schedule(client):
    resp = client.get("/api/schedule", params={
        "origin": "Siam",
        "destination": "Asok",
        "deadline": "09:00"
    })
    assert resp.status_code == 200

def test_post_query_invalid_conversation(auth_client, auth_headers):
    from tests.helpers import StubLLM

    # Stub LLM to prevent crash
    auth_client.app.state.orchestrator.llm = StubLLM(
        ("find_route", {"start": "Siam", "end": "Asok"})
    )

    resp = auth_client.post(
        "/api/query",
        json={"message": "hello", "conversation_id": 99999},
        headers=auth_headers,
    )

    assert resp.status_code in (400, 404)


# ── Schedule endpoint edge cases ──

def test_get_schedule_with_itineraries(client):
    resp = client.get("/api/schedule", params={
        "origin": "Mo Chit",
        "destination": "Siam",
        "deadline": "08:00",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "schedule"
    assert len(data["data"]["itineraries"]) > 0


def test_get_schedule_unknown_origin(client):
    resp = client.get("/api/schedule", params={
        "origin": "Narnia",
        "destination": "Siam",
        "deadline": "08:00",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "error"
    assert "Unknown location" in data["data"]["message"]


def test_get_schedule_unknown_destination(client):
    resp = client.get("/api/schedule", params={
        "origin": "Siam",
        "destination": "Narnia",
        "deadline": "08:00",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "error"


def test_get_schedule_invalid_deadline(client):
    resp = client.get("/api/schedule", params={
        "origin": "Siam",
        "destination": "Asok",
        "deadline": "invalid",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "error"
    assert "Invalid time" in data["data"]["message"]


def test_get_schedule_no_service(client):
    resp = client.get("/api/schedule", params={
        "origin": "Mo Chit",
        "destination": "Siam",
        "deadline": "06:00",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "error"
    assert "No scheduled trips" in data["data"]["message"]