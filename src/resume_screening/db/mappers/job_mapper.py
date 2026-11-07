from typing import cast

from resume_screening.db.models import Job
from resume_screening.db.models import JobRequirement as JobRequirementModel
from resume_screening.schemas.job import (
    JobProfile,
    RequirementCategory,
    RequirementImportance,
)
from resume_screening.schemas.job import JobRequirement as JobRequirementSchema


def job_profile_to_orm(profile: JobProfile) -> Job:
    return Job(
        job_id=profile.job_id,
        title=profile.title,
        requirements=[
            JobRequirementModel(
                requirement_id=requirement.requirement_id,
                description=requirement.description,
                category=requirement.category,
                importance=requirement.importance,
                normalized_skills=list(requirement.normalized_skills),
                minimum_years=requirement.minimum_years,
            )
            for requirement in profile.requirements
        ],
    )


def job_orm_to_profile(job: Job) -> JobProfile:
    return JobProfile(
        job_id=job.job_id,
        title=job.title,
        requirements=[
            JobRequirementSchema(
                requirement_id=requirement.requirement_id,
                description=requirement.description,
                category=cast(
                    RequirementCategory,
                    requirement.category,
                ),
                importance=cast(
                    RequirementImportance,
                    requirement.importance,
                ),
                normalized_skills=list(requirement.normalized_skills),
                minimum_years=requirement.minimum_years,
            )
            for requirement in job.requirements
        ],
    )
