from pydantic import BaseModel, Field

from resume_screening.schemas import (
    CandidateProfile,
    JobProfile,
)


class HealthResponse(BaseModel):
    status: str


class VersionResponse(BaseModel):
    version: str


class ResumeValidationResponse(BaseModel):
    filename: str
    status: str


class ResumeParseResponse(BaseModel):
    filename: str
    markdown: str


class ResumeExtractResponse(BaseModel):
    filename: str
    candidate: CandidateProfile



class JobExtractRequest(BaseModel):
    job_id: str = Field(min_length=1)
    job_description: str = Field(min_length=1)
    title: str | None = None



class JobMatchRequest(BaseModel):
    candidate: CandidateProfile
    job: JobProfile
