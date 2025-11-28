"""API router aggregation for the LabForge service."""

from fastapi import APIRouter

from app.api.routes import courses

api_router = APIRouter()
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])

__all__ = ["api_router"]
