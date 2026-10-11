# spring-boot-starter-test

A Python implementation of the testing tools bundled by the Spring Boot starter `spring-boot-starter-test`. This module demonstrates the pytest and unittest.mock equivalents of JUnit 5, Mockito, and AssertJ.

## Overview

In Spring Boot, `spring-boot-starter-test` bundles all the tools needed to write tests: JUnit 5, Mockito, AssertJ, and Spring Test.

| Spring Testing Concept | Python Equivalent |
|---|---|
| JUnit 5 | pytest |
| Mockito | unittest.mock |
| AssertJ | pytest assertions |
| Spring Test | Fixtures |

## Features

- Mocking dependencies with `Mock(spec=...)`.
- Fixtures that provide a fresh mock and service per test.
- Parametrized tests.
- Exception assertions with `pytest.raises`.
- Clock mocking with `monkeypatch`.
- Deterministic assertions over repeated runs.
- Side effect testing with `tmp_path` for automatic cleanup.

## Project Structure

```
11-starter-test/
├── service.py                 # Sample service under test
├── requirements.txt
├── conftest.py                # Fixtures
└── tests/
    └── test_starter_test.py
```

## Requirements

- Python 3.12 or newer
- pip

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

The test suite focuses on non-happy-path scenarios. It verifies that a dependency exception is wrapped into a domain error, that another dependency exception is propagated, that an empty list is a valid result, that None is handled with defined behavior, that mocks can assert they were not called, that mocks can assert expected arguments and fail on wrong arguments, that the fixture provides a fresh mock, that the service is deterministic over one hundred runs, that the clock can be mocked, that file writes are tested with automatic cleanup, and that parametrized tests reject negative amounts.
