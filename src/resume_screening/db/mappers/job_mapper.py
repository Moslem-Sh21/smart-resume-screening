from resume_screening.db.models import Job, JobRequirement
from resume_screening.schemas.job import JobProfile


def job_profile_to_orm(profile: JobProfile) -> Job:
    return Job(
        job_id=profile.job_id,
        title=profile.title,
        requirements=[
            JobRequirement(
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