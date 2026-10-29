"""Mock Data Factory — Flask application.

Generates realistic mock data based on a user-supplied schema and exports it
as CSV, JSON, XML, SQL, or Excel.

Supports inter-field templates (e.g. `{{first_name|lower}}.{{last_name|lower}}@example.com`)
and schema inference from SQL DDL, JSON samples, or TypeScript interfaces.
"""
from __future__ import annotations

import csv
import io
import json
import logging
import os
import random
import re
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
# Rows × fields: MAX_ROWS alone still allows 100k rows × 200 fields = 20M cells,
# which an in-memory Excel export can't handle on a small server.
MAX_CELLS = int(os.getenv("MOCK_DATA_MAX_CELLS", "2000000"))
MAX_PREVIEW_ROWS = 100
MAX_INFER_SOURCE = 32_000  # ~32KB of source text for inference
MAX_FIELDS = 200            # cap field count per schema
MAX_TEMPLATE_LENGTH = 1_000  # characters per Template field
MAX_CONTENT_LENGTH = 256 * 1024  # 256KB request body cap

# Reject oversized request bodies before Flask hands them to a route.
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

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


# ---------- Generators ---------------------------------------------------

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
    "Blank/Null": lambda c: None if random.random() < ((c or {}).get("blank_percentage", 0) / 100) else "",
    # Template values are filled in a second pass after all other fields exist.
    "Template": lambda _c: None,
}


def generate_value(field_type: str, field_config: dict | None = None) -> Any:
    """Generate a single value for a field type."""
    gen = GENERATORS.get(field_type)
    return gen(field_config) if gen else ""


# ---------- Template engine ---------------------------------------------

# The field name and the filter chain are matched by character classes that
# can't overlap with their neighbours, so an unclosed token such as "{{x|   …"
# fails in linear time instead of backtracking catastrophically. Whitespace
# around filter names is trimmed in Python rather than in the pattern.
_TEMPLATE_TOKEN = re.compile(r"\{\{\s*([^{}|\s]+)\s*(?:\|([^}]*))?\}\}")


def _filter_slug(value: str) -> str:
    return re.sub(r"\W+", "-", str(value)).strip("-").lower()


def _filter_initial(value: str) -> str:
    s = str(value).strip()
    return s[0].upper() if s else ""


def _filter_digits(value: str) -> str:
    return re.sub(r"\D", "", str(value))


TEMPLATE_FILTERS: dict[str, Callable[[Any], Any]] = {
    "lower": lambda v: str(v).lower(),
    "upper": lambda v: str(v).upper(),
    "title": lambda v: str(v).title(),
    "slug": _filter_slug,
    "nospace": lambda v: str(v).replace(" ", ""),
    "initial": _filter_initial,
    "digits": _filter_digits,
    "trim": lambda v: str(v).strip(),
}


def compile_template(template: str) -> list[str | tuple[str, tuple[Callable[[Any], Any], ...]]]:
    """Parse a template once into literal strings and `(field, filters)` tokens.

    Unknown filters are dropped here, so rendering a row is a plain loop with
    no regex work — templates are parsed once per request, not once per row.
    """
    parts: list[str | tuple[str, tuple[Callable[[Any], Any], ...]]] = []
    pos = 0
    for match in _TEMPLATE_TOKEN.finditer(template or ""):
        if match.start() > pos:
            parts.append(template[pos:match.start()])
        filter_names = (f.strip() for f in (match.group(2) or "").split("|"))
        filters = tuple(TEMPLATE_FILTERS[f] for f in filter_names if f in TEMPLATE_FILTERS)
        parts.append((match.group(1), filters))
        pos = match.end()
    if template and pos < len(template):
        parts.append(template[pos:])
    return parts


def render_compiled_template(
    parts: list[str | tuple[str, tuple[Callable[[Any], Any], ...]]], row: dict[str, Any]
) -> str:
    """Render the output of `compile_template` against one row."""
    out: list[str] = []
    for part in parts:
        if isinstance(part, str):
            out.append(part)
            continue
        name, filters = part
        value = row.get(name, "")
        if value is None:
            value = ""
        for fn in filters:
            value = fn(value)
        out.append(str(value))
    return "".join(out)


