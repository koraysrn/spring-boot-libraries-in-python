# postgresql (JDBC driver)

A Python implementation of the PostgreSQL database driver provided by the `postgresql` JDBC driver in Spring Boot. This module manages connection configuration, connection pooling, and safe query execution using psycopg.

## Overview

In Spring Boot, the `postgresql` dependency is the JDBC driver that lets the Java application talk to a PostgreSQL database. It acts as a translator between Java and PostgreSQL, connecting through a URL such as `jdbc:postgresql://localhost:5432/finans`.

| JDBC Concept | Python Equivalent |
|---|---|
| postgresql JDBC driver | psycopg |
| jdbc:postgresql:// URL | DSN built from environment variables |
| HikariCP connection pool | SQLAlchemy pool settings |
| SSL connection | `sslmode=require` |
| Prepared statements | Parameterized queries |

## Features

- Connection string built from environment variables, never hardcoded.
- SSL mode required by default.
- Connection timeout configured to avoid infinite hangs.
- Connection pool with `pool_size`, `max_overflow`, and `pool_pre_ping`.
- Engine creation that does not open a connection until first use.
- Parameterized queries that neutralize SQL injection.
- Streaming support for large result sets.

## Project Structure

```
06-postgresql-driver/
├── db.py                         # Driver configuration and helpers
├── requirements.txt
├── conftest.py
└── tests/
    └── test_postgresql_driver.py
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

## Configuration

The connection is configured through environment variables:

| Variable | Default | Purpose |
|---|---|---|
| DB_HOST | localhost | Database host |
| DB_PORT | 5432 | Database port |
| DB_NAME | finans | Database name |
| DB_USER | postgres | Database user |
| DB_PASSWORD | empty | Database password |
| DB_SSLMODE | require | SSL mode |
| DB_CONNECT_TIMEOUT | 10 | Connection timeout in seconds |

## Testing

```bash
pytest -v
```

Connection failure tests target an unused local port, so they run without a live PostgreSQL server. They verify that a down database, wrong credentials, and a wrong database name all raise an `OperationalError` quickly without hanging. Driver-agnostic safety behaviors are exercised through an in-memory SQLite engine as a stand-in: pool exhaustion raises a timeout, large result sets can be streamed, parameterized queries neutralize SQL injection, Unicode data roundtrips, and unclosed connections are detected when the pool is exhausted.
