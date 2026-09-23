"""Tests for the FastAPI app."""
import os
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
    """GET /health returns ok status with all fields including env and service."""
    # Ensure APP_ENV is not set for this test to verify default
    original_env = os.environ.pop("APP_ENV", None)
    try:
        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "3.0.0"
        assert data["env"] == "dev"
        assert data["service"] == "demo-api"
    finally:
        if original_env is not None:
            os.environ["APP_ENV"] = original_env


def test_health_env_field_default_dev():
    """GET /health returns env field with default value 'dev' when APP_ENV not set."""
    original_env = os.environ.pop("APP_ENV", None)
    try:
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert "env" in response.json()
        assert response.json()["env"] == "dev"
    finally:
        if original_env is not None:
            os.environ["APP_ENV"] = original_env


def test_health_env_field_custom_value():
    """GET /health returns env field with custom value from APP_ENV."""
    original_env = os.environ.get("APP_ENV")
    os.environ["APP_ENV"] = "production"
    try:
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert "env" in response.json()
        assert response.json()["env"] == "production"
    finally:
        if original_env is not None:
            os.environ["APP_ENV"] = original_env
        else:
            os.environ.pop("APP_ENV", None)


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


def test_health_returns_version_field():
    """GET /health returns status=ok and version=3.0.0 fields."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "3.0.0"
    assert data["service"] == "demo-api"


def test_health_includes_uptime_seconds():
    """GET /health includes uptime_seconds field."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    assert "uptime_seconds" in data


def test_health_uptime_seconds_is_non_negative():
    """GET /health uptime_seconds is a non-negative float."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0


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
