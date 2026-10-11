"""
Non-happy-path tests for the H2 equivalent (SQLite in-memory database).
"""

import threading

import pytest
import sqlalchemy
from sqlalchemy import create_engine, inspect, text

from db import Base, create_in_memory_engine
import models  # noqa: F401  registers Account on Base.metadata


def _row_count(engine) -> int:
    with engine.connect() as conn:
        return conn.execute(text("SELECT COUNT(*) FROM account")).scalar()


def test_two_engines_are_isolated():
    engine1 = create_in_memory_engine()
    engine2 = create_in_memory_engine()
    Base.metadata.create_all(bind=engine1)
    Base.metadata.create_all(bind=engine2)

    with engine1.begin() as conn:
        conn.execute(text("INSERT INTO account (name) VALUES ('A')"))

    assert _row_count(engine2) == 0


def _run_scenario() -> int:
    engine = create_in_memory_engine()
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO account (name) VALUES ('A')"))
    return _row_count(engine)


def test_same_scenario_runs_identically_twice():
    assert _run_scenario() == 1
    assert _run_scenario() == 1


def test_exception_in_one_engine_does_not_affect_another():
    engine1 = create_in_memory_engine()
    Base.metadata.create_all(bind=engine1)
    try:
        with engine1.begin() as conn:
            conn.execute(text("INSERT INTO account (name) VALUES ('A')"))
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    engine2 = create_in_memory_engine()
    Base.metadata.create_all(bind=engine2)
    assert _row_count(engine2) == 0


def test_in_memory_data_lost_when_connection_closes():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO account (name) VALUES ('A')"))
    engine.dispose()

    reopened = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=reopened)
    assert _row_count(reopened) == 0


def test_postgresql_specific_sql_differs_on_sqlite():
    engine = create_in_memory_engine()
    # generate_series is a PostgreSQL function that SQLite does not provide.
    with pytest.raises(sqlalchemy.exc.OperationalError):
        with engine.begin() as conn:
            conn.execute(text("SELECT * FROM generate_series(1, 5)"))


def test_concurrent_writes_serialize_on_sqlite(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False, "timeout": 5},
    )
    Base.metadata.create_all(bind=engine)

    errors = []

    def writer(i):
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO account (name) VALUES (:name)"),
                    {"name": f"user{i}"},
                )
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    assert _row_count(engine) == 10


def test_schema_creation_works_on_in_memory_db():
    engine = create_in_memory_engine()
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    assert "account" in inspector.get_table_names()
    columns = {c["name"] for c in inspector.get_columns("account")}
    assert {"id", "name"} <= columns
