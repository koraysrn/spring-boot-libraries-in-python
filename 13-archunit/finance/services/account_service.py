"""Service layer: may import repositories but not controllers."""

from finance.repositories.account_repository import find_account


def get_account(account_id):
    return find_account(account_id)
