"""
CSV parsing service for Cloud CSV to JSON Converter.

Handles CSV content parsing, delimiter detection, and encoding detection.
Supports quoted fields, newlines within fields, empty rows, and BOM characters.
"""

import csv
import io
import re

import chardet


class ParsedCSV(list):
    """
    List subclass containing parsed rows, with headers and row_count attributes,
    and a dict-like .get() method for backwards compatibility.
    """
    def __init__(self, items, headers=None):
        super().__init__(items)
        self.headers = headers
        self.row_count = len(items)

    def get(self, key, default=None):
        if key == 'data':
            return list(self)
        if key == 'headers':
            return self.headers
        if key == 'row_count':
            return self.row_count
        return default


def detect_encoding(raw_bytes):
    """
    Detect the encoding of raw bytes using chardet.
    """
    if not raw_bytes:
        return 'utf-8'

    result = chardet.detect(raw_bytes)
    encoding = result.get('encoding', 'utf-8')

    if encoding is None:
        encoding = 'utf-8'

    encoding_lower = encoding.lower().replace('-', '_')
    encoding_map = {
        'ascii': 'utf-8',
        'utf_8_sig': 'utf-8-sig',
        'utf_8': 'utf-8',
        'iso_8859_1': 'iso-8859-1',
        'windows_1252': 'windows-1252',
    }
    return encoding_map.get(encoding_lower, result.get('encoding', 'utf-8'))


def detect_delimiter(content):
    """
    Auto-detect the delimiter used in CSV content.
    """
    if not content or not content.strip():
        return ','

    content = content.lstrip('\ufeff')
    lines = [line for line in content.split('\n') if line.strip()][:10]

    if not lines:
        return ','

    delimiters = [',', ';', '\t', '|']
    best_delimiter = ','
    best_score = -1

    for delim in delimiters:
        counts = []
        for line in lines:
            try:
                reader = csv.reader(io.StringIO(line), delimiter=delim)
                row = next(reader)
                counts.append(len(row))
            except (csv.Error, StopIteration):
                counts.append(0)

        if not counts:
            continue

        avg_count = sum(counts) / len(counts)
        if avg_count <= 1:
            continue

        consistency = counts.count(counts[0]) / len(counts) if counts else 0
        score = avg_count * consistency

        if score > best_score:
            best_score = score
            best_delimiter = delim

    return best_delimiter


def _strip_bom(content):
    """Remove BOM (Byte Order Mark) characters from content."""
    if content.startswith('\ufeff'):
        content = content[1:]
    if content.startswith('\ufffe') or content.startswith('\ufeff'):
        content = content[1:]
    return content


def parse_csv(content, delimiter=',', has_header=True, encoding='utf-8'):
    """
    Parse CSV content into structured data.
    """
    if not content or not content.strip():
        return ParsedCSV([], headers=None)

    content = _strip_bom(content)
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)

    rows = []
    for row in reader:
        if not row or all(cell.strip() == '' for cell in row):
            continue
        rows.append(row)

    if not rows:
        return ParsedCSV([], headers=None)

    if has_header:
        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]

        data = []
        for row in data_rows:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = row[i].strip()
                else:
                    row_dict[header] = ''
            data.append(row_dict)

        return ParsedCSV(data, headers=headers)
    else:
        data = [[cell.strip() for cell in row] for row in rows]
        return ParsedCSV(data, headers=None)
