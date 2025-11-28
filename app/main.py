"""LabForge API - FastAPI Application."""

from fastapi import FastAPI

from app.api import api_router
from app.schemas.health import HealthResponse

app = FastAPI(
    title="LabForge API",
    description="A FastAPI backend API for managing labs/training for UI",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint to verify the API is running."""
    return HealthResponse(status="healthy", message="LabForge API is running")


app.include_router(api_router)
