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