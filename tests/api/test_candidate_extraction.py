from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routers import resumes

client = TestClient(app)


def test_extract_resume_returns_candidate_profile(
    monkeypatch,
) -> None:
    def fake_parse(
        filename: str,
        content: bytes,
    ) -> str:
        assert filename == "resume.pdf"
        assert content == b"fake pdf content"

        return """
## SUMMARY

## Jane Doe

Toronto, ON | jane@example.com | (613) 555-1234

## TECHNICAL SKILLS

Programming & Data: Python, SQL

Frameworks: PyTorch

## PROFESSIONAL EXPERIENCE

ML Engineer | Example Corp | Toronto, ON | Jan 2024 - Present

- Built ML evaluation pipelines.

## EDUCATION

Ph.D. in Computer Engineering | Example University | May 2021 - Jul 2026

## CERTIFICATIONS

- AWS Certified Machine Learning
"""

    monkeypatch.setattr(
        resumes,
        "parse_resume_to_markdown",
        fake_parse,
    )

    response = client.post(
        "/resumes/extract",
        data={
            "candidate_id": "candidate-001",
        },
        files={
            "file": (
                "resume.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["filename"] == "resume.pdf"

    candidate = body["candidate"]

    assert candidate["candidate_id"] == "candidate-001"
    assert candidate["identity"]["name"] == "Jane Doe"
    assert candidate["identity"]["email"] == "jane@example.com"

    assert candidate["skills"] == [
        "Python",
        "SQL",
        "PyTorch",
    ]

    assert candidate["experiences"][0]["title"] == "ML Engineer"
    assert candidate["experiences"][0]["company"] == "Example Corp"

    assert candidate["education"][0]["degree"] == "Ph.D."

    assert candidate["certifications"] == [
        "AWS Certified Machine Learning",
    ]


def test_extract_resume_requires_candidate_id() -> None:
    response = client.post(
        "/resumes/extract",
        files={
            "file": (
                "resume.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
