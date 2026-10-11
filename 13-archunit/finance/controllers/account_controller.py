"""Controller layer: may import services but not repositories."""

from finance.services.account_service import get_account


def get_account_endpoint(account_id):
    return get_account(account_id)
