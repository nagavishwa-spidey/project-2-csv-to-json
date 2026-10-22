"""
JSON formatting service for Cloud CSV to JSON Converter.

Provides multiple JSON output formats: array of objects, array of arrays,
and nested JSON. Supports both pretty-print and compact output modes.
"""

import json


def to_array_of_objects(data):
    """
    Convert parsed data to an array of JSON objects.
    """
    if not data:
        return []

    if isinstance(data[0], dict):
        return data

    if isinstance(data[0], (list, tuple)) and len(data) > 1:
        headers = data[0]
        result = []
        for row in data[1:]:
            obj = {}
            for i, header in enumerate(headers):
                obj[header] = row[i] if i < len(row) else ''
            result.append(obj)
        return result

    return data


def to_array_of_arrays(data, headers=None):
    """
    Convert parsed data to an array of arrays format.
    """
    if not data:
        return []

    if isinstance(data[0], dict):
        if headers is None:
            headers = list(data[0].keys())
        result = [headers]
        for row in data:
            result.append([row.get(h, '') for h in headers])
        return result

    if headers:
        return [headers] + list(data)
    return list(data)


def to_nested_json(data, key_column):
    """
    Convert parsed data to a nested JSON object keyed by a specific column.
    """
    if not data:
        return {}

    result = {}
    for i, row in enumerate(data):
        if isinstance(row, dict):
            if key_column not in row:
                raise ValueError(
                    f"Key column '{key_column}' not found in data. "
                    f"Available columns: {', '.join(row.keys())}"
                )
            key = row[key_column]
            # Copy row without the key column for cleaner output
            row_copy = {k: v for k, v in row.items() if k != key_column}
            result[str(key)] = row_copy
        elif isinstance(row, (list, tuple)):
            key = str(row[0]) if len(row) > 0 else str(i)
            result[key] = row[1:] if len(row) > 1 else []

    return result


def format_output(data, format_type='array_of_objects', options=None, **kwargs):
    """
    Dispatch to the appropriate JSON formatter based on format_type.
    """
    opts = {}
    if options and isinstance(options, dict):
        opts.update(options)
    opts.update(kwargs)

    pretty_print = opts.get('pretty_print', True)
    indent = opts.get('indent', 2) if pretty_print else None

    if isinstance(data, dict):
        rows = data.get('data', [])
        headers = data.get('headers', None)
    elif hasattr(data, 'headers'):
        rows = list(data)
        headers = data.headers
    else:
        rows = list(data) if data is not None else []
        headers = None

    if format_type == 'array_of_objects':
        result = to_array_of_objects(rows)
    elif format_type == 'array_of_arrays':
        result = to_array_of_arrays(rows, headers)
    elif format_type == 'nested_json':
        key_column = opts.get('key_column')
        if not key_column:
            if headers and len(headers) > 0:
                key_column = headers[0]
            elif rows and isinstance(rows[0], dict) and len(rows[0]) > 0:
                key_column = list(rows[0].keys())[0]
            else:
                raise ValueError("Nested JSON format requires a 'key_column' option.")
        result = to_nested_json(rows, key_column)
    else:
        raise ValueError(
            f"Unsupported format type: '{format_type}'. "
            f"Supported types: array_of_objects, array_of_arrays, nested_json"
        )

    return json.dumps(result, indent=indent, ensure_ascii=False)
