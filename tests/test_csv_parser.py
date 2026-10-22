"""
Unit tests for CSV parsing service.
"""

import pytest
from services.csv_parser import parse_csv, detect_delimiter, detect_encoding


def test_parse_csv_basic_with_header():
    content = "name,age,city\nAlice,30,New York\nBob,25,San Francisco"
    data = parse_csv(content, delimiter=',', has_header=True)
    assert len(data) == 2
    assert data[0] == {"name": "Alice", "age": "30", "city": "New York"}
    assert data[1] == {"name": "Bob", "age": "25", "city": "San Francisco"}


def test_parse_csv_without_header():
    content = "Alice,30,New York\nBob,25,San Francisco"
    data = parse_csv(content, delimiter=',', has_header=False)
    assert len(data) == 2
    assert data[0] == ["Alice", "30", "New York"]
    assert data[1] == ["Bob", "25", "San Francisco"]


def test_detect_delimiter_comma():
    content = "col1,col2,col3\nval1,val2,val3"
    assert detect_delimiter(content) == ','


def test_detect_delimiter_semicolon():
    content = "col1;col2;col3\nval1;val2;val3"
    assert detect_delimiter(content) == ';'


def test_detect_delimiter_tab():
    content = "col1\tcol2\tcol3\nval1\tval2\tval3"
    assert detect_delimiter(content) == '\t'


def test_detect_delimiter_pipe():
    content = "col1|col2|col3\nval1|val2|val3"
    assert detect_delimiter(content) == '|'


def test_detect_encoding():
    raw_utf8 = "hello,world\n1,2".encode('utf-8')
    assert detect_encoding(raw_utf8).lower() in ('utf-8', 'ascii')


def test_quoted_fields_with_commas():
    content = 'id,quote\n1,"Hello, world!"\n2,"Comma, separated, value"'
    data = parse_csv(content, delimiter=',', has_header=True)
    assert len(data) == 2
    assert data[0]['quote'] == "Hello, world!"
    assert data[1]['quote'] == "Comma, separated, value"


def test_empty_rows_handling():
    content = "id,name\n1,Alice\n\n2,Bob\n   \n"
    data = parse_csv(content, delimiter=',', has_header=True)
    assert len(data) == 2
    assert data[1]['name'] == "Bob"


def test_bom_character_handling():
    content = "\ufeffid,name\n1,Alice"
    data = parse_csv(content, delimiter=',', has_header=True)
    assert len(data) == 1
    assert "id" in data[0]
