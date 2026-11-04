from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resume_screening.db.base import Base

if TYPE_CHECKING:
    from resume_screening.db.models.job import Job


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)

    job_db_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
    )

    requirement_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    importance: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    normalized_skills: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    minimum_years: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    job: Mapped[Job] = relationship(
        back_populates="requirements",
    )