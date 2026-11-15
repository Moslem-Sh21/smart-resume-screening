from resume_screening.schemas.candidate import (
    CandidateExperience,
    CandidateProfile,
)
from resume_screening.schemas.job import JobRequirement
from resume_screening.services.matcher import (
    match_requirement_skills,
)


def test_matches_all_required_skills() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=[
            "Python",
            "PyTorch",
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-001",
        description="Experience with Python and PyTorch.",
        category="skill",
        importance="required",
        normalized_skills=[
            "Python",
            "PyTorch",
        ],
    )

    result = match_requirement_skills(
        candidate,
        requirement,
    )

    assert result.status == "matched"
    assert result.score == 1.0
    assert result.matched_skills == [
        "Python",
        "PyTorch",
    ]
    assert result.not_observed_skills == []


def test_partial_skill_match() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=[
            "Python",
            "PyTorch",
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-002",
        description=(
            "Experience with Python, PyTorch, and AWS."
        ),
        category="skill",
        importance="required",
        normalized_skills=[
            "Python",
            "PyTorch",
            "AWS",
        ],
    )

    result = match_requirement_skills(
        candidate,
        requirement,
    )

    assert result.status == "partial"
    assert result.score == 2 / 3

    assert result.matched_skills == [
        "Python",
        "PyTorch",
    ]

    assert result.not_observed_skills == [
        "AWS",
    ]


def test_no_observed_skill_match() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=["Python"],
    )

    requirement = JobRequirement(
        requirement_id="req-003",
        description="Experience with AWS.",
        category="skill",
        importance="required",
        normalized_skills=["AWS"],
    )

    result = match_requirement_skills(
        candidate,
        requirement,
    )

    assert result.status == "not_matched"
    assert result.score == 0.0
    assert result.matched_skills == []
    assert result.not_observed_skills == [
        "AWS",
    ]


def test_requirement_without_normalized_skills_is_unknown() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=["Python"],
    )

    requirement = JobRequirement(
        requirement_id="req-004",
        description=(
            "Demonstrated research impact."
        ),
        category="other",
        importance="required",
    )

    result = match_requirement_skills(
        candidate,
        requirement,
    )

    assert result.status == "unknown"
    assert result.score is None


def test_experience_skills_and_evidence_are_used() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="ML Scientist",
                company="Example Bank",
                skills=[
                    "Python",
                    "PyTorch",
                ],
                evidence_ids=[
                    "ev-001",
                ],
            )
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-005",
        description="Experience using PyTorch.",
        category="skill",
        importance="required",
        normalized_skills=[
            "PyTorch",
        ],
    )

    result = match_requirement_skills(
        candidate,
        requirement,
    )

    assert result.status == "matched"
    assert result.score == 1.0
    assert result.evidence_ids == [
        "ev-001",
    ]


def test_matches_minimum_years_from_relevant_experiences() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="ML Scientist",
                years=3,
                skills=["Python"],
                evidence_ids=["ev-001"],
            ),
            CandidateExperience(
                title="Data Scientist",
                years=2,
                skills=["Python"],
                evidence_ids=["ev-002"],
            ),
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-years-001",
        description="5+ years of Python experience.",
        category="experience",
        importance="required",
        normalized_skills=["Python"],
        minimum_years=5,
    )

    from resume_screening.services.matcher import (
        match_requirement_years,
    )

    result = match_requirement_years(
        candidate,
        requirement,
    )

    assert result.status == "matched"
    assert result.score == 1.0
    assert result.observed_years == 5
    assert result.evidence_ids == [
        "ev-001",
        "ev-002",
    ]


def test_partial_years_match_when_duration_is_known() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="ML Scientist",
                years=3,
                skills=["Python"],
            )
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-years-002",
        description="5+ years of Python experience.",
        category="experience",
        importance="required",
        normalized_skills=["Python"],
        minimum_years=5,
    )

    from resume_screening.services.matcher import (
        match_requirement_years,
    )

    result = match_requirement_years(
        candidate,
        requirement,
    )

    assert result.status == "partial"
    assert result.score == 0.6
    assert result.observed_years == 3


