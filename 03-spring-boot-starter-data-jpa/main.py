"""REST API built on top of the SQLAlchemy repository layer.

This mirrors how Spring Boot controllers call JpaRepository methods.
"""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import repository
from db import Base, SessionLocal, engine
from schemas import AccountCreate, AccountOut, TransactionCreate, TransactionOut

app = FastAPI(title="Finance API - Python equivalent of spring-boot-starter-data-jpa")

Base.metadata.create_all(bind=engine)


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/accounts", response_model=list[AccountOut])
def list_accounts(session: Session = Depends(get_db)):
    return repository.find_all_accounts(session)


@app.post("/accounts", response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate, session: Session = Depends(get_db)):
    account = repository.create_account(
        session, payload.email, payload.name, payload.balance
    )
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    return account


@app.get("/accounts/{account_id}", response_model=AccountOut)
def get_account(account_id: int, session: Session = Depends(get_db)):
    account = repository.find_account_by_id(session, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: int, session: Session = Depends(get_db)):
    if not repository.delete_account(session, account_id):
        raise HTTPException(status_code=404, detail="Account not found")
    session.commit()


@app.post(
    "/accounts/{account_id}/transactions",
    response_model=TransactionOut,
    status_code=201,
)
def add_transaction(
    account_id: int,
    payload: TransactionCreate,
    session: Session = Depends(get_db),
):
    txn = repository.add_transaction(
        session, account_id, payload.amount, payload.description
    )
    if txn is None:
        raise HTTPException(status_code=404, detail="Account not found")
    session.commit()
    return txn
