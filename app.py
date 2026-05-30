"""Mock Data Factory — Flask application.

Generates realistic mock data based on a user-supplied schema and exports it
as CSV, JSON, XML, SQL, or Excel.
"""
from __future__ import annotations

import csv
import io
import json
import logging
import os
import random
import xml.dom.minidom
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any, Callable

import openpyxl
from faker import Faker
from flask import Flask, jsonify, render_template, request, send_file
from openpyxl.utils import get_column_letter

app = Flask(__name__)
fake = Faker()
logger = logging.getLogger(__name__)

# Hard cap to protect against memory exhaustion / DoS.
MAX_ROWS = int(os.getenv("MOCK_DATA_MAX_ROWS", "100000"))
MAX_PREVIEW_ROWS = 100

DEFAULT_SCHEMA = [
    {"name": "id", "type": "Row Number"},
    {"name": "first_name", "type": "First Name"},
    {"name": "last_name", "type": "Last Name"},
    {"name": "email", "type": "Email Address"},
    {"name": "gender", "type": "Gender"},
    {"name": "ip_address", "type": "IP Address v4"},
]

SUPPORTED_FORMATS = {"CSV", "JSON", "XML", "SQL", "EXCEL"}


class SchemaError(ValueError):
    """Raised for any user-facing schema validation failure."""


def _date_within_last_five_years(_config: dict | None = None) -> str:
    start = datetime.now() - timedelta(days=365 * 5)
    end = datetime.now()
    return fake.date_between(start_date=start, end_date=end).strftime("%Y-%m-%d")


def _custom_list(config: dict | None) -> str:
    if config and config.get("values"):
        return random.choice(config["values"])
    return ""


# Dispatch table — extending the generator is just one new entry.
GENERATORS: dict[str, Callable[[dict | None], Any]] = {
    "Row Number": lambda _c: None,  # Filled by index in generate_data.
    "First Name": lambda _c: fake.first_name(),
    "Last Name": lambda _c: fake.last_name(),
    "Full Name": lambda _c: fake.name(),
    "Email Address": lambda _c: fake.email(),
    "Gender": lambda _c: random.choice(("Male", "Female", "Other")),
    "IP Address v4": lambda _c: fake.ipv4(),
    "Phone Number": lambda _c: fake.phone_number(),
    "City": lambda _c: fake.city(),
    "Country": lambda _c: fake.country(),
    "Date": _date_within_last_five_years,
    "Number": lambda _c: random.randint(1, 1000),
    "Decimal": lambda _c: round(random.uniform(0, 1000), 2),
    "Custom List": _custom_list,
    # Legacy "Blank/Null" type — kept for backward compatibility with old
    # client schemas. Prefer the per-field "blank_percentage" modifier now.
    "Blank/Null": lambda c: None if random.random() < ((c or {}).get("blank_percentage", 0) / 100) else fake.word(),
}


def generate_value(field_type: str, field_config: dict | None = None) -> Any:
    """Generate a single value for a field type."""
    gen = GENERATORS.get(field_type)
    return gen(field_config) if gen else ""


def generate_data(schema: dict, max_rows: int | None = None) -> list[dict]:
    """Generate rows for the schema. `max_rows` (if provided) caps row count."""
    requested = int(schema["num_rows"])
    if requested < 1:
        raise SchemaError("num_rows must be at least 1")

    num_rows = min(requested, max_rows) if max_rows else requested
    num_rows = min(num_rows, MAX_ROWS)

    fields = schema["fields"]
    data: list[dict] = []
    # Python 3.7+ dicts preserve insertion order, so iterating `fields`
    # already produces a deterministic column order.
    for i in range(num_rows):
        row: dict[str, Any] = {}
        for field in fields:
            value = generate_value(field["type"], field)
            if field["type"] == "Row Number":
                value = i + 1
            # Per-field blank modifier (works for any type, not just Blank/Null).
            blank_pct = field.get("blank_percentage")
            if blank_pct and random.random() < (blank_pct / 100):
                value = None
            row[field["name"]] = value
        data.append(row)
    return data


def format_csv(data: list[dict]) -> str:
    """Render data as a CSV string."""
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    return output.getvalue()


def format_json(data: list[dict]) -> str:
    """Render data as a JSON string."""
    return json.dumps(data, indent=2)


def format_xml(data: list[dict]) -> str:
    """Render data as a pretty-printed XML string."""
    root = ET.Element("records")
    for item in data:
        record = ET.SubElement(root, "record")
        for key, value in item.items():
            field = ET.SubElement(record, key)
            field.text = "" if value is None else str(value)

    xml_bytes = ET.tostring(root, encoding="utf-8")
    pretty = xml.dom.minidom.parseString(xml_bytes).toprettyxml(indent="  ")
    # Strip the <?xml ... ?> declaration line.
    if pretty.startswith("<?xml"):
        pretty = "\n".join(pretty.splitlines()[1:])
    return pretty


def _infer_sql_type(column: str, data: list[dict]) -> str:
    """Detect the SQL column type from the first non-null value in the column."""
    for row in data:
        value = row.get(column)
        if value is None:
            continue
        # bool is a subclass of int — exclude it to avoid surprising INTEGER columns.
        if isinstance(value, bool):
            return "INTEGER"
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "REAL"
        if isinstance(value, str) and value.strip():
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return "DATE"
            except ValueError:
                return "TEXT"
        return "TEXT"
    return "TEXT"


