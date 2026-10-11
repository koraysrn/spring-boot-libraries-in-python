"""The test suite used to kill mutants.

Each test receives a module-like namespace so that it can run against the
original code or against a mutated version.
"""


def test_is_adult(mod):
    assert mod.is_adult(18) is True
    assert mod.is_adult(17) is False


def test_is_valid_password(mod):
    assert mod.is_valid_password("StrongPass1") is True
    assert mod.is_valid_password("short1") is False
    assert mod.is_valid_password("alllowercase123") is False


def test_deposit(mod):
    assert mod.deposit(100, 50) == 150
    try:
        mod.deposit(100, -10)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_status(mod):
    assert mod.status(True) == "active"
    assert mod.status(False) == "inactive"


def test_zero(mod):
    assert mod.zero() == 0


STRONG_SUITE = [
    test_is_adult,
    test_is_valid_password,
    test_deposit,
    test_status,
    test_zero,
]
