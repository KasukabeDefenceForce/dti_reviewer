# tests/test_api_search.py
import pytest
from flask import Flask
import json
from api import api_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def load_expected():
    path = "tests/expected_data/expected_search_response.json"
    with open(path, "r") as f:
        return json.load(f)


def test_missing_query_key(client):
    resp = client.post("/search", json={})
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["message"] == "Missing 'query' parameter"
    assert body["results"] == []


def test_empty_query_string(client):
    resp = client.post("/search", json={"query": "   "})
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["message"] == "Query cannot be empty"
    assert body["results"] == []


def test_query_too_short(client):
    resp = client.post("/search", json={"query": "hi"})
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["message"] == "Query too short. Minimum 3 characters"
    assert body["results"] == []


def test_search_success(client):
    expected = load_expected()
    resp = client.post("/search", json={"query": "supernovae"})
    assert resp.status_code == 200

    actual = resp.get_json()
    assert actual["message"] == expected["message"]
    assert actual["results"] == expected["results"]
