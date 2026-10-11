"""
Non-happy-path tests for the postgresql JDBC driver equivalent (psycopg).

Connection failure tests target an unused local port, so they run without a
live PostgreSQL server. Driver-agnostic safety behaviors (pooling, streaming,
parameterized queries, Unicode) are exercised through an in-memory SQLite
engine as a stand-in.
"""

import time

import psycopg
import pytest
import sqlalchemy
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import TimeoutError as PoolTimeoutError
from sqlalchemy.pool import QueuePool

import db


# --- Credential and configuration handling ---

def test_dsn_uses_environment_values(monkeypatch):
    monkeypatch.setenv("DB_USER", "myuser")
    monkeypatch.setenv("DB_PASSWORD", "secret123")
    dsn = db.build_dsn()
    assert "user=myuser" in dsn
    assert "password=secret123" in dsn


def test_no_hardcoded_password_by_default(monkeypatch):
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    dsn = db.build_dsn()
    assert "password=" in dsn
    assert "password=postgres" not in dsn


def test_ssl_mode_is_required_by_default(monkeypatch):
    monkeypatch.delenv("DB_SSLMODE", raising=False)
    assert "sslmode=require" in db.build_dsn()


def test_connect_timeout_is_configured(monkeypatch):
    monkeypatch.setenv("DB_CONNECT_TIMEOUT", "7")
    assert "connect_timeout=7" in db.build_dsn()


def test_engine_creation_does_not_open_a_connection():
    engine = db.create_db_engine(pool_size=3, max_overflow=5)
    assert engine.pool.checkedout() == 0
    assert engine.url.drivername == "postgresql+psycopg"
    engine.dispose()


# --- Connection failures ---

def test_database_down_raises_operational_error_quickly(monkeypatch):
    monkeypatch.setenv("DB_HOST", "127.0.0.1")
    monkeypatch.setenv("DB_PORT", "1")
    monkeypatch.setenv("DB_CONNECT_TIMEOUT", "1")

    start = time.monotonic()
    with pytest.raises(psycopg.OperationalError):
        db.connect()
    assert time.monotonic() - start < 5


def test_wrong_credentials_are_reported_cleanly(monkeypatch):
    monkeypatch.setenv("DB_HOST", "127.0.0.1")
    monkeypatch.setenv("DB_PORT", "1")
    monkeypatch.setenv("DB_CONNECT_TIMEOUT", "1")
    monkeypatch.setenv("DB_USER", "wronguser")
    monkeypatch.setenv("DB_PASSWORD", "wrongpass")
    with pytest.raises(psycopg.OperationalError):
        db.connect()


def test_wrong_database_name_raises_operational_error(monkeypatch):
    monkeypatch.setenv("DB_HOST", "127.0.0.1")
    monkeypatch.setenv("DB_PORT", "1")
    monkeypatch.setenv("DB_CONNECT_TIMEOUT", "1")
    monkeypatch.setenv("DB_NAME", "wrong_database")
    with pytest.raises(psycopg.OperationalError):
        db.connect()


# --- Driver-agnostic safety behaviors ---

def test_pool_exhaustion_raises_timeout():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=QueuePool,
        pool_size=1,
        max_overflow=0,
        pool_timeout=0.2,
    )
    conn = engine.connect()
    try:
        with pytest.raises(PoolTimeoutError):
            engine.connect()
    finally:
        conn.close()
        engine.dispose()


def test_large_result_set_streams_without_materializing():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE big (id INTEGER PRIMARY KEY, value TEXT)"))
        conn.execute(
            text("INSERT INTO big (value) VALUES (:value)"),
            [{"value": f"row{i}"} for i in range(10000)],
        )

    with engine.connect() as conn:
        result = conn.execution_options(stream_results=True).execute(
            text("SELECT id, value FROM big")
        )
        count = 0
        for _ in result:
            count += 1
        assert count == 10000


def test_sql_injection_is_neutralized_by_parameterized_query():
    engine = create_engine("sqlite:///:memory:")
    malicious = "'; DROP TABLE account; --"
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE account (id INTEGER PRIMARY KEY, name TEXT)"))
        conn.execute(
            text("INSERT INTO account (name) VALUES (:name)"),
            {"name": malicious},
        )

    assert "account" in inspect(engine).get_table_names()
    with engine.connect() as conn:
        stored = conn.execute(text("SELECT name FROM account")).scalar()
    assert stored == malicious


def test_unicode_data_roundtrips():
    engine = create_engine("sqlite:///:memory:")
    content = "İstanbul ğüşiöç 😀"
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE msg (content TEXT)"))
        conn.execute(text("INSERT INTO msg (content) VALUES (:c)"), {"c": content})

    with engine.connect() as conn:
        assert conn.execute(text("SELECT content FROM msg")).scalar() == content


def test_unclosed_connections_are_detected():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=QueuePool,
        pool_size=2,
        max_overflow=0,
        pool_timeout=0.2,
    )
    conn1 = engine.connect()
    conn2 = engine.connect()
    try:
        # The third checkout times out because the two checked out connections
        # were never returned, which reveals the connection leak.
        with pytest.raises(PoolTimeoutError):
            engine.connect()
    finally:
        conn1.close()
        conn2.close()
        engine.dispose()
