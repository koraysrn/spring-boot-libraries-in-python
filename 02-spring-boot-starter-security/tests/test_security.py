"""
Non-happy-path tests for spring-boot-starter-security.
"""

import base64
import json
from datetime import timedelta

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

import security
from main import app, seed_users
from store import user_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_users():
    user_store.reset()
    seed_users()
    yield


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login(username: str, password: str):
    return client.post("/auth/login", data={"username": username, "password": password})


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_none_alg_token() -> str:
    header = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = b64url(json.dumps({"sub": "admin", "role": "ADMIN"}).encode())
    return f"{header}.{payload}."


# --- Non-happy-path tests ---

def test_protected_endpoint_without_token_returns_401():
    response = client.get("/me")
    assert response.status_code == 401


def test_invalid_token_returns_401():
    response = client.get("/me", headers=auth_header("not-a-valid-token"))
    assert response.status_code == 401


def test_expired_token_returns_401():
    expired = security.create_access_token(
        {"sub": "admin"}, expires_delta=timedelta(seconds=-1)
    )
    response = client.get("/me", headers=auth_header(expired))
    assert response.status_code == 401


def test_none_algorithm_token_returns_401():
    response = client.get("/me", headers=auth_header(make_none_alg_token()))
    assert response.status_code == 401


def test_token_signed_with_other_key_returns_401():
    forged = pyjwt.encode(
        {"sub": "admin", "role": "ADMIN"},
        "wrong-signing-key-that-is-long-enough",
        algorithm="HS256",
    )
    response = client.get("/me", headers=auth_header(forged))
    assert response.status_code == 401


def test_wrong_password_and_unknown_user_give_identical_response():
    wrong_password = login("alice", "wrong-password")
    unknown_user = login("unknown-user", "wrong-password")
    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json()["detail"] == unknown_user.json()["detail"]


def test_normal_user_forbidden_from_admin_endpoint():
    token = login("alice", "alicepass123").json()["access_token"]
    response = client.get("/admin/users", headers=auth_header(token))
    assert response.status_code == 403


def test_admin_can_access_normal_endpoint():
    token = login("admin", "adminpass123").json()["access_token"]
    response = client.get("/me", headers=auth_header(token))
    assert response.status_code == 200
    assert response.json()["role"] == "ADMIN"


def test_password_is_stored_hashed():
    client.post(
        "/auth/register",
        json={"username": "newuser", "password": "newpassword123"},
    )
    record = user_store.get_by_username("newuser")
    assert record is not None
    assert record["password_hash"] != "newpassword123"
    assert record["password_hash"].startswith("$2")


def test_same_password_produces_different_hashes():
    client.post(
        "/auth/register",
        json={"username": "user1", "password": "samepassword123"},
    )
    client.post(
        "/auth/register",
        json={"username": "user2", "password": "samepassword123"},
    )
    hash1 = user_store.get_by_username("user1")["password_hash"]
    hash2 = user_store.get_by_username("user2")["password_hash"]
    assert hash1 != hash2


def test_short_password_registration_is_rejected():
    response = client.post(
        "/auth/register",
        json={"username": "shorty", "password": "short"},
    )
    assert response.status_code == 422


def test_token_without_subject_claim_returns_401():
    token = security.create_access_token({"role": "ADMIN"})
    response = client.get("/me", headers=auth_header(token))
    assert response.status_code == 401


def test_same_token_can_be_reused_demonstrates_stateless_behavior():
    # JWT is stateless by design. The same token stays valid until it expires.
    token = login("alice", "alicepass123").json()["access_token"]
    first = client.get("/me", headers=auth_header(token))
    second = client.get("/me", headers=auth_header(token))
    assert first.status_code == second.status_code == 200


def test_duplicate_registration_returns_409():
    first = client.post(
        "/auth/register",
        json={"username": "dup", "password": "password123"},
    )
    second = client.post(
        "/auth/register",
        json={"username": "dup", "password": "password123"},
    )
    assert first.status_code == 201
    assert second.status_code == 409
