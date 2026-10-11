"""
Non-happy-path tests for the Lombok equivalent (dataclasses and Pydantic).
"""

from dataclasses import FrozenInstanceError

import pytest
from pydantic import ValidationError

from models import Account, AccountEntity, Money, ShoppingCart, User
from pydantic_models import AccountModel


def test_same_fields_are_equal_by_value():
    assert Account(1, "Ali") == Account(1, "Ali")
    assert Account(1, "Ali") != Account(2, "Ali")


def test_frozen_instance_cannot_be_modified():
    money = Money(100.0)
    with pytest.raises(FrozenInstanceError):
        money.amount = 200.0


def test_default_value_is_used():
    account = Account(1, "Ali")
    assert account.balance == 0.0


def test_post_init_validation_raises():
    with pytest.raises(ValueError):
        User("ali@example.com", -5)
    with pytest.raises(ValueError):
        User("not-an-email", 20)


def test_repr_includes_fields():
    text = repr(Account(1, "Ali"))
    assert "Ali" in text
    assert "balance=0.0" in text


def test_mutable_default_is_not_shared():
    cart1 = ShoppingCart()
    cart2 = ShoppingCart()
    cart1.items.append("apple")
    assert cart2.items == []


def test_frozen_value_objects_are_hashable():
    money1 = Money(100.0)
    money2 = Money(100.0)
    assert hash(money1) == hash(money2)
    assert len({money1, money2}) == 1


def test_inheritance_merges_fields():
    entity = AccountEntity(1, "Ali")
    assert entity.id == 1
    assert entity.name == "Ali"


def test_pydantic_validates_but_dataclass_does_not():
    # A dataclass accepts invalid data without complaint.
    account = Account(1, "Ali", balance=-100.0)
    assert account.balance == -100.0

    # Pydantic rejects the same invalid data.
    with pytest.raises(ValidationError):
        AccountModel(id=1, name="Ali", balance=-100.0)


def test_mutable_dataclass_is_unhashable():
    with pytest.raises(TypeError):
        hash(Account(1, "Ali"))
