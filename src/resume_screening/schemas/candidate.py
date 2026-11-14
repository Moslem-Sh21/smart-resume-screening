from pydantic import BaseModel, Field

from resume_screening.schemas.evidence import CandidateEvidence


class CandidateIdentity(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    links: list[str] = Field(default_factory=list)


class CandidateExperience(BaseModel):
    title: str = Field(min_length=1)
    company: str | None = None
    date_range: str | None = None
    years: float | None = Field(default=None, ge=0, le=60)
    skills: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class CandidateEducation(BaseModel):
    degree: str = Field(min_length=1)
    field_of_study: str | None = None
    institution: str | None = None
    date_range: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    candidate_id: str = Field(min_length=1)

    identity: CandidateIdentity = Field(default_factory=CandidateIdentity)

    skills: list[str] = Field(default_factory=list)
    experiences: list[CandidateExperience] = Field(default_factory=list)
    education: list[CandidateEducation] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

    evidence: list[CandidateEvidence] = Field(default_factory=list)
