"""Integration tests for course update functionality."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def build_course_payload(**overrides):
    """Build a valid course payload with optional overrides."""
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


def test_update_course_title():
    """Test updating just the course title."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json={"title": "Updated Course Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Course Title"
    # Verify other fields unchanged
    assert response.json()["instructor"] == "Brian T"


def test_update_course_status():
    """Test updating course status."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json={"status": "archived"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "archived"


def test_update_multiple_fields():
    """Test updating multiple course fields at once."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json={
            "title": "New Title",
            "difficulty": "advanced",
            "tags": ["updated", "tags"],
            "duration_minutes": 180,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["difficulty"] == "advanced"
    assert data["tags"] == ["updated", "tags"]
    assert data["duration_minutes"] == 180


def test_update_course_tags():
    """Test updating course tags."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json={"tags": ["python", "docker", "kubernetes"]},
    )
    assert response.status_code == 200
    assert response.json()["tags"] == ["python", "docker", "kubernetes"]


def test_update_course_supplemental_urls():
    """Test updating supplemental URLs."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json={
            "supplemental_urls": [
                "https://docs.example.com",
                "https://github.com/example",
            ]
        },
    )
    assert response.status_code == 200
    assert len(response.json()["supplemental_urls"]) == 2


def test_update_course_prerequisites():
    """Test updating course prerequisites."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json={"prerequisites": ["Python basics", "CLI experience"]},
    )
    assert response.status_code == 200
    assert response.json()["prerequisites"] == ["Python basics", "CLI experience"]


def test_update_course_overview():
    """Test updating course overview."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    new_overview = "This is a completely new overview describing the course content."
    response = client.patch(
        f"/courses/{course_id}",
        json={"overview": new_overview},
    )
    assert response.status_code == 200
    assert response.json()["overview"] == new_overview


def test_update_course_category():
    """Test updating course category."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json={"category": "Cloud Engineering"},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "Cloud Engineering"


def test_update_preserves_enrollments_and_labs():
    """Test that updating a course doesn't affect its enrollments and labs."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Add enrollment and lab
    client.post(
        f"/courses/{course_id}/enrollments",
        json={"name": "Test User", "email": "test@example.com"},
    )
    client.post(
        f"/courses/{course_id}/labs",
        json={
            "title": "Test Lab",
            "resource_type": "kubernetes",
            "resource_uri": "https://example.com/lab",
        },
    )

    # Update the course
    response = client.patch(
        f"/courses/{course_id}",
        json={"title": "Updated Title"},
    )
    assert response.status_code == 200

    # Verify counts are preserved
    assert response.json()["enrollment_count"] == 1
    assert response.json()["lab_count"] == 1


def test_update_to_draft_status():
    """Test updating published course back to draft."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json={"status": "draft"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "draft"


def test_update_difficulty_levels():
    """Test updating to different difficulty levels."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    for difficulty in ["beginner", "intermediate", "advanced"]:
        response = client.patch(
            f"/courses/{course_id}",
            json={"difficulty": difficulty},
        )
        assert response.status_code == 200
        assert response.json()["difficulty"] == difficulty
