import pytest
from pydantic import ValidationError

from resume_screening.schemas.matching import (
    JobMatchResult,
    RequirementMatch,
)


def test_requirement_match_supports_matched_skills() -> None:
    match = RequirementMatch(
        requirement_id="req-001",
        category="skill",
        importance="required",
        status="partial",
        score=0.5,
        matched_skills=["Python"],
        not_observed_skills=["AWS"],
    )

    assert match.score == 0.5
    assert match.matched_skills == ["Python"]
    assert match.not_observed_skills == ["AWS"]


def test_requirement_match_can_be_unknown() -> None:
    match = RequirementMatch(
        requirement_id="req-002",
        category="experience",
        importance="required",
        status="unknown",
        minimum_years=5,
    )

    assert match.score is None
    assert match.observed_years is None


def test_job_match_result_tracks_assessed_and_unknown() -> None:
    result = JobMatchResult(
        candidate_id="candidate-001",
        job_id="job-001",
        overall_score=0.75,
        required_score=0.8,
        preferred_score=0.5,
        assessed_requirements=3,
        unknown_requirements=1,
    )

    assert result.overall_score == 0.75
    assert result.assessed_requirements == 3
    assert result.unknown_requirements == 1


def test_match_score_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValidationError):
        RequirementMatch(
            requirement_id="req-003",
            category="skill",
            importance="required",
            status="matched",
            score=1.5,
        )
