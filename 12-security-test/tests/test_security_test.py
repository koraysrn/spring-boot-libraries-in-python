"""
Non-happy-path tests for the spring-security-test equivalent.
"""

import app as app_module
from app import app


def test_unauthenticated_request_to_admin_returns_401(client):
    response = client.get("/admin/users")
    assert response.status_code == 401


def test_normal_user_forbidden_from_admin(client, override_current_user):
    override_current_user({"username": "alice", "role": "USER"})
    response = client.get("/admin/users")
    assert response.status_code == 403


def test_admin_can_access_admin_endpoint(client, override_current_user):
    override_current_user({"username": "admin", "role": "ADMIN"})
    response = client.get("/admin/users")
    assert response.status_code == 200


def test_override_active_within_test(client, override_current_user):
    override_current_user({"username": "admin", "role": "ADMIN"})
    assert client.get("/admin/users").status_code == 200


def test_override_cleaned_up_after_test(client):
    # The fixture cleared the override, so the request is unauthenticated.
    assert client.get("/admin/users").status_code == 401


def test_invalid_role_returns_403(client, override_current_user):
    override_current_user({"username": "x", "role": "SUPERMAN"})
    assert client.get("/admin/users").status_code == 403


def test_deleted_user_with_valid_token_returns_401(client):
    login_response = client.post("/auth/login", json={"username": "alice"})
    token = login_response.json()["access_token"]

    del app_module.USERS["alice"]
    try:
        response = client.get(
            "/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
    finally:
        app_module.USERS["alice"] = {"username": "alice", "role": "USER"}


def test_last_override_wins_and_cleanup_resets(client, override_current_user):
    override_current_user({"username": "a", "role": "USER"})
    override_current_user({"username": "admin", "role": "ADMIN"})
    assert client.get("/admin/users").status_code == 200


def test_real_jwt_end_to_end(client):
    login_response = client.post("/auth/login", json={"username": "admin"})
    token = login_response.json()["access_token"]

    admin_response = client.get(
        "/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert admin_response.status_code == 200

    me_response = client.get(
        "/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
