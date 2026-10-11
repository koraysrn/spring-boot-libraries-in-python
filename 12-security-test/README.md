# spring-security-test

A Python implementation of the security testing helpers provided by the Spring Boot starter `spring-security-test`. This module uses FastAPI TestClient and dependency overrides as the equivalent of `@WithMockUser`.

## Overview

In Spring Boot, `spring-security-test` simplifies security testing. Annotations such as `@WithMockUser` simulate an authenticated user so that security rules can be tested without a real login.

| Spring Security Test Concept | Python Equivalent |
|---|---|
| @WithMockUser | dependency_overrides |
| SecurityIntegrationTest | this test suite |
| SecurityContext | get_current_user dependency |

## Features

- Test client for making requests without a running server.
- Override of the `get_current_user` dependency to simulate any user.
- Automatic cleanup of overrides after each test.
- Distinction between 401 unauthenticated and 403 forbidden.
- A real JWT login flow for end-to-end tests.

## Project Structure

```
12-security-test/
├── app.py                     # FastAPI app with security dependencies
├── requirements.txt
├── conftest.py                # TestClient and override fixtures
└── tests/
    └── test_security_test.py
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

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that an unauthenticated request to an admin endpoint returns 401, that a normal user is forbidden with 403, that an admin can access the admin endpoint, that overrides are cleaned up between tests, that an invalid role returns 403, that a deleted user with a valid token returns 401, that the last override wins, and that a real JWT flow works end to end.
