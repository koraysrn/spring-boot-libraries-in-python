"""Pydantic validation schemas.

Spring Boot equivalents:
    - @NotBlank, @Size   -> Field constraints
    - @Email             -> EmailStr
    - @Min               -> Field(ge=0)
    - @Pattern           -> field_validator or pattern
    - custom validator   -> @field_validator
    - @Valid on DTO      -> FastAPI body model
"""

import unicodedata
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("password")
    @classmethod
    def password_must_contain_uppercase(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("password must contain at least one uppercase letter")
        return value


class TransactionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(ge=0)
    description: str = Field(default="", max_length=255)


class AccountUpdate(BaseModel):
    """Partial update model. Every field is optional, like a PATCH body."""

    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    balance: Optional[float] = Field(default=None, ge=0)


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str = Field(min_length=1, max_length=50)

    @field_validator("display_name", mode="before")
    @classmethod
    def normalize_display_name(cls, value):
        if isinstance(value, str):
            return unicodedata.normalize("NFKC", value)
        return value


class ArbitraryPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: dict
