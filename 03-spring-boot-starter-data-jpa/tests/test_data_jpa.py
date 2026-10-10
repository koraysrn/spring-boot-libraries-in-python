"""
Non-happy-path tests for spring-boot-starter-data-jpa.

The tests exercise the ORM layer directly, the same way Spring Boot tests
would exercise JPA repositories with the H2 in-memory database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    StatementError,
    TimeoutError as PoolTimeoutError,
)
from sqlalchemy.orm.exc import DetachedInstanceError, StaleDataError
from sqlalchemy.pool import QueuePool

import repository
from db import Base, SessionLocal, engine
from main import app
from models import Account, Budget, Transaction, account_budget

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def session():
    s = SessionLocal()
    yield s
    s.close()


# --- Non-happy-path tests ---

def test_find_by_id_missing_returns_none(session):
    assert repository.find_account_by_id(session, 999999) is None


def test_duplicate_email_raises_integrity_error(session):
    session.add(Account(email="a@example.com", name="A"))
    session.commit()
    session.add(Account(email="a@example.com", name="B"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_null_name_raises_integrity_error(session):
    session.add(Account(email="b@example.com", name=None))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_name_longer_than_limit_raises_integrity_error(session):
    session.add(Account(email="c@example.com", name="x" * 1000))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_transaction_rollback_on_failure(session):
    session.add(Account(email="a@example.com", name="A"))
    session.add(Account(email="b@example.com", name=None))  # NOT NULL violation
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
    # The first insert must also be rolled back.
    result = session.execute(select(Account).where(Account.name == "A")).first()
    assert result is None


def test_lazy_relationship_raises_after_session_close():
    s = SessionLocal()
    account = repository.create_account(s, "a@example.com", "A")
    s.commit()
    repository.add_transaction(s, account.id, 100.0)
    s.commit()
    s.close()

    with pytest.raises(DetachedInstanceError):
        _ = account.transactions


def test_selectinload_avoids_detached_instance_error():
    s = SessionLocal()
    account = repository.create_account(s, "a@example.com", "A")
    s.commit()
    repository.add_transaction(s, account.id, 100.0)
    s.commit()

    accounts = repository.find_all_accounts_with_transactions(s)
    s.close()

    assert accounts[0].transactions[0].amount == 100.0


def test_lost_update_raises_stale_data_error():
    s1 = SessionLocal()
    account = repository.create_account(s1, "a@example.com", "A", balance=100.0)
    s1.commit()

    s2 = SessionLocal()
    account_s2 = repository.find_account_by_id(s2, account.id)

    account_s1 = repository.find_account_by_id(s1, account.id)
    repository.update_account_balance(s1, account_s1.id, 200.0)
    s1.commit()

    # s2 still holds version 1, so this update must be rejected.
    repository.update_account_balance(s2, account_s2.id, 300.0)
    with pytest.raises(StaleDataError):
        s2.commit()
    s2.rollback()
    s1.close()
    s2.close()


def test_deleting_account_cascades_to_transactions(session):
    account = repository.create_account(session, "a@example.com", "A")
    session.commit()
    repository.add_transaction(session, account.id, 100.0)
    repository.add_transaction(session, account.id, 200.0)
    session.commit()

    repository.delete_account(session, account.id)
    session.commit()

    assert session.execute(select(Transaction)).scalars().all() == []


def test_deleting_account_removes_many_to_many_links(session):
    account = repository.create_account(session, "a@example.com", "A")
    budget = Budget(name="Food", limit_amount=500.0)
    session.add(budget)
    session.commit()

    repository.add_budget_to_account(session, account.id, budget)
    session.commit()

    repository.delete_account(session, account.id)
    session.commit()

    assert session.execute(select(account_budget)).all() == []


def test_selectinload_avoids_n_plus_one_queries():
    query_count = {"n": 0}

    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        query_count["n"] += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        s = SessionLocal()
        for i in range(5):
            account = repository.create_account(s, f"user{i}@example.com", f"User{i}")
            s.commit()
            repository.add_transaction(s, account.id, 10.0)
            s.commit()

        query_count["n"] = 0
        accounts = repository.find_all_accounts_with_transactions(s)
        _ = [a.transactions for a in accounts]
        s.close()

        # Eager loading issues a constant number of queries (accounts + children),
        # not one query per account plus one per child.
        assert query_count["n"] <= 3
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)


def test_connection_pool_exhaustion_raises_timeout():
    small_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=QueuePool,
        pool_size=1,
        max_overflow=0,
        pool_timeout=0.2,
    )
    try:
        conn = small_engine.connect()
        with pytest.raises(PoolTimeoutError):
            small_engine.connect()
        conn.close()
    finally:
        small_engine.dispose()


def test_invalid_type_raises_statement_error(session):
    account = repository.create_account(session, "a@example.com", "A")
    session.commit()

    session.add(Transaction(account_id=account.id, amount="not-a-number"))
    with pytest.raises(StatementError):
        session.flush()
    session.rollback()


def test_unavailable_database_raises_operational_error():
    bad_engine = create_engine("sqlite:///nonexistent_dir_xyz/foo.db")
    try:
        with pytest.raises(OperationalError):
            bad_engine.connect()
    finally:
        bad_engine.dispose()


# --- API level non-happy-path checks ---

def test_api_duplicate_email_returns_409():
    client.post("/accounts", json={"email": "a@example.com", "name": "A"})
    response = client.post(
        "/accounts", json={"email": "a@example.com", "name": "B"}
    )
    assert response.status_code == 409


def test_api_missing_account_returns_404():
    response = client.get("/accounts/999999")
    assert response.status_code == 404
