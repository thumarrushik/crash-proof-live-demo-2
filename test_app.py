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
    """GET /health returns status ok and uptime_seconds."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data


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
