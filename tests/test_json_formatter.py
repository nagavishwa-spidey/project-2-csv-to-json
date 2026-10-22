"""
Unit tests for JSON formatting service.
"""

import json
import pytest
from services.json_formatter import (
    to_array_of_objects,
    to_array_of_arrays,
    to_nested_json,
    format_output
)


def test_to_array_of_objects():
    data = [{"id": "1", "name": "Alice"}]
    res = to_array_of_objects(data)
    assert res == data


def test_to_array_of_arrays():
    data = [{"name": "Alice", "age": "30"}]
    res = to_array_of_arrays(data, headers=["name", "age"])
    assert res == [["name", "age"], ["Alice", "30"]]


def test_to_nested_json():
    data = [{"id": "user1", "name": "Alice"}, {"id": "user2", "name": "Bob"}]
    res = to_nested_json(data, key_column="id")
    assert "user1" in res
    assert res["user1"]["name"] == "Alice"
    assert "user2" in res


def test_to_nested_json_missing_key():
    data = [{"id": "user1", "name": "Alice"}]
    with pytest.raises(ValueError):
        to_nested_json(data, key_column="invalid_col")


def test_format_output_pretty_and_compact():
    data = [{"id": "1"}]
    pretty = format_output(data, format_type='array_of_objects', pretty_print=True)
    compact = format_output(data, format_type='array_of_objects', pretty_print=False)

    assert "\n" in pretty
    assert "\n" not in compact
    assert json.loads(pretty) == json.loads(compact)


def test_format_output_empty():
    res = format_output([], format_type='array_of_objects')
    assert json.loads(res) == []
