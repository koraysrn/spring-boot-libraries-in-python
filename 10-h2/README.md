# h2

A Python implementation of the H2 in-memory test database. This module uses SQLite with an in-memory connection as the equivalent of H2.

## Overview

In Spring Boot, H2 is a small database that runs entirely in memory and requires no files. Tests use it instead of a real PostgreSQL database for speed and isolation. The data disappears when the test finishes.

| H2 Concept | Python Equivalent |
|---|---|
| H2 in-memory database | SQLite `sqlite://` with StaticPool |
| Spring test profile | Fixture creating a fresh schema per test |
| Test isolation | One in-memory engine per test |

## Features

- In-memory SQLite engine shared across connections with StaticPool.
- Fresh schema creation per test through `Base.metadata.create_all`.
- Isolation between tests through separate engines.
- Documentation of the differences between SQLite and PostgreSQL.

## Project Structure

```
10-h2/
├── db.py                    # In-memory engine and declarative base
├── models.py                # Sample Account model
├── requirements.txt
├── conftest.py
└── tests/
    └── test_h2.py
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

The test suite focuses on non-happy-path scenarios. It verifies that two in-memory engines are isolated, that the same scenario runs identically twice, that an exception in one engine does not affect another, that in-memory data is lost when the connection closes, that PostgreSQL specific SQL differs on SQLite, that concurrent writes serialize on SQLite, and that schema creation works on an in-memory database.

## Differences from PostgreSQL

SQLite is not a drop-in replacement for PostgreSQL. Some PostgreSQL features, such as `generate_series`, do not exist in SQLite. SQLite also serializes writers with file locking, while PostgreSQL allows concurrent writers through MVCC. Critical queries must therefore also be tested against the real PostgreSQL database.
