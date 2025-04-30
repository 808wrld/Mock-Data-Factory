# Mock Data Factory

A concise and efficient mock data generation tool that quickly produces test data in various formats, helping developers and testers improve their productivity.

## Project Background

Mock Data Factory is a web-based application designed to address the need for large volumes of test data during development and testing processes. It allows users to define data structures, select data types, and generate customizable test datasets with a single click.

## Technology Stack

- **Backend**: Python, Flask
- **Data Generation**: Faker library
- **Frontend**: HTML/CSS/JavaScript, Bootstrap 5
- **Data Formats**: CSV, JSON, XML, SQL, Excel

## Quick Start

### Installation & Running

```bash
# Clone repository (if applicable)
git clone <repository-url>
cd Mock-Data-Factory

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will start at http://127.0.0.1:5000.

### How to Use

1. **Add Fields**: Click the "ADD ANOTHER FIELD" button to add data fields
2. **Configure Fields**:
   - Enter field name
   - Select data type (name, email, date, etc.)
   - For custom lists, enter comma-separated values
   - For blank/null types, set blank percentage
3. **Set Parameters**: 
   - Specify number of rows to generate
   - Select output format (CSV, JSON, XML, SQL, Excel)
4. **Generate & Preview**: 
   - Click "PREVIEW" button to preview data
   - Click "GENERATE DATA" button to download the complete dataset

### Key Features

- Multiple data types: row numbers, names, emails, addresses, dates, etc.
- Various output formats: CSV, JSON, XML, SQL, Excel
- Drag-and-drop field reordering
- Data preview functionality
- Custom list values
- Blank/null percentage settings
- Light/dark theme toggle