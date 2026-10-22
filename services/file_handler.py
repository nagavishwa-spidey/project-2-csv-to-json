"""
File handling service for Cloud CSV to JSON Converter.

Manages file uploads, validation, and downloadable JSON file generation.
"""

import io
import json
import os
import uuid

from flask import Response, send_file

from config import Config
from services.csv_parser import detect_encoding


def _get_extension(filename):
    """
    Extract the file extension from a filename.

    Args:
        filename (str): The filename to extract extension from.

    Returns:
        str: Lowercase file extension without the dot, or empty string.
    """
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def handle_upload(file):
    """
    Handle an uploaded file: validate type and size, read content, return parsed string.

    Args:
        file: A Flask FileStorage object from the request.

    Returns:
        dict: A dictionary with:
            - 'content' (str): Decoded file content.
            - 'encoding' (str): Detected encoding.
            - 'filename' (str): Original filename.

    Raises:
        ValueError: If the file is invalid (wrong extension, too large, empty).
    """
    if file is None or file.filename == '':
        raise ValueError("No file provided.")

    filename = file.filename

    # Validate extension
    ext = _get_extension(filename)
    if ext not in Config.ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type '.{ext}'. "
            f"Allowed types: {', '.join('.' + e for e in sorted(Config.ALLOWED_EXTENSIONS))}"
        )

    # Read raw bytes
    raw_bytes = file.read()

    # Validate size
    if len(raw_bytes) > Config.MAX_FILE_SIZE:
        max_mb = Config.MAX_FILE_SIZE / (1024 * 1024)
        raise ValueError(f"File too large. Maximum size is {max_mb:.1f}MB.")

    # Validate non-empty
    if len(raw_bytes) == 0:
        raise ValueError("Uploaded file is empty.")

    # Detect encoding and decode
    encoding = detect_encoding(raw_bytes)
    try:
        content = raw_bytes.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        # Fallback to utf-8 with error replacement
        content = raw_bytes.decode('utf-8', errors='replace')
        encoding = 'utf-8'

    return {
        'content': content,
        'encoding': encoding,
        'filename': filename
    }


def generate_download(json_data, filename=None):
    """
    Generate a downloadable JSON file response.

    Args:
        json_data (str): JSON string to include in the file.
        filename (str, optional): Output filename. Defaults to 'converted_<uuid>.json'.

    Returns:
        flask.Response: A Flask response object with the JSON file for download.
    """
    if filename is None:
        filename = f"converted_{uuid.uuid4().hex[:8]}.json"

    # Ensure .json extension
    if not filename.endswith('.json'):
        # Replace existing extension with .json
        base = filename.rsplit('.', 1)[0] if '.' in filename else filename
        filename = f"{base}.json"

    # Create an in-memory file
    buffer = io.BytesIO()
    buffer.write(json_data.encode('utf-8'))
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )
