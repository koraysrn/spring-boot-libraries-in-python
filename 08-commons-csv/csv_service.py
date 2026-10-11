"""CSV read and write helpers, the equivalent of commons-csv.

Spring Boot equivalents:
    - CSVPrinter / CSVFormat  -> csv.writer / csv.DictWriter
    - CSVParser               -> csv.reader / csv.DictReader
    - ExportService.java      -> export_csv
"""

import csv
import io

CSV_INJECTION_PREFIXES = ("=", "+", "-", "@")


def neutralize_csv_injection(value):
    """Prefix values that Excel would interpret as formulas."""
    if isinstance(value, str) and value.startswith(CSV_INJECTION_PREFIXES):
        return "'" + value
    return value


def export_csv(rows, fieldnames=None, delimiter=",", neutralize=True) -> str:
    """Serialize a list of dictionaries into a CSV string."""
    if not rows:
        return ""
    fieldnames = fieldnames or list(rows[0].keys())
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=fieldnames, delimiter=delimiter
    )
    writer.writeheader()
    for row in rows:
        if neutralize:
            row = {key: neutralize_csv_injection(value) for key, value in row.items()}
        writer.writerow(row)
    return buffer.getvalue()


def stream_csv(lines, delimiter=",", fieldnames=None, on_bad_row=None):
    """Yield dictionaries row by row without loading the whole input."""
    reader = csv.reader(lines, delimiter=delimiter)

    if fieldnames is None:
        try:
            fieldnames = next(reader)
        except StopIteration:
            return

    line_number = 0
    for raw in reader:
        line_number += 1
        if len(raw) < len(fieldnames):
            if on_bad_row:
                on_bad_row(
                    line_number,
                    f"missing columns: expected {len(fieldnames)}, got {len(raw)}",
                )
            raw = raw + [None] * (len(fieldnames) - len(raw))
        elif len(raw) > len(fieldnames):
            if on_bad_row:
                on_bad_row(
                    line_number,
                    f"extra columns: expected {len(fieldnames)}, got {len(raw)}",
                )
            raw = raw[: len(fieldnames)]
        yield dict(zip(fieldnames, raw))


def import_csv(text, delimiter=",", fieldnames=None, on_bad_row=None) -> list:
    return list(
        stream_csv(
            io.StringIO(text, newline=""),
            delimiter=delimiter,
            fieldnames=fieldnames,
            on_bad_row=on_bad_row,
        )
    )


def import_csv_bytes(
    data, encoding="utf-8-sig", delimiter=",", on_bad_row=None
) -> list:
    """Decode CSV bytes and parse them. utf-8-sig strips a leading BOM."""
    return import_csv(
        data.decode(encoding),
        delimiter=delimiter,
        on_bad_row=on_bad_row,
    )


def parse_numeric(value):
    """Convert a numeric string to float, leaving non-numeric values intact."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return value
