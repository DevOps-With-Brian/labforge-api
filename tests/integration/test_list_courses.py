"""Integration tests for list courses functionality."""

from fastapi.testclient import TestClient
from tests.conftest import build_course_payload

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
def test_list_empty_courses():
    """Test listing courses when database is empty."""
    response = client.get("/courses")
    assert response.status_code == 200
    assert response.json() == []


def test_list_multiple_courses_with_varying_counts():
    """Test that list courses shows correct aggregates for multiple courses."""
    # Create first course with enrollments and labs
    course1_id = client.post(
        "/courses",
        json=build_course_payload(title="Course 1"),
    ).json()["id"]

    client.post(
        f"/courses/{course1_id}/enrollments",
        json={"name": "Student 1", "email": "student1@example.com"},
    )
    client.post(
        f"/courses/{course1_id}/labs",
        json={
            "title": "Lab 1",
            "resource_type": "kubernetes",
            "resource_uri": "https://example.com/lab1",
        },
    )

    # Create second course with no enrollments or labs
    course2_id = client.post(
        "/courses",
        json=build_course_payload(title="Course 2"),
    ).json()["id"]

    # Create third course with multiple enrollments
    course3_id = client.post(
        "/courses",
        json=build_course_payload(title="Course 3"),
    ).json()["id"]

    for i in range(3):
        client.post(
            f"/courses/{course3_id}/enrollments",
            json={"name": f"Student {i}", "email": f"student{i}@example.com"},
        )

    # List all courses
    response = client.get("/courses")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 3

    # Find each course and verify counts
    course1 = next(c for c in courses if c["id"] == course1_id)
    assert course1["enrollment_count"] == 1
    assert course1["lab_count"] == 1

    course2 = next(c for c in courses if c["id"] == course2_id)
    assert course2["enrollment_count"] == 0
    assert course2["lab_count"] == 0

    course3 = next(c for c in courses if c["id"] == course3_id)
    assert course3["enrollment_count"] == 3
    assert course3["lab_count"] == 0


def test_list_courses_with_multiple_labs():
    """Test course listing with multiple labs attached."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Add multiple labs
    for i in range(5):
        client.post(
            f"/courses/{course_id}/labs",
            json={
                "title": f"Lab {i+1}",
                "resource_type": "kubernetes",
                "resource_uri": f"https://example.com/lab{i+1}",
            },
        )

    # List courses
    response = client.get("/courses")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 1
    assert courses[0]["lab_count"] == 5


def test_list_courses_returns_all_fields():
    """Test that list courses returns all expected fields."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.get("/courses")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) == 1

    course = courses[0]
    # Verify all fields are present
    assert course["id"] == course_id
    assert course["title"] == "DevOps With Brian: CI/CD Foundations"
    assert course["instructor"] == "Brian T"
    assert course["status"] == "published"
    assert course["enrollment_count"] == 0
    assert course["lab_count"] == 0
    assert "created_at" in course
    assert "updated_at" in course