def format_sql(data: list[dict], table_name: str = "mock_data") -> str:
    """Render data as a CREATE TABLE + INSERT script."""
    if not data:
        return ""

    columns = list(data[0].keys())
    lines = [
        "-- SQL Data Export",
        f"-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"CREATE TABLE IF NOT EXISTS {table_name} (",
    ]
    column_defs = [f"    {col} {_infer_sql_type(col, data)}" for col in columns]
    lines.append(",\n".join(column_defs))
    lines.append(");")
    lines.append("")

    column_list = ", ".join(columns)
    for row in data:
        values = []
        for col in columns:
            value = row[col]
            if value is None:
                values.append("NULL")
            elif isinstance(value, bool):
                values.append("1" if value else "0")
            elif isinstance(value, (int, float)):
                values.append(str(value))
            else:
                escaped = str(value).replace("'", "''")
                values.append(f"'{escaped}'")
        lines.append(f"INSERT INTO {table_name} ({column_list}) VALUES ({', '.join(values)});")

    return "\n".join(lines)


def format_excel(data: list[dict]) -> bytes | None:
    """Render data as an .xlsx byte string."""
    if not data:
        return None

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mock Data"

    headers = list(data[0].keys())
    bold = openpyxl.styles.Font(bold=True)
    max_widths = [len(str(h)) for h in headers]

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = bold

    # Single pass: write data and track max width simultaneously.
    for row_idx, row_data in enumerate(data, 2):
        for col_idx, header in enumerate(headers, 1):
            value = row_data[header]
            ws.cell(row=row_idx, column=col_idx, value=value)
            if value is not None:
                width = len(str(value))
                if width > max_widths[col_idx - 1]:
                    max_widths[col_idx - 1] = width

    for col_idx, width in enumerate(max_widths, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width + 2

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


FORMATTERS: dict[str, dict] = {
    "CSV": {"format": format_csv, "mime": "text/csv", "ext": "csv"},
    "JSON": {"format": format_json, "mime": "application/json", "ext": "json"},
    "XML": {"format": format_xml, "mime": "application/xml", "ext": "xml"},
    "SQL": {"format": format_sql, "mime": "text/plain", "ext": "sql"},
    "EXCEL": {
        "format": format_excel,
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ext": "xlsx",
    },
}


def _validate_schema(schema: Any) -> dict:
    """Validate the incoming schema, raising SchemaError on any issue."""
    if not isinstance(schema, dict):
        raise SchemaError("Schema must be a JSON object")
    for key in ("fields", "num_rows", "format"):
        if key not in schema:
            raise SchemaError(f"Schema missing required key: {key}")
    if not isinstance(schema["fields"], list) or not schema["fields"]:
        raise SchemaError("Schema must contain at least one field")
    fmt = str(schema["format"]).upper()
    if fmt not in SUPPORTED_FORMATS:
        raise SchemaError(f"Unsupported format: {schema['format']}")
    try:
        rows = int(schema["num_rows"])
    except (TypeError, ValueError) as exc:
        raise SchemaError("num_rows must be an integer") from exc
    if rows < 1:
        raise SchemaError("num_rows must be at least 1")
    if rows > MAX_ROWS:
        raise SchemaError(f"num_rows must not exceed {MAX_ROWS}")
    return schema


@app.route("/")
def index():
    return render_template("index.html", default_schema=DEFAULT_SCHEMA)


@app.route("/preview", methods=["POST"])
def preview():
    """Return a small preview of the data in the requested format."""
    try:
        schema = _validate_schema(request.get_json(silent=True))
    except SchemaError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        data = generate_data(schema, MAX_PREVIEW_ROWS)
        fmt = schema["format"].upper()
        if fmt in ("CSV", "EXCEL"):
            field_names = [field["name"] for field in schema["fields"]]
            return jsonify({"data": data, "field_order": field_names}), 200

        formatter = FORMATTERS[fmt]["format"]
        return formatter(data), 200, {"Content-Type": "text/plain"}
    except SchemaError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Unexpected error generating preview")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/generate", methods=["POST"])
def generate():
    """Generate the full dataset and stream it back as a file download."""
    try:
        schema = _validate_schema(request.get_json(silent=True))
    except SchemaError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        # Legacy `?preview=true` path — return JSON, no download.
        if request.args.get("preview") == "true":
            data = generate_data(schema)
            field_names = [field["name"] for field in schema["fields"]]
            return jsonify({"data": data, "field_order": field_names})

        data = generate_data(schema)
        fmt = schema["format"].upper()
        info = FORMATTERS[fmt]
        output = info["format"](data)
        if isinstance(output, str):
            output = output.encode("utf-8")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(
            io.BytesIO(output or b""),
            mimetype=info["mime"],
            as_attachment=True,
            download_name=f"mock_data_{timestamp}.{info['ext']}",
        )
    except SchemaError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Unexpected error generating data")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="127.0.0.1", port=int(os.getenv("PORT", "5000")))
