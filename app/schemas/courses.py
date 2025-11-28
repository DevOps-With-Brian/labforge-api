"""Schemas for course management."""

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import Field, HttpUrl

from app.schemas.common import APIModel


class CourseStatus(str, Enum):
    """Lifecycle states for courses."""

    draft = "draft"
    published = "published"
    archived = "archived"


class CourseBase(APIModel):
    """Shared fields across course operations.

    Note on duration_minutes:
        Maximum course duration is 14,400 minutes (10 days). This limit represents
        a practical upper bound for self-paced course content. Courses exceeding
        this limit should be split into multiple courses or a learning path.
        This constraint is enforced at the API validation layer.
    """

    title: str = Field(..., min_length=3, max_length=140)
    overview: str | None = Field(None, max_length=3000)
    instructor: str = Field(..., min_length=2, max_length=80)
    primary_video_url: HttpUrl
    supplemental_urls: list[HttpUrl] = Field(default_factory=list)
    duration_minutes: int = Field(
        ...,
        gt=0,
        lt=14_400,
        description="Course duration in minutes. Maximum is 14,400 (10 days).",
    )
    difficulty: str = Field(
        default="intermediate", pattern="^(beginner|intermediate|advanced)$"
    )
    tags: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    category: str | None = Field(None, max_length=80)


class CourseCreate(CourseBase):
    """Payload for creating a new course."""

    status: CourseStatus = CourseStatus.draft


class CourseUpdate(APIModel):
    """Patch-like payload for updating a course."""

    title: str | None = Field(None, min_length=3, max_length=140)
    overview: str | None = Field(None, max_length=3000)
    instructor: str | None = Field(None, min_length=2, max_length=80)
    primary_video_url: HttpUrl | None = None
    supplemental_urls: list[HttpUrl] | None = None
    duration_minutes: int | None = Field(
        None,
        gt=0,
        lt=14_400,
        description="Course duration in minutes. Maximum is 14,400 (10 days).",
    )
    difficulty: str | None = Field(None, pattern="^(beginner|intermediate|advanced)$")
    tags: list[str] | None = None
    prerequisites: list[str] | None = None
    category: str | None = Field(None, max_length=80)
    status: CourseStatus | None = None


class Course(CourseBase):
    """Persisted course record."""

    id: UUID = Field(default_factory=uuid4)
    status: CourseStatus = CourseStatus.draft
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CoursePublic(Course):
    """Response payload with basic aggregates."""

    enrollment_count: int = 0
    lab_count: int = 0
