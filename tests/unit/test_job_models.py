from sqlalchemy import inspect

from resume_screening.db.base import Base
from resume_screening.db.models import Job, JobRequirement


def test_job_tables_are_registered() -> None:
    assert "jobs" in Base.metadata.tables
    assert "job_requirements" in Base.metadata.tables


def test_job_primary_key_and_columns() -> None:
    mapper = inspect(Job)
    table = mapper.local_table

    assert [column.name for column in mapper.primary_key] == ["id"]

    assert "job_id" in table.columns
    assert "title" in table.columns

    assert table.columns["job_id"].nullable is False
    assert table.columns["job_id"].unique is True
    assert table.columns["title"].nullable is False


def test_job_requirement_foreign_key_points_to_job() -> None:
    table = inspect(JobRequirement).local_table

    foreign_keys = {
        str(foreign_key.column)
        for foreign_key in table.foreign_keys
    }

    assert foreign_keys == {"jobs.id"}


def test_job_requirement_relationship_is_bidirectional() -> None:
    job = Job(
        job_id="JOB-001",
        title="ML Scientist",
    )

    requirement = JobRequirement(
        requirement_id="REQ-001",
        description="Python experience",
        category="skill",
        importance="required",
        normalized_skills=["python"],
        minimum_years=3,
    )

    job.requirements.append(requirement)

    assert job.requirements == [requirement]
    assert requirement.job is job