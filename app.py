"""Minimal FastAPI app with health check and version endpoints."""
import os
import time
from datetime import datetime, timezone
from fastapi import FastAPI

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
    uptime = time.time() - _start_time
    return {
        "status": "ok",
        "started_at": STARTED_AT,
        "version": VERSION,
        "env": env,
        "uptime_seconds": uptime,
        "checks_passed": _checks_passed,
        "service": "demo-api"
    }


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": VERSION, "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
