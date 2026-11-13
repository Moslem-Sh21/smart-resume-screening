from pydantic import BaseModel


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
