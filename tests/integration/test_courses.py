"""Integration tests for course and lab routes."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def build_course_payload(**overrides):
    payload = {
        "title": "DevOps With Brian: CI/CD Foundations",
        "overview": "Hands-on course covering pipelines and Kubernetes delivery.",
        "instructor": "Brian T",
        "primary_video_url": "https://youtube.com/devopswithbrian",
        "supplemental_urls": ["https://github.com/devops-with-brian/sample-repo"],
        "duration_minutes": 120,
        "difficulty": "intermediate",
        "tags": ["devops", "kubernetes"],
        "prerequisites": ["Basic Git", "Docker fundamentals"],
        "category": "DevOps",
        "status": "published",
    }
    payload.update(overrides)
    return payload


def test_create_and_list_courses():
    payload = build_course_payload()
    created = client.post("/courses", json=payload)
    assert created.status_code == 201
    created_data = created.json()
    assert created_data["title"] == payload["title"]
    assert created_data["status"] == payload["status"]
    assert created_data["enrollment_count"] == 0
    assert created_data["lab_count"] == 0

    listed = client.get("/courses")
    assert listed.status_code == 200
    courses = listed.json()
    assert len(courses) == 1
    assert courses[0]["id"] == created_data["id"]


def test_enrollment_tracking():
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    first = client.post(
        f"/courses/{course_id}/enrollments",
        json={"name": "First Learner", "email": "first@example.com"},
    )
    assert first.status_code == 201
    assert first.json()["progress_percent"] == 0

    second = client.post(
        f"/courses/{course_id}/enrollments",
        json={"name": "Second Learner", "email": "second@example.com"},
    )
    assert second.status_code == 201
    assert second.json()["progress_percent"] == 0

    updated = client.patch(
        f"/courses/{course_id}", json={"status": "archived", "tags": ["finished"]}
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "archived"
    assert updated.json()["tags"] == ["finished"]


def test_list_enrollments():
    """Test listing enrollments returns correct data."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Initially empty
    empty_response = client.get(f"/courses/{course_id}/enrollments")
    assert empty_response.status_code == 200
    assert empty_response.json() == []

    # Create enrollments
    first = client.post(
        f"/courses/{course_id}/enrollments",
        json={"name": "First Learner", "email": "first@example.com"},
    )
    assert first.status_code == 201
    first_data = first.json()

    second = client.post(
        f"/courses/{course_id}/enrollments",
        json={"name": "Second Learner", "email": "second@example.com"},
    )
    assert second.status_code == 201
    second_data = second.json()

    # List enrollments and verify
    response = client.get(f"/courses/{course_id}/enrollments")
    assert response.status_code == 200
    enrollments = response.json()
    assert len(enrollments) == 2

    # Verify enrollment data is correct
    enrollment_ids = [e["id"] for e in enrollments]
    assert first_data["id"] in enrollment_ids
    assert second_data["id"] in enrollment_ids

    # Verify enrollment fields
    for enrollment in enrollments:
        assert "id" in enrollment
        assert "course_id" in enrollment
        assert enrollment["course_id"] == course_id
        assert "name" in enrollment
        assert "email" in enrollment
        assert "progress_percent" in enrollment
        assert enrollment["progress_percent"] == 0


def test_list_enrollments_for_nonexistent_course():
    """Test listing enrollments for a non-existent course returns 404."""
    missing_id = uuid4()
    response = client.get(f"/courses/{missing_id}/enrollments")
    assert response.status_code == 404


def test_attach_and_list_labs():
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    lab = {
        "title": "K8s Rolling Update",
        "summary": "Deploy a rolling update to a blue/green pair.",
        "resource_type": "kubernetes",
        "resource_uri": "https://github.com/devops-with-brian/k8s-lab",
        "estimated_minutes": 45,
    }

    created_lab = client.post(f"/courses/{course_id}/labs", json=lab)
    assert created_lab.status_code == 201
    lab_data = created_lab.json()
    assert lab_data["title"] == lab["title"]
    assert lab_data["course_id"] == course_id

    labs = client.get(f"/courses/{course_id}/labs")
    assert labs.status_code == 200
    assert len(labs.json()) == 1
    assert labs.json()[0]["id"] == lab_data["id"]


def test_fetch_missing_course_returns_404():
    missing_id = uuid4()
    response = client.get(f"/courses/{missing_id}")
    assert response.status_code == 404