def test_unknown_duration_is_not_treated_as_zero() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="ML Scientist",
                years=3,
                skills=["Python"],
            ),
            CandidateExperience(
                title="Research Scientist",
                years=None,
                skills=["Python"],
            ),
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-years-003",
        description="5+ years of Python experience.",
        category="experience",
        importance="required",
        normalized_skills=["Python"],
        minimum_years=5,
    )

    from resume_screening.services.matcher import (
        match_requirement_years,
    )

    result = match_requirement_years(
        candidate,
        requirement,
    )

    assert result.status == "unknown"
    assert result.score is None
    assert result.observed_years == 3


def test_irrelevant_experience_years_are_not_counted() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="Java Developer",
                years=6,
                skills=["Java"],
            ),
            CandidateExperience(
                title="ML Scientist",
                years=2,
                skills=["Python"],
            ),
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-years-004",
        description="5+ years of Python experience.",
        category="experience",
        importance="required",
        normalized_skills=["Python"],
        minimum_years=5,
    )

    from resume_screening.services.matcher import (
        match_requirement_years,
    )

    result = match_requirement_years(
        candidate,
        requirement,
    )

    assert result.status == "partial"
    assert result.score == 0.4
    assert result.observed_years == 2


def test_missing_year_information_is_unknown() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="ML Scientist",
                skills=["Python"],
            )
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-years-005",
        description="5+ years of Python experience.",
        category="experience",
        importance="required",
        normalized_skills=["Python"],
        minimum_years=5,
    )

    from resume_screening.services.matcher import (
        match_requirement_years,
    )

    result = match_requirement_years(
        candidate,
        requirement,
    )

    assert result.status == "unknown"
    assert result.score is None
    assert result.observed_years is None


def test_combines_skill_and_years_scores() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="ML Scientist",
                years=3,
                skills=["Python"],
                evidence_ids=["ev-001"],
            )
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-combined-001",
        description="5+ years of Python experience.",
        category="experience",
        importance="required",
        normalized_skills=["Python"],
        minimum_years=5,
    )

    from resume_screening.services.matcher import (
        match_requirement,
    )

    result = match_requirement(
        candidate,
        requirement,
    )

    assert result.status == "partial"
    assert result.score == 0.8
    assert result.matched_skills == ["Python"]
    assert result.observed_years == 3
    assert result.evidence_ids == ["ev-001"]


def test_unknown_years_do_not_zero_out_skill_match() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="ML Scientist",
                years=None,
                skills=["Python"],
                evidence_ids=["ev-001"],
            )
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-combined-002",
        description="5+ years of Python experience.",
        category="experience",
        importance="required",
        normalized_skills=["Python"],
        minimum_years=5,
    )

    from resume_screening.services.matcher import (
        match_requirement,
    )

    result = match_requirement(
        candidate,
        requirement,
    )

    assert result.status == "partial"
    assert result.score == 1.0
    assert result.matched_skills == ["Python"]
    assert result.observed_years is None


def test_combined_match_is_full_when_all_dimensions_match() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        experiences=[
            CandidateExperience(
                title="ML Scientist",
                years=5,
                skills=["Python"],
            )
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-combined-003",
        description="5+ years of Python experience.",
        category="experience",
        importance="required",
        normalized_skills=["Python"],
        minimum_years=5,
    )

    from resume_screening.services.matcher import (
        match_requirement,
    )

    result = match_requirement(
        candidate,
        requirement,
    )

    assert result.status == "matched"
    assert result.score == 1.0


def test_skill_only_requirement_uses_skill_score() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=["Python"],
    )

    requirement = JobRequirement(
        requirement_id="req-combined-004",
        description="Strong Python skills.",
        category="skill",
        importance="required",
        normalized_skills=["Python"],
    )

    from resume_screening.services.matcher import (
        match_requirement,
    )

    result = match_requirement(
        candidate,
        requirement,
    )

    assert result.status == "matched"
    assert result.score == 1.0


