"""Tests for the Mock Data Factory app."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import (  # noqa: E402
    MAX_ROWS,
    SchemaError,
    _infer_sql_type,
    _validate_schema,
    app,
    format_csv,
    format_json,
    format_sql,
    format_xml,
    generate_data,
    generate_value,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def schema():
    return {
        "fields": [
            {"name": "id", "type": "Row Number"},
            {"name": "first_name", "type": "First Name"},
            {"name": "email", "type": "Email Address"},
        ],
        "num_rows": 5,
        "format": "JSON",
    }


# ---- generate_value -------------------------------------------------------

def test_generate_value_known_types_produce_values():
    for t in ["First Name", "Last Name", "Email Address", "City", "Country",
              "Number", "Decimal", "Date", "Gender", "IP Address v4", "Phone Number"]:
        assert generate_value(t) is not None


def test_generate_value_unknown_type_returns_empty_string():
    assert generate_value("Not A Real Type") == ""


def test_custom_list_uses_provided_values():
    config = {"values": ["a", "b", "c"]}
    for _ in range(20):
        assert generate_value("Custom List", config) in {"a", "b", "c"}


def test_custom_list_without_values_returns_empty():
    assert generate_value("Custom List", {}) == ""
    assert generate_value("Custom List", None) == ""


# ---- generate_data --------------------------------------------------------

def test_generate_data_respects_num_rows(schema):
    data = generate_data(schema)
    assert len(data) == 5


def test_generate_data_caps_at_max_rows():
    schema = {
        "fields": [{"name": "id", "type": "Row Number"}],
        "num_rows": MAX_ROWS + 100,
        "format": "JSON",
    }
    data = generate_data(schema)
    assert len(data) == MAX_ROWS


def test_generate_data_row_number_is_sequential(schema):
    data = generate_data(schema)
    assert [row["id"] for row in data] == [1, 2, 3, 4, 5]


def test_generate_data_preserves_field_order():
    schema = {
        "fields": [
            {"name": "z_field", "type": "First Name"},
            {"name": "a_field", "type": "Last Name"},
            {"name": "m_field", "type": "City"},
        ],
        "num_rows": 3,
        "format": "JSON",
    }
    data = generate_data(schema)
    for row in data:
        assert list(row.keys()) == ["z_field", "a_field", "m_field"]


def test_generate_data_rejects_zero_rows():
    schema = {"fields": [{"name": "id", "type": "Row Number"}], "num_rows": 0, "format": "JSON"}
    with pytest.raises(SchemaError):
        generate_data(schema)


def test_blank_percentage_modifier_produces_nulls():
    schema = {
        "fields": [{"name": "name", "type": "First Name", "blank_percentage": 100}],
        "num_rows": 10,
        "format": "JSON",
    }
    data = generate_data(schema)
    assert all(row["name"] is None for row in data)


# ---- formatters -----------------------------------------------------------

def test_format_csv_writes_header_and_rows():
    data = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    out = format_csv(data)
    lines = out.strip().splitlines()
    assert lines[0] == "a,b"
    assert lines[1] == "1,x"
    assert lines[2] == "2,y"


def test_format_csv_empty():
    assert format_csv([]) == ""


def test_format_json_is_parseable():
    data = [{"x": 1}, {"x": 2}]
    parsed = json.loads(format_json(data))
    assert parsed == data


def test_format_xml_has_record_per_row():
    data = [{"name": "Alice"}, {"name": "Bob"}]
    out = format_xml(data)
    assert "<records>" in out
    assert out.count("<record>") == 2
    assert "Alice" in out and "Bob" in out


def test_format_xml_handles_none_as_empty():
    data = [{"x": None}]
    out = format_xml(data)
    assert "<x/>" in out or "<x></x>" in out


def test_format_sql_escapes_single_quotes():
    data = [{"name": "O'Hara"}]
    out = format_sql(data)
    assert "'O''Hara'" in out


def test_format_sql_uses_correct_column_types():
    data = [
        {"id": 1, "price": 9.99, "name": "x", "created": "2024-01-01"},
    ]
    out = format_sql(data)
    assert "id INTEGER" in out
    assert "price REAL" in out
    assert "name TEXT" in out
    assert "created DATE" in out


def test_infer_sql_type_skips_leading_nulls():
    # Bug-regression: original code broke on first iteration even if value was None.
    data = [{"a": None}, {"a": None}, {"a": 42}]
    assert _infer_sql_type("a", data) == "INTEGER"


def test_format_sql_handles_bool_as_integer():
    data = [{"flag": True}, {"flag": False}]
    out = format_sql(data)
    assert "flag INTEGER" in out
    assert "VALUES (1)" in out
    assert "VALUES (0)" in out


def test_format_sql_empty():
    assert format_sql([]) == ""


# ---- _validate_schema -----------------------------------------------------

def test_validate_schema_rejects_missing_keys():
    with pytest.raises(SchemaError):
        _validate_schema({"fields": []})


def test_validate_schema_rejects_empty_fields():
    with pytest.raises(SchemaError):
        _validate_schema({"fields": [], "num_rows": 1, "format": "CSV"})


def test_validate_schema_rejects_unknown_format():
    with pytest.raises(SchemaError):
        _validate_schema({"fields": [{"name": "a", "type": "First Name"}], "num_rows": 1, "format": "yaml"})


def test_validate_schema_rejects_negative_rows():
    with pytest.raises(SchemaError):
        _validate_schema({"fields": [{"name": "a", "type": "First Name"}], "num_rows": -1, "format": "CSV"})


def test_validate_schema_rejects_excessive_rows():
    with pytest.raises(SchemaError):
        _validate_schema({
            "fields": [{"name": "a", "type": "First Name"}],
            "num_rows": MAX_ROWS + 1,
            "format": "CSV",
        })


# ---- HTTP endpoints -------------------------------------------------------

def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Mock Data Factory" in response.data


def test_preview_returns_data_for_csv(client, schema):
    schema["format"] = "CSV"
    response = client.post("/preview", json=schema)
    assert response.status_code == 200
    payload = response.get_json()
    assert "data" in payload
    assert "field_order" in payload
    assert payload["field_order"] == ["id", "first_name", "email"]


def test_preview_returns_text_for_json(client, schema):
    response = client.post("/preview", json=schema)
    assert response.status_code == 200
    json.loads(response.get_data(as_text=True))  # must parse


def test_preview_rejects_invalid_schema(client):
    response = client.post("/preview", json={"bad": "schema"})
    assert response.status_code == 400


def test_preview_rejects_oversized_request(client):
    response = client.post("/preview", json={
        "fields": [{"name": "id", "type": "Row Number"}],
        "num_rows": MAX_ROWS + 1,
        "format": "CSV",
    })
    assert response.status_code == 400


def test_generate_returns_csv_attachment(client, schema):
    schema["format"] = "CSV"
    response = client.post("/generate", json=schema)
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]


def test_generate_returns_excel_with_xlsx_extension(client, schema):
    schema["format"] = "EXCEL"
    response = client.post("/generate", json=schema)
    assert response.status_code == 200
    assert ".xlsx" in response.headers["Content-Disposition"]
