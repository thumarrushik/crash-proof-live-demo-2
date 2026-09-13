"""Minimal FastAPI app with health check endpoint."""
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
