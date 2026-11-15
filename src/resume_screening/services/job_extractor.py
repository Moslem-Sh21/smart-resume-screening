import hashlib
import re
from collections import defaultdict

from resume_screening.schemas.job import (
    JobProfile,
    JobRequirement,
    RequirementCategory,
    RequirementImportance,
)

MARKDOWN_HEADING_PATTERN = re.compile(
    r"^#{1,6}\s+(.+?)\s*$"
)


SECTION_ALIASES = {
    "required qualifications": "required",
    "minimum qualifications": "required",
    "basic qualifications": "required",
    "requirements": "required",
    "qualifications": "required",
    "what you need": "required",
    "what you'll need": "required",
    "who you are": "required",
    "must have": "required",
    "must-haves": "required",
    "preferred qualifications": "preferred",
    "preferred skills": "preferred",
    "nice to have": "preferred",
    "nice to haves": "preferred",
    "nice-to-have": "preferred",
    "bonus qualifications": "preferred",
    "responsibilities": "other",
    "what you'll do": "other",
    "what you will do": "other",
    "about the role": "other",
    "about you": "other",
    "benefits": "other",
}


def normalize_job_heading(heading: str) -> str:
    return " ".join(
        heading.lower().strip().rstrip(":").split()
    )


def detect_job_section(line: str) -> str | None:
    stripped = line.strip()

    heading_match = MARKDOWN_HEADING_PATTERN.match(
        stripped
    )

    if heading_match:
        stripped = heading_match.group(1)

    normalized = normalize_job_heading(stripped)

    return SECTION_ALIASES.get(normalized)


def split_job_sections(
    job_description: str,
) -> dict[str, str]:
    section_lines: dict[str, list[str]] = defaultdict(list)

    current_section = "preamble"

    for line in job_description.splitlines():
        detected_section = detect_job_section(line)

        if detected_section is not None:
            current_section = detected_section
            continue

        section_lines[current_section].append(line)

    return {
        section: "\n".join(lines).strip()
        for section, lines in section_lines.items()
        if "\n".join(lines).strip()
    }


BULLET_REQUIREMENT_PATTERN = re.compile(
    r"^\s*(?:[-*•]|\d+[.)])\s+(.+?)\s*$"
)


def split_requirements(section_text: str) -> list[str]:
    requirements: list[str] = []
    current_parts: list[str] = []

    for line in section_text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        match = BULLET_REQUIREMENT_PATTERN.match(
            stripped
        )

        if match is not None:
            if current_parts:
                requirements.append(
                    " ".join(current_parts)
                )

            requirement = match.group(1).strip()

            current_parts = (
                [requirement]
                if requirement
                else []
            )

            continue

        is_indented = line.startswith(
            (" ", "	")
        )

        if current_parts and is_indented:
            current_parts.append(stripped)

    if current_parts:
        requirements.append(
            " ".join(current_parts)
        )

    return requirements


CERTIFICATION_PATTERN = re.compile(
    r"\b(?:"
    r"certification"
    r"|certified"
    r"|certificate"
    r"|licen[cs]e"
    r"|licensed"
    r")\b",
    re.IGNORECASE,
)


EDUCATION_PATTERN = re.compile(
    r"\b(?:"
    r"degree"
    r"|bachelor(?:'s)?"
    r"|master(?:'s)?"
    r"|ph\.?d\.?"
    r"|doctorate"
    r"|diploma"
    r")\b",
    re.IGNORECASE,
)


EXPERIENCE_PATTERN = re.compile(
    r"\b(?:"
    r"\d+(?:\.\d+)?\+?\s*(?:years?|yrs?)"
    r"|professional experience"
    r"|industry experience"
    r"|work experience"
    r"|experience\s+(?:building|developing|designing|leading|working)"
    r")\b",
    re.IGNORECASE,
)


SKILL_PATTERN = re.compile(
    r"\b(?:"
    r"skills?"
    r"|proficien(?:t|cy)"
    r"|knowledge"
    r"|familiarity"
    r"|hands-on experience"
    r"|experience\s+(?:with|using|in)"
    r")\b",
    re.IGNORECASE,
)


def classify_requirement(
    requirement: str,
) -> RequirementCategory:
    if CERTIFICATION_PATTERN.search(requirement):
        return "certification"

    if EDUCATION_PATTERN.search(requirement):
        return "education"

    if EXPERIENCE_PATTERN.search(requirement):
        return "experience"

    if SKILL_PATTERN.search(requirement):
        return "skill"

    return "other"


YEAR_RANGE_PATTERN = re.compile(
    r"\b"
    r"(?P<minimum>\d+(?:\.\d+)?)"
    r"\s*(?:-|–|—|to)\s*"
    r"\d+(?:\.\d+)?"
    r"\s*(?:years?|yrs?)\b",
    re.IGNORECASE,
)


YEARS_OR_MORE_PATTERN = re.compile(
    r"\b"
    r"(?P<minimum>\d+(?:\.\d+)?)"
    r"\s+(?:or\s+more|plus)"
    r"\s+(?:years?|yrs?)\b",
    re.IGNORECASE,
)


MINIMUM_YEARS_PATTERN = re.compile(
    r"\b"
    r"(?:at\s+least\s+|minimum\s+(?:of\s+)?)?"
    r"(?P<minimum>\d+(?:\.\d+)?)"
    r"\s*\+?\s*"
    r"(?:years?|yrs?)\b",
    re.IGNORECASE,
)


