import html
import re
from collections import defaultdict

from resume_screening.schemas import (
    CandidateEducation,
    CandidateExperience,
    CandidateIdentity,
    CandidateProfile,
)

MARKDOWN_HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*$")

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?1[\s.-]?)?"
    r"(?:\(\d{3}\)|\d{3})"
    r"[\s.-]\d{3}[\s.-]\d{4}"
    r"(?!\d)"
)

URL_PATTERN = re.compile(r"https?://[^\s|]+")


SECTION_ALIASES = {
    "summary": "summary",
    "professional summary": "summary",
    "profile": "summary",
    "core expertise": "skills",
    "technical skills": "skills",
    "skills": "skills",
    "professional experience": "experience",
    "work experience": "experience",
    "experience": "experience",
    "employment history": "experience",
    "education": "education",
    "academic background": "education",
    "certifications": "certifications",
    "certificates": "certifications",
    "licenses & certifications": "certifications",
    "independent project": "other",
    "independent projects": "other",
    "projects": "other",
    "selected publications": "other",
    "publications": "other",
    "awards": "other",
}


SKILL_CATEGORY_LABELS = (
    "Technical Skills",
    "Core Expertise",
    "Programming & Data",
    "Programming & Data Processing",
    "Machine Learning & Statistics",
    "NLP & Generative AI",
    "Generative AI & LLMs",
    "Frameworks",
    "Frameworks & Libraries",
    "ML Engineering & APIs",
    "Cloud & ML Engineering",
    "Cloud & High-Performance Computing",
    "Data Visualization",
)


SKILL_CATEGORY_PATTERN = re.compile(
    r"(?i)(?:"
    + "|".join(
        re.escape(label)
        for label in SKILL_CATEGORY_LABELS
    )
    + r")\s*:"
)

SKILL_SPLIT_PATTERN = re.compile(r"[,|\n]+")


def normalize_heading(heading: str) -> str:
    return " ".join(heading.lower().split())


def split_resume_sections(markdown: str) -> dict[str, str]:
    section_lines: dict[str, list[str]] = defaultdict(list)
    current_section = "preamble"

    for line in markdown.splitlines():
        heading_match = MARKDOWN_HEADING_PATTERN.match(line.strip())

        if heading_match:
            heading = normalize_heading(heading_match.group(1))
            detected_section = SECTION_ALIASES.get(heading)

            if detected_section is not None:
                current_section = detected_section
                continue

        section_lines[current_section].append(line)

    return {
        section: "\n".join(lines).strip()
        for section, lines in section_lines.items()
        if "\n".join(lines).strip()
    }


def extract_candidate_identity(summary: str) -> CandidateIdentity:
    name: str | None = None

    for line in summary.splitlines():
        heading_match = MARKDOWN_HEADING_PATTERN.match(line.strip())

        if heading_match:
            candidate_name = heading_match.group(1).strip()

            if normalize_heading(candidate_name) not in SECTION_ALIASES:
                name = candidate_name
                break

    email_match = EMAIL_PATTERN.search(summary)
    phone_match = PHONE_PATTERN.search(summary)

    links = [
        url.rstrip(".,);]")
        for url in URL_PATTERN.findall(summary)
    ]

    return CandidateIdentity(
        name=name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        links=list(dict.fromkeys(links)),
    )


def normalize_skill(skill: str) -> str:
    return " ".join(
        skill.strip(" -*#•\t").split()
    )


def extract_skills(skills_section: str) -> list[str]:
    cleaned_section = html.unescape(skills_section)

    cleaned_section = SKILL_CATEGORY_PATTERN.sub(
        "\n",
        cleaned_section,
    )

    raw_skills = SKILL_SPLIT_PATTERN.split(cleaned_section)

    skills: list[str] = []
    seen: set[str] = set()

    for raw_skill in raw_skills:
        skill = normalize_skill(raw_skill)

        if not skill:
            continue

        comparison_key = skill.casefold()

        if comparison_key in seen:
            continue

        seen.add(comparison_key)
        skills.append(skill)

    return skills


MONTH_PATTERN = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)

DATE_TOKEN_PATTERN = rf"(?:{MONTH_PATTERN}\s+)?(?:19|20)\d{{2}}"

DATE_RANGE_PATTERN = re.compile(
    rf"\b{DATE_TOKEN_PATTERN}"
    rf"\s*(?:-|–|—|to)\s*"
    rf"(?:Present|Current|{DATE_TOKEN_PATTERN})\b",
    re.IGNORECASE,
)

MARKDOWN_HEADING_PREFIX_PATTERN = re.compile(r"^#{1,6}\s+")


def clean_experience_line(line: str) -> str:
    cleaned = html.unescape(line.strip())

    return MARKDOWN_HEADING_PREFIX_PATTERN.sub(
        "",
        cleaned,
    ).strip()


def is_experience_header(line: str) -> bool:
    cleaned = clean_experience_line(line)

    if cleaned.startswith(("-", "*", "•")):
        return False

    parts = [
        part.strip()
        for part in cleaned.split("|")
    ]

    if len(parts) < 3:
        return False

    return DATE_RANGE_PATTERN.search(parts[-1]) is not None


