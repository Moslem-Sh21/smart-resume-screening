from fastapi import APIRouter

from apps.api.schemas import VersionResponse
from resume_screening import __version__

router = APIRouter(
    tags=["system"],
)


@router.get("/version", response_model=VersionResponse)
def get_version() -> VersionResponse:
    return VersionResponse(version=__version__)