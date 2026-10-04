from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.exception_handlers import invalid_file_exception_handler
from resume_screening.exceptions import InvalidFileError

app_under_test = FastAPI()

app_under_test.add_exception_handler(
    InvalidFileError,
    invalid_file_exception_handler,
)


@app_under_test.get("/trigger-invalid-file")
def trigger_invalid_file() -> None:
    raise InvalidFileError("Unsupported file type '.exe'.")


client = TestClient(app_under_test)


def test_invalid_file_exception_handler() -> None:
    response = client.get("/trigger-invalid-file")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unsupported file type '.exe'."
    }