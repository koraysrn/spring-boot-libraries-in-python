# shedlock-spring and shedlock-provider-jdbc-template

A Python implementation of ShedLock, the distributed lock for scheduled jobs. This module prevents a scheduled task from running on multiple nodes at the same time by storing a lock in a database table.

## Overview

In Spring Boot, ShedLock prevents scheduled jobs from running more than once when the application runs on several servers. Before a job runs, it writes a lock to the database. Other servers see the lock and skip the job.

| ShedLock Concept | Python Equivalent |
|---|---|
| ShedLock | `ShedLock` class |
| @SchedulerLock(name=...) | `acquire` and `release` around the task |
| lockAtMostFor | `lock_for_seconds` |
| shedlock-provider-jdbc | The `shedlock` database table |
| @Scheduled | APScheduler cron job |

## Features

- Atomic lock acquisition with a single UPSERT statement.
- Lock expiry through `lock_until`, so a crashed node cannot hold a lock forever.
- Owner tracking through `locked_by`.
- Lock release in a `finally` block, even when the task raises.
- Expired lock cleanup.
- Injection of the clock for deterministic clock skew testing.
- APScheduler integration with a cron trigger.

## Project Structure

```
07-shedlock/
├── lock.py                # ShedLock implementation
├── scheduler.py           # Scheduled task wiring
├── requirements.txt
├── conftest.py
└── tests/
    └── test_shedlock.py
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

## Usage

```python
from lock import ShedLock
from scheduler import run_task_with_lock
from sqlalchemy import create_engine

engine = create_engine("sqlite:///shedlock.db")
lock = ShedLock(engine)

def create_invoices():
    pass

run_task_with_lock(lock, "daily-invoice", "node-1", create_invoices)
```

The `shedlock` table has these columns:

| Column | Purpose |
|---|---|
| name | Unique task name, the lock key |
| lock_until | Expiry timestamp |
| locked_at | When the lock was acquired |
| locked_by | Which node holds the lock |

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that a second worker skips when a lock is held, that concurrent workers resolve to exactly one winner, that an expired lock allows a new owner, that a raised exception releases the lock, that a missing table raises a clear error, that expired locks are cleaned up, that different names use separate locks, that rapid reacquire attempts are handled, that clock skew affects lock acquisition, that a long running task loses its lock after expiry, and that a shutdown interrupt releases the lock.
