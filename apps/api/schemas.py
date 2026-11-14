from pydantic import BaseModel

from resume_screening.schemas import CandidateProfile


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
