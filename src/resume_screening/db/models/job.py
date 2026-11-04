from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resume_screening.db.base import Base

if TYPE_CHECKING:
    from resume_screening.db.models.job_requirement import JobRequirement


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    job_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    requirements: Mapped[list[JobRequirement]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )