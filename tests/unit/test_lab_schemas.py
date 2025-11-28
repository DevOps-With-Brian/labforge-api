"""Unit tests for lab exercise schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.labs import LabExercise, LabExerciseCreate, LabResourceType


def test_lab_resource_type_enum_values():
    """Test that all LabResourceType enum values are valid."""
    assert LabResourceType.kubernetes.value == "kubernetes"
    assert LabResourceType.terraform.value == "terraform"
    assert LabResourceType.yaml.value == "yaml"
    assert LabResourceType.docker_compose.value == "docker_compose"
    assert LabResourceType.walkthrough.value == "walkthrough"
    assert LabResourceType.link.value == "link"
    assert LabResourceType.other.value == "other"


def test_lab_exercise_create_minimal():
    """Test creating lab exercise with minimal required fields."""
    lab = LabExerciseCreate(
        title="Basic Lab",
        resource_type=LabResourceType.kubernetes,
        resource_uri="https://example.com/lab",
    )
    assert lab.title == "Basic Lab"
    assert lab.resource_type == LabResourceType.kubernetes
    assert str(lab.resource_uri) == "https://example.com/lab"
    assert lab.summary is None
    assert lab.estimated_minutes is None


def test_lab_exercise_create_with_all_fields():
    """Test creating lab exercise with all fields populated."""
    lab = LabExerciseCreate(
        title="Advanced Lab",
        summary="Comprehensive lab covering multiple topics",
        resource_type=LabResourceType.terraform,
        resource_uri="https://github.com/example/terraform-lab",
        estimated_minutes=90,
    )
    assert lab.title == "Advanced Lab"
    assert lab.summary == "Comprehensive lab covering multiple topics"
    assert lab.resource_type == LabResourceType.terraform
    assert lab.estimated_minutes == 90


def test_lab_exercise_create_missing_title():
    """Test that title is required for lab creation."""
    with pytest.raises(ValidationError) as exc_info:
        LabExerciseCreate(
            resource_type=LabResourceType.kubernetes,
            resource_uri="https://example.com/lab",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("title",) and e["type"] == "missing" for e in errors)


def test_lab_exercise_create_missing_resource_type():
    """Test that resource_type is required for lab creation."""
    with pytest.raises(ValidationError) as exc_info:
        LabExerciseCreate(
            title="Lab Title",
            resource_uri="https://example.com/lab",
        )
    errors = exc_info.value.errors()
    assert any(
        e["loc"] == ("resource_type",) and e["type"] == "missing" for e in errors
    )


def test_lab_exercise_create_missing_resource_uri():
    """Test that resource_uri is required for lab creation."""
    with pytest.raises(ValidationError) as exc_info:
        LabExerciseCreate(
            title="Lab Title",
            resource_type=LabResourceType.kubernetes,
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("resource_uri",) and e["type"] == "missing" for e in errors)


def test_lab_exercise_create_invalid_resource_type():
    """Test that invalid resource type is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        LabExerciseCreate(
            title="Lab Title",
            resource_type="invalid_type",
            resource_uri="https://example.com/lab",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("resource_type",) for e in errors)


def test_lab_exercise_create_empty_title():
    """Test that empty title is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        LabExerciseCreate(
            title="",
            resource_type=LabResourceType.kubernetes,
            resource_uri="https://example.com/lab",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("title",) for e in errors)


def test_lab_exercise_create_empty_resource_uri():
    """Test that empty resource URI is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        LabExerciseCreate(
            title="Lab Title",
            resource_type=LabResourceType.kubernetes,
            resource_uri="",
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("resource_uri",) for e in errors)


def test_lab_exercise_create_negative_estimated_minutes():
    """Test that negative estimated minutes is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        LabExerciseCreate(
            title="Lab Title",
            resource_type=LabResourceType.kubernetes,
            resource_uri="https://example.com/lab",
            estimated_minutes=-10,
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("estimated_minutes",) for e in errors)


def test_lab_exercise_create_zero_estimated_minutes():
    """Test that zero estimated minutes is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        LabExerciseCreate(
            title="Lab Title",
            resource_type=LabResourceType.kubernetes,
            resource_uri="https://example.com/lab",
            estimated_minutes=0,
        )
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("estimated_minutes",) for e in errors)


def test_lab_exercise_public_schema():
    """Test LabExercise public schema with all fields."""
    from uuid import UUID
    test_id = UUID("12345678-1234-5678-1234-567812345678")
    course_id = UUID("87654321-4321-8765-4321-876543218765")
    
    lab = LabExercise(
        id=test_id,
        course_id=course_id,
        title="Public Lab",
        summary="This is a public lab",
        resource_type=LabResourceType.link,
        resource_uri="https://github.com/example/lab",
        estimated_minutes=45,
    )
    assert lab.id == test_id
    assert lab.course_id == course_id
    assert lab.title == "Public Lab"
    assert lab.summary == "This is a public lab"
    assert lab.resource_type == LabResourceType.link
    assert lab.estimated_minutes == 45


def test_lab_exercise_all_resource_types():
    """Test creating labs with each resource type."""
    resource_types = [
        LabResourceType.kubernetes,
        LabResourceType.terraform,
        LabResourceType.yaml,
        LabResourceType.docker_compose,
        LabResourceType.walkthrough,
        LabResourceType.link,
        LabResourceType.other,
    ]
    
    for resource_type in resource_types:
        lab = LabExerciseCreate(
            title=f"Lab for {resource_type.value}",
            resource_type=resource_type,
            resource_uri=f"https://example.com/{resource_type.value}",
        )
        assert lab.resource_type == resource_type


def test_lab_exercise_summary_max_length():
    """Test that very long summaries are accepted (up to 1000 chars per schema)."""
    long_summary = "x" * 1000
    lab = LabExerciseCreate(
        title="Lab with long summary",
        summary=long_summary,
        resource_type=LabResourceType.kubernetes,
        resource_uri="https://example.com/lab",
    )
    assert len(lab.summary) == 1000


def test_lab_exercise_title_max_length():
    """Test that titles up to max length are accepted."""
    long_title = "x" * 140
    lab = LabExerciseCreate(
        title=long_title,
        resource_type=LabResourceType.kubernetes,
        resource_uri="https://example.com/lab",
    )
    assert len(lab.title) == 140


def test_lab_exercise_uri_max_length():
    """Test that long URIs are accepted."""
    long_uri = "https://example.com/" + "x" * 450
    lab = LabExerciseCreate(
        title="Lab with long URI",
        resource_type=LabResourceType.link,
        resource_uri=long_uri,
    )
    # HttpUrl may normalize trailing slashes, so just verify it's close to expected length
    assert len(str(lab.resource_uri)) >= 469
