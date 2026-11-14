from resume_screening.services.candidate_extractor import (
    normalize_heading,
    split_resume_sections,
)


def test_normalize_heading() -> None:
    assert normalize_heading("  TECHNICAL   SKILLS  ") == "technical skills"


def test_split_resume_sections_maps_known_headings() -> None:
    markdown = """
## SUMMARY

## Jane Doe

Toronto, ON | jane@example.com

Machine learning engineer.

## CORE EXPERTISE

Python | PyTorch | SQL

## PROFESSIONAL EXPERIENCE

Machine Learning Engineer | Example Corp | Jan 2024 - Present

- Built ML evaluation pipelines.

## EDUCATION

Ph.D. in Computer Engineering | Example University

## CERTIFICATIONS

AWS Machine Learning
"""

    sections = split_resume_sections(markdown)

    assert "summary" in sections
    assert "skills" in sections
    assert "experience" in sections
    assert "education" in sections
    assert "certifications" in sections

    assert "## Jane Doe" in sections["summary"]
    assert "jane@example.com" in sections["summary"]

    assert "Python | PyTorch | SQL" in sections["skills"]

    assert "Machine Learning Engineer" in sections["experience"]
    assert "Built ML evaluation pipelines." in sections["experience"]

    assert "Ph.D. in Computer Engineering" in sections["education"]
    assert "AWS Machine Learning" in sections["certifications"]


def test_unknown_heading_is_preserved_as_content() -> None:
    markdown = """
## PROFESSIONAL EXPERIENCE

## AI Consultant | Example Company | 2023 - 2025

- Built a retrieval system.
"""

    sections = split_resume_sections(markdown)

    assert "experience" in sections
    assert "## AI Consultant | Example Company | 2023 - 2025" in sections["experience"]
    assert "Built a retrieval system." in sections["experience"]


def test_other_sections_do_not_contaminate_education() -> None:
    markdown = """
## EDUCATION

Ph.D. in Computer Engineering | Example University

## INDEPENDENT PROJECT

Smart Resume Screening

## SELECTED PUBLICATIONS

Example publication
"""

    sections = split_resume_sections(markdown)

    assert "Smart Resume Screening" not in sections["education"]
    assert "Example publication" not in sections["education"]

    assert "Smart Resume Screening" in sections["other"]
    assert "Example publication" in sections["other"]


def test_extract_candidate_identity() -> None:
    summary = """
## Jane Doe

Toronto, ON | jane@example.com | (613) 555-1234

https://www.linkedin.com/in/jane-doe
https://github.com/janedoe

Machine learning engineer.
"""

    from resume_screening.services.candidate_extractor import (
        extract_candidate_identity,
    )

    identity = extract_candidate_identity(summary)

    assert identity.name == "Jane Doe"
    assert identity.email == "jane@example.com"
    assert identity.phone == "(613) 555-1234"

    assert identity.links == [
        "https://www.linkedin.com/in/jane-doe",
        "https://github.com/janedoe",
    ]


def test_extract_candidate_identity_does_not_invent_links() -> None:
    summary = """
## Jane Doe

Toronto, ON | jane@example.com | LinkedIn | GitHub | Google Scholar
"""

    from resume_screening.services.candidate_extractor import (
        extract_candidate_identity,
    )

    identity = extract_candidate_identity(summary)

    assert identity.name == "Jane Doe"
    assert identity.email == "jane@example.com"
    assert identity.links == []


def test_extract_candidate_identity_preserves_missing_values() -> None:
    summary = """
Machine learning engineer with experience in Python and PyTorch.
"""

    from resume_screening.services.candidate_extractor import (
        extract_candidate_identity,
    )

    identity = extract_candidate_identity(summary)

    assert identity.name is None
    assert identity.email is None
    assert identity.phone is None
    assert identity.links == []


def test_extract_skills_from_skill_categories() -> None:
    from resume_screening.services.candidate_extractor import extract_skills

    skills_section = """
Programming & Data: Python, SQL, C++, NumPy, Pandas

Frameworks: PyTorch, TensorFlow, scikit-learn, OpenCV

Data Visualization: Matplotlib, Plotly
"""

    skills = extract_skills(skills_section)

    assert skills == [
        "Python",
        "SQL",
        "C++",
        "NumPy",
        "Pandas",
        "PyTorch",
        "TensorFlow",
        "scikit-learn",
        "OpenCV",
        "Matplotlib",
        "Plotly",
    ]


