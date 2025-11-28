"""Integration tests for course and lab routes."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import build_course_payload

client = TestClient(app, raise_server_exceptions=False)


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
