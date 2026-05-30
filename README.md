# Mock Data Factory

A concise and efficient mock data generation tool that produces test data in CSV, JSON, XML, SQL, and Excel formats.

## Features

- 15 built-in data types: names, emails, addresses, dates, IP, phone, custom lists, etc.
- Per-field `Null %` modifier to inject nulls into any column
- Five output formats: CSV, JSON, XML, SQL (CREATE TABLE + INSERT), Excel (`.xlsx`)
- Drag-and-drop field reordering
- Live preview before download
- Light/dark theme toggle
- DoS-protected: requests above `MAX_ROWS` (default 100k) are rejected

## Tech Stack

- **Backend**: Python 3.9+, Flask, Faker, openpyxl
- **Frontend**: Bootstrap 5.3, SortableJS, vanilla JS

## Quick Start

```bash
git clone https://github.com/808wrld/Mock-Data-Factory.git
cd Mock-Data-Factory

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

### Environment variables

| Variable             | Default  | Purpose                                    |
| -------------------- | -------- | ------------------------------------------ |
| `FLASK_DEBUG`        | `0`      | Set to `1` to enable Flask debug mode.     |
| `PORT`               | `5000`   | Port for the development server.           |
| `MOCK_DATA_MAX_ROWS` | `100000` | Hard cap on rows per request (DoS guard).  |

## Usage

1. Add fields with the **ADD ANOTHER FIELD** button.
2. For each field set a name and a data type.
3. (Optional) Configure `Null %` to randomly null out values, or add a Custom List of comma-separated values.
4. Set row count and output format.
5. **PREVIEW** to inspect a sample, or **GENERATE DATA** to download the full dataset.

## Tests

```bash
pip install pytest
pytest
```

Tests cover the generator, formatters (CSV/JSON/XML/SQL/Excel), schema validation, and HTTP endpoints.

## Project Structure

```
.
├── app.py                  # Flask app, generators, formatters
├── templates/index.html    # Single-page UI shell
├── static/
│   ├── css/main.css        # Theme variables + layout
│   └── js/app.js           # Schema editor + preview/download flow
├── tests/test_app.py       # pytest suite
├── requirements.txt
└── pyproject.toml          # pytest + ruff config
```

## Deployment

The app is a standard Flask WSGI app — host it anywhere Python runs (Render, Fly.io, Railway, Heroku, a VPS, etc.). For production:

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:$PORT app:app
```

Serverless platforms like Netlify Functions are not a great fit for this app: Faker has cold-start cost and the response sizes (potentially MBs of CSV/Excel) can exceed function size limits.

## License

MIT
