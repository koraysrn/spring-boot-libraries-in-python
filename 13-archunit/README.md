# archunit-junit5

A Python implementation of the architecture rule testing provided by ArchUnit. This module checks that code follows layer dependency rules such as controller -> service -> repository.

## Overview

In Spring Boot, ArchUnit verifies architecture rules as tests. Rules such as "controllers may not access repositories directly" are written in code and run like any other test.

The standard Python tool for this is import-linter. This module reimplements the same layering concept by hand, parsing imports with the built-in `ast` module.

| ArchUnit Concept | Python Equivalent |
|---|---|
| ArchUnit | `ArchitectureRules` checker |
| layeredArchitecture() | `DEFAULT_LAYERS` dict |
| LayeredArchitectureTest.java | tests/test_archunit.py |

## Features

- Layer rules that allow `controllers -> services -> repositories`.
- A `utils` layer that every other layer may import.
- Violation messages that name the importer, the import, and the layers.
- Parsing of imports from Python source files with `ast`.
- Automatic coverage of new modules through layer name prefix matching.

## Project Structure

```
13-archunit/
├── arch.py                  # Architecture rule checker
├── finance/                 # Sample package following the rules
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   └── utils/
├── requirements.txt
├── conftest.py
└── tests/
    └── test_archunit.py
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

The test suite focuses on non-happy-path scenarios. It verifies that a controller importing a repository is a violation, that a service importing a controller is a violation, that a repository importing a service is a violation, that the correct direction passes, that utils are allowed everywhere, that a new module is covered automatically, that violation messages are descriptive, and that the sample files follow the architecture.
