"""Minimal FastAPI app with health check and version endpoints."""
from datetime import datetime, timezone
from fastapi import FastAPI

app = FastAPI()

# Capture the process start time in ISO-8601 UTC format
STARTED_AT = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "started_at": STARTED_AT}


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": "3.0.0", "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
