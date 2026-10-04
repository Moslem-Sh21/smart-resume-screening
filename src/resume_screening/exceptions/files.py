from resume_screening.exceptions.base import ResumeScreeningError


class InvalidFileError(ResumeScreeningError):
    """Raised when an uploaded file is invalid or unsupported."""