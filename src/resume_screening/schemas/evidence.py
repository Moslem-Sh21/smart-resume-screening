from pydantic import BaseModel, Field


class CandidateEvidence(BaseModel):
    evidence_id: str = Field(min_length=1)
    section: str = Field(min_length=1)
    text: str = Field(min_length=1)
    page: int | None = Field(default=None, ge=1)
