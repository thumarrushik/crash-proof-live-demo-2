"""Minimal FastAPI app with health check and version endpoints."""
import time
from fastapi import FastAPI

app = FastAPI()

# Track process start time for uptime calculation
_start_time = time.time()


@app.get("/health")
def health():
    """Health check endpoint."""
    uptime = time.time() - _start_time
    return {"status": "ok", "uptime_seconds": uptime}


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": "3.0.0", "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