def extract_minimum_years(
    requirement: str,
) -> float | None:
    patterns = (
        YEAR_RANGE_PATTERN,
        YEARS_OR_MORE_PATTERN,
        MINIMUM_YEARS_PATTERN,
    )

    for pattern in patterns:
        match = pattern.search(requirement)

        if match is not None:
            return float(match.group("minimum"))

    return None


SKILL_ALIASES = {
    "Python": ("Python",),
    "SQL": ("SQL",),
    "C++": ("C++",),
    "Java": ("Java",),
    "JavaScript": ("JavaScript",),
    "PyTorch": ("PyTorch",),
    "TensorFlow": ("TensorFlow",),
    "scikit-learn": ("scikit-learn",),
    "Pandas": ("Pandas",),
    "NumPy": ("NumPy",),
    "Hugging Face": ("Hugging Face",),
    "LangChain": ("LangChain",),
    "LangGraph": ("LangGraph",),
    "Retrieval-Augmented Generation": (
        "RAG",
        "Retrieval-Augmented Generation",
    ),
    "Large Language Models": (
        "LLM",
        "LLMs",
        "Large Language Model",
        "Large Language Models",
    ),
    "Natural Language Processing": (
        "NLP",
        "Natural Language Processing",
    ),
    "Deep Learning": (
        "Deep Learning",
    ),
    "Foundation Models": (
        "Foundation Model",
        "Foundation Models",
        "Foundation-Model",
        "Foundation-Models",
    ),
    "Pre-training": (
        "Pre-training",
        "Pretraining",
    ),
    "Post-training": (
        "Post-training",
        "Posttraining",
    ),
    "Model Efficiency": (
        "Model Efficiency",
    ),
    "GPU Training": (
        "GPU Training",
        "GPU-Accelerated Training",
    ),
    "AWS": ("AWS",),
    "Azure": ("Azure",),
    "GCP": ("GCP",),
    "Databricks": ("Databricks",),
    "Docker": ("Docker",),
    "Kubernetes": ("Kubernetes",),
    "MLflow": ("MLflow",),
    "Git": ("Git",),
    "FastAPI": ("FastAPI",),
    "REST APIs": (
        "REST API",
        "REST APIs",
    ),
    "OpenSearch": ("OpenSearch",),
    "PostgreSQL": ("PostgreSQL",),
    "Spark": ("Spark",),
    "Airflow": ("Airflow",),
}


def extract_explicit_skills(
    requirement: str,
) -> list[str]:
    detected_skills: list[str] = []

    for canonical_skill, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            alias_pattern = re.compile(
                rf"(?<!\w){re.escape(alias)}(?!\w)",
                re.IGNORECASE,
            )

            if alias_pattern.search(requirement):
                detected_skills.append(
                    canonical_skill
                )
                break

    return detected_skills


def generate_requirement_id(
    job_id: str,
    description: str,
    importance: RequirementImportance,
) -> str:
    normalized_description = " ".join(
        description.casefold().split()
    )

    normalized_job_id = " ".join(
        job_id.casefold().split()
    )

    identity_text = (
        f"{normalized_job_id}|"
        f"{importance}|"
        f"{normalized_description}"
    )

    digest = hashlib.sha256(
        identity_text.encode("utf-8")
    ).hexdigest()[:12]

    return f"req-{digest}"


def build_job_requirements(
    job_id: str,
    job_description: str,
) -> list[JobRequirement]:
    sections = split_job_sections(job_description)

    requirements: list[JobRequirement] = []

    importance_order: tuple[
        RequirementImportance,
        ...
    ] = (
        "required",
        "preferred",
    )

    for importance in importance_order:
        section_text = sections.get(
            importance,
            "",
        )

        descriptions = split_requirements(
            section_text
        )

        for description in descriptions:
            requirements.append(
                JobRequirement(
                    requirement_id=generate_requirement_id(
                        job_id,
                        description,
                        importance,
                    ),
                    description=description,
                    category=classify_requirement(
                        description
                    ),
                    importance=importance,
                    normalized_skills=extract_explicit_skills(
                        description
                    ),
                    minimum_years=extract_minimum_years(
                        description
                    ),
                )
            )

    return requirements


JOB_TITLE_LABEL_PATTERN = re.compile(
    r"^(?:job\s+title|position|role)\s*:\s*(.+?)\s*$",
    re.IGNORECASE,
)


def extract_job_title(
    job_description: str,
) -> str | None:
    for line in job_description.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        labeled_title = JOB_TITLE_LABEL_PATTERN.match(
            stripped
        )

        if labeled_title:
            title = labeled_title.group(1).strip()

            if title:
                return title

        heading_match = MARKDOWN_HEADING_PATTERN.match(
            stripped
        )

        if heading_match:
            heading = heading_match.group(1).strip()

            if detect_job_section(heading) is None:
                return heading

    return None


def extract_job_profile(
    job_id: str,
    job_description: str,
    title: str | None = None,
) -> JobProfile:
    supplied_title = (
        title.strip()
        if title is not None
        else None
    )

    resolved_title = (
        supplied_title
        or extract_job_title(job_description)
    )

    if not resolved_title:
        raise ValueError(
            "Job title could not be determined."
        )

    return JobProfile(
        job_id=job_id,
        title=resolved_title,
        requirements=build_job_requirements(
            job_id,
            job_description,
        ),
    )
