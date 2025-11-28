"""SQLAlchemy models for courses, enrollments, and labs."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.schemas.courses import CourseStatus
from app.schemas.labs import LabResourceType


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class Course(Base):
    """Course record for self-paced content."""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    title: Mapped[str] = mapped_column(String(140), nullable=False)
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructor: Mapped[str] = mapped_column(String(80), nullable=False)
    primary_video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    supplemental_urls: Mapped[list[str]] = mapped_column(JSON, default=lambda: [])
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), default="intermediate")
    tags: Mapped[list[str]] = mapped_column(JSON, default_factory=list)
    prerequisites: Mapped[list[str]] = mapped_column(JSON, default=lambda: [])
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[CourseStatus] = mapped_column(
        Enum(CourseStatus), nullable=False, default=CourseStatus.draft
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    labs: Mapped[list["LabExercise"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )


class Enrollment(Base):
    """Enrollment record for a learner in a course."""

    __tablename__ = "enrollments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    course_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    course: Mapped[Course] = relationship(back_populates="enrollments")


class LabExercise(Base):
    """Lab exercises attached to a course."""

    __tablename__ = "lab_exercises"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    course_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(140), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    resource_type: Mapped[LabResourceType] = mapped_column(
        Enum(LabResourceType), nullable=False
    )
    resource_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    course: Mapped[Course] = relationship(back_populates="labs")
