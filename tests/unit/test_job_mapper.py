from resume_screening.db.mappers.job_mapper import job_profile_to_orm
from resume_screening.schemas.job import JobProfile, JobRequirement


def test_job_profile_to_orm_maps_job_and_requirements() -> None:
    profile = JobProfile(
        job_id="JOB-001",
        title="Machine Learning Scientist",
        requirements=[
            JobRequirement(
                requirement_id="REQ-001",
                description="Strong Python skills",
                category="skill",
                importance="required",
                normalized_skills=["python"],
                minimum_years=3,
            ),
            JobRequirement(
                requirement_id="REQ-002",
                description="Experience with machine learning",
                category="experience",
                importance="preferred",
                normalized_skills=["machine learning"],
                minimum_years=2,
            ),
        ],
    )

    job = job_profile_to_orm(profile)

    assert job.job_id == "JOB-001"
    assert job.title == "Machine Learning Scientist"
    assert len(job.requirements) == 2

    first_requirement = job.requirements[0]

    assert first_requirement.requirement_id == "REQ-001"
    assert first_requirement.normalized_skills == ["python"]
    assert first_requirement.minimum_years == 3
    assert first_requirement.job is job
