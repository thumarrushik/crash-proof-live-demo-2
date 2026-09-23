"""Minimal FastAPI app with health check and version endpoints."""
import os
from fastapi import FastAPI

app = FastAPI()

# App version string
VERSION = "3.0.0"


@app.get("/health")
def health():
    """Health check endpoint."""
<<<<<<< HEAD
    env = os.getenv("APP_ENV", "dev")
    return {"status": "ok", "version": VERSION, "env": env}
=======
    return {"status": "ok", "version": VERSION, "service": "demo-api"}
>>>>>>> origin/main


@app.get("/version")
def version():
    """Version endpoint."""
    return {"version": VERSION, "build": "local", "commit": "dev"}


@app.get("/ping")
def ping():
    """Ping endpoint."""
    return {"ping": "pong"}
