"""
Non-happy-path tests for the ArchUnit equivalent (architecture rule checker).
"""

import pathlib

from arch import extract_imported_modules

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
FINANCE_DIR = BASE_DIR / "finance"


def test_controller_importing_repository_is_a_violation(rules):
    violations = rules.check_imports(
        "finance.controllers.account_controller",
        ["finance.repositories.account_repository"],
    )
    assert len(violations) == 1


def test_service_importing_controller_is_a_violation(rules):
    violations = rules.check_imports(
        "finance.services.account_service",
        ["finance.controllers.account_controller"],
    )
    assert len(violations) == 1


def test_repository_importing_service_is_a_violation(rules):
    violations = rules.check_imports(
        "finance.repositories.account_repository",
        ["finance.services.account_service"],
    )
    assert len(violations) == 1


def test_correct_direction_passes(rules):
    controller_ok = rules.check_imports(
        "finance.controllers.account_controller",
        ["finance.services.account_service"],
    )
    service_ok = rules.check_imports(
        "finance.services.account_service",
        ["finance.repositories.account_repository"],
    )
    assert controller_ok == []
    assert service_ok == []


def test_utils_are_allowed_everywhere(rules):
    violations = rules.check_imports(
        "finance.controllers.account_controller",
        ["finance.utils.helpers"],
    )
    assert violations == []


def test_new_module_is_covered_automatically(rules):
    violations = rules.check_imports(
        "finance.controllers.user_controller",
        ["finance.repositories.user_repository"],
    )
    assert len(violations) == 1


def test_violation_message_is_descriptive(rules):
    violations = rules.check_imports(
        "finance.controllers.account_controller",
        ["finance.repositories.account_repository"],
    )
    message = violations[0]
    assert "finance.controllers.account_controller" in message
    assert "finance.repositories.account_repository" in message
    assert "controllers" in message
    assert "repositories" in message


def test_sample_files_follow_the_architecture(rules):
    controller = (FINANCE_DIR / "controllers" / "account_controller.py").read_text()
    service = (FINANCE_DIR / "services" / "account_service.py").read_text()
    repository = (FINANCE_DIR / "repositories" / "account_repository.py").read_text()

    assert (
        rules.check_source("finance.controllers.account_controller", controller) == []
    )
    assert rules.check_source("finance.services.account_service", service) == []
    assert rules.check_source("finance.repositories.account_repository", repository) == []


def test_extract_imported_modules():
    source = "from finance.services.account_service import get_account\nimport os\n"
    assert extract_imported_modules(source) == [
        "finance.services.account_service",
        "os",
    ]
