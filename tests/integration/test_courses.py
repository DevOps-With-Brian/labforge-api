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


def test_update_course_with_empty_payload():
    """Test that updating a course with empty payload returns unchanged course."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]
    original = client.get(f"/courses/{course_id}").json()

    updated = client.patch(f"/courses/{course_id}", json={})
    assert updated.status_code == 200

    # Verify course is unchanged except for updated_at
    updated_data = updated.json()
    assert updated_data["title"] == original["title"]
    assert updated_data["overview"] == original["overview"]
    assert updated_data["instructor"] == original["instructor"]
    assert updated_data["status"] == original["status"]
    assert updated_data["tags"] == original["tags"]
    assert updated_data["duration_minutes"] == original["duration_minutes"]


def test_update_course_partial_update_only_changes_specified_fields():
    """Test that PATCH only updates specified fields, leaving others unchanged."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]
    original = client.get(f"/courses/{course_id}").json()

    # Update only the title
    updated = client.patch(f"/courses/{course_id}", json={"title": "New Title Here"})
    assert updated.status_code == 200

    updated_data = updated.json()
    # Title should be updated
    assert updated_data["title"] == "New Title Here"

    # All other fields should remain unchanged
    assert updated_data["overview"] == original["overview"]
    assert updated_data["instructor"] == original["instructor"]
    assert updated_data["status"] == original["status"]
    assert updated_data["tags"] == original["tags"]
    assert updated_data["prerequisites"] == original["prerequisites"]
    assert updated_data["duration_minutes"] == original["duration_minutes"]
    assert updated_data["difficulty"] == original["difficulty"]
    assert updated_data["category"] == original["category"]
    assert updated_data["primary_video_url"] == original["primary_video_url"]
    assert updated_data["supplemental_urls"] == original["supplemental_urls"]


def test_update_course_with_invalid_title_too_short():
    """Test that updating with a title that is too short returns 422."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    updated = client.patch(f"/courses/{course_id}", json={"title": "AB"})
    assert updated.status_code == 422


def test_update_course_with_invalid_title_too_long():
    """Test that updating with a title that is too long returns 422."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    updated = client.patch(f"/courses/{course_id}", json={"title": "A" * 141})
    assert updated.status_code == 422


def test_update_course_with_invalid_difficulty():
    """Test that updating with invalid difficulty returns 422."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    updated = client.patch(f"/courses/{course_id}", json={"difficulty": "expert"})
    assert updated.status_code == 422


def test_update_course_with_invalid_duration():
    """Test that updating with invalid duration returns 422."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Test zero duration
    updated = client.patch(f"/courses/{course_id}", json={"duration_minutes": 0})
    assert updated.status_code == 422

    # Test negative duration
    updated = client.patch(f"/courses/{course_id}", json={"duration_minutes": -5})
    assert updated.status_code == 422


def test_update_course_with_invalid_status():
    """Test that updating with invalid status returns 422."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    updated = client.patch(f"/courses/{course_id}", json={"status": "invalid_status"})
    assert updated.status_code == 422


def test_update_course_with_invalid_instructor():
    """Test that updating with a single character instructor returns 422."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    updated = client.patch(f"/courses/{course_id}", json={"instructor": "A"})
    assert updated.status_code == 422


def test_update_course_nonexistent_returns_404():
    """Test that updating a non-existent course returns 404."""
    nonexistent_id = uuid4()
    updated = client.patch(
        f"/courses/{nonexistent_id}", json={"title": "Updated Title"}
    )
    assert updated.status_code == 404


def test_update_course_multiple_fields():
    """Test updating multiple fields at once."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]
    original = client.get(f"/courses/{course_id}").json()

    update_payload = {
        "title": "Updated Course Title",
        "overview": "Updated overview content.",
        "instructor": "Jane Doe",
        "difficulty": "advanced",
        "status": "draft",
    }

    updated = client.patch(f"/courses/{course_id}", json=update_payload)
    assert updated.status_code == 200

    updated_data = updated.json()
    # Updated fields should reflect new values
    assert updated_data["title"] == "Updated Course Title"
    assert updated_data["overview"] == "Updated overview content."
    assert updated_data["instructor"] == "Jane Doe"
    assert updated_data["difficulty"] == "advanced"
    assert updated_data["status"] == "draft"

    # Unchanged fields should remain the same
    assert updated_data["tags"] == original["tags"]
    assert updated_data["prerequisites"] == original["prerequisites"]
    assert updated_data["duration_minutes"] == original["duration_minutes"]
    assert updated_data["category"] == original["category"]


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
