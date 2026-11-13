from docling.exceptions import ConversionError
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routers import resumes

client = TestClient(app)


def test_parse_resume_returns_markdown(monkeypatch) -> None:
    def fake_parse(
        filename: str,
        content: bytes,
    ) -> str:
        assert filename == "resume.pdf"
        assert content == b"fake pdf content"

        return "# Jane Doe\n\n## Experience\n\nML Engineer"

    monkeypatch.setattr(
        resumes,
        "parse_resume_to_markdown",
        fake_parse,
    )

    response = client.post(
        "/resumes/parse",
        files={
            "file": (
                "resume.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "resume.pdf",
        "markdown": "# Jane Doe\n\n## Experience\n\nML Engineer",
    }


def test_parse_resume_returns_400_when_docling_fails(
    monkeypatch,
) -> None:
    def fake_parse(
        _filename: str,
        _content: bytes,
    ) -> str:
        raise ConversionError("test conversion failure")

    monkeypatch.setattr(
        resumes,
        "parse_resume_to_markdown",
        fake_parse,
    )

    response = client.post(
        "/resumes/parse",
        files={
            "file": (
                "resume.pdf",
                b"corrupted pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Resume could not be parsed.",
    }
