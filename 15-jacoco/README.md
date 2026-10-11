# jacoco-maven-plugin

A Python implementation of the code coverage measurement provided by the JaCoCo Maven plugin. This module uses coverage.py to measure line and branch coverage.

## Overview

In Spring Boot, JaCoCo measures how much of the code is covered by tests and produces a coverage report.

| JaCoCo Concept | Python Equivalent |
|---|---|
| JaCoCo report | coverage.py report |
| Branch coverage | branch=True and missing branch lines |
| Coverage threshold | check_threshold |

## Features

- Line coverage measurement with coverage.py.
- Branch coverage detection through missing arcs.
- Identification of dead code through uncovered lines.
- Coverage threshold checks that fail when coverage is too low.
- Demonstration that high coverage does not guarantee correct logic.

## Project Structure

```
15-jacoco/
├── calculator.py             # Sample module with branches and dead code
├── requirements.txt
├── conftest.py
└── tests/
    └── test_jacoco.py
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

## Measuring Coverage

```bash
pytest --cov=calculator --cov-report=term-missing
```

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that an uncovered else branch produces missing arcs, that an uncovered except branch produces missing arcs, that covering every branch produces no missing arcs, that dead code lines are reported, that a fully called function has no missing body lines, that coverage does not guarantee correct logic, and that a coverage threshold fails when coverage is below the limit.
