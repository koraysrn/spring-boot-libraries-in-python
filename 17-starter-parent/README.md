# spring-boot-starter-parent

A Python implementation of the dependency version management provided by the Spring Boot parent POM. This module uses a lock file to pin exact dependency versions, the Python equivalent of the parent POM.

## Overview

In Spring Boot, `spring-boot-starter-parent` is not a library. It is a parent POM that manages compatible versions of every Spring Boot library from one place. The developer does not write versions; Spring Boot selects them automatically.

| Parent POM Concept | Python Equivalent |
|---|---|
| Parent POM | lock.json |
| Compatible version matrix | pinned versions |
| Java version | requires-python |

## Features

- `requires-python` declaration in `pyproject.toml`.
- A lock file that pins every dependency to an exact version.
- Python version enforcement.
- Detection of removed dependencies not reflected in the lock file.
- Detection of version conflicts between requirements and constraints.
- Deterministic lock generation.

## Project Structure

```
17-starter-parent/
├── pyproject.toml            # Project metadata and dependency ranges
├── lock.json                 # Pinned dependency versions
├── lock_manager.py           # Version management helpers
├── requirements.txt
├── conftest.py
└── tests/
    └── test_starter_parent.py
```

## Requirements

- Python 3.12 or newer

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that a missing lock file raises, that an unpinned lock entry is detected, that conflicting versions are reported, that Python 3.11 is rejected under `requires-python >=3.12`, that Python 3.12 is accepted, that lock generation is deterministic, that a removed dependency is detected, and that the real files are consistent.
