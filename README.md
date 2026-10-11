# Spring Boot Libraries in Python

A step-by-step reimplementation of the core Spring Boot libraries in Python. The purpose of this repository is not to build a production Python web framework. The purpose is to understand exactly what Spring Boot does under the hood by rebuilding each capability by hand, one library at a time.

## Motivation

Spring Boot starters look like magic. A single line in `pom.xml` brings an embedded web server, an ORM, security, validation, database migrations, scheduled job locking, and code coverage tooling. This repository removes the magic by taking each starter apart and rebuilding its behavior in Python with FastAPI, SQLAlchemy, Pydantic, Alembic, and the Python testing ecosystem.

By rebuilding each library manually, the developer sees what Spring Boot automates and why those automations exist. Every concept that Spring Boot hides behind an annotation or a starter is recreated explicitly in Python.

## Concept Mapping

| Spring Boot Component | Python Equivalent |
|---|---|
| Maven and pom.xml | pip and pyproject.toml |
| spring-boot-starter-web | FastAPI + Uvicorn + Pydantic |
| spring-boot-starter-security | FastAPI Security + JWT + Passlib |
| spring-boot-starter-data-jpa | SQLAlchemy ORM |
| spring-boot-starter-validation | Pydantic |
| Flyway | Alembic |
| PostgreSQL JDBC driver | psycopg and asyncpg |
| ShedLock | APScheduler + lock table |
| commons-csv | built-in csv module |
| Lombok | dataclasses and Pydantic |
| H2 | SQLite in-memory |
| spring-boot-starter-test | pytest + unittest.mock |
| spring-security-test | TestClient + dependency overrides |
| ArchUnit | import-linter |
| spring-boot-maven-plugin | Docker and PyInstaller |
| JaCoCo | coverage.py and pytest-cov |
| PIT (Pitest) | mutmut |

## Repository Structure

Each library lives in its own numbered folder. The numbering follows the order in which the concepts build on each other. For example, the web layer is built first, the data layer builds on the web layer, and security builds on both.

```
spring-boot-libraries-in-python/
├── 01-spring-boot-starter-web/
├── 02-spring-boot-starter-security/
├── 03-spring-boot-starter-data-jpa/
├── 04-spring-boot-starter-validation/
├── 05-flyway/
├── 06-postgresql-driver/
├── 07-shedlock/
├── 08-commons-csv/
├── 09-lombok/
├── 10-h2/
├── 11-spring-boot-starter-test/
├── 12-spring-security-test/
├── 13-archunit/
├── 14-spring-boot-maven-plugin/
├── 15-jacoco/
├── 16-pitest/
└── 17-spring-boot-starter-parent/
```

## Status

| # | Library | Spring Boot Equivalent | Status |
|---|---|---|---|
| 01 | spring-boot-starter-web | REST API, web server, JSON | Completed |
| 02 | spring-boot-starter-security | Authentication and authorization | Completed |
| 03 | spring-boot-starter-data-jpa | Database access (JPA/Hibernate) | Completed |
| 04 | spring-boot-starter-validation | Data validation | Completed |
| 05 | flyway | Database schema version control | Completed |
| 06 | postgresql | PostgreSQL driver | Completed |
| 07 | shedlock | Distributed lock for scheduled jobs | Completed |
| 08 | commons-csv | CSV read/write | Completed |
| 09 | lombok | Boilerplate code generation | Completed |
| 10 | h2 | In-memory test database | Completed |
| 11 | spring-boot-starter-test | Testing tools | Completed |
| 12 | spring-security-test | Security testing tools | Completed |
| 13 | archunit | Architecture rule tests | Completed |
| 14 | spring-boot-maven-plugin | Executable packaging | Planned |
| 15 | jacoco | Code coverage | Planned |
| 16 | pitest | Mutation testing | Planned |
| 17 | spring-boot-starter-parent | Version management | Planned |

## Testing Philosophy

Every library is tested against non-happy-path scenarios. A library is considered working only when it behaves correctly with broken, missing, invalid, and malicious input. A single successful request proves nothing. The quality of the implementation is measured by how it behaves when things go wrong.

Example scenarios covered in library 01:

- A string path parameter returns 422 instead of crashing.
- A missing record returns 404.
- A wrong HTTP method returns 405.
- An empty request body returns 422.
- Malformed JSON returns 422 without crashing the server.
- An unknown request field is rejected with 422.
- An oversized body returns 413.
- One hundred concurrent requests all succeed.
- A wrong content type returns 415.
- Special characters in the URL do not crash the server.

The principle is simple. A happy-path test proves that the library can be installed. Non-happy-path tests prove that the library is actually understood.

## Prerequisites

- Python 3.12 or newer
- pip

## Getting Started

Each library folder is self-contained and has its own `requirements.txt`.

```bash
# Clone the repository
git clone https://github.com/koraysrn/spring-boot-libraries-in-python.git
cd spring-boot-libraries-in-python

# Enter the first library folder
cd 01-spring-boot-starter-web

# Create a virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload

# Run the tests
pytest -v
```

## Library 01: spring-boot-starter-web

This library gives a Spring Boot application its web server capability. It bundles three things:

- Tomcat, an embedded web server.
- Spring MVC, the routing system that maps requests to methods.
- Jackson, the JSON serializer and deserializer.

The Python equivalent builds the same three capabilities with:

- Uvicorn as the embedded ASGI server.
- FastAPI routes as the routing system.
- Pydantic as the JSON validation and serialization layer.

The implementation also adds the protective layers that Spring Boot provides automatically, including content type enforcement, request body size limits, a global exception handler, and CORS configuration.

## Contributing

Contributions follow the repository convention:

- One folder per Spring Boot library.
- All code, comments, docstrings, API error messages, test files, and documentation are written in English.
- Every library must include non-happy-path tests, not only happy-path tests.
- Every library folder includes a README that explains the Spring Boot counterpart.

## License

This project is licensed for learning purposes. A formal license file will be added as the repository grows.
