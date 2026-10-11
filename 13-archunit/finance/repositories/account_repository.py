"""Repository layer: must not import controllers or services."""


def find_account(account_id):
    return {"id": account_id, "name": "Account"}