def render_template_value(template: str, row: dict[str, Any]) -> str:
    """Replace `{{field|filter}}` tokens in `template` using values from `row`.

    Unknown fields render as empty strings; unknown filters are ignored.
    """
    if not template:
        return ""
    return render_compiled_template(compile_template(template), row)


# ---------- Core generation ---------------------------------------------

def _apply_blank_percentage(value: Any, field: dict) -> Any:
    """Null out `value` with probability `field["blank_percentage"]` percent."""
    blank_pct = field.get("blank_percentage")
    if blank_pct and random.random() < (blank_pct / 100):
        return None
    return value


def generate_data(schema: dict, max_rows: int | None = None) -> list[dict]:
    """Generate rows for the schema. `max_rows` (if provided) caps row count."""
    requested = int(schema["num_rows"])
    if requested < 1:
        raise SchemaError("num_rows must be at least 1")

    num_rows = min(requested, max_rows) if max_rows else requested
    num_rows = min(num_rows, MAX_ROWS)

    fields = schema["fields"]
    template_fields = [
        (field, compile_template(field.get("template", "") or ""))
        for field in fields
        if field["type"] == "Template"
    ]
    data: list[dict] = []

    for i in range(num_rows):
        row: dict[str, Any] = {}
        # Pass 1 — non-template fields.
        for field in fields:
            if field["type"] == "Template":
                row[field["name"]] = None
                continue
            value = generate_value(field["type"], field)
            if field["type"] == "Row Number":
                value = i + 1
            row[field["name"]] = _apply_blank_percentage(value, field)

        # Pass 2 — templates can reference any other field.
        for field, compiled in template_fields:
            value = render_compiled_template(compiled, row)
            row[field["name"]] = _apply_blank_percentage(value, field)

        data.append(row)
    return data


# ---------- Formatters --------------------------------------------------

def _column_order(data: list[dict]) -> list[str]:
    """Return field names in schema order, taken from the first row.

    All rows share the same keys (generate_data always emits every field),
    so the first row's key order is authoritative for every formatter.
    """
    return list(data[0].keys())


def _stringify_value(value: Any) -> str:
    """Render a value as export text: None becomes an empty string."""
    return "" if value is None else str(value)


# Leading characters that spreadsheet apps (Excel, Sheets, LibreOffice)
# interpret as the start of a formula. A string value starting with one of
# these gets prefixed with a single quote so it's treated as literal text.
_FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@", "\t", "\r")


def _neutralize_formula(value: Any) -> Any:
    """Prefix values that would be interpreted as spreadsheet formulas."""
    if isinstance(value, str) and value.startswith(_FORMULA_TRIGGER_CHARS):
        return "'" + value
    return value


def _sanitize_row_for_export(row: dict) -> dict:
    return {k: _neutralize_formula(v) for k, v in row.items()}


def format_csv(data: list[dict], escape_formulas: bool = True) -> str:
    """Format rows as CSV.

    `escape_formulas` (default on) prefixes values that a spreadsheet would
    run as a formula with a single quote. Turn it off when the CSV is meant
    for code rather than Excel/Sheets, so values like "+1-202-555-0100" come
    through unchanged.
    """
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=_column_order(data))
        writer.writeheader()
        if escape_formulas:
            writer.writerows(_sanitize_row_for_export(row) for row in data)
        else:
            writer.writerows(data)
    return output.getvalue()


def format_json(data: list[dict]) -> str:
    return json.dumps(data, indent=2)


_XML_NAME_INVALID = re.compile(r"[^A-Za-z0-9_\-.]")
_XML_NAME_BAD_START = re.compile(r"^[^A-Za-z_]")


def _sanitize_xml_name(name: str) -> str:
    """Coerce a column name into a syntactically valid XML element name."""
    if not name:
        return "_field"
    safe = _XML_NAME_INVALID.sub("_", name)
    if _XML_NAME_BAD_START.match(safe):
        safe = "_" + safe
    return safe


def format_xml(data: list[dict]) -> str:
    root = ET.Element("records")
    for item in data:
        record = ET.SubElement(root, "record")
        for key, value in item.items():
            field = ET.SubElement(record, _sanitize_xml_name(key))
            field.text = _stringify_value(value)

    xml_bytes = ET.tostring(root, encoding="utf-8")
    pretty = xml.dom.minidom.parseString(xml_bytes).toprettyxml(indent="  ")
    if pretty.startswith("<?xml"):
        pretty = "\n".join(pretty.splitlines()[1:])
    return pretty


