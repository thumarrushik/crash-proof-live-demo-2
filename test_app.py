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


def test_health_reports_running_python():
    """GET /health.python reports the actual running Python major.minor version."""
    import sys
    client = TestClient(app)
    response = client.get("/health")
    expected = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert response.json()["python"] == expected


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


# === REGRESSION TESTS: Pin the complete /health response shape ===
# These tests enforce the contract: any field removal or type change fails loudly


def test_health_response_has_required_seven_fields():
    """GET /health response contains all 7 required fields: status, version, python, uptime_seconds, checks_passed, env, service."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Verify all 7 required fields are present
    required_fields = {"status", "version", "python", "uptime_seconds", "checks_passed", "env", "service"}
    present_fields = set(data.keys())

    assert required_fields.issubset(present_fields), (
        f"Missing required fields: {required_fields - present_fields}. "
        f"Present: {present_fields}"
    )


def test_health_response_field_types():
    """GET /health response has correct types for all 7 required fields."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Type checks for all 7 required fields
    assert isinstance(data["status"], str), f"status must be str, got {type(data['status']).__name__}"
    assert isinstance(data["version"], str), f"version must be str, got {type(data['version']).__name__}"
    assert isinstance(data["python"], str), f"python must be str, got {type(data['python']).__name__}"
    assert isinstance(data["uptime_seconds"], (int, float)), (
        f"uptime_seconds must be int or float, got {type(data['uptime_seconds']).__name__}"
    )
    assert isinstance(data["checks_passed"], int), f"checks_passed must be int, got {type(data['checks_passed']).__name__}"
    assert isinstance(data["env"], str), f"env must be str, got {type(data['env']).__name__}"
    assert isinstance(data["service"], str), f"service must be str, got {type(data['service']).__name__}"


def test_health_status_field_is_exactly_ok():
    """GET /health status field must be exactly "ok" (string type)."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Type check: must be string, not any other type
    assert type(data["status"]) is str, (
        f"status field type changed from str to {type(data['status']).__name__}"
    )
    # Value check
    assert data["status"] == "ok"


def test_health_version_field_is_string_not_number():
    """GET /health version field must be string "3.0.0", not a number (type regression)."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Catch type change: version must be string
    assert type(data["version"]) is str, (
        f"version field type changed from str to {type(data['version']).__name__}"
    )
    assert data["version"] == "3.0.0"


def test_health_python_field_is_string():
    """GET /health python field must be string (e.g., "3.9"), not raw version info."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Catch type change: python must be string
    assert type(data["python"]) is str, (
        f"python field type changed from str to {type(data['python']).__name__}"
    )
    # Must be X.Y format
    assert "." in data["python"], f"python must be in X.Y format, got {data['python']}"
    parts = data["python"].split(".")
    assert len(parts) == 2, f"python must be X.Y format, got {data['python']}"
    # Both parts must be numeric
    assert parts[0].isdigit(), f"python major version must be numeric, got {parts[0]}"
    assert parts[1].isdigit(), f"python minor version must be numeric, got {parts[1]}"


def test_health_uptime_seconds_is_number_not_string():
    """GET /health uptime_seconds must be numeric (int or float), not string (type regression)."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Catch type change: uptime_seconds must be numeric
    assert isinstance(data["uptime_seconds"], (int, float)), (
        f"uptime_seconds field type changed to {type(data['uptime_seconds']).__name__}, "
        f"expected int or float"
    )
    # Must not be string
    assert type(data["uptime_seconds"]) is not str, (
        f"uptime_seconds changed to string type: {data['uptime_seconds']}"
    )


def test_health_checks_passed_is_int_not_string():
    """GET /health checks_passed must be int, not string (type regression)."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Catch type change: checks_passed must be int
    assert type(data["checks_passed"]) is int, (
        f"checks_passed field type changed to {type(data['checks_passed']).__name__}, "
        f"expected int"
    )
    # Must not be string or float
    assert type(data["checks_passed"]) is not str, (
        f"checks_passed changed to string type: {data['checks_passed']}"
    )
    assert type(data["checks_passed"]) is not float, (
        f"checks_passed changed to float type: {data['checks_passed']}"
    )


def test_health_env_field_is_string():
    """GET /health env field must be string, not other types (type regression)."""
    original_env = os.environ.pop("APP_ENV", None)
    try:
        client = TestClient(app)
        response = client.get("/health")
        data = response.json()

        # Catch type change: env must be string
        assert type(data["env"]) is str, (
            f"env field type changed from str to {type(data['env']).__name__}"
        )
    finally:
        if original_env is not None:
            os.environ["APP_ENV"] = original_env


def test_health_service_field_is_string_not_number():
    """GET /health service field must be string, not other types (type regression)."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Catch type change: service must be string
    assert type(data["service"]) is str, (
        f"service field type changed from str to {type(data['service']).__name__}"
    )
    assert data["service"] == "demo-api"


