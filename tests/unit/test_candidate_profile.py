from resume_screening.schemas import (
    CandidateEducation,
    CandidateExperience,
    CandidateIdentity,
    CandidateProfile,
)


def test_candidate_profile_separates_identity_from_ranking_data() -> None:
    profile = CandidateProfile(
        candidate_id="candidate-001",
        identity=CandidateIdentity(
            name="Jane Doe",
            email="jane@example.com",
            phone="555-1234",
            links=["https://example.com/jane"],
        ),
        skills=["Python", "PyTorch"],
        experiences=[
            CandidateExperience(
                title="Machine Learning Engineer",
                company="Example Corp",
                date_range="Jan 2024 - Present",
                highlights=[
                    "Built machine learning evaluation pipelines.",
                ],
            )
        ],
        education=[
            CandidateEducation(
                degree="Ph.D.",
                field_of_study="Computer Engineering",
                institution="Example University",
                date_range="2020 - 2024",
            )
        ],
        certifications=["AWS Machine Learning"],
    )

    assert profile.identity.name == "Jane Doe"
    assert profile.identity.email == "jane@example.com"

    assert profile.skills == ["Python", "PyTorch"]
    assert profile.experiences[0].company == "Example Corp"
    assert profile.education[0].degree == "Ph.D."
    assert profile.certifications == ["AWS Machine Learning"]


def test_candidate_profile_preserves_missing_information_as_unknown() -> None:
    profile = CandidateProfile(
        candidate_id="candidate-002",
    )

    assert profile.identity.name is None
    assert profile.identity.email is None
    assert profile.identity.phone is None
    assert profile.identity.links == []

    assert profile.skills == []
    assert profile.experiences == []
    assert profile.education == []
    assert profile.certifications == []
