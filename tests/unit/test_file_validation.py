import pytest

from resume_screening.exceptions import InvalidFileError
from resume_screening.services.file_validation import validate_file_extension


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