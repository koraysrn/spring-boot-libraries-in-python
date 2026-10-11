# flyway-core and flyway-database-postgresql

A Python implementation of the database schema version control provided by Flyway. This module manages numbered migration files that are applied in order, using Alembic.

## Overview

In Spring Boot, Flyway is the version control system for the database schema. Numbered files such as `V1__init.sql` and `V2__add_column.sql` are applied in order. Flyway does for the database schema what Git does for code.

| Flyway Concept | Python Equivalent |
|---|---|
| flyway-core | Alembic |
| flyway-database-postgresql | SQLAlchemy PostgreSQL dialect |
| `V1__init.sql` | `0001_create_account.py` |
| Flyway checksum | `checksum_guard.py` |
| Flyway schema history table | Alembic `alembic_version` table |

## Features

- Numbered migration files applied in order.
- Reversible migrations with `upgrade()` and `downgrade()`.
- Transactional migrations so a failed migration leaves no partial schema.
- A checksum guard that mimics Flyway's protection against modifying applied migrations.
- Batch mode support for large tables on SQLite.
- A consistent schema even when two processes migrate concurrently.

## Project Structure

```
05-flyway/
├── alembic.ini                 # Alembic configuration
├── alembic/
│   ├── env.py                  # Migration environment
│   ├── script.py.mako          # Migration template
│   └── versions/               # Numbered migration files
│       ├── 0001_create_account.py
│       └── 0002_add_balance_column.py
├── db.py                       # Declarative base
├── models.py                   # Target database schema
├── checksum_guard.py           # Flyway style checksum protection
├── requirements.txt
├── conftest.py
└── tests/
    └── test_flyway.py
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

## Running Migrations

```bash
alembic upgrade head     # apply every migration
alembic downgrade -1     # revert the latest migration
alembic current          # show the current revision
```

The default `sqlalchemy.url` points to a local SQLite database. For PostgreSQL, set the URL to `postgresql+psycopg://user:pass@localhost:5432/db` in `alembic.ini` or through the `DATABASE_URL` environment variable.

## Migrations

| Revision | Description |
|---|---|
| 0001 | Creates the account table |
| 0002 | Adds the balance column |

Every migration implements both `upgrade()` and `downgrade()`. Applied migrations must never be edited; a new migration must be added instead.

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that an empty database applies every migration in order, that a downgrade followed by an upgrade rebuilds the schema, that modifying an applied migration raises a checksum error, that a failing migration is not recorded as applied, that duplicate revisions raise a conflict, that a missing migration file is not silently skipped, that adding a not null column without a default fails on a populated table, that a migration without a downgrade cannot be reverted, that batch mode handles large tables, and that concurrent upgrades serialized by a lock leave a consistent schema.

SQLite through SQLAlchemy does not roll back DDL statements, so a failing migration can leave partial DDL behind on SQLite. On PostgreSQL, which is Flyway's target database, transactional DDL rolls back the entire failing migration.
