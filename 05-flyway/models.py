"""Target database schema used by Alembic's drift detection.

These models describe the final state of the database after every migration
has been applied. Alembic can compare this metadata against the live schema.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[float] = mapped_column(nullable=False, server_default="0")
