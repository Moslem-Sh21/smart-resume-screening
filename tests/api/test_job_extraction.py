from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_extract_job_returns_structured_profile() -> None:
    response = client.post(
        "/jobs/extract",
        json={
            "job_id": "job-001",
            "job_description": """
# Machine Learning Engineer

## Required Qualifications

- 3+ years of experience building machine learning systems.
- Strong Python and SQL skills.
- Bachelor's degree in Computer Science.

## Preferred Qualifications

- Experience with AWS and Docker.
- Familiarity with Retrieval-Augmented Generation.
""",
        },
    )

    assert response.status_code == 200

    profile = response.json()

    assert profile["job_id"] == "job-001"
    assert profile["title"] == "Machine Learning Engineer"

    assert len(profile["requirements"]) == 5

    experience = profile["requirements"][0]

    assert experience["importance"] == "required"
    assert experience["category"] == "experience"
    assert experience["minimum_years"] == 3.0

    skill = profile["requirements"][1]

    assert skill["importance"] == "required"
    assert skill["category"] == "skill"
    assert skill["normalized_skills"] == [
        "Python",
        "SQL",
    ]

    cloud = profile["requirements"][3]

    assert cloud["importance"] == "preferred"
    assert cloud["normalized_skills"] == [
        "AWS",
        "Docker",
    ]

    rag = profile["requirements"][4]

    assert rag["normalized_skills"] == [
        "Retrieval-Augmented Generation",
    ]

    for requirement in profile["requirements"]:
        assert requirement["requirement_id"].startswith(
            "req-"
        )


def test_extract_job_accepts_explicit_title() -> None:
    response = client.post(
        "/jobs/extract",
        json={
            "job_id": "job-002",
            "title": "Data Scientist",
            "job_description": """
Required Qualifications

- Strong Python skills.
""",
        },
    )

    assert response.status_code == 200

    profile = response.json()

    assert profile["title"] == "Data Scientist"


def test_extract_job_returns_400_when_title_is_unknown() -> None:
    response = client.post(
        "/jobs/extract",
        json={
            "job_id": "job-003",
            "job_description": """
Required Qualifications

- Strong Python skills.
""",
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Job title could not be determined."
    }


def test_extract_job_requires_description() -> None:
    response = client.post(
        "/jobs/extract",
        json={
            "job_id": "job-004",
            "title": "Machine Learning Engineer",
        },
    )

    assert response.status_code == 422
