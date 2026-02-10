"""Main FastAPI application."""

from fastapi import FastAPI

app = FastAPI(
    title="ShortLink API",
    description="A simple URL shortening service",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "ShortLink API is running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
