"""
Input validation utilities for Cloud CSV to JSON Converter.

Provides validation functions for CSV content, format types, and uploaded files.
"""

from config import Config


def validate_csv_content(content):
    """
    Validate that the provided content is non-empty and has valid CSV structure.

    Args:
        content (str): CSV content string to validate.

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if content is None:
        return False, "Content is required."

    if not isinstance(content, str):
        return False, "Content must be a string."

    stripped = content.strip()
    if not stripped:
        return False, "Content is empty."

    # Check that there's at least one line of actual data
    lines = [line for line in stripped.split('\n') if line.strip()]
    if len(lines) < 1:
        return False, "Content has no data rows."

    return True, None


def validate_format_type(fmt):
    """
    Validate that the format type is one of the supported output formats.

    Args:
        fmt (str): Format type string to validate.

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if fmt is None:
        return False, "Format type is required."

    if not isinstance(fmt, str):
        return False, "Format type must be a string."

    if fmt not in Config.SUPPORTED_FORMATS:
        return False, (
            f"Invalid format type '{fmt}'. "
            f"Supported formats: {', '.join(sorted(Config.SUPPORTED_FORMATS))}"
        )

    return True, None


def validate_file(file):
    """
    Validate an uploaded file for correct extension and size limit.

    Args:
        file: A Flask FileStorage object.

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if file is None:
        return False, "No file provided."

    if not hasattr(file, 'filename') or file.filename == '':
        return False, "No file selected."

    # Check extension
    filename = file.filename
    if '.' not in filename:
        return False, "File must have an extension (.csv, .tsv, or .txt)."

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in Config.ALLOWED_EXTENSIONS:
        return False, (
            f"Invalid file type '.{ext}'. "
            f"Allowed types: {', '.join('.' + e for e in sorted(Config.ALLOWED_EXTENSIONS))}"
        )

    # Check size by reading content length if available
    # Note: actual size check is done in file_handler.handle_upload()
    # after reading the file, since content_length may not always be reliable.

    return True, None