def test_requirement_without_assessable_fields_is_unknown() -> None:
    candidate = CandidateProfile(
        candidate_id="candidate-001",
    )

    requirement = JobRequirement(
        requirement_id="req-combined-005",
        description="Demonstrated research impact.",
        category="other",
        importance="required",
    )

    from resume_screening.services.matcher import (
        match_requirement,
    )

    result = match_requirement(
        candidate,
        requirement,
    )

    assert result.status == "unknown"
    assert result.score is None


def test_match_job_aggregates_required_requirements() -> None:
    from resume_screening.schemas.job import JobProfile
    from resume_screening.services.matcher import (
        match_job,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=[
            "Python",
            "PyTorch",
        ],
    )

    job = JobProfile(
        job_id="job-001",
        title="ML Scientist",
        requirements=[
            JobRequirement(
                requirement_id="req-job-001",
                description="Python required.",
                category="skill",
                importance="required",
                normalized_skills=["Python"],
            ),
            JobRequirement(
                requirement_id="req-job-002",
                description="AWS required.",
                category="skill",
                importance="required",
                normalized_skills=["AWS"],
            ),
        ],
    )

    result = match_job(
        candidate,
        job,
    )

    assert result.required_score == 0.5
    assert result.overall_score == 0.5
    assert result.assessed_requirements == 2
    assert result.unknown_requirements == 0


def test_preferred_score_does_not_override_required_score() -> None:
    from resume_screening.schemas.job import JobProfile
    from resume_screening.services.matcher import (
        match_job,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=[
            "Python",
            "Docker",
        ],
    )

    job = JobProfile(
        job_id="job-002",
        title="ML Engineer",
        requirements=[
            JobRequirement(
                requirement_id="req-job-003",
                description="Python and AWS required.",
                category="skill",
                importance="required",
                normalized_skills=[
                    "Python",
                    "AWS",
                ],
            ),
            JobRequirement(
                requirement_id="req-job-004",
                description="Docker preferred.",
                category="skill",
                importance="preferred",
                normalized_skills=["Docker"],
            ),
        ],
    )

    result = match_job(
        candidate,
        job,
    )

    assert result.required_score == 0.5
    assert result.preferred_score == 1.0
    assert result.overall_score == 0.5


def test_unknown_requirements_are_excluded_from_average() -> None:
    from resume_screening.schemas.job import JobProfile
    from resume_screening.services.matcher import (
        match_job,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=["Python"],
    )

    job = JobProfile(
        job_id="job-003",
        title="Research Scientist",
        requirements=[
            JobRequirement(
                requirement_id="req-job-005",
                description="Python required.",
                category="skill",
                importance="required",
                normalized_skills=["Python"],
            ),
            JobRequirement(
                requirement_id="req-job-006",
                description=(
                    "Demonstrated research impact."
                ),
                category="other",
                importance="required",
            ),
        ],
    )

    result = match_job(
        candidate,
        job,
    )

    assert result.required_score == 1.0
    assert result.overall_score == 1.0

    assert result.assessed_requirements == 1
    assert result.unknown_requirements == 1


def test_preferred_score_is_used_when_no_required_is_assessable() -> None:
    from resume_screening.schemas.job import JobProfile
    from resume_screening.services.matcher import (
        match_job,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        skills=["Docker"],
    )

    job = JobProfile(
        job_id="job-004",
        title="ML Engineer",
        requirements=[
            JobRequirement(
                requirement_id="req-job-007",
                description=(
                    "Strong communication ability."
                ),
                category="other",
                importance="required",
            ),
            JobRequirement(
                requirement_id="req-job-008",
                description="Docker preferred.",
                category="skill",
                importance="preferred",
                normalized_skills=["Docker"],
            ),
        ],
    )

    result = match_job(
        candidate,
        job,
    )

    assert result.required_score is None
    assert result.preferred_score == 1.0
    assert result.overall_score == 1.0

    assert result.assessed_requirements == 1
    assert result.unknown_requirements == 1


