"""
Non-happy-path tests for spring-boot-starter-validation.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from main import app
from schemas import (
    AccountUpdate,
    ArbitraryPayload,
    ProfileUpdate,
    RegisterRequest,
    TransactionRequest,
)

client = TestClient(app)

VALID_PASSWORD = "StrongPass1"


# --- Non-happy-path tests ---

def test_invalid_email_rejected():
    with pytest.raises(ValidationError):
        RegisterRequest(email="ali@", password=VALID_PASSWORD)


def test_short_password_rejected():
    with pytest.raises(ValidationError):
        RegisterRequest(email="ali@example.com", password="Short1")  # 6 chars


def test_long_password_rejected():
    with pytest.raises(ValidationError):
        RegisterRequest(email="ali@example.com", password="A" * 65)


def test_negative_amount_rejected():
    with pytest.raises(ValidationError):
        TransactionRequest(amount=-5)


def test_empty_email_rejected():
    with pytest.raises(ValidationError):
        RegisterRequest(email="", password=VALID_PASSWORD)


def test_missing_required_field_rejected():
    with pytest.raises(ValidationError):
        RegisterRequest(email="ali@example.com")  # password is missing


def test_extra_unknown_field_rejected():
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="ali@example.com",
            password=VALID_PASSWORD,
            is_admin=True,
        )


def test_password_without_uppercase_rejected():
    with pytest.raises(ValidationError):
        RegisterRequest(email="ali@example.com", password="lowercase1")


def test_email_with_spaces_is_normalized():
    request = RegisterRequest(email=" ALI@X.COM ", password=VALID_PASSWORD)
    assert request.email == "ali@x.com"


def test_numeric_field_with_string_rejected():
    with pytest.raises(ValidationError):
        TransactionRequest(amount="yuz")


def test_deeply_nested_json_does_not_crash():
    nested = "leaf"
    for _ in range(1000):
        nested = {"nested": nested}
    model = ArbitraryPayload(data=nested)
    assert model.data is not None


def test_unicode_is_normalized_and_emoji_accepted():
    normalized = ProfileUpdate(display_name="Ａｌｉ")
    assert normalized.display_name == "Ali"

    emoji = ProfileUpdate(display_name="Ali 😀")
    assert emoji.display_name == "Ali 😀"


def test_partial_update_allows_missing_optional_fields():
    update = AccountUpdate(balance=100.0)
    assert update.name is None
    assert update.balance == 100.0


# --- API level checks: FastAPI returns 422 automatically ---

def test_api_invalid_email_returns_422():
    response = client.post(
        "/auth/register",
        json={"email": "ali@", "password": "StrongPass1"},
    )
    assert response.status_code == 422


def test_api_negative_amount_returns_422():
    response = client.post("/transactions", json={"amount": -5})
    assert response.status_code == 422
