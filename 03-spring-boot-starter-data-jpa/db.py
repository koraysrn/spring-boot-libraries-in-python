"""Database engine, session factory, and declarative base."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

# SQLite in-memory is used for tests, mirroring how Spring Boot tests replace
# PostgreSQL with the H2 in-memory database. For production, set DATABASE_URL
# to a PostgreSQL URL such as postgresql+psycopg://user:pass@localhost/db.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

_is_sqlite = DATABASE_URL.startswith("sqlite")
_is_memory = DATABASE_URL in ("sqlite:///:memory:", "sqlite://")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    poolclass=StaticPool if _is_memory else None,
)

# expire_on_commit=False keeps loaded attributes available after commit so that
# detached instance behavior is predictable and easy to test.
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
