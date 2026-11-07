from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db_session
from resume_screening.db.mappers.job_mapper import (
    job_orm_to_profile,
    job_profile_to_orm,
)
from resume_screening.db.repositories.job_repository import JobRepository
from resume_screening.schemas.job import JobProfile

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


@router.post(
    "",
    response_model=JobProfile,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    profile: JobProfile,
    session: DatabaseSession,
) -> JobProfile:
    repository = JobRepository(session)

    existing_job = repository.get_by_job_id(profile.job_id)

    if existing_job is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job '{profile.job_id}' already exists.",
        )

    job = job_profile_to_orm(profile)

    try:
        repository.add(job)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job '{profile.job_id}' already exists.",
        ) from None

    return job_orm_to_profile(job)


@router.get(
    "/{job_id}",
    response_model=JobProfile,
)
def get_job(
    job_id: str,
    session: DatabaseSession,
) -> JobProfile:
    repository = JobRepository(session)

    job = repository.get_by_job_id(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' was not found.",
        )

    return job_orm_to_profile(job)
