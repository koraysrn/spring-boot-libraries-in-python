"""PostgreSQL driver configuration and connection helpers.

Spring Boot equivalents:
    - postgresql JDBC driver -> psycopg
    - jdbc:postgresql://...  -> DSN built from environment variables
    - HikariCP connection pool -> SQLAlchemy pool settings
    - prepared statements   -> parameterized queries
"""

import os

import psycopg
from sqlalchemy import create_engine

DEFAULTS = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "finans",
    "DB_USER": "postgres",
    "DB_PASSWORD": "",
    "DB_SSLMODE": "require",
    "DB_CONNECT_TIMEOUT": "10",
}


def _env(name: str) -> str:
    return os.environ.get(name) or DEFAULTS[name]


def build_dsn() -> str:
    """Build a libpq connection string from environment variables."""
    return (
        f"host={_env('DB_HOST')} port={_env('DB_PORT')} dbname={_env('DB_NAME')} "
        f"user={_env('DB_USER')} password={_env('DB_PASSWORD')} "
        f"sslmode={_env('DB_SSLMODE')} connect_timeout={_env('DB_CONNECT_TIMEOUT')}"
    )


def build_connection_kwargs() -> dict:
    return {
        "sslmode": _env("DB_SSLMODE"),
        "connect_timeout": int(_env("DB_CONNECT_TIMEOUT")),
    }


def build_url() -> str:
    return (
        f"postgresql+psycopg://{_env('DB_USER')}:{_env('DB_PASSWORD')}"
        f"@{_env('DB_HOST')}:{_env('DB_PORT')}/{_env('DB_NAME')}"
    )


def connect():
    return psycopg.connect(build_dsn())


def create_db_engine(pool_size: int = 5, max_overflow: int = 10):
    return create_engine(
        build_url(),
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
        connect_args=build_connection_kwargs(),
    )