def test_extract_skills_handles_merged_categories() -> None:
    from resume_screening.services.candidate_extractor import extract_skills

    skills_section = """
Machine Learning & Statistics: Deep Learning, Predictive Modeling,
Fairness & Bias Evaluation NLP & Generative AI: Large Language Models,
Retrieval-Augmented Generation, Vision-Language Models
"""

    skills = extract_skills(skills_section)

    assert "Deep Learning" in skills
    assert "Predictive Modeling" in skills
    assert "Fairness & Bias Evaluation" in skills
    assert "Large Language Models" in skills
    assert "Retrieval-Augmented Generation" in skills
    assert "Vision-Language Models" in skills

    assert "NLP & Generative AI" not in skills


def test_extract_skills_decodes_html_entities() -> None:
    from resume_screening.services.candidate_extractor import extract_skills

    skills_section = """
Technical Skills: Explainable AI, Fairness &amp; Bias Evaluation
"""

    skills = extract_skills(skills_section)

    assert "Explainable AI" in skills
    assert "Fairness & Bias Evaluation" in skills


def test_extract_skills_removes_case_insensitive_duplicates() -> None:
    from resume_screening.services.candidate_extractor import extract_skills

    skills_section = """
Python, PyTorch, python, PYTORCH
"""

    skills = extract_skills(skills_section)

    assert skills == [
        "Python",
        "PyTorch",
    ]


def test_extract_experiences() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_experiences,
    )

    experience_section = """
Machine Learning Engineer | Example Corp | Toronto, ON | Jan 2024 - Present

- Built machine learning evaluation pipelines.
- Improved model performance by 15%.

Data Scientist | Another Company | Ottawa, ON | May 2021 - Dec 2023

- Developed predictive models.
- Worked with Python and SQL.
"""

    experiences = extract_experiences(experience_section)

    assert len(experiences) == 2

    assert experiences[0].title == "Machine Learning Engineer"
    assert experiences[0].company == "Example Corp"
    assert experiences[0].date_range == "Jan 2024 - Present"
    assert experiences[0].highlights == [
        "Built machine learning evaluation pipelines.",
        "Improved model performance by 15%.",
    ]

    assert experiences[1].title == "Data Scientist"
    assert experiences[1].company == "Another Company"
    assert experiences[1].date_range == "May 2021 - Dec 2023"
    assert experiences[1].highlights == [
        "Developed predictive models.",
        "Worked with Python and SQL.",
    ]


def test_extract_experiences_handles_markdown_job_heading() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_experiences,
    )

    experience_section = """
## AI Consultant | KnowQuest | Toronto, ON | Sep 2023 - Sep 2025

- Built a retrieval-augmented generation system.
"""

    experiences = extract_experiences(experience_section)

    assert len(experiences) == 1
    assert experiences[0].title == "AI Consultant"
    assert experiences[0].company == "KnowQuest"
    assert experiences[0].date_range == "Sep 2023 - Sep 2025"
    assert experiences[0].highlights == [
        "Built a retrieval-augmented generation system.",
    ]


def test_extract_experiences_does_not_treat_bullets_as_headers() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_experiences,
    )

    experience_section = """
ML Engineer | Example Corp | Toronto, ON | 2022 - 2024

- Compared model A | model B | model C during evaluation.
"""

    experiences = extract_experiences(experience_section)

    assert len(experiences) == 1
    assert experiences[0].highlights == [
        "Compared model A | model B | model C during evaluation.",
    ]


def test_extract_education() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_education,
    )

    education_section = """
Ph.D. in Computer Engineering | Example University | May 2021 - Jul 2026

M.Sc. in Computer Engineering | Another University | Sep 2015 - May 2018
"""

    education = extract_education(
        education_section
    )

    assert len(education) == 2

    assert education[0].degree == "Ph.D."
    assert education[0].field_of_study == "Computer Engineering"
    assert education[0].institution == "Example University"
    assert education[0].date_range == "May 2021 - Jul 2026"

    assert education[1].degree == "M.Sc."
    assert education[1].field_of_study == "Computer Engineering"
    assert education[1].institution == "Another University"
    assert education[1].date_range == "Sep 2015 - May 2018"


def test_extract_education_handles_single_date() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_education,
    )

    education_section = """
M.Sc. in Computer Engineering | Example University | Sep 2015
"""

    education = extract_education(
        education_section
    )

    assert len(education) == 1
    assert education[0].date_range == "Sep 2015"


