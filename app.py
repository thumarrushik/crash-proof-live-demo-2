"""Minimal FastAPI app with health check and version endpoints."""
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": "1.0.0", "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
