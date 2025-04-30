from flask import Flask, request, jsonify, send_file, render_template
from faker import Faker
import csv
import json
import io
import random
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import xml.dom.minidom
try:
    import openpyxl
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

app = Flask(__name__)
fake = Faker()

def generate_value(field_type, field_config=None):
    """Generate a single value based on the field type and configuration."""
    if field_type == "Row Number":
        return None  # Will be filled in later
    elif field_type == "First Name":
        return fake.first_name()
    elif field_type == "Last Name":
        return fake.last_name()
    elif field_type == "Full Name":
        return fake.name()
    elif field_type == "Email Address":
        return fake.email()
    elif field_type == "Gender":
        return random.choice(["Male", "Female", "Other"])
    elif field_type == "IP Address v4":
        return fake.ipv4()
    elif field_type == "Phone Number":
        return fake.phone_number()
    elif field_type == "City":
        return fake.city()
    elif field_type == "Country":
        return fake.country()
    elif field_type == "Date":
        start_date = datetime.now() - timedelta(days=365*5)  # 5 years ago
        end_date = datetime.now()
        return fake.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d')
    elif field_type == "Number":
        return random.randint(1, 1000)
    elif field_type == "Decimal":
        return round(random.uniform(0, 1000), 2)
    elif field_type == "Custom List":
        if field_config and "values" in field_config:
            return random.choice(field_config["values"])
        return ""
    elif field_type == "Blank/Null":
        blank_percentage = field_config.get("blank_percentage", 0) if field_config else 0
        return None if random.random() < (blank_percentage / 100) else fake.word()
    return ""

def generate_data(schema, max_rows=None):
    """Generate data based on the schema, with an optional limit on rows."""
    num_rows = min(schema["num_rows"], max_rows) if max_rows else schema["num_rows"]
    data = []
    
    # Extract field names in the exact order they appear in the schema
    field_names = [field["name"] for field in schema["fields"]]
    
    for i in range(num_rows):
        row = {}
        for field in schema["fields"]:
            value = generate_value(field["type"], field)
            if field["type"] == "Row Number":
                value = i + 1
            row[field["name"]] = value
        
        # Create an ordered dictionary to ensure field order matches schema order
        ordered_row = {name: row.get(name) for name in field_names}
        data.append(ordered_row)
    return data

def format_csv(data):
    """Format data as CSV string."""
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return output.getvalue()

def format_json(data):
    """Format data as JSON string."""
    return json.dumps(data, indent=2)

def format_xml(data):
    """Format data as XML string."""
    root = ET.Element("records")
    
    for item in data:
        record = ET.SubElement(root, "record")
        for key, value in item.items():
            field = ET.SubElement(record, key)
            # Handle None values
            if value is not None:
                field.text = str(value)
            else:
                field.text = ""
    
    # Pretty print XML
    xml_string = ET.tostring(root, encoding='utf-8')
    dom = xml.dom.minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Remove the XML declaration line
    if pretty_xml.startswith('<?xml'):
        pretty_xml = '\n'.join(pretty_xml.split('\n')[1:])
        
    return pretty_xml

def format_sql(data, table_name='mock_data'):
    """Format data as SQL INSERT statements."""
    if not data:
        return ""
    
    sql_output = [f"-- SQL Data Export\n-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    
    # Create table statement
    columns = list(data[0].keys())
    sql_output.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")
    column_defs = []
    
    for col in columns:
        # Determine column type based on the first non-null value
        col_type = "TEXT"  # Default type
        for row in data:
            value = row[col]
            if value is not None:
                if isinstance(value, int):
                    col_type = "INTEGER"
                elif isinstance(value, float):
                    col_type = "REAL"
                elif isinstance(value, str) and value.strip() != "":
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                        col_type = "DATE"
                    except ValueError:
                        col_type = "TEXT"
                break
        
        column_defs.append(f"    {col} {col_type}")
    
    sql_output.append(",\n".join(column_defs))
    sql_output.append(");\n")
    
    # Insert statements
    for row in data:
        values = []
        for col in columns:
            value = row[col]
            if value is None:
                values.append("NULL")
            elif isinstance(value, (int, float)):
                values.append(str(value))
            else:
                # Escape single quotes in string values
                values.append(f"'{str(value).replace('\'', '\'\'')}'" if value is not None else "NULL")
        
        sql_output.append(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});")
    
    return "\n".join(sql_output)

