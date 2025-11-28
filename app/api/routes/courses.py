"""Routes for managing courses, enrollments, and lab attachments."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Course as CourseModel
from app.db.models import Enrollment as EnrollmentModel
from app.db.models import LabExercise as LabExerciseModel
from app.db.session import get_session
from app.schemas import (
    CourseCreate,
    CoursePublic,
    CourseUpdate,
    Enrollment,
    EnrollmentCreate,
    LabExercise,
    LabExerciseCreate,
)

router = APIRouter()


def _to_db_dict(payload: BaseModel, *, exclude_unset: bool = False) -> dict[str, Any]:
    """Convert a Pydantic model to a dict suitable for SQLAlchemy models.

    Uses `mode="json"` to serialize complex types (e.g., HttpUrl) to their
    JSON-compatible string representations, which is required because SQLAlchemy
    models expect string types for URL fields rather than Pydantic's URL objects.
    """
    return payload.model_dump(mode="json", exclude_unset=exclude_unset)


async def _get_course_or_404(session: AsyncSession, course_id: str) -> CourseModel:
    course = await session.get(CourseModel, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course


async def _counts(session: AsyncSession, course_id: str) -> tuple[int, int]:
    enrollment_count = await session.scalar(
        select(func.count(EnrollmentModel.id)).where(
            EnrollmentModel.course_id == course_id
        )
    )
    lab_count = await session.scalar(
        select(func.count(LabExerciseModel.id)).where(
            LabExerciseModel.course_id == course_id
        )
    )
    return int(enrollment_count or 0), int(lab_count or 0)


async def _to_public(session: AsyncSession, course: CourseModel) -> CoursePublic:
    enrollment_count, lab_count = await _counts(session, course.id)
    base = CoursePublic.model_validate(course, from_attributes=True)
    return base.model_copy(
        update={
            "enrollment_count": enrollment_count,
            "lab_count": lab_count,
        }
    )


@router.get("", response_model=list[CoursePublic])
async def list_courses(
    session: AsyncSession = Depends(get_session),
) -> list[CoursePublic]:
    """List all courses with aggregates."""
    stmt = (
        select(
            CourseModel,
            func.count(EnrollmentModel.id).label("enrollment_count"),
            func.count(LabExerciseModel.id).label("lab_count"),
        )
        .outerjoin(EnrollmentModel, EnrollmentModel.course_id == CourseModel.id)
        .outerjoin(LabExerciseModel, LabExerciseModel.course_id == CourseModel.id)
        .group_by(CourseModel.id)
    )
    result = await session.execute(stmt)
    courses = []
    for course, enrollment_count, lab_count in result.all():
        base = CoursePublic.model_validate(course, from_attributes=True)
        courses.append(
            base.model_copy(
                update={
                    "enrollment_count": int(enrollment_count or 0),
                    "lab_count": int(lab_count or 0),
                }
            )
        )
    return courses


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CoursePublic)
async def create_course(
    payload: CourseCreate, session: AsyncSession = Depends(get_session)
) -> CoursePublic:
    """Create a new course."""
    course = CourseModel(**_to_db_dict(payload))
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return await _to_public(session, course)


@router.get("/{course_id}", response_model=CoursePublic)
async def get_course(
    course_id: str, session: AsyncSession = Depends(get_session)
) -> CoursePublic:
    """Retrieve a single course."""
    course = await _get_course_or_404(session, course_id)
    return await _to_public(session, course)


@router.patch("/{course_id}", response_model=CoursePublic)
async def update_course(
    course_id: str, payload: CourseUpdate, session: AsyncSession = Depends(get_session)
) -> CoursePublic:
    """Update course metadata."""
    course = await _get_course_or_404(session, course_id)
    updates = _to_db_dict(payload, exclude_unset=True)
    if updates:
        for key, value in updates.items():
            setattr(course, key, value)
        await session.commit()
        await session.refresh(course)
    return await _to_public(session, course)


@router.post(
    "/{course_id}/enrollments",
    status_code=status.HTTP_201_CREATED,
    response_model=Enrollment,
)
async def create_enrollment(
    course_id: str,
    payload: EnrollmentCreate,
    session: AsyncSession = Depends(get_session),
) -> Enrollment:
    """Enroll a learner in a self-paced course."""
    await _get_course_or_404(session, course_id)
    enrollment = EnrollmentModel(course_id=course_id, **_to_db_dict(payload))
    session.add(enrollment)
    await session.commit()
    await session.refresh(enrollment)
    return Enrollment.model_validate(enrollment, from_attributes=True)


@router.get("/{course_id}/enrollments", response_model=list[Enrollment])
async def list_enrollments(
    course_id: str, session: AsyncSession = Depends(get_session)
) -> list[Enrollment]:
    """List enrollments for a course."""
    await _get_course_or_404(session, course_id)
    enrollments = (
        await session.execute(
            select(EnrollmentModel).where(EnrollmentModel.course_id == course_id)
        )
    ).scalars()
    return [
        Enrollment.model_validate(enrollment, from_attributes=True)
        for enrollment in enrollments
    ]


@router.post(
    "/{course_id}/labs",
    status_code=status.HTTP_201_CREATED,
    response_model=LabExercise,
)
async def attach_lab(
    course_id: str,
    payload: LabExerciseCreate,
    session: AsyncSession = Depends(get_session),
) -> LabExercise:
    """Attach a lab exercise to a course."""
    await _get_course_or_404(session, course_id)
    lab = LabExerciseModel(course_id=course_id, **_to_db_dict(payload))
    session.add(lab)
    await session.commit()
    await session.refresh(lab)
    return LabExercise.model_validate(lab, from_attributes=True)


@router.get("/{course_id}/labs", response_model=list[LabExercise])
async def list_labs(
    course_id: str, session: AsyncSession = Depends(get_session)
) -> list[LabExercise]:
    """List lab exercises attached to a course."""
    await _get_course_or_404(session, course_id)
    labs = (
        await session.execute(
            select(LabExerciseModel).where(LabExerciseModel.course_id == course_id)
        )
    ).scalars()
    return [LabExercise.model_validate(lab, from_attributes=True) for lab in labs]
