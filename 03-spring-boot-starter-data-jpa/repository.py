"""Data access functions, the equivalent of Spring Data JPA repositories.

Spring Boot equivalents:
    - JpaRepository.findAll()   -> find_all_accounts
    - findById(id)              -> find_account_by_id
    - save(entity)              -> create_account / add_transaction
    - delete(entity)            -> delete_account
    - @EntityGraph / fetch join -> find_all_accounts_with_transactions
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Account, Budget, Transaction


def find_account_by_id(session: Session, account_id: int) -> Account | None:
    return session.get(Account, account_id)


def find_all_accounts(session: Session) -> list[Account]:
    return list(
        session.execute(select(Account).order_by(Account.id)).scalars()
    )


def find_all_accounts_with_transactions(session: Session) -> list[Account]:
    # selectinload eagerly loads the transactions in a second query, avoiding
    # the N+1 query problem that lazy loading would cause.
    return list(
        session.execute(
            select(Account)
            .options(selectinload(Account.transactions))
            .order_by(Account.id)
        ).scalars()
    )


def create_account(
    session: Session,
    email: str,
    name: str,
    balance: float = 0.0,
) -> Account:
    account = Account(email=email, name=name, balance=balance)
    session.add(account)
    return account


def update_account_balance(
    session: Session,
    account_id: int,
    new_balance: float,
) -> Account | None:
    account = session.get(Account, account_id)
    if account is None:
        return None
    account.balance = new_balance
    return account


def delete_account(session: Session, account_id: int) -> bool:
    account = session.get(Account, account_id)
    if account is None:
        return False
    session.delete(account)
    return True


def add_transaction(
    session: Session,
    account_id: int,
    amount: float,
    description: str = "",
) -> Transaction | None:
    account = session.get(Account, account_id)
    if account is None:
        return None
    txn = Transaction(account=account, amount=amount, description=description)
    session.add(txn)
    return txn


def add_budget_to_account(
    session: Session,
    account_id: int,
    budget: Budget,
) -> bool:
    account = session.get(Account, account_id)
    if account is None:
        return False
    account.budgets.append(budget)
    return True
