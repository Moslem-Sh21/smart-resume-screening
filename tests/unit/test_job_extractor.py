from resume_screening.services.job_extractor import (
    detect_job_section,
    normalize_job_heading,
    split_job_sections,
)


def test_normalize_job_heading() -> None:
    heading = "  Required   Qualifications: "

    assert (
        normalize_job_heading(heading)
        == "required qualifications"
    )


def test_detect_job_section_handles_markdown_heading() -> None:
    assert (
        detect_job_section(
            "## Required Qualifications"
        )
        == "required"
    )

    assert (
        detect_job_section(
            "## Preferred Qualifications"
        )
        == "preferred"
    )


def test_detect_job_section_handles_plain_heading() -> None:
    assert (
        detect_job_section(
            "Minimum Qualifications:"
        )
        == "required"
    )

    assert (
        detect_job_section(
            "Nice to Have:"
        )
        == "preferred"
    )


def test_split_job_sections() -> None:
    description = """
## About the role

Build ML systems for financial applications.

## Required Qualifications

- 3+ years of machine learning experience.
- Strong Python and SQL skills.

## Preferred Qualifications

- Experience with AWS.
- Familiarity with RAG.

## Responsibilities

- Build production ML pipelines.
"""

    sections = split_job_sections(description)

    assert "required" in sections
    assert "preferred" in sections
    assert "other" in sections

    assert (
        "3+ years of machine learning experience."
        in sections["required"]
    )

    assert (
        "Strong Python and SQL skills."
        in sections["required"]
    )

    assert (
        "Experience with AWS."
        in sections["preferred"]
    )

    assert (
        "Build production ML pipelines."
        in sections["other"]
    )


def test_required_and_preferred_do_not_mix() -> None:
    description = """
Required Qualifications

- Python
- SQL

Preferred Qualifications

- AWS
- Docker
"""

    sections = split_job_sections(description)

    assert "Python" in sections["required"]
    assert "SQL" in sections["required"]

    assert "AWS" not in sections["required"]
    assert "Docker" not in sections["required"]

    assert "AWS" in sections["preferred"]
    assert "Docker" in sections["preferred"]


def test_split_requirements_from_bullets() -> None:
    from resume_screening.services.job_extractor import (
        split_requirements,
    )

    section = """
- 3+ years of machine learning experience.
- Strong Python and SQL skills.
- Bachelor's degree in Computer Science.
"""

    requirements = split_requirements(section)

    assert requirements == [
        "3+ years of machine learning experience.",
        "Strong Python and SQL skills.",
        "Bachelor's degree in Computer Science.",
    ]


def test_split_requirements_supports_multiple_bullet_styles() -> None:
    from resume_screening.services.job_extractor import (
        split_requirements,
    )

    section = """
* Python experience
• AWS experience
1. Machine learning experience
2) SQL experience
"""

    requirements = split_requirements(section)

    assert requirements == [
        "Python experience",
        "AWS experience",
        "Machine learning experience",
        "SQL experience",
    ]


def test_split_requirements_ignores_non_bullet_text() -> None:
    from resume_screening.services.job_extractor import (
        split_requirements,
    )

    section = """
We are looking for an experienced engineer.

- Strong Python skills.
- Experience with machine learning.

This role works with multiple teams.
"""

    requirements = split_requirements(section)

    assert requirements == [
        "Strong Python skills.",
        "Experience with machine learning.",
    ]


def test_split_requirements_handles_empty_section() -> None:
    from resume_screening.services.job_extractor import (
        split_requirements,
    )

    assert split_requirements("") == []


def test_classify_requirement_as_experience() -> None:
    from resume_screening.services.job_extractor import (
        classify_requirement,
    )

    requirement = (
        "3+ years of experience building "
        "machine learning systems."
    )

    assert classify_requirement(requirement) == "experience"


