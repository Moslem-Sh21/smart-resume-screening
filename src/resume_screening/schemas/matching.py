from typing import Literal

from pydantic import BaseModel, Field

from resume_screening.schemas.job import (
    RequirementCategory,
    RequirementImportance,
)

RequirementMatchStatus = Literal[
    "matched",
    "partial",
    "not_matched",
    "unknown",
]

DegreeLevel = Literal[
    "diploma",
    "associate",
    "bachelor",
    "master",
    "doctorate",
]


class RequirementMatch(BaseModel):
    requirement_id: str = Field(min_length=1)

    category: RequirementCategory
    importance: RequirementImportance
    status: RequirementMatchStatus

    score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    matched_skills: list[str] = Field(
        default_factory=list
    )
    not_observed_skills: list[str] = Field(
        default_factory=list
    )

    matched_certifications: list[str] = Field(
        default_factory=list
    )

    minimum_years: float | None = Field(
        default=None,
        ge=0,
        le=60,
    )
    observed_years: float | None = Field(
        default=None,
        ge=0,
        le=60,
    )

    required_degree_level: DegreeLevel | None = None
    observed_degree_level: DegreeLevel | None = None

    evidence_ids: list[str] = Field(
        default_factory=list
    )


class JobMatchResult(BaseModel):
    candidate_id: str = Field(min_length=1)
    job_id: str = Field(min_length=1)

    overall_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    required_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    preferred_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    assessed_requirements: int = Field(
        default=0,
        ge=0,
    )
    unknown_requirements: int = Field(
        default=0,
        ge=0,
    )

    requirement_matches: list[
        RequirementMatch
    ] = Field(default_factory=list)
