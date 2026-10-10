# spring-boot-starter-security

A Python implementation of the security layer provided by the Spring Boot starter `spring-boot-starter-security`. This module delivers authentication, authorization, password hashing, and JWT issuance and validation using FastAPI dependencies, bcrypt, and PyJWT.

## Overview

In Spring Boot, `spring-boot-starter-security` acts as the application firewall. It answers two core questions:

- Authentication: who is this user?
- Authorization: what is this user allowed to do?

The table below maps each Spring Security concept to its Python equivalent used in this module.

| Spring Security Concept | Python Equivalent |
|---|---|
| SecurityFilterChain | FastAPI dependencies |
| Authentication | JWT bearer tokens and user lookup |
| Authorization | Role based dependency checks |
| BCryptPasswordEncoder | bcrypt library |
| UsernamePasswordAuthenticationFilter | `/auth/login` endpoint |

## Features

- User registration with password validation.
- Password hashing with bcrypt, including a random salt per hash.
- Login endpoint that returns a signed JWT access token.
- JWT validation that rejects expired, malformed, `alg=none`, and wrongly signed tokens.
- Protected endpoints requiring a valid bearer token.
- Role based authorization with a 403 response for insufficient permissions.
- Identical error responses for wrong passwords and unknown users to prevent username enumeration.
- Timing equalization on the login endpoint to reduce timing side channels.
- Secret key loaded from the environment variable `SECRET_KEY`.

## Project Structure

```
02-spring-boot-starter-security/
├── main.py                 # Application entry point and endpoints
├── security.py             # Hashing, JWT, and security dependencies
├── store.py                # Thread-safe in-memory user store
├── models.py               # Pydantic request and response models
├── requirements.txt        # Dependencies
├── conftest.py             # Test path configuration
└── tests/
    └── test_security.py    # Non-happy-path test suite
```

## Requirements

- Python 3.12 or newer
- pip

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Set the signing key before running the server:

```bash
set SECRET_KEY=your-secret-key   # Windows cmd
```

## Running the Server

```bash
uvicorn main:app --reload
```

The server starts at `http://127.0.0.1:8000`. The interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## API Endpoints

| Method | Path | Authentication | Description |
|---|---|---|---|
| GET | `/public` | None | Public endpoint |
| POST | `/auth/register` | None | Creates a user account |
| POST | `/auth/login` | None | Authenticates and returns a JWT |
| GET | `/me` | Required | Returns the current user |
| GET | `/admin/users` | Admin role | Lists all users |

### Seeded users

| Username | Password | Role |
|---|---|---|
| admin | adminpass123 | ADMIN |
| alice | alicepass123 | USER |

### Register request

| Field | Type | Constraints |
|---|---|---|
| username | string | 3 to 50 characters |
| password | string | 8 to 72 characters |

The password is capped at 72 characters because bcrypt truncates input at 72 bytes.

### Authentication flow

1. Send a POST request to `/auth/login` with form fields `username` and `password`.
2. The response contains an `access_token`.
3. Send the token in the `Authorization: Bearer <token>` header for protected endpoints.

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that the service rejects missing, malformed, expired, `alg=none`, and wrongly signed tokens, that role checks return 403 for insufficient permissions, that passwords are stored only as hashes with unique salts, and that wrong passwords and unknown users produce identical error responses.
