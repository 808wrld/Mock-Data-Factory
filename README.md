# Mock Data Factory

> Schema-driven mock data generator. Build a schema in the browser, export to CSV · JSON · XML · SQL · Excel.

[![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-000?logo=flask)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/tests-32%20passing-1F6A3E)](./tests)
[![License](https://img.shields.io/badge/license-MIT-D94F1E)](#license)

```
   ┌─────────────────────────────────────────────┐
   │  SCHEMA                            FIELDS   │
   │  ─────────────────────────────────────────  │
   │  ::   id            ROW NUMBER          ×   │
   │  ::   first_name    FIRST NAME          ×   │
   │  ::   email         EMAIL ADDRESS  null:5%  │
   │  + add field                                │
   │  ─────────────────────────────────────────  │
   │  ROWS  [ 1000 ]    FORMAT  [ CSV ▾ ]        │
   │                            [PREVIEW][GEN]   │
   └─────────────────────────────────────────────┘
```

---

## Why

You need 10,000 rows of realistic-looking test data and you need them now. Open the page, pick fields, pick a format, download. No signup, no rate limits, no telemetry — runs on your own machine.

## What's in the box

- **15 data types**: row numbers, names, emails, phone, IP, city, country, dates, numbers, decimals, gender, custom lists.
- **5 export formats**: CSV, JSON, XML, SQL (`CREATE TABLE` + `INSERT`), Excel (`.xlsx`).
- **Per-field null modifier**: inject any percentage of nulls into any column.
- **Drag-and-drop reordering**, live preview, light/dark theme.
- **DoS guardrails**: requests above `MOCK_DATA_MAX_ROWS` (default 100k) are rejected before allocation.

## Quick start

```bash
git clone https://github.com/808wrld/Mock-Data-Factory.git
cd Mock-Data-Factory

python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py
```

Open <http://127.0.0.1:5000>.

### Configuration

| Variable             | Default  | Purpose                                              |
| -------------------- | -------- | ---------------------------------------------------- |
| `FLASK_DEBUG`        | `0`      | Set to `1` to enable Flask debug mode (dev only).    |
| `PORT`               | `5000`   | Port for the development server.                     |
| `MOCK_DATA_MAX_ROWS` | `100000` | Hard cap on rows per request (DoS guard).            |

## API

Two endpoints, both accept the same JSON schema.

### `POST /preview`

Returns a sample (≤ 100 rows). For CSV/Excel returns `{data, field_order}` JSON; for JSON/XML/SQL returns the formatted text directly.

```bash
curl -s http://127.0.0.1:5000/preview \
  -H 'Content-Type: application/json' \
  -d '{
    "fields": [
      {"name": "id",   "type": "Row Number"},
      {"name": "name", "type": "Full Name"},
      {"name": "email","type": "Email Address", "blank_percentage": 10}
    ],
    "num_rows": 5,
    "format": "JSON"
  }'
```

### `POST /generate`

Returns a downloadable file (`Content-Disposition: attachment`).

```bash
curl -OJ http://127.0.0.1:5000/generate \
  -H 'Content-Type: application/json' \
  -d '{"fields":[{"name":"id","type":"Row Number"}],"num_rows":1000,"format":"CSV"}'
```

### Schema reference

```jsonc
{
  "fields": [
    {"name": "<column_name>", "type": "<data_type>",
     "values": ["a","b"],          // required when type == "Custom List"
     "blank_percentage": 0          // optional, 0-100, nulls % of values
    }
  ],
  "num_rows": 100,                  // 1 .. MOCK_DATA_MAX_ROWS
  "format": "CSV" | "JSON" | "XML" | "SQL" | "EXCEL"
}
```

## Project layout

```
.
├── app.py                  Flask app · generators · formatters · validation
├── templates/index.html    Single-page UI shell (Jinja-rendered)
├── static/
│   ├── css/main.css        Blueprint-aesthetic theme + layout
│   └── js/app.js           Schema editor · preview · download flow
├── tests/test_app.py       pytest suite — 32 tests
├── requirements.txt        Runtime dependencies
├── pyproject.toml          pytest + ruff config
└── README.md
```

## Development

```bash
pip install pytest ruff
pytest                   # 32 tests in ~1s
ruff check .             # lint
```

## Production deployment

The app is a standard Flask WSGI application — host anywhere Python runs.

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:$PORT app:app
```

Recommended hosts: **Render**, **Fly.io**, **Railway**, **Heroku**, or any VPS. Serverless platforms (Netlify Functions, Vercel Functions) are not a great fit — Faker has a cold-start cost and exported files can exceed function size/time limits.

## Design

The UI is intentionally not a Bootstrap default. It uses an industrial-blueprint aesthetic:

- **Typography**: `Instrument Serif` italic for the display, `Geist` for body, `Geist Mono` for labels and field names.
- **Palette**: warm paper background, deep ink, single safety-orange accent for the primary CTA.
- **Geometry**: sharp 90° corners, hairline rules, blueprint grid background.

To remix the theme, edit the CSS variables at the top of `static/css/main.css`.

## License

MIT.
