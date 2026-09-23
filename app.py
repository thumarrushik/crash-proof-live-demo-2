"""Minimal FastAPI app with health check and version endpoints."""
import sys
from fastapi import FastAPI

app = FastAPI()

# App version string
VERSION = "3.0.0"


@app.get("/health")
def health():
    """Health check endpoint."""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return {"status": "ok", "version": VERSION, "python": python_version}


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": VERSION, "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
