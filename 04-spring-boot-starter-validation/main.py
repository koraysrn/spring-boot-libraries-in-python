"""REST API demonstrating automatic request validation.

This is the Python equivalent of spring-boot-starter-validation. FastAPI
validates the request body against the Pydantic schemas and returns a 422
response automatically when validation fails.
"""

from fastapi import FastAPI

from schemas import AccountUpdate, ProfileUpdate, RegisterRequest, TransactionRequest

app = FastAPI(title="Finance API - Python equivalent of spring-boot-starter-validation")


@app.post("/auth/register")
def register(payload: RegisterRequest):
    return {"email": payload.email, "password_length": len(payload.password)}


@app.post("/transactions")
def create_transaction(payload: TransactionRequest):
    return {"amount": payload.amount, "description": payload.description}


@app.patch("/accounts/{account_id}")
def update_account(account_id: int, payload: AccountUpdate):
    return {"id": account_id, **payload.model_dump(exclude_none=True)}


@app.patch("/profile")
def update_profile(payload: ProfileUpdate):
    return {"display_name": payload.display_name}
