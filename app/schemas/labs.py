"""Schemas for event lab exercises."""

from enum import Enum
from uuid import UUID, uuid4

from pydantic import Field, HttpUrl

from app.schemas.common import APIModel


class LabResourceType(str, Enum):
    """Resource types supported for lab exercises."""

    yaml = "yaml"
    terraform = "terraform"
    kubernetes = "kubernetes"
    docker_compose = "docker_compose"
    walkthrough = "walkthrough"
    link = "link"
    other = "other"


class LabExerciseCreate(APIModel):
    """Payload for attaching a lab exercise to an event."""

    title: str = Field(..., min_length=3, max_length=140)
    summary: str | None = Field(None, max_length=1000)
    resource_type: LabResourceType
    resource_uri: HttpUrl
    estimated_minutes: int | None = Field(None, gt=0, lt=480)


class LabExercise(LabExerciseCreate):
    """Persisted lab exercise tied to an event."""

    id: UUID = Field(default_factory=uuid4)
    course_id: UUID
