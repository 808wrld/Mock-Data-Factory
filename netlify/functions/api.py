from flask import Flask, request, jsonify, send_file, render_template
from faker import Faker
import csv
import json
import io
import random
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import from the parent directory
from app import generate_data, format_csv, format_json, format_xml, format_sql

# Initialize Flask app
app = Flask(__name__)
fake = Faker()

# Set up the serverless function handler
def handler(event, context):
    # Get the path and HTTP method from the event
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')
    
    # Create a Flask request context
    with app.test_request_context(
        path=path,
        method=http_method,
        headers=event.get('headers', {}),
        data=event.get('body', ''),
        query_string=event.get('queryStringParameters', {})
    ):
        # Process the request with Flask
        response = app.dispatch_request()
        
        # Convert Flask response to Netlify function response format
        status_code = response.status_code
        headers = dict(response.headers)
        body = response.get_data(as_text=True)
        
        return {
            'statusCode': status_code,
            'headers': headers,
            'body': body
        }

# Define routes
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
    """Generate a preview of the data in the requested format."""
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
            return jsonify(data), 200
        
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
    """Generate mock data based on the provided schema and format it for download."""
    try:
        schema = request.json
        if not schema or "fields" not in schema or "num_rows" not in schema or "format" not in schema:
            return jsonify({"error": "Invalid schema format"}), 400

        # If preview mode (legacy support), return JSON data
        if request.args.get('preview') == 'true':
            data = generate_data(schema)
            return jsonify(data)

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
            try:
                import openpyxl
                from openpyxl.utils import get_column_letter
                from app import format_excel
                
                output = format_excel(data)
                return send_file(
                    io.BytesIO(output),
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=f'mock_data_{current_time}.xlsx'
                )
            except ImportError:
                return jsonify({"error": "Excel generation requires openpyxl. Please install it with 'pip install openpyxl'"}), 500
        else:
            return jsonify({"error": f"Unsupported format: {format_type}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
