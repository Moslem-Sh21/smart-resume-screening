from fastapi.testclient import TestClient

from apps.api.main import app
from resume_screening.config import get_settings

client = TestClient(app)


def test_validate_pdf_resume() -> None:
    response = client.post(
        "/resumes/validate",
        files={
            "file": (
                "resume.pdf",
                b"dummy pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "resume.pdf",
        "status": "valid",
    }


def test_reject_unsupported_resume_type() -> None:
    response = client.post(
        "/resumes/validate",
        files={
            "file": (
                "resume.txt",
                b"dummy text content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_reject_oversized_resume() -> None:
    settings = get_settings()

    oversized_content = b"x" * (
        settings.max_upload_size_mb * 1024 * 1024 + 1
    )

    response = client.post(
        "/resumes/validate",
        files={
            "file": (
                "resume.pdf",
                oversized_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "File exceeds the maximum size" in response.json()["detail"]

def test_reject_empty_resume() -> None:
    response = client.post(
        "/resumes/validate",
        files={
            "file": (
                "resume.pdf",
                b"",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "Uploaded file is empty" in response.json()["detail"]