"""
Non-happy-path tests for spring-boot-starter-web.

The goal is not to prove that "it works when everything is fine", but to prove
that the application behaves correctly with broken, missing, invalid and
malicious input.
"""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app, store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_store():
    """Reset the store before every test (test isolation)."""
    store.reset()
    yield


# --- Non-happy-path tests ---

def test_get_account_with_string_id_returns_422():
    response = client.get("/accounts/abc")
    assert response.status_code == 422


def test_get_missing_account_returns_404():
    response = client.get("/accounts/999999")
    assert response.status_code == 404


def test_get_unknown_url_returns_404():
    response = client.get("/unknown-url")
    assert response.status_code == 404


def test_delete_collection_without_id_returns_405():
    response = client.delete("/accounts")
    assert response.status_code == 405


def test_post_empty_body_returns_422():
    response = client.post("/accounts")
    assert response.status_code == 422


def test_post_invalid_json_does_not_crash():
    response = client.post(
        "/accounts",
        content=b"{",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code in (400, 422)


def test_post_unknown_field_is_rejected():
    response = client.post(
        "/accounts",
        json={"name": "Ali", "balance": 10.0, "hacker": True},
    )
    assert response.status_code == 422


def test_large_body_returns_413():
    big_body = b"x" * (2 * 1024 * 1024)  # 2 MB, limit is 1 MB
    response = client.post(
        "/accounts",
        content=big_body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413


def test_many_records_are_paginated():
    for i in range(500):
        store.create({"name": f"User{i}", "balance": 0.0})

    default = client.get("/accounts")
    assert default.status_code == 200
    assert len(default.json()) == 100  # default limit

    fifty = client.get("/accounts", params={"skip": 0, "limit": 50})
    assert len(fifty.json()) == 50

    # A limit above 100 must return an explicit validation error (422).
    capped = client.get("/accounts", params={"limit": 100000})
    assert capped.status_code == 422


def test_100_concurrent_requests():
    async def fire_requests():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as c:
            responses = await asyncio.gather(
                *[c.get("/accounts") for _ in range(100)]
            )
            return responses

    responses = asyncio.run(fire_requests())
    assert all(r.status_code == 200 for r in responses)


def test_wrong_content_type_returns_415():
    response = client.post(
        "/accounts",
        content=b"name=Ali",
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code == 415


def test_negative_id_returns_404():
    response = client.get("/accounts/-1")
    assert response.status_code == 404


def test_special_characters_do_not_crash_server():
    try:
        client.get("/accounts/%00")
    except Exception:
        pass  # An invalid path may be rejected on the client side
    # The server must still be up.
    assert client.get("/accounts").status_code == 200


# --- Additional structural checks ---

def test_static_export_route_is_not_shadowed_by_dynamic_route():
    response = client.get("/accounts/export")
    assert response.status_code == 200
    assert response.json()["format"] == "csv"


def test_create_and_get_roundtrip():
    created = client.post("/accounts", json={"name": "Ali", "balance": 100.0})
    assert created.status_code == 201
    account_id = created.json()["id"]

    fetched = client.get(f"/accounts/{account_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Ali"
