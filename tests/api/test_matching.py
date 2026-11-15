from fastapi.testclient import TestClient

from apps.api.main import app


def test_score_candidate_job_returns_match_result() -> None:
    payload = {
        "candidate": {
            "candidate_id": "candidate-001",
            "skills": [
                "Python",
                "Docker",
            ],
        },
        "job": {
            "job_id": "job-001",
            "title": "ML Engineer",
            "requirements": [
                {
                    "requirement_id": "req-001",
                    "description": "Python and AWS required.",
                    "category": "skill",
                    "importance": "required",
                    "normalized_skills": [
                        "Python",
                        "AWS",
                    ],
                    "minimum_years": None,
                },
                {
                    "requirement_id": "req-002",
                    "description": "Docker preferred.",
                    "category": "skill",
                    "importance": "preferred",
                    "normalized_skills": [
                        "Docker",
                    ],
                    "minimum_years": None,
                },
            ],
        },
    }

    with TestClient(app) as client:
        response = client.post(
            "/matching/score",
            json=payload,
        )

    assert response.status_code == 200

    result = response.json()

    assert result["candidate_id"] == "candidate-001"
    assert result["job_id"] == "job-001"

    assert result["required_score"] == 0.5
    assert result["preferred_score"] == 1.0
    assert result["overall_score"] == 0.5

    assert result["assessed_requirements"] == 2
    assert result["unknown_requirements"] == 0

    assert len(
        result["requirement_matches"]
    ) == 2


def test_score_candidate_job_validates_request() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/matching/score",
            json={
                "candidate": {
                    "candidate_id": "candidate-001",
                }
            },
        )

    assert response.status_code == 422
