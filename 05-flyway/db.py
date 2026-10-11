"""Declarative base shared by the models and the Alembic environment."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
