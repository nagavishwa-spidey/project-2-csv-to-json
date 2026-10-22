"""
Unit tests for file handler service.
"""

import io
import pytest
from werkzeug.datastructures import FileStorage
from services.file_handler import handle_upload, generate_download


def test_handle_upload_valid_csv():
    file = FileStorage(
        stream=io.BytesIO(b"id,name\n1,Alice"),
        filename="test.csv",
        content_type="text/csv"
    )
    result = handle_upload(file)
    assert result['filename'] == 'test.csv'
    assert "1,Alice" in result['content']


def test_handle_upload_invalid_extension():
    file = FileStorage(
        stream=io.BytesIO(b"binary"),
        filename="test.exe",
        content_type="application/octet-stream"
    )
    with pytest.raises(ValueError, match="Invalid file type"):
        handle_upload(file)


def test_handle_upload_empty():
    file = FileStorage(
        stream=io.BytesIO(b""),
        filename="empty.csv",
        content_type="text/csv"
    )
    with pytest.raises(ValueError, match="empty"):
        handle_upload(file)
