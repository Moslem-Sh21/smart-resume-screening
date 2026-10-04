from fastapi.testclient import TestClient

from apps.api.main import app

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