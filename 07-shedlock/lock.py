"""Distributed lock for scheduled jobs, the equivalent of ShedLock.

Spring Boot equivalents:
    - ShedLock                     -> ShedLock
    - @SchedulerLock(name=...)     -> acquire / release around the task
    - lockAtMostFor                -> lock_for_seconds
    - shedlock-provider-jdbc       -> the shedlock table in a database
"""

import time

from sqlalchemy import text


class ShedLock:
    def __init__(self, engine, clock=time.time):
        self.engine = engine
        self.clock = clock
        self._create_table()

    def _create_table(self):
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS shedlock ("
                    "name TEXT PRIMARY KEY, "
                    "lock_until REAL NOT NULL, "
                    "locked_at REAL NOT NULL, "
                    "locked_by TEXT NOT NULL)"
                )
            )

    def acquire(self, name: str, owner: str, lock_for_seconds: float = 30) -> bool:
        """Atomically acquire the lock.

        A single UPSERT statement guarantees that only one owner can hold a
        given lock at a time. An existing lock is overwritten only when it has
        expired.
        """
        now = self.clock()
        until = now + lock_for_seconds
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO shedlock (name, lock_until, locked_at, locked_by) "
                    "VALUES (:name, :until, :now, :owner) "
                    "ON CONFLICT(name) DO UPDATE SET "
                    "lock_until = excluded.lock_until, "
                    "locked_at = excluded.locked_at, "
                    "locked_by = excluded.locked_by "
                    "WHERE shedlock.lock_until <= :now"
                ),
                {"name": name, "until": until, "now": now, "owner": owner},
            )
            locked_by = conn.execute(
                text("SELECT locked_by FROM shedlock WHERE name = :name"),
                {"name": name},
            ).scalar()
            return locked_by == owner

    def release(self, name: str, owner: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("DELETE FROM shedlock WHERE name = :name AND locked_by = :owner"),
                {"name": name, "owner": owner},
            )

    def is_locked(self, name: str) -> bool:
        with self.engine.connect() as conn:
            lock_until = conn.execute(
                text("SELECT lock_until FROM shedlock WHERE name = :name"),
                {"name": name},
            ).scalar()
            if lock_until is None:
                return False
            return lock_until > self.clock()

    def cleanup_expired(self) -> int:
        with self.engine.begin() as conn:
            result = conn.execute(
                text("DELETE FROM shedlock WHERE lock_until <= :now"),
                {"now": self.clock()},
            )
            return result.rowcount
