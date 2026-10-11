"""In-memory database setup, the equivalent of the H2 test database."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def create_in_memory_engine():
    """Create an in-memory SQLite engine shared across connections.

    StaticPool reuses a single connection so that the in-memory database
    persists across all connections opened through this engine.
    """
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
