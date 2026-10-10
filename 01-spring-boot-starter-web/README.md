# 01 - spring-boot-starter-web (Python: FastAPI + Uvicorn + Pydantic)

## What does the Spring Boot side do?

It gives the application **web server capabilities**:

| Spring Boot Component | Purpose | Python Equivalent |
|---|---|---|
| Tomcat | Embedded web server | Uvicorn (ASGI server) |
| Spring MVC | Routes HTTP requests to the right method | FastAPI routes |
| Jackson | Java object <-> JSON conversion | Pydantic + FastAPI automatic JSON |

## Files

- [`main.py`](main.py) — Application (endpoints, CORS, body limit, exception handler, in-memory store)
- [`tests/test_web.py`](tests/test_web.py) — 15 non-happy-path tests
- [`requirements.txt`](requirements.txt) — Dependencies
- [`conftest.py`](conftest.py) — Test path setup

## Setup and run

```bash
cd 01-spring-boot-starter-web
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt

# Run the server (Uvicorn is the Tomcat equivalent)
uvicorn main:app --reload

# Run the tests
pytest -v
```

## TODO list status

- [x] Installed FastAPI and Uvicorn via `pip install "fastapi[standard]"`
- [x] Created a `FastAPI()` application instance in `main.py`
- [x] Defined the `Account` Pydantic model (`id`, `name`, `balance`)
- [x] Wrote the `GET /accounts` endpoint (with pagination)
- [x] Wrote the `GET /accounts/{id}` endpoint (returns 404 when missing)
- [x] Wrote the `POST /accounts` endpoint (with body validation)
- [x] Added `PUT` and `DELETE` endpoints
- [x] Ready to run with `uvicorn main:app --reload`
- [x] Unknown URL returns 404
- [x] Wrong HTTP method returns 405

## Applied safeguards

- **Static route defined first:** `/accounts/export` comes before `/accounts/{id}`, so the word "export" is never parsed as an int.
- **Type coercion:** `{id}` is typed as int; `GET /accounts/abc` -> 422.
- **`extra="forbid"`:** Unknown fields are rejected (mass assignment protection).
- **Content-Type enforcement:** Non-`application/json` Content-Type on JSON methods -> 415 (Spring Boot's 415 equivalent).
- **Request body size limit:** Over 1 MB -> 413 (DoS protection).
- **Global exception handler:** Never leaks stack traces, never crashes.
- **CORS:** Only trusted origins are allowed.
- **Pagination:** `skip`/`limit` parameters, `limit` capped at 100; exceeding it returns 422.
