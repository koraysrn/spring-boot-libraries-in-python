"""Pydantic models for request and response bodies."""

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=50)
    # bcrypt truncates input at 72 bytes, so the field is capped accordingly.
    password: str = Field(min_length=8, max_length=72)


class User(BaseModel):
    id: int
    username: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str
