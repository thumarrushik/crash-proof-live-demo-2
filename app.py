"""Minimal FastAPI app with health check and version endpoints."""
import os
from fastapi import FastAPI

app = FastAPI()

# App version string
VERSION = "3.0.0"


@app.get("/health")
def health():
    """Health check endpoint."""
    env = os.getenv("APP_ENV", "dev")
    return {"status": "ok", "version": VERSION, "env": env}


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": VERSION, "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