def test_classify_requirement_as_skill() -> None:
    from resume_screening.services.job_extractor import (
        classify_requirement,
    )

    assert (
        classify_requirement(
            "Strong Python and SQL skills."
        )
        == "skill"
    )

    assert (
        classify_requirement(
            "Experience with AWS."
        )
        == "skill"
    )

    assert (
        classify_requirement(
            "Familiarity with RAG."
        )
        == "skill"
    )


def test_classify_requirement_as_education() -> None:
    from resume_screening.services.job_extractor import (
        classify_requirement,
    )

    requirement = (
        "Bachelor's degree in Computer Science "
        "or a related field."
    )

    assert classify_requirement(requirement) == "education"


def test_classify_requirement_as_certification() -> None:
    from resume_screening.services.job_extractor import (
        classify_requirement,
    )

    assert (
        classify_requirement(
            "AWS certification is required."
        )
        == "certification"
    )


def test_classify_requirement_as_other() -> None:
    from resume_screening.services.job_extractor import (
        classify_requirement,
    )

    requirement = (
        "Excellent communication and collaboration."
    )

    assert classify_requirement(requirement) == "other"


def test_extract_minimum_years_from_plus_format() -> None:
    from resume_screening.services.job_extractor import (
        extract_minimum_years,
    )

    requirement = (
        "3+ years of experience building "
        "machine learning systems."
    )

    assert extract_minimum_years(requirement) == 3.0


def test_extract_minimum_years_from_at_least_format() -> None:
    from resume_screening.services.job_extractor import (
        extract_minimum_years,
    )

    requirement = (
        "At least 5 years of professional experience."
    )

    assert extract_minimum_years(requirement) == 5.0


def test_extract_minimum_years_from_range() -> None:
    from resume_screening.services.job_extractor import (
        extract_minimum_years,
    )

    requirement = (
        "2-4 years of data science experience."
    )

    assert extract_minimum_years(requirement) == 2.0


def test_extract_minimum_years_from_or_more_format() -> None:
    from resume_screening.services.job_extractor import (
        extract_minimum_years,
    )

    requirement = (
        "3 or more years of machine learning experience."
    )

    assert extract_minimum_years(requirement) == 3.0


def test_extract_minimum_years_returns_none_when_missing() -> None:
    from resume_screening.services.job_extractor import (
        extract_minimum_years,
    )

    requirement = "Experience with AWS and Python."

    assert extract_minimum_years(requirement) is None


def test_extract_explicit_skills() -> None:
    from resume_screening.services.job_extractor import (
        extract_explicit_skills,
    )

    requirement = (
        "Strong Python and SQL skills with "
        "experience using PyTorch."
    )

    assert extract_explicit_skills(requirement) == [
        "Python",
        "SQL",
        "PyTorch",
    ]


def test_extract_explicit_skills_handles_cloud_tools() -> None:
    from resume_screening.services.job_extractor import (
        extract_explicit_skills,
    )

    requirement = (
        "Experience with AWS, Docker, and Kubernetes."
    )

    assert extract_explicit_skills(requirement) == [
        "AWS",
        "Docker",
        "Kubernetes",
    ]


def test_extract_explicit_skills_does_not_infer_related_skills() -> None:
    from resume_screening.services.job_extractor import (
        extract_explicit_skills,
    )

    requirement = "Experience with PyTorch."

    assert extract_explicit_skills(requirement) == [
        "PyTorch",
    ]


def test_extract_explicit_skills_handles_rag_terms() -> None:
    from resume_screening.services.job_extractor import (
        extract_explicit_skills,
    )

    requirement = (
        "Experience building Retrieval-Augmented "
        "Generation systems with LangChain."
    )

    assert extract_explicit_skills(requirement) == [
        "LangChain",
        "Retrieval-Augmented Generation",
    ]


def test_extract_explicit_skills_returns_empty_when_none_found() -> None:
    from resume_screening.services.job_extractor import (
        extract_explicit_skills,
    )

    requirement = (
        "Excellent communication and collaboration skills."
    )

    assert extract_explicit_skills(requirement) == []


