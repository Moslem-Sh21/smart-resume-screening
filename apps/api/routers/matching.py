from fastapi import APIRouter

from apps.api.schemas import JobMatchRequest
from resume_screening.schemas.matching import JobMatchResult
from resume_screening.services.matcher import match_job

router = APIRouter(
    prefix="/matching",
    tags=["matching"],
)


@router.post(
    "/score",
    response_model=JobMatchResult,
)
def score_candidate_job(
    request: JobMatchRequest,
) -> JobMatchResult:
    return match_job(
        request.candidate,
        request.job,
    )
