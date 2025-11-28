"""Unit tests for course validation logic."""

import pytest
from pydantic import ValidationError

from app.schemas.courses import CourseCreate, CourseStatus


def test_course_create_with_valid_data():
    """Test creating a course with valid data."""
    course_data = {
        "title": "Test Course",
        "overview": "A test course",
        "instructor": "John Doe",
        "primary_video_url": "https://youtube.com/watch?v=test",
        "duration_minutes": 60,
        "difficulty": "beginner",
        "status": "draft",
    }
    course = CourseCreate(**course_data)
    assert course.title == "Test Course"
    assert course.status == CourseStatus.draft


def test_course_create_with_invalid_url():
    """Test that invalid URLs are rejected."""
    course_data = {
        "title": "Test Course",
        "instructor": "John Doe",
        "primary_video_url": "not-a-url",  # Invalid URL
        "duration_minutes": 60,
        "difficulty": "beginner",
        "status": "draft",
    }
    with pytest.raises(ValidationError) as exc_info:
        CourseCreate(**course_data)

    assert "primary_video_url" in str(exc_info.value)


def test_course_create_requires_title():
    """Test that title is required."""
    course_data = {
        "instructor": "John Doe",
        "primary_video_url": "https://youtube.com/watch?v=test",
        "duration_minutes": 60,
        "difficulty": "beginner",
        "status": "draft",
    }
    with pytest.raises(ValidationError) as exc_info:
        CourseCreate(**course_data)

    assert "title" in str(exc_info.value)


def test_course_title_max_length():
    """Test that title cannot exceed max length."""
    course_data = {
        "title": "x" * 141,  # Exceeds 140 character limit
        "instructor": "John Doe",
        "primary_video_url": "https://youtube.com/watch?v=test",
        "duration_minutes": 60,
        "difficulty": "beginner",
        "status": "draft",
    }
    with pytest.raises(ValidationError) as exc_info:
        CourseCreate(**course_data)

    assert "title" in str(exc_info.value)


def test_course_duration_must_be_positive():
    """Test that duration must be positive."""
    course_data = {
        "title": "Test Course",
        "instructor": "John Doe",
        "primary_video_url": "https://youtube.com/watch?v=test",
        "duration_minutes": -10,  # Negative duration
        "difficulty": "beginner",
        "status": "draft",
    }
    with pytest.raises(ValidationError) as exc_info:
        CourseCreate(**course_data)

    assert "duration_minutes" in str(exc_info.value)


def test_course_status_enum_validation():
    """Test that only valid status values are accepted."""
    course_data = {
        "title": "Test Course",
        "instructor": "John Doe",
        "primary_video_url": "https://youtube.com/watch?v=test",
        "duration_minutes": 60,
        "difficulty": "beginner",
        "status": "invalid_status",  # Invalid status
    }
    with pytest.raises(ValidationError) as exc_info:
        CourseCreate(**course_data)

    assert "status" in str(exc_info.value)


def test_course_with_supplemental_urls():
    """Test course with supplemental URLs."""
    course_data = {
        "title": "Test Course",
        "instructor": "John Doe",
        "primary_video_url": "https://youtube.com/watch?v=test",
        "supplemental_urls": [
            "https://github.com/test/repo",
            "https://docs.example.com",
        ],
        "duration_minutes": 60,
        "difficulty": "beginner",
        "status": "draft",
    }
    course = CourseCreate(**course_data)
    assert len(course.supplemental_urls) == 2
    assert str(course.supplemental_urls[0]) == "https://github.com/test/repo"
