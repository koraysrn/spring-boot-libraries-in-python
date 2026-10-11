"""
Non-happy-path tests for the commons-csv equivalent (built-in csv module).
"""

from csv_service import (
    export_csv,
    import_csv,
    import_csv_bytes,
    parse_numeric,
    stream_csv,
)


def test_value_with_comma_stays_in_one_cell():
    csv_text = export_csv([{"name": "Ali, Veli", "amount": 100}])
    rows = import_csv(csv_text)
    assert rows[0]["name"] == "Ali, Veli"


def test_value_with_double_quote_is_escaped():
    csv_text = export_csv([{"note": 'He said "hi"'}])
    rows = import_csv(csv_text)
    assert rows[0]["note"] == 'He said "hi"'


def test_empty_file_returns_empty_list():
    assert import_csv("") == []


def test_header_only_file_returns_empty_list():
    assert import_csv("name,amount\n") == []


def test_missing_column_row_is_reported():
    bad_rows = []
    rows = import_csv(
        "name,amount\nAli\n",
        on_bad_row=lambda line, msg: bad_rows.append((line, msg)),
    )
    assert rows == [{"name": "Ali", "amount": None}]
    assert len(bad_rows) == 1


def test_extra_column_row_is_ignored():
    bad_rows = []
    rows = import_csv(
        "name,amount\nAli,10,EXTRA\n",
        on_bad_row=lambda line, msg: bad_rows.append((line, msg)),
    )
    assert rows == [{"name": "Ali", "amount": "10"}]
    assert len(bad_rows) == 1


def test_large_file_is_streamed():
    def lines():
        yield "id,name\n"
        for i in range(1_000_000):
            yield f"{i},row{i}\n"

    count = sum(1 for _ in stream_csv(lines()))
    assert count == 1_000_000


def test_turkish_characters_are_preserved():
    data = "isim\nİstanbul ğüşiöç\n".encode("utf-8-sig")
    rows = import_csv_bytes(data)
    assert rows[0]["isim"] == "İstanbul ğüşiöç"


def test_semicolon_delimiter_is_supported():
    rows = import_csv("name;amount\nAli;10\n", delimiter=";")
    assert rows[0]["amount"] == "10"


def test_csv_injection_is_neutralized_on_export():
    csv_text = export_csv([{"note": "=1+1"}, {"note": "+cmd()"}])
    rows = import_csv(csv_text)
    assert rows[0]["note"] == "'=1+1"
    assert rows[1]["note"] == "'+cmd()"


def test_mixed_line_endings_are_parsed():
    rows = import_csv("a,b\r\n1,2\n3,4\r\n")
    assert len(rows) == 2
    assert rows[0]["a"] == "1"
    assert rows[1]["b"] == "4"


def test_numeric_type_conversion_is_controlled():
    assert parse_numeric("100.5") == 100.5
    assert parse_numeric("abc") == "abc"
    assert parse_numeric(None) is None
    assert parse_numeric("") is None
