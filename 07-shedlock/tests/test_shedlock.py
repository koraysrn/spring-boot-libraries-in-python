"""
Non-happy-path tests for the ShedLock equivalent (distributed lock).
"""

import threading
import time

import pytest
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from lock import ShedLock
from scheduler import create_scheduler, run_task_with_lock


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield eng
    eng.dispose()


@pytest.fixture
def lock(engine):
    return ShedLock(engine)


# --- Non-happy-path tests ---

def test_second_worker_skips_when_locked(lock):
    assert lock.acquire("fatura", "node-1") is True
    assert lock.acquire("fatura", "node-2") is False


def test_concurrent_workers_only_one_wins(tmp_path):
    eng = create_engine(
        f"sqlite:///{tmp_path / 'lock.db'}",
        connect_args={"check_same_thread": False, "timeout": 5},
    )
    lock = ShedLock(eng)
    results = []
    barrier = threading.Barrier(2)

    def worker(owner):
        barrier.wait()
        results.append(lock.acquire("job", owner))

    threads = [threading.Thread(target=worker, args=(f"node-{i}",)) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count(True) == 1
    eng.dispose()


def test_expired_lock_allows_new_owner(lock):
    assert lock.acquire("fatura", "node-1", lock_for_seconds=30) is True
    with lock.engine.begin() as conn:
        conn.execute(
            text("UPDATE shedlock SET lock_until = :past WHERE name = 'fatura'"),
            {"past": time.time() - 10},
        )
    assert lock.acquire("fatura", "node-2", lock_for_seconds=30) is True


def test_lock_is_released_when_task_raises(lock):
    def task():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        run_task_with_lock(lock, "fatura", "node-1", task)
    assert lock.acquire("fatura", "node-2") is True


def test_acquire_raises_when_table_missing(lock):
    with lock.engine.begin() as conn:
        conn.execute(text("DROP TABLE shedlock"))
    with pytest.raises(sqlalchemy.exc.OperationalError):
        lock.acquire("fatura", "node-1")


def test_expired_locks_are_cleaned_up(lock):
    lock.acquire("old", "node-1", lock_for_seconds=0)
    lock.acquire("active", "node-1", lock_for_seconds=60)

    removed = lock.cleanup_expired()

    assert removed == 1
    assert lock.is_locked("active") is True
    assert lock.is_locked("old") is False


def test_different_names_use_separate_locks(lock):
    assert lock.acquire("task-a", "node-1") is True
    assert lock.acquire("task-b", "node-2") is True


def test_short_interval_reacquire_is_handled(lock):
    results = [
        lock.acquire("rapid", f"node-{i}", lock_for_seconds=30) for i in range(10)
    ]
    assert results == [True] + [False] * 9


def test_clock_skew_affects_lock_acquisition(engine):
    lock = ShedLock(engine)
    assert lock.acquire("job", "node-1", lock_for_seconds=30) is True

    behind = ShedLock(engine, clock=lambda: time.time() - 60)
    assert behind.acquire("job", "node-2", lock_for_seconds=30) is False

    ahead = ShedLock(engine, clock=lambda: time.time() + 60)
    assert ahead.acquire("job", "node-3", lock_for_seconds=30) is True


def test_long_running_task_loses_lock_after_expiry(lock):
    assert lock.acquire("job", "node-1", lock_for_seconds=1) is True
    time.sleep(1.1)
    # The lock expired while the first task may still be running. A second
    # node can acquire, which is why tasks must be idempotent.
    assert lock.acquire("job", "node-2", lock_for_seconds=30) is True


def test_lock_released_on_shutdown_interrupt(lock):
    def task():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        run_task_with_lock(lock, "job", "node-1", task)
    assert lock.acquire("job", "node-2") is True


def test_scheduler_registers_cron_job(lock):
    scheduler = create_scheduler(
        lock,
        lambda: None,
        owner="node-1",
        name="daily-invoice",
        hour=9,
        minute=0,
    )
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].name == "daily-invoice"
    assert str(jobs[0].trigger) == "cron[hour='9', minute='0']"
