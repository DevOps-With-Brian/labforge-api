"""Unit tests for enrollment schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.enrollments import Enrollment, EnrollmentCreate


def test_enrollment_create_with_valid_data():
    """Test creating an enrollment with valid data."""
    enrollment_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "notes": "Interested in DevOps",
    }
    enrollment = EnrollmentCreate(**enrollment_data)
    assert enrollment.name == "John Doe"
    assert enrollment.email == "john@example.com"


def test_enrollment_create_requires_name():
    """Test that name is required."""
    enrollment_data = {
        "email": "john@example.com",
    }
    with pytest.raises(ValidationError) as exc_info:
        EnrollmentCreate(**enrollment_data)
    
    assert "name" in str(exc_info.value)


def test_enrollment_create_requires_email():
    """Test that email is required."""
    enrollment_data = {
        "name": "John Doe",
    }
    with pytest.raises(ValidationError) as exc_info:
        EnrollmentCreate(**enrollment_data)
    
    assert "email" in str(exc_info.value)


def test_enrollment_create_validates_email_format():
    """Test that email format is validated."""
    enrollment_data = {
        "name": "John Doe",
        "email": "not-an-email",  # Invalid email
    }
    with pytest.raises(ValidationError) as exc_info:
        EnrollmentCreate(**enrollment_data)
    
    assert "email" in str(exc_info.value)


def test_enrollment_name_min_length():
    """Test that name must be at least 2 characters."""
    enrollment_data = {
        "name": "A",  # Too short
        "email": "john@example.com",
    }
    with pytest.raises(ValidationError) as exc_info:
        EnrollmentCreate(**enrollment_data)
    
    assert "name" in str(exc_info.value)


def test_enrollment_name_max_length():
    """Test that name cannot exceed max length."""
    enrollment_data = {
        "name": "x" * 81,  # Exceeds 80 character limit
        "email": "john@example.com",
    }
    with pytest.raises(ValidationError) as exc_info:
        EnrollmentCreate(**enrollment_data)
    
    assert "name" in str(exc_info.value)


def test_enrollment_notes_max_length():
    """Test that notes cannot exceed max length."""
    enrollment_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "notes": "x" * 501,  # Exceeds 500 character limit
    }
    with pytest.raises(ValidationError) as exc_info:
        EnrollmentCreate(**enrollment_data)
    
    assert "notes" in str(exc_info.value)


def test_enrollment_full_model_with_defaults():
    """Test the full Enrollment model with defaults."""
    enrollment = Enrollment(
        name="John Doe",
        email="john@example.com",
        course_id=uuid4(),
    )
    assert enrollment.progress_percent == 0
    assert enrollment.id is not None
    assert enrollment.created_at is not None


def test_enrollment_progress_cannot_exceed_100():
    """Test that progress cannot exceed 100%."""
    with pytest.raises(ValidationError) as exc_info:
        Enrollment(
            name="John Doe",
            email="john@example.com",
            course_id=uuid4(),
            progress_percent=150,  # Invalid: > 100
        )
    
    assert "progress_percent" in str(exc_info.value)


def test_enrollment_progress_cannot_be_negative():
    """Test that progress cannot be negative."""
    with pytest.raises(ValidationError) as exc_info:
        Enrollment(
            name="John Doe",
            email="john@example.com",
            course_id=uuid4(),
            progress_percent=-10,  # Invalid: < 0
        )
    
    assert "progress_percent" in str(exc_info.value)
