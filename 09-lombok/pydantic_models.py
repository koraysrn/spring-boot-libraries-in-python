"""Pydantic model shown for comparison with the dataclass version.

The key difference: Pydantic validates input, a dataclass does not.
"""

from pydantic import BaseModel, Field


class AccountModel(BaseModel):
    id: int
    name: str
    balance: float = Field(default=0.0, ge=0)