def _infer_sql_type(column: str, data: list[dict]) -> str:
    for row in data:
        value = row.get(column)
        if value is None:
            continue
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


def _quote_sql_identifier(name: str) -> str:
    """Quote a SQL identifier (table or column name) for safe interpolation.

    Field names are user-controlled; wrapping in double quotes and doubling
    any embedded double quotes prevents identifier injection while staying
    valid across common SQL dialects (SQLite, Postgres, standard SQL).
    """
    escaped = str(name).replace('"', '""')
    return f'"{escaped}"'


def format_sql(data: list[dict], table_name: str = "mock_data") -> str:
    if not data:
        return ""

    columns = _column_order(data)
    quoted_table = _quote_sql_identifier(table_name)
    lines = [
        "-- SQL Data Export",
        "-- Dialect: SQLite / PostgreSQL (double-quoted identifiers, standard string escaping).",
        "-- For MySQL, enable ANSI_QUOTES and NO_BACKSLASH_ESCAPES before importing.",
        f"-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"CREATE TABLE IF NOT EXISTS {quoted_table} (",
    ]
    column_defs = [f"    {_quote_sql_identifier(col)} {_infer_sql_type(col, data)}" for col in columns]
    lines.append(",\n".join(column_defs))
    lines.append(");")
    lines.append("")

    column_list = ", ".join(_quote_sql_identifier(col) for col in columns)
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
        lines.append(f"INSERT INTO {quoted_table} ({column_list}) VALUES ({', '.join(values)});")

    return "\n".join(lines)


def format_excel(data: list[dict]) -> bytes | None:
    if not data:
        return None

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mock Data"

    headers = _column_order(data)
    bold = openpyxl.styles.Font(bold=True)
    max_widths = [len(str(h)) for h in headers]

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = bold

    for row_idx, row_data in enumerate(data, 2):
        for col_idx, header in enumerate(headers, 1):
            value = row_data[header]
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            if isinstance(value, str):
                # openpyxl turns strings starting with "=" into formulas (and
                # "#N/A"-style strings into errors). Force plain text instead of
                # prefixing a quote, which would show up as part of the value.
                cell.data_type = "s"
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


# ---------- Schema validation -------------------------------------------

def _validate_schema(schema: Any) -> dict:
    if not isinstance(schema, dict):
        raise SchemaError("Schema must be a JSON object")
    for key in ("fields", "num_rows", "format"):
        if key not in schema:
            raise SchemaError(f"Schema missing required key: {key}")
    if not isinstance(schema["fields"], list) or not schema["fields"]:
        raise SchemaError("Schema must contain at least one field")
    if len(schema["fields"]) > MAX_FIELDS:
        raise SchemaError(f"Schema may contain at most {MAX_FIELDS} fields")

    # Per-field shape check — keeps malformed input from reaching the
    # generator (and turning into a 500).
    seen_names: set[str] = set()
    for idx, field in enumerate(schema["fields"], 1):
        if not isinstance(field, dict):
            raise SchemaError(f"Field #{idx} must be an object")
        name = field.get("name")
        if not isinstance(name, str) or not name.strip():
            raise SchemaError(f"Field #{idx} requires a non-empty name")
        if name in seen_names:
            raise SchemaError(f'Duplicate field name "{name}"')
        seen_names.add(name)
        ftype = field.get("type")
        if not isinstance(ftype, str) or not ftype:
            raise SchemaError(f'Field "{name}" requires a "type" string')
        if ftype not in GENERATORS:
            raise SchemaError(f'Field "{name}" has an unknown type "{ftype}"')
        if ftype == "Custom List":
            values = field.get("values")
            if not isinstance(values, list) or not values:
                raise SchemaError(f'Custom List field "{name}" needs a non-empty "values" list')
            if not all(isinstance(v, (str, int, float, bool)) for v in values):
                raise SchemaError(f'Custom List field "{name}" values must be strings or numbers')
        if ftype == "Template":
            template = field.get("template")
            if not isinstance(template, str) or not template.strip():
                raise SchemaError(f'Template field "{name}" needs a "template" string')
            if len(template) > MAX_TEMPLATE_LENGTH:
                raise SchemaError(
                    f'Template field "{name}" must be at most {MAX_TEMPLATE_LENGTH} characters'
                )
        pct = field.get("blank_percentage")
        if pct is not None:
            try:
                pct_int = int(pct)
            except (TypeError, ValueError) as exc:
                raise SchemaError(f'blank_percentage on "{name}" must be an integer') from exc
            if not 0 <= pct_int <= 100:
                raise SchemaError(f'blank_percentage on "{name}" must be between 0 and 100')
            # Store the normalized number: the generator divides by it, so a
            # numeric string like "50" used to pass validation and then 500.
            field["blank_percentage"] = pct_int

    escape_formulas = schema.get("csv_formula_escape", True)
    if not isinstance(escape_formulas, bool):
        raise SchemaError("csv_formula_escape must be true or false")

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
    cells = rows * len(schema["fields"])
    if cells > MAX_CELLS:
        raise SchemaError(
            f"num_rows × fields = {cells:,} cells; the limit is {MAX_CELLS:,}. "
            "Reduce the row count or the number of fields."
        )
    return schema


# ---------- Schema inference --------------------------------------------

def _name_tokens(name: str) -> list[str]:
    """Split snake_case, kebab-case and camelCase names into lower-case words.

    "createdAt" -> ["created", "at"], "IPAddress" -> ["ip", "address"].
    """
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", name)
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", spaced)
    return [t.lower() for t in re.split(r"[^A-Za-z0-9]+", spaced) if t]


def _has_phrase(tokens: list[str], *phrase: str) -> bool:
    """True when `phrase` appears as consecutive words in `tokens`."""
    n = len(phrase)
    return any(tuple(tokens[i:i + n]) == phrase for i in range(len(tokens) - n + 1))


def _is_row_number(t: list[str]) -> bool:
    return bool(t) and t[-1] == "id"


def _is_email(t: list[str]) -> bool:
    return bool({"email", "mail", "emailaddress"} & set(t))


def _is_ip(t: list[str]) -> bool:
    return bool({"ip", "ipv4", "ipaddress", "ipaddr"} & set(t))


def _is_phone(t: list[str]) -> bool:
    return bool({"phone", "tel", "telephone", "mobile", "cell", "cellphone", "phonenumber"} & set(t))


def _is_first_name(t: list[str]) -> bool:
    return (
        any(_has_phrase(t, w, "name") for w in ("first", "given", "fore"))
        or bool({"firstname", "givenname", "forename", "fname"} & set(t))
    )


def _is_last_name(t: list[str]) -> bool:
    return (
        any(_has_phrase(t, w, "name") for w in ("last", "family", "sur"))
        or bool({"lastname", "surname", "familyname", "lname"} & set(t))
    )


def _is_full_name(t: list[str]) -> bool:
    return (
        t in (["name"], ["user", "name"], ["username"])
        or _has_phrase(t, "full", "name")
        or _has_phrase(t, "display", "name")
        or bool({"fullname", "displayname"} & set(t))
    )


_DATE_WORDS = {
    "created", "updated", "deleted", "modified", "date", "time", "datetime",
    "timestamp", "birth", "birthday", "birthdate", "dob",
}


def _is_date(t: list[str]) -> bool:
    # "*_at" (created_at, publishedAt) is the usual timestamp convention.
    return bool(_DATE_WORDS & set(t)) or (len(t) > 1 and t[-1] == "at")


# Order matters — first match wins. Names are compared word by word, so
# e.g. "paid" is not an id, "message" is not an age and "hotel" is not a phone.
NAME_HEURISTICS: list[tuple[Callable[[list[str]], bool], str]] = [
    (_is_row_number, "Row Number"),
    (_is_email, "Email Address"),
    (_is_ip, "IP Address v4"),
    (_is_phone, "Phone Number"),
    (_is_first_name, "First Name"),
    (_is_last_name, "Last Name"),
    (_is_full_name, "Full Name"),
    (lambda t: bool({"gender", "sex"} & set(t)), "Gender"),
    (lambda t: bool({"city", "town"} & set(t)), "City"),
    (lambda t: bool({"country", "nation", "nationality"} & set(t)), "Country"),
    (_is_date, "Date"),
    (lambda t: bool({"price", "amount", "cost", "salary", "balance", "total", "decimal", "rate",
                     "discount"} & set(t)), "Decimal"),
    (lambda t: bool({"count", "qty", "quantity", "number", "age", "rank", "score", "year"} & set(t)),
     "Number"),
]


def _name_to_type(name: str, fallback: str = "Full Name") -> str:
    tokens = _name_tokens(name)
    for matches, dtype in NAME_HEURISTICS:
        if matches(tokens):
            return dtype
    return fallback


def _sql_type_to_default(sql_type: str) -> str:
    """Coarse fallback when name heuristics don't match — keyed off the SQL type."""
    t = sql_type.upper()
    if any(x in t for x in ("INT", "SERIAL", "BIGINT", "SMALLINT")):
        return "Number"
    if any(x in t for x in ("DECIMAL", "NUMERIC", "FLOAT", "DOUBLE", "REAL", "MONEY")):
        return "Decimal"
    if any(x in t for x in ("DATE", "TIME", "TIMESTAMP")):
        return "Date"
    if any(x in t for x in ("BOOL", "BIT")):
        return "Custom List"
    return "Full Name"


def _ts_type_to_default(ts_type: str) -> str:
    t = ts_type.strip().rstrip(";").strip()
    if t == "number":
        return "Number"
    if t == "boolean":
        return "Custom List"
    if t == "Date":
        return "Date"
    return "Full Name"


_CREATE_TABLE_RE = re.compile(
    r"create\s+table\s+(?:if\s+not\s+exists\s+)?[`\"\[]?(\w+)[`\"\]]?\s*\(",
    re.IGNORECASE,
)
_COLUMN_LINE_RE = re.compile(
    r"^\s*[`\"\[]?(\w+)[`\"\]]?\s+([A-Za-z][A-Za-z0-9_]*(?:\s*\(\s*\d+\s*(?:,\s*\d+\s*)*\))?)",
)


def _extract_paren_body(source: str, open_paren_idx: int) -> str:
    """Return the substring between matching parens starting at `open_paren_idx`."""
    depth = 0
    start = open_paren_idx + 1
    for i in range(open_paren_idx, len(source)):
        ch = source[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return source[start:i]
    raise SchemaError("Unclosed parenthesis in CREATE TABLE")


def infer_from_sql(source: str) -> list[dict]:
    """Parse a CREATE TABLE statement and return a list of inferred fields."""
    match = _CREATE_TABLE_RE.search(source)
    if not match:
        raise SchemaError("Could not find a CREATE TABLE statement")
    # match.end() - 1 points to the opening "(" of the column list.
    body = _extract_paren_body(source, match.end() - 1)

    fields: list[dict] = []
    depth = 0
    buf: list[str] = []
    raw_lines: list[str] = []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            raw_lines.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        raw_lines.append("".join(buf))

    skip_keywords = {"primary", "foreign", "unique", "constraint", "key", "check", "index"}

    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
        first_word = line.split()[0].strip("`\"[]").lower() if line.split() else ""
        if first_word in skip_keywords:
            continue
        m = _COLUMN_LINE_RE.match(line)
        if not m:
            continue
        col_name = m.group(1)
        sql_type = m.group(2)
        fallback = _sql_type_to_default(sql_type)
        dtype = _name_to_type(col_name, fallback)
        field: dict[str, Any] = {"name": col_name, "type": dtype}
        if dtype == "Custom List" and fallback == "Custom List":
            field["values"] = ["true", "false"]
        fields.append(field)

    if not fields:
        raise SchemaError("CREATE TABLE statement had no recognizable columns")
    return fields


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_IPV4_RE = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def _json_value_to_type(name: str, value: Any) -> dict:
    if isinstance(value, bool):
        return {"name": name, "type": "Custom List", "values": ["true", "false"]}
    if isinstance(value, int):
        return {"name": name, "type": _name_to_type(name, "Number")}
    if isinstance(value, float):
        return {"name": name, "type": _name_to_type(name, "Decimal")}
    if value is None:
        return {"name": name, "type": _name_to_type(name)}
    if isinstance(value, str):
        if _EMAIL_RE.match(value):
            return {"name": name, "type": "Email Address"}
        if _IPV4_RE.match(value):
            return {"name": name, "type": "IP Address v4"}
        if _DATE_RE.match(value):
            return {"name": name, "type": "Date"}
        return {"name": name, "type": _name_to_type(name)}
    if isinstance(value, list):
        return {"name": name, "type": _name_to_type(name)}
    if isinstance(value, dict):
        return {"name": name, "type": _name_to_type(name)}
    return {"name": name, "type": "Full Name"}


def infer_from_json(source: str) -> list[dict]:
    """Parse a JSON object or array of objects and return inferred fields."""
    try:
        parsed = json.loads(source)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"Invalid JSON: {exc.msg}") from exc

    if isinstance(parsed, list):
        if not parsed:
            raise SchemaError("JSON array is empty")
        sample = parsed[0]
    else:
        sample = parsed

    if not isinstance(sample, dict):
        raise SchemaError("JSON must be an object or an array of objects")

    return [_json_value_to_type(k, v) for k, v in sample.items()]


_TS_INTERFACE_RE = re.compile(
    r"(?:interface|type)\s+\w+\s*=?\s*\{([^}]+)\}",
    re.DOTALL,
)
# `(.+)$` instead of `(.+?)\s*$`: the lazy group and the trailing `\s*`
# overlapped, which made long whitespace runs quadratic. The type is
# stripped by the caller instead.
_TS_FIELD_RE = re.compile(r"^\s*(\w+)\s*\??\s*:\s*(.+)$")


def infer_from_typescript(source: str) -> list[dict]:
    """Parse a single TypeScript interface or type alias and return inferred fields."""
    match = _TS_INTERFACE_RE.search(source)
    if not match:
        raise SchemaError("Could not find a TypeScript interface or type")

    # Split on semicolons OR newlines so single-line and multi-line bodies work.
    body = match.group(1)
    parts = re.split(r"[;\n]", body)

    fields: list[dict] = []
    for part in parts:
        line = part.strip()
        if not line or line.startswith("//"):
            continue
        m = _TS_FIELD_RE.match(line)
        if not m:
            continue
        name, ts_type = m.group(1), m.group(2)
        fallback = _ts_type_to_default(ts_type)
        dtype = _name_to_type(name, fallback)
        field: dict[str, Any] = {"name": name, "type": dtype}
        if dtype == "Custom List" and fallback == "Custom List":
            field["values"] = ["true", "false"]
        fields.append(field)

    if not fields:
        raise SchemaError("Interface body had no recognizable fields")
    return fields


INFER_HANDLERS: dict[str, Callable[[str], list[dict]]] = {
    "sql": infer_from_sql,
    "json": infer_from_json,
    "typescript": infer_from_typescript,
    "ts": infer_from_typescript,
}


# ---------- Routes ------------------------------------------------------

@app.errorhandler(413)
def request_too_large(_e):
    return jsonify({"error": f"Request body exceeds {MAX_CONTENT_LENGTH} bytes"}), 413


@app.route("/")
def index():
    return render_template("index.html", default_schema=DEFAULT_SCHEMA)


@app.route("/preview", methods=["POST"])
def preview():
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
    try:
        schema = _validate_schema(request.get_json(silent=True))
    except SchemaError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        if request.args.get("preview") == "true":
            data = generate_data(schema)
            field_names = [field["name"] for field in schema["fields"]]
            return jsonify({"data": data, "field_order": field_names})

        data = generate_data(schema)
        fmt = schema["format"].upper()
        info = FORMATTERS[fmt]
        if fmt == "CSV":
            output = format_csv(data, escape_formulas=schema.get("csv_formula_escape", True))
        else:
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


@app.route("/infer-schema", methods=["POST"])
def infer_schema():
    """Infer a schema from SQL DDL, a JSON sample, or a TypeScript interface."""
    payload = request.get_json(silent=True) or {}
    kind = str(payload.get("kind", "")).lower().strip()
    source = payload.get("source", "")
    if not isinstance(source, str) or not source.strip():
        return jsonify({"error": "Provide source text to infer from"}), 400
    if len(source) > MAX_INFER_SOURCE:
        return jsonify({"error": f"Source exceeds {MAX_INFER_SOURCE} characters"}), 400

    handler = INFER_HANDLERS.get(kind)
    if not handler:
        return jsonify({"error": f"Unknown kind: {kind}. Use sql, json, or typescript."}), 400

    try:
        fields = handler(source)
    except SchemaError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Unexpected error inferring schema")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"fields": fields}), 200


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="127.0.0.1", port=int(os.getenv("PORT", "5000")))
