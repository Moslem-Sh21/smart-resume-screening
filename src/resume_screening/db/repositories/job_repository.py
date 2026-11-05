from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from resume_screening.db.models import Job


class JobRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, job: Job) -> Job:
        self._session.add(job)
        self._session.flush()
        return job

    def get_by_job_id(self, job_id: str) -> Job | None:
        statement = (
            select(Job)
            .options(selectinload(Job.requirements))
            .where(Job.job_id == job_id)
        )

        return self._session.scalar(statement)