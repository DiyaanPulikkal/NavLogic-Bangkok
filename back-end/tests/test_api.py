import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

import app as app_module
from engine.orchestrator import Orchestrator


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


def test_post_query(client):
    from tests.helpers import StubLLM
    client.app.state.orchestrator.llm = StubLLM(
        ("find_route", {"start": "Siam", "end": "Asok"})
    )
    resp = client.post("/api/query", json={"message": "route from Siam to Asok"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "route"
    assert data["data"]["from"] == "Siam (CEN)"
