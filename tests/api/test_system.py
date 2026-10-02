from fastapi.testclient import TestClient

from apps.api.main import app
from resume_screening import __version__

client = TestClient(app)


def test_version() -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": __version__}