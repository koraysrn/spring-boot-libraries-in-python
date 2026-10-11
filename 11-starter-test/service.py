"""Sample service layer used to demonstrate pytest and unittest.mock."""

from datetime import date


class Repository:
    def find_all(self):
        raise NotImplementedError

    def find_by_id(self, item_id):
        raise NotImplementedError

    def transfer(self, source_id, target_id, amount):
        raise NotImplementedError


class AccountService:
    def __init__(self, repository):
        self.repository = repository

    def list_accounts(self):
        """Return the repository result; an empty list is a valid result."""
        return self.repository.find_all()

    def get_account(self, item_id):
        return self.repository.find_by_id(item_id)

    def get_account_name(self, item_id):
        account = self.repository.find_by_id(item_id)
        if account is None:
            return "unknown"
        return account["name"]

    def transfer(self, source_id, target_id, amount):
        """Wraps a dependency failure into a domain error."""
        if amount < 0:
            raise ValueError("amount must be non-negative")
        try:
            return self.repository.transfer(source_id, target_id, amount)
        except RuntimeError as exc:
            raise RuntimeError("transfer failed") from exc

    def is_birthday_today(self, birthday) -> bool:
        today = date.today()
        return (birthday.month, birthday.day) == (today.month, today.day)

    def write_report(self, path, content):
        with open(path, "w") as file:
            file.write(content)
