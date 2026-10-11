# lombok

A Python implementation of the boilerplate code generation provided by Lombok in Spring Boot. This module uses dataclasses and Pydantic as the equivalents of Lombok annotations.

## Overview

In Java, Lombok generates repeated getter, setter, constructor, `equals`, `hashCode`, and `toString` methods at compile time using annotations such as `@Getter` and `@Setter`.

| Lombok Annotation | Python Equivalent |
|---|---|
| @Getter @Setter | @dataclass (mutable) |
| @Value | @dataclass(frozen=True) |
| @AllArgsConstructor | Generated `__init__` |
| @EqualsAndHashCode | Generated `__eq__` / `__hash__` |
| @ToString | Generated `__repr__` |
| @NoArgsConstructor | `field(default=...)` |

## Features

- Mutable data class with generated `__init__`, `__eq__`, and `__repr__`.
- Immutable value object through `frozen=True`.
- Default values through `field(default=...)`.
- Safe mutable defaults through `field(default_factory=...)`.
- Post init validation through `__post_init__`.
- Inheritance support that merges fields.
- A Pydantic model for comparison, demonstrating that Pydantic validates while a dataclass does not.

## Project Structure

```
09-lombok/
├── models.py                 # Dataclass models
├── pydantic_models.py        # Pydantic model for comparison
├── requirements.txt
├── conftest.py
└── tests/
    └── test_lombok.py
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

The test suite focuses on non-happy-path scenarios. It verifies value equality, that frozen instances cannot be modified, that defaults are applied, that post init validation raises, that repr includes fields, that mutable defaults are not shared, that frozen value objects are hashable, that inheritance merges fields, that Pydantic validates where a dataclass does not, and that mutable dataclasses are unhashable.
