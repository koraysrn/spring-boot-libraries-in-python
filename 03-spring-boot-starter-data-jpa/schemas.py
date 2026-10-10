"""Pydantic schemas for the REST API layer."""

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=255)
    name: str = Field(min_length=1, max_length=100)
    balance: float = Field(ge=0, default=0.0)


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float
    description: str = Field(default="", max_length=255)


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    balance: float


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    amount: float
    description: str