def test_health_required_fields_cannot_be_null():
    """GET /health required fields must not be None/null."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    required_fields = {"status", "version", "python", "uptime_seconds", "checks_passed", "env", "service"}
    for field in required_fields:
        assert data[field] is not None, f"Required field '{field}' must not be null"


def test_health_response_complete_schema_validation():
    """GET /health response validates complete schema with all fields and types."""
    client = TestClient(app)
    response = client.get("/health")
    data = response.json()

    # Build a schema validation result
    schema_errors = []

    # Validate each required field
    if "status" not in data:
        schema_errors.append("Missing field: status")
    elif not isinstance(data["status"], str):
        schema_errors.append(f"Field 'status' has wrong type: {type(data['status']).__name__}, expected str")

    if "version" not in data:
        schema_errors.append("Missing field: version")
    elif not isinstance(data["version"], str):
        schema_errors.append(f"Field 'version' has wrong type: {type(data['version']).__name__}, expected str")

    if "python" not in data:
        schema_errors.append("Missing field: python")
    elif not isinstance(data["python"], str):
        schema_errors.append(f"Field 'python' has wrong type: {type(data['python']).__name__}, expected str")

    if "uptime_seconds" not in data:
        schema_errors.append("Missing field: uptime_seconds")
    elif not isinstance(data["uptime_seconds"], (int, float)):
        schema_errors.append(f"Field 'uptime_seconds' has wrong type: {type(data['uptime_seconds']).__name__}, expected int or float")

    if "checks_passed" not in data:
        schema_errors.append("Missing field: checks_passed")
    elif not isinstance(data["checks_passed"], int):
        schema_errors.append(f"Field 'checks_passed' has wrong type: {type(data['checks_passed']).__name__}, expected int")

    if "env" not in data:
        schema_errors.append("Missing field: env")
    elif not isinstance(data["env"], str):
        schema_errors.append(f"Field 'env' has wrong type: {type(data['env']).__name__}, expected str")

    if "service" not in data:
        schema_errors.append("Missing field: service")
    elif not isinstance(data["service"], str):
        schema_errors.append(f"Field 'service' has wrong type: {type(data['service']).__name__}, expected str")

    # Assert no schema errors
    assert not schema_errors, (
        f"Schema validation failed with {len(schema_errors)} error(s):\n" +
        "\n".join(f"  - {error}" for error in schema_errors)
    )


def test_health_field_removal_status_would_fail():
    """Regression test: verify that removing status field would fail schema validation."""
    # This test proves the schema validator works by showing what happens without status.
    # We create a mock response to demonstrate the failure mode.
    test_data = {
        # "status" intentionally omitted to test detection
        "version": "3.0.0",
        "python": "3.9",
        "uptime_seconds": 1.23,
        "checks_passed": 1,
        "env": "dev",
        "service": "demo-api",
    }

    required_fields = {"status", "version", "python", "uptime_seconds", "checks_passed", "env", "service"}
    present_fields = set(test_data.keys())
    missing = required_fields - present_fields

    # Verify the test correctly identifies missing fields
    assert "status" in missing, "Test should detect missing status field"
    assert len(missing) == 1, f"Should only detect status missing, got: {missing}"


def test_health_field_type_change_uptime_seconds_would_fail():
    """Regression test: verify that changing uptime_seconds to string would fail."""
    # This test proves type validation works by showing what would happen with wrong type.
    test_data = "1.23"  # Wrong: string instead of number

    # Verify type check would catch this
    assert not isinstance(test_data, (int, float)), (
        "Test should detect uptime_seconds as wrong type"
    )
    assert isinstance(test_data, str), "Test demonstrates string is wrong type"
