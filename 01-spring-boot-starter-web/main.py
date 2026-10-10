"""
Python (FastAPI) equivalent of the spring-boot-starter-web library.

Spring Boot equivalents:
    - Tomcat     -> Uvicorn (embedded ASGI server)
    - Spring MVC -> FastAPI routes (request routing)
    - Jackson    -> Pydantic + FastAPI's automatic JSON support

This module builds the web layer of a REST API application and is written
to be resilient against non-happy-path scenarios (404, 405, 415, 422, 413,
concurrency).
"""

import threading

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Finance API - Python equivalent of spring-boot-starter-web")

# --- CORS: equivalent of Spring's CORS configuration ---
# Only trusted origins are allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Content-Type enforcement: equivalent of Spring Boot's 415 ---
# Return 415 when a JSON-expecting method receives a non-JSON Content-Type.
JSON_METHODS = {"POST", "PUT", "PATCH"}


@app.middleware("http")
async def enforce_json_content_type(request: Request, call_next):
    if request.method in JSON_METHODS:
        content_type = request.headers.get("content-type", "")
        if content_type and not content_type.startswith("application/json"):
            return JSONResponse(
                status_code=415,
                content={"detail": "Unsupported media type; expected application/json"},
            )
    return await call_next(request)


# --- Request body size limit: DoS protection against oversized requests ---
MAX_BODY_BYTES = 1_000_000  # 1 MB


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"},
                )
        except ValueError:
            pass  # Ignore a malformed Content-Length header
    return await call_next(request)


# --- Global exception handler: never leak stack traces, never crash ---
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )


# --- Models ---
# AccountCreate: the request body sent by the client.
# extra="forbid" -> unknown fields are rejected (mass assignment protection).
class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    balance: float = Field(ge=0)


# Account: the response model returned to the client (bounded via response_model).
class Account(BaseModel):
    id: int
    name: str
    balance: float


# --- In-memory, thread-safe store ---
class AccountStore:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self._accounts = {}
            self._next_id = 1

    def all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        with self._lock:
            items = list(self._accounts.values())
            items.sort(key=lambda a: a["id"])
            return items[skip : skip + limit]

    def count(self) -> int:
        with self._lock:
            return len(self._accounts)

    def get(self, account_id: int) -> dict | None:
        with self._lock:
            return self._accounts.get(account_id)

    def create(self, data: dict) -> dict:
        with self._lock:
            account_id = self._next_id
            self._next_id += 1
            account = {
                "id": account_id,
                "name": data["name"],
                "balance": data["balance"],
            }
            self._accounts[account_id] = account
            return account

    def update(self, account_id: int, data: dict) -> dict | None:
        with self._lock:
            if account_id not in self._accounts:
                return None
            account = {
                "id": account_id,
                "name": data["name"],
                "balance": data["balance"],
            }
            self._accounts[account_id] = account
            return account

    def delete(self, account_id: int) -> bool:
        with self._lock:
            if account_id not in self._accounts:
                return False
            del self._accounts[account_id]
            return True


store = AccountStore()


# --- Endpoints ---
# NOTE: The static route (/accounts/export) is defined BEFORE the dynamic
# route (/accounts/{id}). Otherwise the dynamic route would try to parse
# "export" as an int and return 422.
@app.get("/accounts/export")
def export_accounts():
    return {"exported": True, "format": "csv", "count": store.count()}


@app.get("/accounts", response_model=list[Account])
def list_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    return store.all(skip=skip, limit=limit)


@app.post("/accounts", response_model=Account, status_code=201)
def create_account(payload: AccountCreate):
    return store.create(payload.model_dump())


@app.get("/accounts/{account_id}", response_model=Account)
def get_account(account_id: int):
    account = store.get(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.put("/accounts/{account_id}", response_model=Account)
def update_account(account_id: int, payload: AccountCreate):
    updated = store.update(account_id, payload.model_dump())
    if updated is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated


@app.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: int):
    if not store.delete(account_id):
        raise HTTPException(status_code=404, detail="Account not found")
