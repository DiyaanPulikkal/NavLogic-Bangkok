"""Tests for conversations CRUD endpoints."""


def test_create_conversation(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/conversations",
        json={"title": "My Trip"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "My Trip"
    assert "id" in data


def test_create_conversation_default_title(auth_client, auth_headers):
    resp = auth_client.post(
        "/api/conversations",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New conversation"


def test_create_conversation_unauthenticated(auth_client):
    resp = auth_client.post("/api/conversations", json={"title": "test"})
    assert resp.status_code in (401, 403)


def test_list_conversations_empty(auth_client, auth_headers):
    resp = auth_client.get("/api/conversations", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_conversations(auth_client, auth_headers):
    auth_client.post("/api/conversations", json={"title": "First"}, headers=auth_headers)
    auth_client.post("/api/conversations", json={"title": "Second"}, headers=auth_headers)

    resp = auth_client.get("/api/conversations", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_get_conversation(auth_client, auth_headers):
    create_resp = auth_client.post(
        "/api/conversations",
        json={"title": "Details"},
        headers=auth_headers,
    )
    conv_id = create_resp.json()["id"]

    resp = auth_client.get(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Details"
    assert data["messages"] == []


def test_get_conversation_not_found(auth_client, auth_headers):
    resp = auth_client.get("/api/conversations/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_rename_conversation(auth_client, auth_headers):
    create_resp = auth_client.post(
        "/api/conversations",
        json={"title": "Old Title"},
        headers=auth_headers,
    )
    conv_id = create_resp.json()["id"]

    resp = auth_client.patch(
        f"/api/conversations/{conv_id}",
        json={"title": "New Title"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


def test_rename_conversation_not_found(auth_client, auth_headers):
    resp = auth_client.patch(
        "/api/conversations/9999",
        json={"title": "New Title"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_delete_conversation(auth_client, auth_headers):
    create_resp = auth_client.post(
        "/api/conversations",
        json={"title": "To Delete"},
        headers=auth_headers,
    )
    conv_id = create_resp.json()["id"]

    resp = auth_client.delete(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert resp.status_code == 204

    # Verify it's gone
    resp = auth_client.get(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_conversation_not_found(auth_client, auth_headers):
    resp = auth_client.delete("/api/conversations/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_conversation_isolation(auth_client, db_session):
    """User A cannot access User B's conversations."""
    from db import crud
    from auth.hashing import hash_password
    from auth.jwt import create_access_token

    user_a = crud.create_user(db_session, "a@example.com", hash_password("pass"))
    user_b = crud.create_user(db_session, "b@example.com", hash_password("pass"))

    headers_a = {"Authorization": f"Bearer {create_access_token({'sub': str(user_a.id)})}"}
    headers_b = {"Authorization": f"Bearer {create_access_token({'sub': str(user_b.id)})}"}

    # User A creates a conversation
    resp = auth_client.post("/api/conversations", json={"title": "A's chat"}, headers=headers_a)
    conv_id = resp.json()["id"]

    # User B cannot see it
    resp = auth_client.get(f"/api/conversations/{conv_id}", headers=headers_b)
    assert resp.status_code == 404

    # User B's list is empty
    resp = auth_client.get("/api/conversations", headers=headers_b)
    assert resp.json() == []
