"""ORM entities mapped to database tables.

Spring Boot equivalents:
    - @Entity              -> SQLAlchemy mapped classes
    - @Table(name="...")   -> __tablename__
    - @OneToMany           -> relationship(back_populates=...)
    - @ManyToMany          -> relationship(secondary=...)
    - @Version             -> __mapper_args__ = {"version_id_col": version_id}
    - cascade = ALL        -> cascade="all, delete-orphan"
"""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base

# Junction table for the many-to-many relationship between Account and Budget.
account_budget = Table(
    "account_budget",
    Base.metadata,
    Column(
        "account_id",
        ForeignKey("account.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "budget_id",
        ForeignKey("budget.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Account(Base):
    __tablename__ = "account"
    __table_args__ = (
        CheckConstraint("length(name) <= 100", name="ck_account_name_length"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[float] = mapped_column(nullable=False, default=0.0)

    # version_id implements optimistic locking, the equivalent of JPA @Version.
    # It is declared as a Column so that __mapper_args__ can reference it.
    version_id = Column(Integer, nullable=False, default=1)

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
        lazy="select",
    )
    budgets: Mapped[list["Budget"]] = relationship(
        secondary=account_budget,
        back_populates="accounts",
        lazy="select",
    )

    __mapper_args__ = {"version_id_col": version_id}


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")

    account: Mapped["Account"] = relationship(back_populates="transactions")


class Budget(Base):
    __tablename__ = "budget"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    limit_amount: Mapped[float] = mapped_column(nullable=False)

    accounts: Mapped[list["Account"]] = relationship(
        secondary=account_budget,
        back_populates="budgets",
        lazy="select",
    )
