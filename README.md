# Mock Data Factory

> Schema-driven mock data generator with field templates and schema inference. CSV · JSON · XML · SQL · Excel.

[![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-000?logo=flask)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/tests-72%20passing-1F6A3E)](./tests)
[![i18n](https://img.shields.io/badge/i18n-EN%20·%20中-6F4A78)](#bilingual-ui)
[![License](https://img.shields.io/badge/license-MIT-D94F1E)](#license)

```
   ┌─────────────────────────────────────────────────────────┐
   │  SCHEMA              [✨ INFER] [↑] [↓] [🔗]           │
   │  ──────────────────────────────────────────────────     │
   │  ::  id           ROW NUMBER                       ×    │
   │  ::  first_name   FIRST NAME                       ×    │
   │  ::  email        TEMPLATE   {{first_name|lower}}…  ×   │
   │  + add another field                                    │
   │  ──────────────────────────────────────────────────     │
   │  ROWS  [ 1000 ]    FORMAT  [ CSV ▾ ]   [PREVIEW] [GEN] │
   └─────────────────────────────────────────────────────────┘
```

---

## Highlights

- **Schema inference** — paste a SQL `CREATE TABLE`, JSON sample, or TypeScript `interface` and we'll guess sensible field types.
- **Field templates** — compose values from other fields with filters: `{{first_name|lower}}.{{last_name|lower}}@example.com`.
- **Schema persistence** — auto-saves to `localStorage`, exports as JSON, and shares via copyable URL hash.
- **Bilingual UI** — EN / 中 toggle in the top-right corner; auto-picks Chinese for `zh-*` browser locales.
- **15 data types**, **5 export formats**, per-field null modifier, drag-and-drop reordering, light/dark theme.
- **Safety caps**: `MOCK_DATA_MAX_ROWS` (default 100k) rows per request, 200 fields per schema, 256 KB request body, 32 KB inference source — anything over the limit is rejected with a clean 400/413.

## Quick start

```bash
git clone https://github.com/808wrld/Mock-Data-Factory.git
cd Mock-Data-Factory

python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py
```

Open <http://127.0.0.1:5000>. (Use `PORT=5050` if macOS's AirPlay is hogging 5000.)

## Configuration

| Variable             | Default  | Purpose                                              |
| -------------------- | -------- | ---------------------------------------------------- |
| `FLASK_DEBUG`        | `0`      | Set to `1` to enable Flask debug mode (dev only).    |
| `PORT`               | `5000`   | Port for the development server.                     |
| `MOCK_DATA_MAX_ROWS` | `100000` | Hard cap on rows per request (DoS guard).            |

## Features in detail

### Field templates

Add a `Template` field, then write a string that references other fields by `{{name}}`:

```
{{first_name|lower}}.{{last_name|lower}}@example.com
```

Filters chain with `|`:

| Filter    | Effect                            | Example                          |
| --------- | --------------------------------- | -------------------------------- |
| `lower`   | lower-case                        | `Alice` → `alice`                |
| `upper`   | upper-case                        | `alice` → `ALICE`                |
| `title`   | Title Case                        | `alice doe` → `Alice Doe`        |
| `slug`    | URL-safe lower-case               | `Hello World!` → `hello-world`   |
| `nospace` | strip spaces                      | `Hello World` → `HelloWorld`     |
| `initial` | first letter, upper-case          | `alice` → `A`                    |
| `digits`  | digits only                       | `(415) 555-1212` → `4155551212`  |
| `trim`    | strip leading/trailing whitespace |                                  |

Template fields are resolved in a second pass after all other fields, so they can reference any field regardless of order.

### Schema inference

Click **✨ Infer** to paste a sample and have the schema generated for you. Three sources are recognized:

**SQL DDL**
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  first_name VARCHAR(100),
  email VARCHAR(255),
  balance DECIMAL(10, 2),
  active BOOLEAN,
  created_at TIMESTAMP
);
```

**JSON sample**
```json
{"id": 1, "first_name": "Alice", "email": "alice@example.com", "born": "1990-01-01"}
```
(Arrays are accepted too — the first element is used as the sample.)

**TypeScript interface**
```ts
interface User {
  id: number;
  firstName: string;
  email: string;
  active: boolean;
  createdAt: Date;
}
```

Column names are matched against heuristics (e.g. `*email*` → Email Address, `*_at` / `*date*` → Date, `*phone*` → Phone Number). Unknown columns fall back to the SQL/TS type.

### Schema persistence

- Every change auto-saves to `localStorage` (debounced).
- **↓ Export** downloads the schema as `schema_YYYY-MM-DD.json`.
- **↑ Import** loads any previously exported file.
- **🔗 Share** copies a self-contained URL like `…/#s=eyJmaWVsZH…` — open it in any browser to restore the schema.

### Bilingual UI

The top-right **EN / 中** pill swaps every visible string between English and Simplified Chinese:

- Static markup uses `data-i18n` / `data-i18n-placeholder` / `data-i18n-title` attributes; toggling rewalks the DOM.
- Dynamic strings (toasts, validation errors, preview captions, data-type dropdown labels) go through a `t(key, vars)` helper.
- Data-type `option.value`s stay English so the backend keeps a single canonical name — only the display text changes.
- The brand word *Mock Data Factory* stays English (it's a wordmark). Chinese display text falls back to `Noto Serif SC` / `Noto Sans SC`.
- Initial language: `localStorage` → browser locale (`zh-*` → Chinese) → English. Persisted under `mdf.lang.v1`.

## API

Three endpoints, all accept JSON.

### `POST /preview`

Returns a sample (≤ 100 rows). CSV/Excel return `{data, field_order}`; JSON/XML/SQL return the formatted text directly.

```bash
curl -s http://127.0.0.1:5000/preview \
  -H 'Content-Type: application/json' \
  -d '{"fields":[
        {"name":"first","type":"First Name"},
        {"name":"email","type":"Template",
         "template":"{{first|lower}}@example.com"}
      ],"num_rows":3,"format":"JSON"}'
```

### `POST /generate`

Returns a downloadable file (`Content-Disposition: attachment`).

```bash
curl -OJ http://127.0.0.1:5000/generate \
  -H 'Content-Type: application/json' \
  -d '{"fields":[{"name":"id","type":"Row Number"}],"num_rows":1000,"format":"CSV"}'
```

### `POST /infer-schema`

Infers field list from a SQL DDL, JSON sample, or TypeScript interface.

```bash
curl -s http://127.0.0.1:5000/infer-schema \
  -H 'Content-Type: application/json' \
  -d '{"kind":"sql","source":"CREATE TABLE u (id INT, email TEXT);"}'
```

Response:
```json
{"fields": [
  {"name": "id",    "type": "Row Number"},
  {"name": "email", "type": "Email Address"}
]}
```

### Schema reference

```jsonc
{
  "fields": [
    {"name": "<column_name>", "type": "<data_type>",
     "values": ["a","b"],          // required when type == "Custom List"
     "template": "{{x|lower}}",    // required when type == "Template"
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
├── app.py                  Flask app · generators · formatters · templates · inference
├── templates/index.html    Single-page UI shell (Jinja-rendered)
├── static/
│   ├── css/main.css        Warm editorial theme
│   └── js/app.js           Schema editor · persistence · preview · download
├── tests/test_app.py       pytest suite — 72 tests
├── requirements.txt        Runtime dependencies
├── pyproject.toml          pytest + ruff config
└── README.md
```

## Development

```bash
pip install pytest ruff
pytest                   # 72 tests in <1s
ruff check .             # lint
```

## Production deployment

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:$PORT app:app
```

Recommended hosts: **Render**, **Fly.io**, **Railway**, **Heroku**, or any VPS.

## Design

Warm editorial aesthetic — `Fraunces` italic display + `Hanken Grotesk` body + `JetBrains Mono` code; cream paper background with terracotta accent and gentle radial gold/plum gradients. To remix the theme, edit the CSS variables at the top of `static/css/main.css`.

## License

MIT.
