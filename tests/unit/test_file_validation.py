import pytest

from resume_screening.config import get_settings
from resume_screening.exceptions import InvalidFileError
from resume_screening.services.file_validation import (
    validate_file_extension,
    validate_file_size,
)


def test_accepts_pdf() -> None:
    validate_file_extension("resume.pdf")


def test_accepts_docx_case_insensitive() -> None:
    validate_file_extension("resume.DOCX")


def test_rejects_unsupported_extension() -> None:
    with pytest.raises(
        InvalidFileError,
        match="Unsupported file type",
    ):
        validate_file_extension("resume.exe")

def test_rejects_file_without_extension() -> None:
    with pytest.raises(
        InvalidFileError,
        match="File must have an extension",
    ):
        validate_file_extension("resume")

def test_accepts_file_within_size_limit() -> None:
    settings = get_settings()
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    validate_file_size(max_size_bytes)


def test_rejects_file_over_size_limit() -> None:
    settings = get_settings()
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    with pytest.raises(
        InvalidFileError,
        match="File exceeds the maximum size",
    ):
        validate_file_size(max_size_bytes + 1)