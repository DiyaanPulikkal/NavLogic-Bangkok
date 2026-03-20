"""Tests for JWT token creation and decoding."""

import pytest
from fastapi import HTTPException

from auth.jwt import create_access_token, create_refresh_token, decode_token
from auth.hashing import hash_password, verify_password


# ── JWT ──

def test_create_and_decode_access_token():
    token = create_access_token({"sub": "42"})
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    token = create_refresh_token({"sub": "42"})
    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"


def test_decode_wrong_type_raises():
    access_token = create_access_token({"sub": "1"})
    with pytest.raises(HTTPException) as exc_info:
        decode_token(access_token, expected_type="refresh")
    assert exc_info.value.status_code == 401


def test_decode_invalid_token_raises():
    with pytest.raises(HTTPException) as exc_info:
        decode_token("not.a.valid.jwt", expected_type="access")
    assert exc_info.value.status_code == 401


def test_decode_expired_token(monkeypatch):
    from datetime import datetime, timedelta, timezone
    from jose import jwt
    from auth.jwt import SECRET_KEY, ALGORITHM

    expired_payload = {
        "sub": "1",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token, expected_type="access")
    assert exc_info.value.status_code == 401


# ── Password hashing ──

def test_hash_and_verify_password():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert verify_password("mypassword", hashed)
    assert not verify_password("wrong", hashed)

def test_decode_missing_sub_claim():
    token = create_access_token({})
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token, expected_type="access")
    assert exc_info.value.status_code == 401

def test_decode_missing_type_claim():
    from jose import jwt
    from auth.jwt import SECRET_KEY, ALGORITHM

    token = jwt.encode({"sub": "1"}, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException):
        decode_token(token, expected_type="access")

def test_tampered_token():
    token = create_access_token({"sub": "1"})
    tampered = token + "corruption"

    with pytest.raises(HTTPException):
        decode_token(tampered, expected_type="access")

def test_token_not_expired_yet():
    token = create_access_token({"sub": "1"})
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "1"
