"""
Non-happy-path tests for the spring-boot-starter-parent equivalent (lock file).
"""

import pathlib

import pytest

import lock_manager

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PYPROJECT = (BASE_DIR / "pyproject.toml").read_text()
LOCK = (BASE_DIR / "lock.json").read_text()


def test_missing_lock_file_raises():
    with pytest.raises(RuntimeError, match="Lock file is missing"):
        lock_manager.assert_lock_present("")


def test_unpinned_lock_entry_is_detected():
    with pytest.raises(RuntimeError, match="not pinned"):
        lock_manager.validate_lock_pinned('{"fastapi": ">=0.115.0"}')


def test_conflicting_versions_are_reported():
    with pytest.raises(RuntimeError, match="Version conflict"):
        lock_manager.check_version_conflicts(
            ["fastapi>=0.130.0"], ["fastapi<0.120.0"]
        )


def test_python_311_is_rejected():
    with pytest.raises(RuntimeError, match="does not satisfy"):
        lock_manager.enforce_python_requirement(">=3.12", (3, 11))


def test_python_312_is_accepted():
    assert lock_manager.enforce_python_requirement(">=3.12", (3, 12)) is True


def test_lock_generation_is_deterministic():
    first = lock_manager.generate_lock(PYPROJECT)
    second = lock_manager.generate_lock(PYPROJECT)
    assert first == second


def test_removed_dependency_is_detected():
    pyproject = (
        '[project]\nname = "finance"\nrequires-python = ">=3.12"\n'
        'dependencies = ["fastapi>=0.115.0"]\n'
    )
    with pytest.raises(RuntimeError, match="removed dependencies"):
        lock_manager.check_lock_matches(pyproject, LOCK)


def test_real_files_are_consistent():
    project = lock_manager.parse_pyproject(PYPROJECT)
    assert lock_manager.enforce_python_requirement(
        project["project"]["requires-python"]
    )
    assert lock_manager.check_lock_matches(PYPROJECT, LOCK)
    assert lock_manager.validate_lock_pinned(LOCK)
