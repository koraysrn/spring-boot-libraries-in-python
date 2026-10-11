"""Dataclass models, the equivalent of Lombok annotations.

Spring Boot equivalents:
    - @Getter @Setter        -> @dataclass (mutable)
    - @Value                 -> @dataclass(frozen=True)
    - @AllArgsConstructor    -> generated __init__
    - @EqualsAndHashCode     -> generated __eq__ / __hash__
    - @ToString              -> generated __repr__
    - @NoArgsConstructor     -> field(default=...)
"""

from dataclasses import dataclass, field


@dataclass
class Account:
    """Lombok @Getter @Setter equivalent: mutable with generated methods."""

    id: int
    name: str
    balance: float = 0.0


@dataclass(frozen=True)
class Money:
    """Lombok @Value equivalent: an immutable value object."""

    amount: float
    currency: str = "TRY"


@dataclass
class ShoppingCart:
    # default_factory prevents mutable defaults from being shared.
    items: list = field(default_factory=list)


@dataclass
class User:
    email: str
    age: int

    def __post_init__(self):
        if self.age < 0:
            raise ValueError("age must be non-negative")
        if "@" not in self.email:
            raise ValueError("invalid email")


@dataclass
class BaseEntity:
    id: int


@dataclass
class AccountEntity(BaseEntity):
    name: str