def test_generate_requirement_id_is_deterministic() -> None:
    from resume_screening.services.job_extractor import (
        generate_requirement_id,
    )

    first = generate_requirement_id(
        "job-001",
        "Strong Python and SQL skills.",
        "required",
    )

    second = generate_requirement_id(
        "job-001",
        "Strong Python and SQL skills.",
        "required",
    )

    assert first == second
    assert first.startswith("req-")


def test_requirement_id_changes_with_importance() -> None:
    from resume_screening.services.job_extractor import (
        generate_requirement_id,
    )

    required_id = generate_requirement_id(
        "job-001",
        "Experience with AWS.",
        "required",
    )

    preferred_id = generate_requirement_id(
        "job-001",
        "Experience with AWS.",
        "preferred",
    )

    assert required_id != preferred_id


def test_build_job_requirements() -> None:
    from resume_screening.services.job_extractor import (
        build_job_requirements,
    )

    description = """
Required Qualifications

- 3+ years of experience building machine learning systems.
- Strong Python and SQL skills.
- Bachelor's degree in Computer Science.

Preferred Qualifications

- Experience with AWS and Docker.
- Familiarity with Retrieval-Augmented Generation.
"""

    requirements = build_job_requirements(
        "job-001",
        description,
    )

    assert len(requirements) == 5

    experience = requirements[0]

    assert experience.importance == "required"
    assert experience.category == "experience"
    assert experience.minimum_years == 3.0
    assert experience.normalized_skills == []

    skill = requirements[1]

    assert skill.importance == "required"
    assert skill.category == "skill"
    assert skill.normalized_skills == [
        "Python",
        "SQL",
    ]
    assert skill.minimum_years is None

    education = requirements[2]

    assert education.importance == "required"
    assert education.category == "education"

    cloud = requirements[3]

    assert cloud.importance == "preferred"
    assert cloud.category == "skill"
    assert cloud.normalized_skills == [
        "AWS",
        "Docker",
    ]

    rag = requirements[4]

    assert rag.importance == "preferred"
    assert rag.category == "skill"
    assert rag.normalized_skills == [
        "Retrieval-Augmented Generation",
    ]


def test_build_job_requirements_ignores_other_sections() -> None:
    from resume_screening.services.job_extractor import (
        build_job_requirements,
    )

    description = """
Responsibilities

- Build production machine learning systems.
- Work with engineering teams.

Required Qualifications

- Strong Python skills.
"""

    requirements = build_job_requirements(
        "job-001",
        description,
    )

    assert len(requirements) == 1
    assert requirements[0].description == (
        "Strong Python skills."
    )


def test_extract_job_title_from_markdown_heading() -> None:
    from resume_screening.services.job_extractor import (
        extract_job_title,
    )

    description = """
# Machine Learning Engineer

## Required Qualifications

- Strong Python skills.
"""

    assert (
        extract_job_title(description)
        == "Machine Learning Engineer"
    )


def test_extract_job_title_from_labeled_field() -> None:
    from resume_screening.services.job_extractor import (
        extract_job_title,
    )

    description = """
Job Title: Applied AI Research Scientist

Required Qualifications

- Strong Python skills.
"""

    assert (
        extract_job_title(description)
        == "Applied AI Research Scientist"
    )


def test_extract_job_title_does_not_use_section_heading() -> None:
    from resume_screening.services.job_extractor import (
        extract_job_title,
    )

    description = """
Required Qualifications

- Strong Python skills.
"""

    assert extract_job_title(description) is None


