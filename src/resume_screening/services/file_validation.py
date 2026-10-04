from pathlib import Path

from resume_screening.config import get_settings
from resume_screening.exceptions import InvalidFileError


def validate_file_extension(filename: str) -> None:
    settings = get_settings()

    extension = Path(filename).suffix.lower().lstrip(".")

    if not extension:
        raise InvalidFileError("File must have an extension.")

    if extension not in settings.allowed_file_extensions:
        allowed = ", ".join(sorted(settings.allowed_file_extensions))
        raise InvalidFileError(
            f"Unsupported file type '.{extension}'. Allowed types: {allowed}."
        )

def validate_file_size(size_bytes: int) -> None:
    settings = get_settings()

    if size_bytes <= 0:
        raise InvalidFileError("Uploaded file is empty.")

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if size_bytes > max_size_bytes:
        raise InvalidFileError(
            f"File exceeds the maximum size of {settings.max_upload_size_mb} MB."
        )

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def validate_content_type(content_type: str | None) -> None:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise InvalidFileError(
            f"Unsupported content type '{content_type}'."
        )