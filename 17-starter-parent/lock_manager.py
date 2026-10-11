"""Dependency version management, the equivalent of spring-boot-starter-parent.

The Spring Boot parent POM manages compatible dependency versions from one
place. The Python equivalent is a lock file that pins exact versions so that
every environment installs the same dependencies.
"""

import json
import re
import sys
import tomllib


def parse_pyproject(text):
    return tomllib.loads(text)


def current_python():
    return sys.version_info[:2]


def _version_tuple(version_str):
    return tuple(int(part) for part in version_str.split(".")[:2])


def enforce_python_requirement(requires_python, version=None):
    if version is None:
        version = current_python()
    match = re.match(r">=(\d+)\.(\d+)", requires_python)
    if not match:
        raise ValueError(f"Unsupported requires-python: {requires_python}")
    minimum = (int(match.group(1)), int(match.group(2)))
    if version < minimum:
        raise RuntimeError(
            f"Python {version[0]}.{version[1]} does not satisfy "
            f"requires-python {requires_python}"
        )
    return True


def generate_lock(pyproject_text):
    """Resolve dependencies to pinned minimums, deterministically."""
    project = parse_pyproject(pyproject_text)
    lock = {}
    for dep in project["project"]["dependencies"]:
        match = re.match(r"([A-Za-z0-9_.-]+)>=\s*([0-9.]+)", dep)
        if match:
            lock[match.group(1)] = match.group(2)
    return lock


def assert_lock_present(lock_text):
    if not lock_text.strip():
        raise RuntimeError(
            "Lock file is missing; dependency versions are not reproducible"
        )


def validate_lock_pinned(lock_text):
    assert_lock_present(lock_text)
    lock = json.loads(lock_text)
    for name, version in lock.items():
        if not re.match(r"^\d+\.\d+\.\d+$", str(version)):
            raise RuntimeError(
                f"Dependency {name} is not pinned to an exact version: {version}"
            )
    return True


def check_lock_matches(pyproject_text, lock_text):
    project = parse_pyproject(pyproject_text)
    dep_names = {
        re.match(r"([A-Za-z0-9_.-]+)", dep).group(1)
        for dep in project["project"]["dependencies"]
    }
    lock = json.loads(lock_text)
    lock_names = set(lock.keys())

    problems = []
    extra = lock_names - dep_names
    missing = dep_names - lock_names
    if extra:
        problems.append(f"Lock contains removed dependencies: {sorted(extra)}")
    if missing:
        problems.append(f"Lock is missing dependencies: {sorted(missing)}")
    if problems:
        raise RuntimeError("; ".join(problems))
    return True


def check_version_conflicts(requirements, constraints):
    minimums = {}
    for spec in requirements:
        match = re.match(r"([A-Za-z0-9_.-]+)>=\s*([0-9.]+)", spec)
        if match:
            minimums[match.group(1)] = _version_tuple(match.group(2))

    for spec in constraints:
        match = re.match(r"([A-Za-z0-9_.-]+)<\s*([0-9.]+)", spec)
        if match:
            name = match.group(1)
            maximum = _version_tuple(match.group(2))
            if name in minimums and minimums[name] >= maximum:
                raise RuntimeError(
                    f"Version conflict for {name}: "
                    f"requires >= {minimums[name]} but < {maximum}"
                )
    return True
