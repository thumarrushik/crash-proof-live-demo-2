"""Minimal FastAPI app with health check and version endpoints."""
import time
from fastapi import FastAPI

app = FastAPI()

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
    uptime = time.time() - _start_time
    return {
        "status": "ok",
        "version": VERSION,
        "service": "demo-api",
        "uptime_seconds": uptime,
        "checks_passed": _checks_passed,
    }


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": VERSION, "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
