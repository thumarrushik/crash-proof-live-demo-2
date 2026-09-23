"""Minimal FastAPI app with health check and version endpoints."""
import os
from fastapi import FastAPI

app = FastAPI()

# App version string
VERSION = "3.0.0"

# Counter for health checks served since process start
_checks_passed = 0


@app.get("/health")
def health():
    """Health check endpoint."""
    global _checks_passed
    _checks_passed += 1
    env = os.getenv("APP_ENV", "dev")
    return {"status": "ok", "version": VERSION, "env": env, "checks_passed": _checks_passed, "service": "demo-api"}


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": VERSION, "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
