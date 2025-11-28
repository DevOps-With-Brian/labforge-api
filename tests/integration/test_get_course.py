"""Integration tests for retrieving individual courses."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


from tests.conftest import build_course_payload


def test_get_course_with_no_enrollments_or_labs():
    """Test getting a course that has no enrollments or labs."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == course_id
    assert data["enrollment_count"] == 0
    assert data["lab_count"] == 0


def test_get_course_with_enrollments():
    """Test getting a course with enrollments shows correct count."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Add multiple enrollments
    for i in range(3):
        client.post(
            f"/courses/{course_id}/enrollments",
            json={"name": f"User {i}", "email": f"user{i}@example.com"},
        )

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["enrollment_count"] == 3
    assert response.json()["lab_count"] == 0


def test_get_course_with_labs():
    """Test getting a course with labs shows correct count."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Add multiple labs
    for i in range(2):
        client.post(
            f"/courses/{course_id}/labs",
            json={
                "title": f"Lab {i}",
                "resource_type": "kubernetes",
                "resource_uri": f"https://example.com/lab{i}",
            },
        )

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["enrollment_count"] == 0
    assert response.json()["lab_count"] == 2


def test_get_course_with_both_enrollments_and_labs():
    """Test getting a course with both enrollments and labs."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Add enrollments
    for i in range(5):
        client.post(
            f"/courses/{course_id}/enrollments",
            json={"name": f"User {i}", "email": f"user{i}@example.com"},
        )

    # Add labs
    for i in range(3):
        client.post(
            f"/courses/{course_id}/labs",
            json={
                "title": f"Lab {i}",
                "resource_type": "terraform",
                "resource_uri": f"https://example.com/lab{i}",
            },
        )

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["enrollment_count"] == 5
    assert response.json()["lab_count"] == 3


def test_get_course_returns_all_fields():
    """Test that getting a course returns all expected fields."""
    payload = build_course_payload(
        title="Complete Course",
        overview="Detailed overview",
        instructor="Jane Doe",
        category="DevOps",
        difficulty="advanced",
        tags=["tag1", "tag2"],
        prerequisites=["prereq1"],
        supplemental_urls=["https://example.com"],
    )
    course_id = client.post("/courses", json=payload).json()["id"]

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()

    # Verify all fields present
    assert data["id"] == course_id
    assert data["title"] == "Complete Course"
    assert data["overview"] == "Detailed overview"
    assert data["instructor"] == "Jane Doe"
    assert data["category"] == "DevOps"
    assert data["difficulty"] == "advanced"
    assert data["tags"] == ["tag1", "tag2"]
    assert data["prerequisites"] == ["prereq1"]
    # URLs may be normalized with trailing slash
    assert len(data["supplemental_urls"]) == 1
    assert "https://example.com" in data["supplemental_urls"][0]
    assert data["status"] == "published"
    assert data["duration_minutes"] == 120
    assert "created_at" in data
    assert "updated_at" in data
    assert "primary_video_url" in data


def test_get_course_after_update():
    """Test that getting a course after update returns updated values."""
    course_id = client.post("/courses", json=build_course_payload()).json()["id"]

    # Update the course
    client.patch(
        f"/courses/{course_id}",
        json={"title": "Updated Title", "status": "archived"},
    )

    # Get the course
    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "archived"


def test_get_draft_course():
    """Test getting a course with draft status."""
    course_id = client.post(
        "/courses",
        json=build_course_payload(status="draft"),
    ).json()["id"]

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "draft"


def test_get_archived_course():
    """Test getting a course with archived status."""
    course_id = client.post(
        "/courses",
        json=build_course_payload(status="archived"),
    ).json()["id"]

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "archived"
