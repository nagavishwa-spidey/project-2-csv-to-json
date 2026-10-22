"""
Flask Application for Cloud CSV to JSON Converter.

Exposes RESTful endpoints for CSV parsing, detection, preview, conversion,
and download, along with serving the single-page application dashboard.
"""

import io
import json
import uuid
from flask import Flask, render_template, request, jsonify, Response, send_file
from flask_cors import CORS

from config import Config
from services.csv_parser import parse_csv, detect_delimiter, detect_encoding
from services.json_formatter import format_output
from services.file_handler import handle_upload, generate_download
from utils.validators import validate_csv_content, validate_format_type, validate_file

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# In-memory storage for generated downloads (session-scoped)
DOWNLOAD_CACHE = {}


@app.route('/')
def index():
    """Render the main application interface."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for cloud monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "cloud-csv-to-json-converter",
        "version": "1.0.0"
    }), 200


@app.route('/api/detect', methods=['POST'])
def detect():
    """
    Auto-detect delimiter and encoding from uploaded file or raw CSV text.
    """
    content = ""
    encoding = "utf-8"

    if 'file' in request.files:
        uploaded_file = request.files['file']
        valid, err = validate_file(uploaded_file)
        if not valid:
            return jsonify({"error": err}), 400
        try:
            upload_data = handle_upload(uploaded_file)
            content = upload_data['content']
            encoding = upload_data['encoding']
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    elif request.is_json:
        data = request.get_json() or {}
        content = data.get('text', '')
    else:
        content = request.form.get('text', '')

    valid, err = validate_csv_content(content)
    if not valid:
        return jsonify({"error": err}), 400

    delimiter = detect_delimiter(content)
    return jsonify({
        "delimiter": delimiter,
        "encoding": encoding,
        "sampleLines": len([line for line in content.split('\n') if line.strip()][:5])
    }), 200


@app.route('/api/preview', methods=['POST'])
def preview():
    """
    Parse and return the first 10 rows of CSV as JSON for client-side preview.
    """
    content = ""
    delimiter = request.form.get('delimiter')
    has_header = request.form.get('hasHeader', 'true').lower() in ('true', '1', 'yes')

    if 'file' in request.files:
        uploaded_file = request.files['file']
        valid, err = validate_file(uploaded_file)
        if not valid:
            return jsonify({"error": err}), 400
        try:
            upload_data = handle_upload(uploaded_file)
            content = upload_data['content']
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    elif request.is_json:
        data = request.get_json() or {}
        content = data.get('text', '')
        delimiter = data.get('delimiter', delimiter)
        if 'hasHeader' in data:
            has_header = bool(data.get('hasHeader'))
    else:
        content = request.form.get('text', '')

    valid, err = validate_csv_content(content)
    if not valid:
        return jsonify({"error": err}), 400

    if not delimiter or delimiter == 'auto':
        delimiter = detect_delimiter(content)

    try:
        parsed_data = parse_csv(content, delimiter=delimiter, has_header=has_header)
        preview_data = parsed_data[:10]
        return jsonify({
            "totalRows": len(parsed_data),
            "previewRows": len(preview_data),
            "delimiter": delimiter,
            "data": preview_data
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to preview CSV: {str(e)}"}), 400


@app.route('/api/convert', methods=['POST'])
def convert():
    """
    Convert CSV content or file into requested JSON format.
    """
    content = ""
    delimiter = None
    has_header = True
    format_type = "array_of_objects"
    pretty_print = True
    key_column = None

    if 'file' in request.files:
        uploaded_file = request.files['file']
        valid, err = validate_file(uploaded_file)
        if not valid:
            return jsonify({"error": err}), 400
        try:
            upload_data = handle_upload(uploaded_file)
            content = upload_data['content']
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        delimiter = request.form.get('delimiter')
        has_header = request.form.get('hasHeader', 'true').lower() in ('true', '1', 'yes')
        format_type = request.form.get('format', 'array_of_objects')
        pretty_print = request.form.get('prettyPrint', 'true').lower() in ('true', '1', 'yes')
        key_column = request.form.get('keyColumn')
    elif request.is_json:
        data = request.get_json() or {}
        content = data.get('text', '')
        delimiter = data.get('delimiter')
        has_header = data.get('hasHeader', True)
        format_type = data.get('format', 'array_of_objects')
        pretty_print = data.get('prettyPrint', True)
        key_column = data.get('keyColumn')
    else:
        content = request.form.get('text', '')
        delimiter = request.form.get('delimiter')
        has_header = request.form.get('hasHeader', 'true').lower() in ('true', '1', 'yes')
        format_type = request.form.get('format', 'array_of_objects')
        pretty_print = request.form.get('prettyPrint', 'true').lower() in ('true', '1', 'yes')
        key_column = request.form.get('keyColumn')

    valid, err = validate_csv_content(content)
    if not valid:
        return jsonify({"error": err}), 400

    valid_fmt, err_fmt = validate_format_type(format_type)
    if not valid_fmt:
        return jsonify({"error": err_fmt}), 400

    if not delimiter or delimiter == 'auto':
        delimiter = detect_delimiter(content)

    try:
        parsed_data = parse_csv(content, delimiter=delimiter, has_header=has_header)
        json_output = format_output(
            parsed_data,
            format_type=format_type,
            pretty_print=pretty_print,
            key_column=key_column
        )

        job_id = str(uuid.uuid4())
        DOWNLOAD_CACHE[job_id] = json_output

        return jsonify({
            "success": True,
            "jobId": job_id,
            "format": format_type,
            "rowCount": len(parsed_data),
            "result": json.loads(json_output) if not pretty_print else json_output,
            "jsonString": json_output
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Conversion error: {str(e)}"}), 500


@app.route('/api/download/<job_id>', methods=['GET'])
def download(job_id):
    """Serve converted JSON file for download using generated job_id."""
    if job_id not in DOWNLOAD_CACHE:
        return jsonify({"error": "Download file not found or expired"}), 404

    json_str = DOWNLOAD_CACHE[job_id]
    return generate_download(json_str, filename=f"converted_{job_id[:8]}.json")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