def test_extract_job_profile() -> None:
    from resume_screening.services.job_extractor import (
        extract_job_profile,
    )

    description = """
# Machine Learning Engineer

## Required Qualifications

- 3+ years of experience building machine learning systems.
- Strong Python and SQL skills.
- Bachelor's degree in Computer Science.

## Preferred Qualifications

- Experience with AWS and Docker.
"""

    profile = extract_job_profile(
        job_id="job-001",
        job_description=description,
    )

    assert profile.job_id == "job-001"
    assert profile.title == "Machine Learning Engineer"

    assert len(profile.requirements) == 4

    assert profile.requirements[0].importance == "required"
    assert profile.requirements[0].category == "experience"
    assert profile.requirements[0].minimum_years == 3.0

    assert profile.requirements[1].normalized_skills == [
        "Python",
        "SQL",
    ]

    assert profile.requirements[2].category == "education"

    assert profile.requirements[3].importance == "preferred"
    assert profile.requirements[3].normalized_skills == [
        "AWS",
        "Docker",
    ]


def test_extract_job_profile_uses_explicit_title() -> None:
    from resume_screening.services.job_extractor import (
        extract_job_profile,
    )

    description = """
Required Qualifications

- Strong Python skills.
"""

    profile = extract_job_profile(
        job_id="job-002",
        job_description=description,
        title="Data Scientist",
    )

    assert profile.title == "Data Scientist"


def test_extract_job_profile_requires_title() -> None:
    from resume_screening.services.job_extractor import (
        extract_job_profile,
    )

    description = """
Required Qualifications

- Strong Python skills.
"""

    try:
        extract_job_profile(
            job_id="job-003",
            job_description=description,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Job title could not be determined."
        )
    else:
        raise AssertionError(
            "Expected ValueError for missing job title."
        )


def test_who_you_are_is_treated_as_required_section() -> None:
    from resume_screening.services.job_extractor import (
        split_job_sections,
    )

    description = """
## Who You Are

- Ph.D. in Computer Science.
- Experience using Python and PyTorch.
"""

    sections = split_job_sections(description)

    assert "required" in sections

    assert (
        "Ph.D. in Computer Science."
        in sections["required"]
    )

    assert (
        "Experience using Python and PyTorch."
        in sections["required"]
    )


def test_split_requirements_joins_indented_continuation_lines() -> None:
    from resume_screening.services.job_extractor import (
        split_requirements,
    )

    section = """
- Ph.D. in a relevant technical field with 3+ years of
  relevant research experience or equivalent experience.
- Strong knowledge of deep learning and natural language
  processing.
- Experience with end-to-end LLM systems, cloud platforms,
  or Databricks.
"""

    requirements = split_requirements(section)

    assert requirements == [
        (
            "Ph.D. in a relevant technical field with 3+ years "
            "of relevant research experience or equivalent "
            "experience."
        ),
        (
            "Strong knowledge of deep learning and natural "
            "language processing."
        ),
        (
            "Experience with end-to-end LLM systems, cloud "
            "platforms, or Databricks."
        ),
    ]


def test_skill_aliases_map_to_canonical_names() -> None:
    from resume_screening.services.job_extractor import (
        extract_explicit_skills,
    )

    requirement = (
        "Experience with LLMs, NLP, and RAG."
    )

    assert extract_explicit_skills(requirement) == [
        "Retrieval-Augmented Generation",
        "Large Language Models",
        "Natural Language Processing",
    ]


def test_skill_aliases_do_not_create_duplicates() -> None:
    from resume_screening.services.job_extractor import (
        extract_explicit_skills,
    )

    requirement = (
        "Experience with Large Language Models "
        "(LLMs)."
    )

    assert extract_explicit_skills(requirement) == [
        "Large Language Models",
    ]


def test_extracts_real_ai_research_skills() -> None:
    from resume_screening.services.job_extractor import (
        extract_explicit_skills,
    )

    requirement = (
        "Experience with foundation-model architecture, "
        "pre-training, post-training, model efficiency, "
        "deep learning, and large-scale GPU training."
    )

    assert extract_explicit_skills(requirement) == [
        "Deep Learning",
        "Foundation Models",
        "Pre-training",
        "Post-training",
        "Model Efficiency",
        "GPU Training",
    ]
