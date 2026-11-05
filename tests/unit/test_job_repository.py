from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from resume_screening.db.models import Job
from resume_screening.db.repositories.job_repository import JobRepository


def test_add_tracks_and_flushes_job() -> None:
    session = MagicMock(spec=Session)
    repository = JobRepository(session)

    job = Job(
        job_id="JOB-001",
        title="Machine Learning Scientist",
    )

    result = repository.add(job)

    session.add.assert_called_once_with(job)
    session.flush.assert_called_once_with()

    assert result is job


def test_get_by_job_id_returns_job() -> None:
    session = MagicMock(spec=Session)
    repository = JobRepository(session)

    job = Job(
        job_id="JOB-001",
        title="Machine Learning Scientist",
    )

    session.scalar.return_value = job

    result = repository.get_by_job_id("JOB-001")

    session.scalar.assert_called_once()

    assert result is job