"""Minimal application packaged by the Dockerfile."""

from fastapi import FastAPI

app = FastAPI(title="Finance API")


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
