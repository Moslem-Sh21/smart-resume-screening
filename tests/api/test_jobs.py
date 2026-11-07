from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db_session
from apps.api.main import app
from resume_screening.db.models import Job, JobRequirement


@contextmanager
def client_with_session(session: Session) -> Iterator[TestClient]:
    def override_db_session() -> Session:
        return session

    app.dependency_overrides[get_db_session] = override_db_session

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_create_job_returns_201() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None

    payload = {
        "job_id": "JOB-001",
        "title": "Machine Learning Scientist",
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "description": "Strong Python skills",
                "category": "skill",
                "importance": "required",
                "normalized_skills": ["python"],
                "minimum_years": 3.0,
            }
        ],
    }

    with client_with_session(session) as client:
        response = client.post("/jobs", json=payload)

    assert response.status_code == 201
    assert response.json() == payload

    session.add.assert_called_once()
    session.flush.assert_called_once()
    session.commit.assert_called_once()


def test_create_duplicate_job_returns_409() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = Job(
        job_id="JOB-001",
        title="Existing Job",
    )

    with client_with_session(session) as client:
        response = client.post(
            "/jobs",
            json={
                "job_id": "JOB-001",
                "title": "Machine Learning Scientist",
                "requirements": [],
            },
        )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Job 'JOB-001' already exists.",
    }

    session.commit.assert_not_called()


def test_get_job_returns_200() -> None:
    session = MagicMock(spec=Session)

    job = Job(
        job_id="JOB-001",
        title="Machine Learning Scientist",
        requirements=[
            JobRequirement(
                requirement_id="REQ-001",
                description="Strong Python skills",
                category="skill",
                importance="required",
                normalized_skills=["python"],
                minimum_years=3.0,
            )
        ],
    )

    session.scalar.return_value = job

    with client_with_session(session) as client:
        response = client.get("/jobs/JOB-001")

    assert response.status_code == 200
    assert response.json() == {
        "job_id": "JOB-001",
        "title": "Machine Learning Scientist",
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "description": "Strong Python skills",
                "category": "skill",
                "importance": "required",
                "normalized_skills": ["python"],
                "minimum_years": 3.0,
            }
        ],
    }


def test_get_missing_job_returns_404() -> None:
    session = MagicMock(spec=Session)
    session.scalar.return_value = None

    with client_with_session(session) as client:
        response = client.get("/jobs/UNKNOWN")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Job 'UNKNOWN' was not found.",
    }
