"""
Integration tests for Flask CSV to JSON API endpoints.
"""

import io
import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"Cloud CSV to JSON" in res.data


def test_health_check(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'


def test_api_convert_json_payload(client):
    payload = {
        "text": "id,name\n1,Alice\n2,Bob",
        "format": "array_of_objects",
        "hasHeader": True,
        "prettyPrint": False
    }
    res = client.post('/api/convert', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['rowCount'] == 2
    assert len(data['result']) == 2
    assert data['result'][0]['name'] == 'Alice'


def test_api_convert_file_upload(client):
    data = {
        'file': (io.BytesIO(b"id,val\n10,foo\n20,bar"), 'sample.csv'),
        'format': 'array_of_arrays'
    }
    res = client.post('/api/convert', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    res_data = res.get_json()
    assert res_data['success'] is True
    assert res_data['rowCount'] == 2


def test_api_detect_delimiter(client):
    payload = {"text": "name;age;role\nAlice;28;Dev"}
    res = client.post('/api/detect', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['delimiter'] == ';'


def test_api_preview(client):
    payload = {
        "text": "id,score\n1,95\n2,88\n3,76",
        "hasHeader": True
    }
    res = client.post('/api/preview', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['totalRows'] == 3
    assert len(data['data']) == 3


def test_api_convert_invalid_input(client):
    res = client.post('/api/convert', json={"text": ""})
    assert res.status_code == 400
    assert "error" in res.get_json()