def extract_experiences(
    experience_section: str,
) -> list[CandidateExperience]:
    experiences: list[CandidateExperience] = []

    current_experience: CandidateExperience | None = None

    for line in experience_section.splitlines():
        stripped_line = line.strip()

        if not stripped_line:
            continue

        if is_experience_header(stripped_line):
            if current_experience is not None:
                experiences.append(current_experience)

            cleaned_header = clean_experience_line(stripped_line)

            parts = [
                part.strip()
                for part in cleaned_header.split("|")
            ]

            current_experience = CandidateExperience(
                title=parts[0],
                company=parts[1] or None,
                date_range=parts[-1],
            )

            continue

        if current_experience is None:
            continue

        if stripped_line.startswith(("- ", "* ", "• ")):
            highlight = stripped_line[2:].strip()

            if highlight:
                current_experience.highlights.append(
                    html.unescape(highlight)
                )

    if current_experience is not None:
        experiences.append(current_experience)

    return experiences


DEGREE_MARKER_PATTERN = re.compile(
    r"(?i)(?<!\w)(?:"
    r"Ph\.?D\.?"
    r"|M\.?Sc\.?"
    r"|B\.?Sc\.?"
    r"|M\.?Eng\.?"
    r"|B\.?Eng\.?"
    r"|MBA\b"
    r"|Master(?:'s)?\b"
    r"|Bachelor(?:'s)?\b"
    r")"
)

SINGLE_DATE_PATTERN = re.compile(
    rf"\b{DATE_TOKEN_PATTERN}\b",
    re.IGNORECASE,
)


def split_education_entries(
    education_section: str,
) -> list[str]:
    entries: list[str] = []

    for line in education_section.splitlines():
        cleaned_line = html.unescape(
            MARKDOWN_HEADING_PREFIX_PATTERN.sub(
                "",
                line.strip(),
            )
        )

        if not cleaned_line:
            continue

        degree_matches = list(
            DEGREE_MARKER_PATTERN.finditer(cleaned_line)
        )

        if not degree_matches:
            continue

        for index, match in enumerate(degree_matches):
            start = match.start()

            if index + 1 < len(degree_matches):
                end = degree_matches[index + 1].start()
            else:
                end = len(cleaned_line)

            entry = cleaned_line[start:end].strip()

            if entry:
                entries.append(entry)

    return entries


def split_degree_and_field(
    degree_text: str,
) -> tuple[str, str | None]:
    parts = re.split(
        r"\s+in\s+",
        degree_text.strip(),
        maxsplit=1,
        flags=re.IGNORECASE,
    )

    degree = parts[0].strip()

    if len(parts) == 1:
        return degree, None

    field_of_study = parts[1].strip()

    return degree, field_of_study or None


def extract_education(
    education_section: str,
) -> list[CandidateEducation]:
    education_entries: list[CandidateEducation] = []

    for entry in split_education_entries(
        education_section
    ):
        parts = [
            part.strip()
            for part in entry.split("|")
        ]

        if len(parts) < 2:
            continue

        degree, field_of_study = split_degree_and_field(
            parts[0]
        )

        institution = parts[1] or None

        date_range: str | None = None

        if len(parts) >= 3:
            date_text = parts[-1]

            range_match = DATE_RANGE_PATTERN.search(
                date_text
            )

            if range_match:
                date_range = range_match.group(0)
            else:
                single_date_match = SINGLE_DATE_PATTERN.search(
                    date_text
                )

                if single_date_match:
                    date_range = single_date_match.group(0)

        education_entries.append(
            CandidateEducation(
                degree=degree,
                field_of_study=field_of_study,
                institution=institution,
                date_range=date_range,
            )
        )

    return education_entries


def extract_certifications(
    certifications_section: str,
) -> list[str]:
    certifications: list[str] = []
    seen: set[str] = set()

    for line in certifications_section.splitlines():
        certification = html.unescape(line.strip())

        certification = MARKDOWN_HEADING_PREFIX_PATTERN.sub(
            "",
            certification,
        ).strip()

        certification = certification.lstrip("-*• ").strip()

        if not certification:
            continue

        comparison_key = certification.casefold()

        if comparison_key in seen:
            continue

        seen.add(comparison_key)
        certifications.append(certification)

    return certifications


def extract_candidate_profile(
    candidate_id: str,
    markdown: str,
) -> CandidateProfile:
    sections = split_resume_sections(markdown)

    identity_source = (
        sections.get("summary")
        or sections.get("preamble")
        or ""
    )

    return CandidateProfile(
        candidate_id=candidate_id,
        identity=extract_candidate_identity(identity_source),
        skills=extract_skills(
            sections.get("skills", "")
        ),
        experiences=extract_experiences(
            sections.get("experience", "")
        ),
        education=extract_education(
            sections.get("education", "")
        ),
        certifications=extract_certifications(
            sections.get("certifications", "")
        ),
    )
