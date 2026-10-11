def is_adult(age):
    return age >= 18


def is_valid_password(password):
    return len(password) >= 8 and any(c.isupper() for c in password)


def deposit(balance, amount):
    if amount < 0:
        raise ValueError("amount must be non-negative")
    return balance + amount


def status(active):
    return "active" if active else "inactive"


def zero():
    return 0
