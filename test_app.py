"""Tests for the FastAPI app."""
import pytest
from fastapi.testclient import TestClient
from app import app


def test_health_returns_200():
    """GET /health returns 200 status code."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_status():
    """GET /health returns {"status":"ok", "version":"3.0.0"}."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.json() == {"status": "ok", "version": "3.0.0"}


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


def test_health_version_equals_version_endpoint():
    """GET /health.version equals GET /version.version."""
    client = TestClient(app)
    health_response = client.get("/health")
    version_response = client.get("/version")

    assert health_response.status_code == 200
    assert version_response.status_code == 200
    assert health_response.json()["version"] == version_response.json()["version"]


def test_health_reports_running_python():
    import sys
    r = client.get("/health")
    expected = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert r.json()["python"] == expected
