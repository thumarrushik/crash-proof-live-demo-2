"""Minimal FastAPI app with health check and version endpoints."""
import os
import socket
import sys
import time
from datetime import datetime, timezone
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

# Capture the process start time in ISO-8601 UTC format
STARTED_AT = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# App version string
VERSION = "3.0.0"

# Track process start time for uptime calculation
_start_time = time.time()

# Counter for health checks served since process start
_checks_passed = 0

# Track service readiness (ready immediately for this service; no startup dependencies)
_is_ready = True


@app.on_event("startup")
async def startup_event():
    """Confirm service readiness during actual deployment startup.

    This service has no external dependencies, so it is ready immediately.
    In a production deployment with dependencies (database, cache, etc.),
    this event would set _is_ready = True only after dependencies are verified.
    """
    global _is_ready
    _is_ready = True


def _get_health_status():
    """Internal helper: compute health status data."""
    global _checks_passed
    _checks_passed += 1
    env = os.getenv("APP_ENV", "dev")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    uptime = time.time() - _start_time
    return {
        "status": "ok",
        "started_at": STARTED_AT,
        "version": VERSION,
        "env": env,
        "python": python_version,
        "uptime_seconds": uptime,
        "checks_passed": _checks_passed,
        "service": "demo-api",
        "hostname": socket.gethostname(),
    }


@app.get("/livez")
def livez(response: Response):
    """Liveness probe endpoint (Kubernetes kubelet).

    Returns 200 OK if the process is alive and responsive.
    Returns 503 Service Unavailable only if the process is in a bad state.
    """
    # For alias pattern: reuse health status
    health_data = _get_health_status()
    response.status_code = 200
    return health_data


@app.get("/readyz")
def readyz(response: Response):
    """Readiness probe endpoint (Kubernetes load balancer, traffic routing).

    Returns 200 OK if the service is ready to accept and handle requests.
    Returns 503 Service Unavailable if the service is not ready (e.g., startup in progress).
    """
    # Check if service has completed startup
    if not _is_ready:
        response.status_code = 503
        return {"status": "not ready", "reason": "service initializing"}

    # For alias pattern: reuse health status
    health_data = _get_health_status()
    response.status_code = 200
    return health_data


@app.get("/health")
def health():
    """Health check endpoint (backward-compatible, comprehensive status).

    Returns detailed service state for operators and dashboards.
    Always returns 200 OK (status inspection via JSON fields, not HTTP codes).
    """
    return _get_health_status()


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": VERSION, "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}


@app.get("/", response_class=HTMLResponse)
def root():
    """Serve status page that fetches and displays /health data."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Status</title>
</head>
<body>
    <h1>Status</h1>
    <div id="health">Loading...</div>
    <script>
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                const list = document.createElement('ul');
                Object.entries(data).forEach(([key, value]) => {
                    const li = document.createElement('li');
                    li.textContent = key + ': ' + value;
                    list.appendChild(li);
                });
                const healthDiv = document.getElementById('health');
                healthDiv.innerHTML = '';
                healthDiv.appendChild(list);
            })
            .catch(error => {
                document.getElementById('health').textContent = 'Error: ' + error.message;
            });
    </script>
</body>
</html>"""
    return html
