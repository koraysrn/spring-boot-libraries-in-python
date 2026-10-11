# spring-boot-starter-validation

A Python implementation of the validation layer provided by the Spring Boot starter `spring-boot-starter-validation`. This module validates incoming data before it reaches the application or database using Pydantic.

## Overview

In Spring Boot, `spring-boot-starter-validation` checks user input before it reaches the database. Rules are declared with annotations such as `@NotBlank`, `@Email`, and `@Min`, and invalid data produces an automatic error response.

| Spring Validation Concept | Python Equivalent |
|---|---|
| @NotBlank, @Size | `Field` constraints |
| @Email | `EmailStr` |
| @Min | `Field(ge=0)` |
| @Pattern | `Field(pattern=...)` or `field_validator` |
| Custom validator | `@field_validator` |
| @Valid on a DTO | FastAPI body model |

## Features

- Email validation with `EmailStr`.
- Password length constraints and a custom uppercase rule.
- Numeric fields constrained to zero or greater.
- Unknown fields rejected with `extra="forbid"`.
- Email normalization that strips whitespace and lowercases the value.
- Unicode normalization with NFKC for display names.
- Partial update models where every field is optional.
- Automatic 422 responses from FastAPI on invalid input.

## Project Structure

```
04-spring-boot-starter-validation/
├── schemas.py               # Pydantic validation models
├── main.py                  # REST API entry point
├── requirements.txt         # Dependencies
├── conftest.py              # Test path configuration
└── tests/
    └── test_validation.py   # Non-happy-path test suite
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

## Running the Server

```bash
uvicorn main:app --reload
```

## Models

### RegisterRequest

| Field | Type | Constraints |
|---|---|---|
| email | EmailStr | Valid email, normalized to lowercase without surrounding spaces |
| password | string | 8 to 64 characters, at least one uppercase letter |

### TransactionRequest

| Field | Type | Constraints |
|---|---|---|
| amount | float | Zero or greater |
| description | string | Up to 255 characters |

### AccountUpdate

| Field | Type | Constraints |
|---|---|---|
| name | optional string | 1 to 100 characters |
| balance | optional float | Zero or greater |

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that invalid emails, short and long passwords, negative amounts, empty strings, missing fields, unknown fields, passwords without an uppercase letter, and non-numeric values are all rejected. It also verifies that whitespace around an email is normalized, that deeply nested JSON does not crash the parser, that Unicode is normalized with NFKC, and that partial updates accept missing optional fields.
