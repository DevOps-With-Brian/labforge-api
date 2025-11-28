"""Schemas for course enrollment flows."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import EmailStr, Field

from app.schemas.common import APIModel


class EnrollmentCreate(APIModel):
    """Payload for enrolling a learner into a course."""

    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    notes: str | None = Field(None, max_length=500)


class Enrollment(EnrollmentCreate):
    """Persisted enrollment record."""

    id: UUID = Field(default_factory=uuid4)
    course_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    progress_percent: int = Field(default=0, ge=0, le=100)
