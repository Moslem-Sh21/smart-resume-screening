from typing import Annotated

from docling.exceptions import ConversionError
from fastapi import APIRouter, File, Form, UploadFile
from starlette.concurrency import run_in_threadpool

from apps.api.schemas import (
    ResumeExtractResponse,
    ResumeParseResponse,
    ResumeValidationResponse,
)
from resume_screening.exceptions import InvalidFileError
from resume_screening.services.candidate_extractor import (
    extract_candidate_profile,
)
from resume_screening.services.file_validation import (
    validate_content_type,
    validate_file_extension,
    validate_file_size,
)
from resume_screening.services.resume_parser import (
    parse_resume_to_markdown,
)

router = APIRouter(
    prefix="/resumes",
    tags=["resumes"],
)


@router.post(
    "/validate",
    response_model=ResumeValidationResponse,
)
async def validate_resume_file(
    file: Annotated[UploadFile, File()],
) -> ResumeValidationResponse:
    if file.filename is None:
        raise InvalidFileError(
            "Uploaded file must have a filename."
        )

    validate_file_extension(file.filename)
    validate_content_type(file.content_type)

    if file.size is None:
        raise InvalidFileError(
            "Uploaded file size could not be determined."
        )

    validate_file_size(file.size)

    return ResumeValidationResponse(
        filename=file.filename,
        status="valid",
    )


@router.post(
    "/parse",
    response_model=ResumeParseResponse,
)
async def parse_resume_file(
    file: Annotated[UploadFile, File()],
) -> ResumeParseResponse:
    if file.filename is None:
        raise InvalidFileError(
            "Uploaded file must have a filename."
        )

    validate_file_extension(file.filename)
    validate_content_type(file.content_type)

    if file.size is None:
        raise InvalidFileError(
            "Uploaded file size could not be determined."
        )

    validate_file_size(file.size)

    content = await file.read()

    try:
        markdown = await run_in_threadpool(
            parse_resume_to_markdown,
            file.filename,
            content,
        )
    except ConversionError as exc:
        raise InvalidFileError(
            "Resume could not be parsed."
        ) from exc

    return ResumeParseResponse(
        filename=file.filename,
        markdown=markdown,
    )


@router.post(
    "/extract",
    response_model=ResumeExtractResponse,
)
async def extract_resume_candidate(
    candidate_id: Annotated[str, Form(min_length=1)],
    file: Annotated[UploadFile, File()],
) -> ResumeExtractResponse:
    if file.filename is None:
        raise InvalidFileError(
            "Uploaded file must have a filename."
        )

    validate_file_extension(file.filename)
    validate_content_type(file.content_type)

    if file.size is None:
        raise InvalidFileError(
            "Uploaded file size could not be determined."
        )

    validate_file_size(file.size)

    content = await file.read()

    try:
        markdown = await run_in_threadpool(
            parse_resume_to_markdown,
            file.filename,
            content,
        )
    except ConversionError as exc:
        raise InvalidFileError(
            "Resume could not be parsed."
        ) from exc

    candidate = extract_candidate_profile(
        candidate_id=candidate_id,
        markdown=markdown,
    )

    return ResumeExtractResponse(
        filename=file.filename,
        candidate=candidate,
    )