def test_extract_education_handles_merged_entries() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_education,
    )

    education_section = (
        "Ph.D. in Computer Engineering | Queen's University | "
        "May 2021 - Jul 2026 M.Sc. in Computer Engineering | "
        "IUT | Sep 2015"
    )

    education = extract_education(
        education_section
    )

    assert len(education) == 2

    assert education[0].degree == "Ph.D."
    assert education[0].institution == "Queen's University"
    assert education[0].date_range == "May 2021 - Jul 2026"

    assert education[1].degree == "M.Sc."
    assert education[1].institution == "IUT"
    assert education[1].date_range == "Sep 2015"


def test_extract_education_ignores_non_degree_text() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_education,
    )

    education_section = """
Dissertation: Responsible Machine Learning

Research focused on generative AI.
"""

    education = extract_education(
        education_section
    )

    assert education == []


def test_extract_certifications() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_certifications,
    )

    certifications_section = """
- AWS Certified Machine Learning
- PMP
- Microsoft Azure AI Engineer Associate
"""

    certifications = extract_certifications(
        certifications_section
    )

    assert certifications == [
        "AWS Certified Machine Learning",
        "PMP",
        "Microsoft Azure AI Engineer Associate",
    ]


def test_extract_certifications_handles_markdown_headings() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_certifications,
    )

    certifications_section = """
### AWS Certified Machine Learning
### PMP
"""

    certifications = extract_certifications(
        certifications_section
    )

    assert certifications == [
        "AWS Certified Machine Learning",
        "PMP",
    ]


def test_extract_certifications_removes_duplicates() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_certifications,
    )

    certifications_section = """
AWS Certified Machine Learning
aws certified machine learning
"""

    certifications = extract_certifications(
        certifications_section
    )

    assert certifications == [
        "AWS Certified Machine Learning",
    ]


def test_extract_certifications_handles_empty_section() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_certifications,
    )

    assert extract_certifications("") == []


def test_extract_candidate_profile() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_candidate_profile,
    )

    markdown = """
## SUMMARY

## Jane Doe

Toronto, ON | jane@example.com | (613) 555-1234

Machine learning engineer.

## TECHNICAL SKILLS

Programming & Data: Python, SQL

Frameworks: PyTorch, scikit-learn

## PROFESSIONAL EXPERIENCE

Machine Learning Engineer | Example Corp | Toronto, ON | Jan 2024 - Present

- Built machine learning evaluation pipelines.
- Improved model performance.

Data Scientist | Another Company | Ottawa, ON | May 2021 - Dec 2023

- Developed predictive models.

## EDUCATION

Ph.D. in Computer Engineering | Example University | May 2021 - Jul 2026

## CERTIFICATIONS

- AWS Certified Machine Learning
"""

    profile = extract_candidate_profile(
        candidate_id="candidate-001",
        markdown=markdown,
    )

    assert profile.candidate_id == "candidate-001"

    assert profile.identity.name == "Jane Doe"
    assert profile.identity.email == "jane@example.com"
    assert profile.identity.phone == "(613) 555-1234"

    assert profile.skills == [
        "Python",
        "SQL",
        "PyTorch",
        "scikit-learn",
    ]

    assert len(profile.experiences) == 2

    assert profile.experiences[0].title == (
        "Machine Learning Engineer"
    )
    assert profile.experiences[0].company == "Example Corp"
    assert profile.experiences[0].date_range == (
        "Jan 2024 - Present"
    )
    assert profile.experiences[0].highlights == [
        "Built machine learning evaluation pipelines.",
        "Improved model performance.",
    ]

    assert profile.experiences[1].title == "Data Scientist"
    assert profile.experiences[1].company == "Another Company"

    assert len(profile.education) == 1

    assert profile.education[0].degree == "Ph.D."
    assert profile.education[0].field_of_study == (
        "Computer Engineering"
    )
    assert profile.education[0].institution == (
        "Example University"
    )

    assert profile.certifications == [
        "AWS Certified Machine Learning",
    ]


def test_extract_candidate_profile_handles_missing_sections() -> None:
    from resume_screening.services.candidate_extractor import (
        extract_candidate_profile,
    )

    markdown = """
## SUMMARY

## Jane Doe

jane@example.com
"""

    profile = extract_candidate_profile(
        candidate_id="candidate-002",
        markdown=markdown,
    )

    assert profile.candidate_id == "candidate-002"

    assert profile.identity.name == "Jane Doe"
    assert profile.identity.email == "jane@example.com"

    assert profile.skills == []
    assert profile.experiences == []
    assert profile.education == []
    assert profile.certifications == []
