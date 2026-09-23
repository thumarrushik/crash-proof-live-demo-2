"""Tests for the FastAPI app."""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from app import app


def test_health_returns_200():
    """GET /health returns 200 status code."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status():
    """GET /health returns status and started_at fields."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert "started_at" in data


def test_health_started_at_is_valid_iso8601():
    """GET /health started_at field parses as a valid ISO-8601 datetime."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    started_at = data["started_at"]

    # Remove trailing 'Z' and parse as ISO-8601
    iso_str = started_at.rstrip("Z")
    parsed_time = datetime.fromisoformat(iso_str)

    # Verify it's a datetime object
    assert isinstance(parsed_time, datetime)


def test_version_returns_200():
    """GET /version returns 200 status code."""
    client = TestClient(app)
    response = client.get("/version")
    assert response.status_code == 200


def test_version_returns_correct_version():
    """GET /version returns {"version":"3.0.0", "build":"local", "commit":"dev"}."""
    client = TestClient(app)
    response = client.get("/version")
    assert response.json() == {"version": "3.0.0", "build": "local", "commit": "dev"}


def test_ping_returns_200():
    """GET /ping returns 200 status code."""
    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200


def test_ping_returns_pong():
    """GET /ping returns {"ping":"pong"}."""
    client = TestClient(app)
    response = client.get("/ping")
    assert response.json() == {"ping": "pong"}