def format_excel(data):
    """Format data as Excel file (bytes)."""
    if not EXCEL_AVAILABLE:
        raise Exception("Excel generation requires openpyxl. Please install it with 'pip install openpyxl'")
    
    if not data:
        return None
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mock Data"
    
    # Write headers
    headers = list(data[0].keys())
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.value = header
        cell.font = openpyxl.styles.Font(bold=True)
    
    # Write data
    for row_idx, row_data in enumerate(data, 2):
        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=row_idx, column=col_idx).value = row_data[header]
    
    # Auto-adjust column widths
    for col_idx, header in enumerate(headers, 1):
        column_letter = get_column_letter(col_idx)
        max_length = len(str(header))
        
        for row_idx, row_data in enumerate(data, 2):
            cell_value = row_data[header]
            if cell_value is not None:
                max_length = max(max_length, len(str(cell_value)))
        
        adjusted_width = max_length + 2  # Add some padding
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output.getvalue()

@app.route('/')
def index():
    # Define default schema with 6 predefined fields
    default_schema = [
        {"name": "id", "type": "Row Number"},
        {"name": "first_name", "type": "First Name"},
        {"name": "last_name", "type": "Last Name"},
        {"name": "email", "type": "Email Address"},
        {"name": "gender", "type": "Gender"},
        {"name": "ip_address", "type": "IP Address v4"}
    ]
    return render_template('index.html', default_schema=default_schema)

@app.route('/preview', methods=['POST'])
def preview():
    """Generate a preview of the data in the requested format.
    
    Handles CSV, JSON, XML, SQL formats with a limited number of rows.
    For Excel, returns a message indicating preview is not available.
    """
    try:
        schema = request.json
        if not schema or "fields" not in schema or "num_rows" not in schema or "format" not in schema:
            return jsonify({"error": "Invalid schema format"}), 400
        
        # Limit preview to 20 rows maximum
        max_preview_rows = 20
        format_type = schema["format"].upper()
        
        # Generate limited data
        data = generate_data(schema, max_preview_rows)
        
        # For CSV and Excel, return the raw data as JSON for table rendering
        if format_type in ["CSV", "EXCEL"]:
            # Preserve field order from schema by including it in the response
            field_names = [field["name"] for field in schema["fields"]]
            return jsonify({"data": data, "field_order": field_names}), 200
        
        # For other formats, return formatted text
        if format_type == "JSON":
            return format_json(data), 200, {'Content-Type': 'text/plain'}
        elif format_type == "XML":
            return format_xml(data), 200, {'Content-Type': 'text/plain'}
        elif format_type == "SQL":
            return format_sql(data), 200, {'Content-Type': 'text/plain'}
        else:
            return jsonify({"error": f"Unsupported format: {format_type}"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    """Generate mock data based on the provided schema and format it for download.
    
    Supports CSV, JSON, XML, SQL, and Excel formats.
    """
    try:
        schema = request.json
        if not schema or "fields" not in schema or "num_rows" not in schema or "format" not in schema:
            return jsonify({"error": "Invalid schema format"}), 400

        # If preview mode (legacy support), return JSON data
        if request.args.get('preview') == 'true':
            data = generate_data(schema)
            # Preserve field order from schema
            field_names = [field["name"] for field in schema["fields"]]
            return jsonify({"data": data, "field_order": field_names})

        # Generate the data
        data = generate_data(schema)
        format_type = schema["format"].upper()
        
        # Format data and prepare response based on format
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "CSV":
            output = format_csv(data)
            return send_file(
                io.BytesIO(output.encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'mock_data_{current_time}.csv'
            )
        elif format_type == "JSON":
            output = format_json(data)
            return send_file(
                io.BytesIO(output.encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'mock_data_{current_time}.json'
            )
        elif format_type == "XML":
            output = format_xml(data)
            return send_file(
                io.BytesIO(output.encode('utf-8')),
                mimetype='application/xml',
                as_attachment=True,
                download_name=f'mock_data_{current_time}.xml'
            )
        elif format_type == "SQL":
            output = format_sql(data)
            return send_file(
                io.BytesIO(output.encode('utf-8')),
                mimetype='text/plain',
                as_attachment=True,
                download_name=f'mock_data_{current_time}.sql'
            )
        elif format_type == "EXCEL":
            if not EXCEL_AVAILABLE:
                return jsonify({"error": "Excel generation requires openpyxl. Please install it with 'pip install openpyxl'"}), 500
                
            output = format_excel(data)
            return send_file(
                io.BytesIO(output),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'mock_data_{current_time}.xlsx'
            )
        else:
            return jsonify({"error": f"Unsupported format: {format_type}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 