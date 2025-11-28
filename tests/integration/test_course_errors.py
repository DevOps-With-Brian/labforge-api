"""Integration tests for course error handling and edge cases."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import build_course_payload

client = TestClient(app, raise_server_exceptions=False)


def test_get_nonexistent_course():
    """Test fetching a course that doesn't exist returns 404."""
    missing_id = str(uuid4())
    response = client.get(f"/courses/{missing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_update_nonexistent_course():
    """Test updating a course that doesn't exist returns 404."""
    missing_id = str(uuid4())
    response = client.patch(
        f"/courses/{missing_id}",
        json={"title": "Updated Title"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_create_enrollment_for_nonexistent_course():
    """Test creating enrollment for non-existent course returns 404."""
    missing_id = str(uuid4())
    response = client.post(
        f"/courses/{missing_id}/enrollments",
        json={"name": "Test User", "email": "test@example.com"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_list_enrollments_for_nonexistent_course():
    """Test listing enrollments for non-existent course returns 404."""
    missing_id = str(uuid4())
    response = client.get(f"/courses/{missing_id}/enrollments")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_attach_lab_to_nonexistent_course():
    """Test attaching lab to non-existent course returns 404."""
    missing_id = str(uuid4())
    response = client.post(
        f"/courses/{missing_id}/labs",
        json={
            "title": "Test Lab",
            "resource_type": "kubernetes",
            "resource_uri": "https://example.com/lab",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_list_labs_for_nonexistent_course():
    """Test listing labs for non-existent course returns 404."""
    missing_id = str(uuid4())
    response = client.get(f"/courses/{missing_id}/labs")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_update_course_with_empty_payload():
    """Test updating a course with no changes still succeeds."""
    # Create a course first
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Update with empty payload (all fields optional)
    response = client.patch(f"/courses/{course_id}", json={})
    assert response.status_code == 200

    # Verify course data unchanged
    course_data = response.json()
    assert course_data["title"] == "DevOps With Brian: CI/CD Foundations"


def test_list_empty_enrollments():
    """Test listing enrollments for course with no enrollments."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.get(f"/courses/{course_id}/enrollments")
    assert response.status_code == 200
    assert response.json() == []


def test_list_empty_labs():
    """Test listing labs for course with no labs."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.get(f"/courses/{course_id}/labs")
    assert response.status_code == 200
    assert response.json() == []


def test_enrollment_with_notes():
    """Test creating enrollment with optional notes field."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.post(
        f"/courses/{course_id}/enrollments",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "notes": "Referred by colleague",
        },
    )
    assert response.status_code == 201
    enrollment_data = response.json()
    assert enrollment_data["notes"] == "Referred by colleague"


def test_enrollment_default_progress():
    """Test that enrollment starts with progress_percent of 0 by default."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.post(
        f"/courses/{course_id}/enrollments",
        json={
            "name": "Test User",
            "email": "test@example.com",
        },
    )
    assert response.status_code == 201
    enrollment_data = response.json()
    assert enrollment_data["progress_percent"] == 0


def test_lab_without_estimated_minutes():
    """Test creating lab without optional estimated_minutes field."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.post(
        f"/courses/{course_id}/labs",
        json={
            "title": "Quick Lab",
            "resource_type": "terraform",
            "resource_uri": "https://example.com/lab",
        },
    )
    assert response.status_code == 201
    lab_data = response.json()
    assert lab_data["estimated_minutes"] is None


def test_lab_with_summary():
    """Test creating lab with optional summary field."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.post(
        f"/courses/{course_id}/labs",
        json={
            "title": "Detailed Lab",
            "summary": "This lab covers advanced topics",
            "resource_type": "link",
            "resource_uri": "https://github.com/example/lab",
            "estimated_minutes": 60,
        },
    )
    assert response.status_code == 201
    lab_data = response.json()
    assert lab_data["summary"] == "This lab covers advanced topics"


def test_list_courses_shows_updated_counts():
    """Test that listing courses shows correct enrollment and lab counts."""
    # Create course
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Add enrollments
    client.post(
        f"/courses/{course_id}/enrollments",
        json={"name": "User 1", "email": "user1@example.com"},
    )
    client.post(
        f"/courses/{course_id}/enrollments",
        json={"name": "User 2", "email": "user2@example.com"},
    )

    # Add lab
    client.post(
        f"/courses/{course_id}/labs",
        json={
            "title": "Lab 1",
            "resource_type": "kubernetes",
            "resource_uri": "https://example.com/lab1",
        },
    )

    # Get single course (not list) to verify counts for this specific course
    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    course = response.json()
    assert course["enrollment_count"] == 2
    assert course["lab_count"] == 1


def test_get_single_course_shows_counts():
    """Test that getting a single course shows correct counts."""
    # Create course
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Add enrollment and lab
    client.post(
        f"/courses/{course_id}/enrollments",
        json={"name": "User", "email": "user@example.com"},
    )
    client.post(
        f"/courses/{course_id}/labs",
        json={
            "title": "Lab",
            "resource_type": "kubernetes",
            "resource_uri": "https://example.com/lab",
        },
    )

    # Get single course
    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    course = response.json()
    assert course["enrollment_count"] == 1
    assert course["lab_count"] == 1
