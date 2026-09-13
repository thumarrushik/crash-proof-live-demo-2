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
    """GET /health returns {"status":"ok"}."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
