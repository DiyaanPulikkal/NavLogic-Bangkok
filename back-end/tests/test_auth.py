"""Tests for auth endpoints: register, login, refresh."""


def test_register_success(auth_client):
    resp = auth_client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_duplicate_email(auth_client, test_user):
    resp = auth_client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "anything",
    })
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"]


def test_register_invalid_email(auth_client):
    resp = auth_client.post("/api/auth/register", json={
        "email": "not-an-email",
        "password": "secret123",
    })
    assert resp.status_code == 422


def test_login_success(auth_client, test_user):
    _, password = test_user
    resp = auth_client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": password,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(auth_client, test_user):
    resp = auth_client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.json()["detail"]


def test_login_nonexistent_user(auth_client):
    resp = auth_client.post("/api/auth/login", json={
        "email": "nobody@example.com",
        "password": "anything",
    })
    assert resp.status_code == 401


def test_refresh_success(auth_client, test_user):
    _, password = test_user
    login_resp = auth_client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": password,
    })
    refresh_token = login_resp.json()["refresh_token"]

    resp = auth_client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_with_access_token_fails(auth_client, test_user):
    _, password = test_user
    login_resp = auth_client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": password,
    })
    access_token = login_resp.json()["access_token"]

    resp = auth_client.post("/api/auth/refresh", json={
        "refresh_token": access_token,
    })
    assert resp.status_code == 401


def test_refresh_invalid_token(auth_client):
    resp = auth_client.post("/api/auth/refresh", json={
        "refresh_token": "not.a.valid.token",
    })
    assert resp.status_code == 401

def test_register_missing_fields(auth_client):
    resp = auth_client.post("/api/auth/register", json={})
    assert resp.status_code == 422

def test_register_empty_password(auth_client):
    resp = auth_client.post("/api/auth/register", json={
        "email": "user@example.com",
        "password": "",
    })
    assert resp.status_code == 422

def test_refresh_token_reuse(auth_client, test_user):
    _, password = test_user
    login_resp = auth_client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": password,
    })

    refresh_token = login_resp.json()["refresh_token"]

    # First use
    resp1 = auth_client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp1.status_code == 200

    # Second use (depends on your design)
    resp2 = auth_client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token,
    })

    assert resp2.status_code == 200  

def test_login_missing_fields(auth_client):
    resp = auth_client.post("/api/auth/login", json={})
    assert resp.status_code == 422