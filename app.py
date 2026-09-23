"""Minimal FastAPI app with health check and version endpoints."""
import os
import sys
import time
from datetime import datetime, timezone
from fastapi import FastAPI
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


@app.get("/health")
def health():
    """Health check endpoint."""
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
    }


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