def test_doctorate_satisfies_bachelor_requirement() -> None:
    from resume_screening.schemas.candidate import (
        CandidateEducation,
    )
    from resume_screening.services.matcher import (
        match_requirement_education,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        education=[
            CandidateEducation(
                degree="Ph.D. in Computer Engineering",
                evidence_ids=["ev-edu-001"],
            )
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-edu-001",
        description=(
            "Bachelor's degree in Computer Science "
            "or a related field."
        ),
        category="education",
        importance="required",
    )

    result = match_requirement_education(
        candidate,
        requirement,
    )

    assert result.status == "matched"
    assert result.score == 1.0
    assert result.required_degree_level == "bachelor"
    assert result.observed_degree_level == "doctorate"
    assert result.evidence_ids == ["ev-edu-001"]


def test_master_does_not_satisfy_doctorate_requirement() -> None:
    from resume_screening.schemas.candidate import (
        CandidateEducation,
    )
    from resume_screening.services.matcher import (
        match_requirement_education,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        education=[
            CandidateEducation(
                degree="M.Sc. in Computer Science",
            )
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-edu-002",
        description="Ph.D. required.",
        category="education",
        importance="required",
    )

    result = match_requirement_education(
        candidate,
        requirement,
    )

    assert result.status == "not_matched"
    assert result.score == 0.0
    assert result.required_degree_level == "doctorate"
    assert result.observed_degree_level == "master"


def test_missing_candidate_education_is_unknown() -> None:
    from resume_screening.services.matcher import (
        match_requirement_education,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
    )

    requirement = JobRequirement(
        requirement_id="req-edu-003",
        description="Bachelor's degree required.",
        category="education",
        importance="required",
    )

    result = match_requirement_education(
        candidate,
        requirement,
    )

    assert result.status == "unknown"
    assert result.score is None
    assert result.required_degree_level == "bachelor"
    assert result.observed_degree_level is None


def test_explicit_certification_match() -> None:
    from resume_screening.services.matcher import (
        match_requirement_certification,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        certifications=[
            "AWS Certified Machine Learning - Specialty",
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-cert-001",
        description=(
            "AWS Certified Machine Learning - Specialty "
            "certification preferred."
        ),
        category="certification",
        importance="preferred",
    )

    result = match_requirement_certification(
        candidate,
        requirement,
    )

    assert result.status == "matched"
    assert result.score == 1.0
    assert result.matched_certifications == [
        "AWS Certified Machine Learning - Specialty",
    ]


def test_certification_punctuation_differences_still_match() -> None:
    from resume_screening.services.matcher import (
        match_requirement_certification,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        certifications=[
            "AWS Certified Machine Learning - Specialty",
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-cert-002",
        description=(
            "AWS Certified Machine Learning: Specialty "
            "certification preferred."
        ),
        category="certification",
        importance="preferred",
    )

    result = match_requirement_certification(
        candidate,
        requirement,
    )

    assert result.status == "matched"
    assert result.score == 1.0


def test_unproven_certification_match_is_unknown() -> None:
    from resume_screening.services.matcher import (
        match_requirement_certification,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
        certifications=[
            "AWS Certified Machine Learning - Specialty",
        ],
    )

    requirement = JobRequirement(
        requirement_id="req-cert-003",
        description="Cloud certification preferred.",
        category="certification",
        importance="preferred",
    )

    result = match_requirement_certification(
        candidate,
        requirement,
    )

    assert result.status == "unknown"
    assert result.score is None


def test_missing_certification_information_is_unknown() -> None:
    from resume_screening.services.matcher import (
        match_requirement_certification,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-001",
    )

    requirement = JobRequirement(
        requirement_id="req-cert-004",
        description="AWS certification preferred.",
        category="certification",
        importance="preferred",
    )

    result = match_requirement_certification(
        candidate,
        requirement,
    )

    assert result.status == "unknown"
    assert result.score is None


def test_realistic_candidate_job_match() -> None:
    from resume_screening.schemas.candidate import (
        CandidateEducation,
    )
    from resume_screening.schemas.job import JobProfile
    from resume_screening.services.matcher import (
        match_job,
    )

    candidate = CandidateProfile(
        candidate_id="candidate-matthew-001",
        skills=[
            "Python",
            "PyTorch",
            "Docker",
            "Large Language Models",
        ],
        experiences=[
            CandidateExperience(
                title="Applied ML Scientist",
                company="Example Bank",
                years=3,
                skills=[
                    "Python",
                    "PyTorch",
                    "Large Language Models",
                ],
                evidence_ids=[
                    "ev-exp-001",
                ],
            ),
            CandidateExperience(
                title="ML Researcher",
                company="Example University",
                years=2,
                skills=[
                    "Python",
                    "PyTorch",
                ],
                evidence_ids=[
                    "ev-exp-002",
                ],
            ),
        ],
        education=[
            CandidateEducation(
                degree="Ph.D. in Computer Engineering",
                field_of_study="Computer Engineering",
                institution="Example University",
                evidence_ids=[
                    "ev-edu-001",
                ],
            )
        ],
        certifications=[
            "AWS Certified Machine Learning - Specialty",
        ],
    )

    job = JobProfile(
        job_id="job-ai-scientist-001",
        title="Applied AI Research Scientist",
        requirements=[
            JobRequirement(
                requirement_id="req-real-001",
                description=(
                    "Experience using Python and PyTorch."
                ),
                category="skill",
                importance="required",
                normalized_skills=[
                    "Python",
                    "PyTorch",
                ],
            ),
            JobRequirement(
                requirement_id="req-real-002",
                description=(
                    "5+ years of Python experience."
                ),
                category="experience",
                importance="required",
                normalized_skills=[
                    "Python",
                ],
                minimum_years=5,
            ),
            JobRequirement(
                requirement_id="req-real-003",
                description=(
                    "Bachelor's degree in a technical field."
                ),
                category="education",
                importance="required",
            ),
            JobRequirement(
                requirement_id="req-real-004",
                description="Experience with AWS.",
                category="skill",
                importance="required",
                normalized_skills=[
                    "AWS",
                ],
            ),
            JobRequirement(
                requirement_id="req-real-005",
                description=(
                    "Demonstrated research impact."
                ),
                category="other",
                importance="required",
            ),
            JobRequirement(
                requirement_id="req-real-006",
                description="Docker experience preferred.",
                category="skill",
                importance="preferred",
                normalized_skills=[
                    "Docker",
                ],
            ),
            JobRequirement(
                requirement_id="req-real-007",
                description=(
                    "AWS Certified Machine Learning - "
                    "Specialty certification preferred."
                ),
                category="certification",
                importance="preferred",
            ),
        ],
    )

    result = match_job(
        candidate,
        job,
    )

    assert result.candidate_id == "candidate-matthew-001"
    assert result.job_id == "job-ai-scientist-001"

    assert result.required_score == 0.75
    assert result.preferred_score == 1.0
    assert result.overall_score == 0.75

    assert result.assessed_requirements == 6
    assert result.unknown_requirements == 1

    matches = {
        match.requirement_id: match
        for match in result.requirement_matches
    }

    assert matches["req-real-001"].status == "matched"
    assert matches["req-real-001"].score == 1.0

    assert matches["req-real-002"].status == "matched"
    assert matches["req-real-002"].observed_years == 5

    assert matches["req-real-003"].status == "matched"
    assert (
        matches["req-real-003"].observed_degree_level
        == "doctorate"
    )

    assert matches["req-real-004"].status == "not_matched"
    assert matches["req-real-004"].score == 0.0
    assert matches["req-real-004"].not_observed_skills == [
        "AWS",
    ]

    assert matches["req-real-005"].status == "unknown"
    assert matches["req-real-005"].score is None

    assert matches["req-real-006"].status == "matched"

    assert matches[
        "req-real-007"
    ].matched_certifications == [
        "AWS Certified Machine Learning - Specialty",
    ]
