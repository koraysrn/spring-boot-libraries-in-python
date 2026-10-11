"""
Non-happy-path tests for the spring-boot-starter-test equivalent.
"""

from datetime import date
from unittest.mock import Mock

import pytest

import service as service_module
from service import AccountService, Repository


class FakeDate:
    @staticmethod
    def today():
        return date(2026, 5, 17)


# --- Non-happy-path tests ---

def test_transfer_wraps_dependency_exception(service):
    service.repository.transfer.side_effect = RuntimeError("db down")
    with pytest.raises(RuntimeError, match="transfer failed"):
        service.transfer(1, 2, 10)


def test_list_accounts_propagates_dependency_exception(service):
    service.repository.find_all.side_effect = RuntimeError("db down")
    with pytest.raises(RuntimeError, match="db down"):
        service.list_accounts()


def test_empty_list_is_a_valid_result(service):
    service.repository.find_all.return_value = []
    assert service.list_accounts() == []


def test_none_is_handled_with_defined_behavior(service):
    service.repository.find_by_id.return_value = None
    assert service.get_account_name(7) == "unknown"


def test_mock_was_not_called(service):
    service.repository.find_all.assert_not_called()
    service.repository.find_by_id.assert_not_called()


def test_mock_called_with_expected_arguments(service):
    service.get_account(42)
    service.repository.find_by_id.assert_called_once_with(42)


def test_assert_called_with_fails_on_wrong_arguments(service):
    service.get_account(1)
    with pytest.raises(AssertionError):
        service.repository.find_by_id.assert_called_with(2)


def test_service_fixture_starts_with_unused_mock(service):
    # A fresh mock per test keeps tests independent of execution order.
    assert service.repository.find_all.call_count == 0
    assert service.repository.find_by_id.call_count == 0


def test_service_is_deterministic_over_100_runs():
    for _ in range(100):
        repository = Mock(spec=Repository)
        repository.find_all.return_value = []
        service = AccountService(repository)
        assert service.list_accounts() == []


def test_birthday_check_uses_mocked_clock(monkeypatch):
    service = AccountService(Mock())
    monkeypatch.setattr(service_module, "date", FakeDate)

    assert service.is_birthday_today(date(2000, 5, 17)) is True
    assert service.is_birthday_today(date(2000, 6, 1)) is False


def test_write_report_writes_content_to_tmp_path(tmp_path):
    service = AccountService(Mock())
    path = tmp_path / "report.txt"
    service.write_report(str(path), "content")
    assert path.read_text() == "content"
    # tmp_path is removed automatically after the test.


@pytest.mark.parametrize("amount", [0, 1, 100])
def test_transfer_accepts_non_negative_amounts(amount):
    repository = Mock(spec=Repository)
    repository.transfer.return_value = "ok"
    service = AccountService(repository)
    assert service.transfer(1, 2, amount) == "ok"


@pytest.mark.parametrize("amount", [-1, -100])
def test_transfer_rejects_negative_amounts(amount):
    service = AccountService(Mock())
    with pytest.raises(ValueError):
        service.transfer(1, 2, amount)
