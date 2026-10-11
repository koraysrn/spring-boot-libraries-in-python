# pitest-maven and pitest-junit5-plugin

A Python implementation of the mutation testing provided by PIT (Pitest). This module breaks code in small ways and checks whether the test suite detects each break.

## Overview

In Spring Boot, PIT performs mutation testing. It deliberately breaks the code, for example by changing `>` into `<`, and checks whether the tests catch the broken code. Surviving mutants indicate weak tests.

The standard Python tool for this is mutmut. This module reimplements the same mutation operators with the built-in `ast` module.

| PIT Concept | Python Equivalent |
|---|---|
| Mutation operator | AST transformer |
| Killed mutant | A test fails |
| Survived mutant | Every test passes |
| Mutation score | Killed mutants divided by total mutants |

## Features

- Eight mutation operators: comparison flip, boundary change, boolean flip, constant change, deleted return, removed condition, emptied string, and deleted raise.
- A strong test suite that kills every mutant.
- A weak test suite demonstration where a mutant survives.
- Mutation classification through a simple runner.

## Project Structure

```
16-pitest/
├── target.py                 # Code under mutation test
├── mutator.py                # Mutation operators
├── runner.py                 # Runs the suite against mutants
├── suite.py                  # Strong test suite
├── requirements.txt
├── conftest.py
└── tests/
    └── test_pitest.py
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

The test suite verifies that all eight expected mutations are generated, that the strong test suite kills every mutant, and that a weak test suite lets the boundary mutant survive. This demonstrates that mutation score is a more meaningful signal than line coverage.
