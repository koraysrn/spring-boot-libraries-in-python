"""Sample model used to demonstrate schema creation on the in-memory DB."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
