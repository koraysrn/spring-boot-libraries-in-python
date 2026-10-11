# commons-csv

A Python implementation of the CSV reading and writing provided by the `commons-csv` library in Spring Boot. This module uses the built-in `csv` module, which is the standard Python equivalent.

## Overview

In Spring Boot, `commons-csv` reads and writes CSV files. The `ExportService` class uses it to export and import user transactions.

| commons-csv Concept | Python Equivalent |
|---|---|
| CSVPrinter / CSVFormat | csv.writer / csv.DictWriter |
| CSVParser | csv.reader / csv.DictReader |
| ExportService.java | export_csv |

## Features

- CSV export from a list of dictionaries with a header row.
- CSV import with header detection.
- Streaming import that does not load the whole file into memory.
- Reporting of rows with missing or extra columns.
- Support for custom delimiters such as semicolon.
- UTF-8 with BOM handling through `utf-8-sig`.
- CSV injection neutralization for values starting with `=`, `+`, `-`, or `@`.
- Controlled numeric type conversion.

## Project Structure

```
08-commons-csv/
├── csv_service.py           # CSV helpers
├── requirements.txt
├── conftest.py
└── tests/
    └── test_commons_csv.py
```

## Requirements

- Python 3.12 or newer

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Usage

```python
from csv_service import export_csv, import_csv

rows = export_csv([{"name": "Ali", "amount": 100}])
parsed = import_csv(rows)
```

## Testing

```bash
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that values containing commas and double quotes are escaped correctly, that empty and header only files return an empty list, that rows with missing or extra columns are reported, that large files are streamed, that Turkish characters survive a UTF-8 with BOM roundtrip, that semicolon delimiters are supported, that formula injection is neutralized on export, that mixed line endings are parsed, and that numeric type conversion is controlled.
