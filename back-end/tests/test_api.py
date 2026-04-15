"""
tests/test_api.py — integration tests for FastAPI surface.

Covers the five HTTP endpoints that survived the engine rewrite:

  GET  /api/route       — no-LLM, Dijkstra + steps
  GET  /api/stations    — PrologInterface.get_stations_with_lines
  GET  /api/attractions — PrologInterface.get_all_pois
  POST /api/query       — auth-gated chat (LLM stubbed)
  (Auth and conversation routers live elsewhere; covered by their own tests.)

/api/schedule was removed with the timetable subsystem.
"""

import pytest
from fastapi.testclient import TestClient

import app as app_module


@pytest.fixture
def client(monkeypatch):
    """TestClient with a real Orchestrator (no LLM)."""
    from tests.helpers import OrchestratorNoLLM

    monkeypatch.setattr(app_module, "Orchestrator", OrchestratorNoLLM)
    from app import app
    with TestClient(app) as c:
        yield c


# ==================================================================
# /api/route — pure routing (no auth, no LLM)
# ==================================================================


def test_get_route_success(client):
    resp = client.get("/api/route", params={"start": "Siam", "end": "Asok"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "plan"
    assert data["data"]["origin"] == "Siam (CEN)"
    assert data["data"]["destination"] == "Asok (E4)"
    assert data["data"]["total_time"] > 0
    assert len(data["data"]["steps"]) >= 1


def test_get_route_unknown_origin_returns_404(client):
    resp = client.get("/api/route", params={"start": "Narnia", "end": "Siam"})
    assert resp.status_code == 404
    assert "Narnia" in resp.json()["detail"]


def test_get_route_unknown_destination_returns_404(client):
    resp = client.get("/api/route", params={"start": "Siam", "end": "Narnia"})
    assert resp.status_code == 404


def test_get_route_missing_start_returns_422(client):
    resp = client.get("/api/route", params={"end": "Asok"})
    assert resp.status_code == 422


def test_get_route_missing_end_returns_422(client):
    resp = client.get("/api/route", params={"start": "Siam"})
    assert resp.status_code == 422


def test_get_route_resolves_poi_display_name(client):
    resp = client.get("/api/route", params={"start": "Grand Palace", "end": "Siam"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "plan"
    assert data["data"]["origin"] == "Sanam Chai (BL31)"


# ==================================================================
# /api/stations — data endpoint
# ==================================================================


def test_get_stations_shape(client):
    resp = client.get("/api/stations")
    assert resp.status_code == 200
    stations = resp.json()
    assert isinstance(stations, list) and len(stations) > 0
    for s in stations:
        assert set(s.keys()) == {"name", "lines"}
        assert isinstance(s["lines"], list)


def test_get_stations_has_known_entry(client):
    resp = client.get("/api/stations")
    by_name = {s["name"]: s["lines"] for s in resp.json()}
    assert "Siam (CEN)" in by_name
    assert len(by_name["Siam (CEN)"]) >= 2


# ==================================================================
# /api/attractions — data endpoint
# ==================================================================


def test_get_attractions_shape(client):
    resp = client.get("/api/attractions")
    assert resp.status_code == 200
    attractions = resp.json()
    assert isinstance(attractions, list) and len(attractions) > 0
    for a in attractions:
        assert "name" in a and "station" in a and "tags" in a
        assert isinstance(a["tags"], list)


def test_get_attractions_includes_known_poi(client):
    resp = client.get("/api/attractions")
    names = [a["name"] for a in resp.json()]
    assert any("Grand Palace" in n for n in names)


# ==================================================================
# /api/query — chat (auth-gated, LLM stubbed)
# ==================================================================


def test_post_query_plan_route(auth_client, auth_headers, db_session):
    from tests.helpers import StubLLM
    from db import crud
    from auth.jwt import decode_token

    token = auth_headers["Authorization"].split(" ")[1]
    user_id = decode_token(token, expected_type="access")["sub"]
    conv = crud.create_conversation(db_session, user_id, "Test Chat")

    auth_client.app.state.orchestrator.llm = StubLLM(
        ("plan", {"origin": "Siam", "goal": {"route_to": "Asok"}}),
        answer_text="From Siam to Asok: ~6 min.",
    )

    resp = auth_client.post(
        "/api/query",
        json={"message": "route from Siam to Asok", "conversation_id": conv.id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "plan"
    assert data["data"]["origin"] == "Siam (CEN)"
    assert data["data"]["destination"] == "Asok (E4)"
    assert data["data"]["answer"] == "From Siam to Asok: ~6 min."

    # Both messages persisted; model message carries the full result blob.
    messages = crud.get_messages_for_conversation(db_session, conv.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "model"
    assert messages[1].content == "From Siam to Asok: ~6 min."
    assert messages[1].response_data is not None
    assert messages[1].response_data["type"] == "plan"


def test_post_query_answer_type_persists_text_only(auth_client, auth_headers, db_session):
    """Plain text 'answer' responses should persist the text, not the blob."""
    from tests.helpers import StubLLM
    from db import crud
    from auth.jwt import decode_token

    token = auth_headers["Authorization"].split(" ")[1]
    user_id = decode_token(token, expected_type="access")["sub"]
    conv = crud.create_conversation(db_session, user_id, "Q&A")

    auth_client.app.state.orchestrator.llm = StubLLM("Plain text reply.")

    resp = auth_client.post(
        "/api/query",
        json={"message": "hello", "conversation_id": conv.id},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "answer"

    messages = crud.get_messages_for_conversation(db_session, conv.id)
    assert messages[1].content == "Plain text reply."
    assert messages[1].response_data is None  # no blob for plain answers


def test_post_query_unauthenticated_returns_401_or_403(client):
    resp = client.post(
        "/api/query", json={"message": "hello", "conversation_id": 1}
    )
    assert resp.status_code in (401, 403)


def test_post_query_invalid_conversation_returns_404(auth_client, auth_headers):
    from tests.helpers import StubLLM

    auth_client.app.state.orchestrator.llm = StubLLM(
        ("plan", {"origin": "Siam", "goal": {"route_to": "Asok"}}),
        answer_text="x",
    )

    resp = auth_client.post(
        "/api/query",
        json={"message": "hello", "conversation_id": 99999},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ==================================================================
# Negative: /api/schedule was deleted.
# ==================================================================


def test_schedule_endpoint_is_gone(client):
    resp = client.get(
        "/api/schedule",
        params={"origin": "Siam", "destination": "Asok", "deadline": "09:00"},
    )
    assert resp.status_code == 404
