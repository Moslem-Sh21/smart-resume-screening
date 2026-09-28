from typing import Literal

from pydantic import BaseModel, Field

RequirementCategory = Literal[
    "skill",
    "experience",
    "education",
    "certification",
    "other",
]

RequirementImportance = Literal[
    "required",
    "preferred",
]


class JobRequirement(BaseModel):
    requirement_id: str = Field(min_length=1)
    description: str = Field(min_length=1)

    category: RequirementCategory
    importance: RequirementImportance

    normalized_skills: list[str] = Field(default_factory=list)

    minimum_years: float | None = Field(
        default=None,
        ge=0,
        le=60,
    )


class JobProfile(BaseModel):
    job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)

    requirements: list[JobRequirement] = Field(default_factory=list)
