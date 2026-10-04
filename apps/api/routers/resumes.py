from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from apps.api.schemas import ResumeValidationResponse
from resume_screening.exceptions import InvalidFileError
from resume_screening.services.file_validation import validate_file_extension

router = APIRouter(
    prefix="/resumes",
    tags=["resumes"],
)


@router.post("/validate", response_model=ResumeValidationResponse)
async def validate_resume_file(
    file: Annotated[UploadFile, File()],
) -> ResumeValidationResponse:
    if file.filename is None:
        raise InvalidFileError("Uploaded file must have a filename.")

    validate_file_extension(file.filename)

    return ResumeValidationResponse(
        filename=file.filename,
        status="valid",
    )