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
    """GET /health returns status=ok and version=3.0.0 fields."""
    client = TestClient(app)
    response = client.get("/health")
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "3.0.0"


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


def test_health_includes_checks_passed():
    """GET /health includes checks_passed field."""
    client = TestClient(app)
    response = client.get("/health")
    assert "checks_passed" in response.json()
    assert isinstance(response.json()["checks_passed"], int)


def test_checks_passed_increments_across_calls():
    """checks_passed counter increments across two /health calls."""
    client = TestClient(app)

    # First call
    response1 = client.get("/health")
    count1 = response1.json()["checks_passed"]
    assert count1 >= 1  # Should be at least 1

    # Second call
    response2 = client.get("/health")
    count2 = response2.json()["checks_passed"]
    assert count2 == count1 + 1  # Should increment by exactly 1


def test_health_service_field_present():
    """GET /health includes service field."""
    client = TestClient(app)
    response = client.get("/health")
    assert "service" in response.json()


def test_health_service_field_equals_demo_api():
    """GET /health service field equals "demo-api"."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.json()["service"] == "demo-api"
