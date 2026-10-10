# spring-boot-starter-data-jpa

A Python implementation of the data access layer provided by the Spring Boot starter `spring-boot-starter-data-jpa`. This module maps Python classes to database tables and provides repository style data access using SQLAlchemy ORM.

## Overview

In Spring Boot, `spring-boot-starter-data-jpa` simplifies database access. JPA is the standard that maps tables to Java objects, and Hibernate is the tool that actually performs the mapping. Instead of writing SQL, the application calls methods such as `accountRepository.findAll()`.

| Spring Data JPA Concept | Python Equivalent |
|---|---|
| JPA | SQLAlchemy ORM |
| Hibernate | SQLAlchemy engine and Session |
| @Entity | SQLAlchemy mapped class |
| @Table(name="...") | `__tablename__` |
| @OneToMany | `relationship(back_populates=...)` |
| @ManyToMany | `relationship(secondary=...)` |
| JpaRepository | repository functions |
| @Version | `__mapper_args__ = {"version_id_col": "version_id"}` |
| cascade = ALL | `cascade="all, delete-orphan"` |
| @Transactional | Session commit and rollback |

## Features

- Account, Transaction, and Budget entities mapped to tables.
- One-to-many relationship between Account and Transaction.
- Many-to-many relationship between Account and Budget through a junction table.
- Repository functions for create, read, update, and delete operations.
- Eager loading with `selectinload` to avoid the N+1 query problem.
- Optimistic locking through a version column to prevent lost updates.
- Cascading deletes from Account to its transactions.
- Unique and not null constraints enforced at the database level.
- A connection pool that raises a timeout instead of blocking forever.

## Project Structure

```
03-spring-boot-starter-data-jpa/
├── db.py                   # Engine, session factory, and declarative base
├── models.py               # Account, Transaction, and Budget entities
├── repository.py           # Data access functions
├── schemas.py              # Pydantic schemas for the API layer
├── main.py                 # REST API entry point
├── requirements.txt        # Dependencies
├── conftest.py             # Test path configuration
└── tests/
    └── test_data_jpa.py    # Non-happy-path test suite
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

The tests use an in-memory SQLite database, mirroring how Spring Boot tests replace PostgreSQL with the H2 database. For production, set `DATABASE_URL` to a PostgreSQL URL:

```bash
set DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/db
```

This requires the `psycopg` driver, the Python equivalent of the PostgreSQL JDBC driver.

## Running the Server

```bash
uvicorn main:app --reload
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/accounts` | Lists accounts |
| POST | `/accounts` | Creates an account |
| GET | `/accounts/{id}` | Returns a single account |
| DELETE | `/accounts/{id}` | Deletes an account and its transactions |
| POST | `/accounts/{id}/transactions` | Adds a transaction to an account |

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that a missing entity returns `None`, that unique and not null violations raise integrity errors, that oversized strings are rejected by the length constraint, that a failed transaction rolls back every change, that lazy loading after session close raises a clear error, that optimistic locking prevents lost updates, that cascading deletes remove children and junction rows, that eager loading avoids N+1 queries, that the connection pool raises a timeout when exhausted, that invalid types raise a statement error, and that an unavailable database raises an operational error without crashing the application.
