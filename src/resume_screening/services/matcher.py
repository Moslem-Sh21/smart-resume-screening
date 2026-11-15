import re

from resume_screening.schemas.candidate import CandidateProfile
from resume_screening.schemas.job import (
    JobProfile,
    JobRequirement,
)
from resume_screening.schemas.matching import (
    DegreeLevel,
    JobMatchResult,
    RequirementMatch,
)


def normalize_skill_key(skill: str) -> str:
    return " ".join(
        skill.casefold().split()
    )


def collect_candidate_skill_keys(
    candidate: CandidateProfile,
) -> set[str]:
    skill_keys = {
        normalize_skill_key(skill)
        for skill in candidate.skills
    }

    for experience in candidate.experiences:
        skill_keys.update(
            normalize_skill_key(skill)
            for skill in experience.skills
        )

    return skill_keys


def collect_skill_evidence_ids(
    candidate: CandidateProfile,
    matched_skills: list[str],
) -> list[str]:
    matched_keys = {
        normalize_skill_key(skill)
        for skill in matched_skills
    }

    evidence_ids: list[str] = []

    for experience in candidate.experiences:
        experience_skill_keys = {
            normalize_skill_key(skill)
            for skill in experience.skills
        }

        if not (
            experience_skill_keys
            & matched_keys
        ):
            continue

        for evidence_id in experience.evidence_ids:
            if evidence_id not in evidence_ids:
                evidence_ids.append(evidence_id)

    return evidence_ids


def match_requirement_skills(
    candidate: CandidateProfile,
    requirement: JobRequirement,
) -> RequirementMatch:
    if not requirement.normalized_skills:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
            minimum_years=requirement.minimum_years,
        )

    candidate_skill_keys = (
        collect_candidate_skill_keys(candidate)
    )

    matched_skills: list[str] = []
    not_observed_skills: list[str] = []

    for skill in requirement.normalized_skills:
        if normalize_skill_key(skill) in candidate_skill_keys:
            matched_skills.append(skill)
        else:
            not_observed_skills.append(skill)

    score = (
        len(matched_skills)
        / len(requirement.normalized_skills)
    )

    if score == 1.0:
        status = "matched"
    elif score == 0.0:
        status = "not_matched"
    else:
        status = "partial"

    return RequirementMatch(
        requirement_id=requirement.requirement_id,
        category=requirement.category,
        importance=requirement.importance,
        status=status,
        score=score,
        matched_skills=matched_skills,
        not_observed_skills=not_observed_skills,
        minimum_years=requirement.minimum_years,
        evidence_ids=collect_skill_evidence_ids(
            candidate,
            matched_skills,
        ),
    )


def experience_supports_requirement(
    experience_skills: list[str],
    requirement_skills: list[str],
) -> bool:
    if not requirement_skills:
        return True

    experience_skill_keys = {
        normalize_skill_key(skill)
        for skill in experience_skills
    }

    requirement_skill_keys = {
        normalize_skill_key(skill)
        for skill in requirement_skills
    }

    return bool(
        experience_skill_keys
        & requirement_skill_keys
    )


def collect_relevant_experience_years(
    candidate: CandidateProfile,
    requirement: JobRequirement,
) -> tuple[float | None, bool]:
    relevant_experiences = [
        experience
        for experience in candidate.experiences
        if experience_supports_requirement(
            experience.skills,
            requirement.normalized_skills,
        )
    ]

    if not relevant_experiences:
        return None, False

    known_years = [
        experience.years
        for experience in relevant_experiences
        if experience.years is not None
    ]

    has_unknown_years = any(
        experience.years is None
        for experience in relevant_experiences
    )

    if not known_years:
        return None, has_unknown_years

    return sum(known_years), has_unknown_years


def collect_experience_evidence_ids(
    candidate: CandidateProfile,
    requirement: JobRequirement,
) -> list[str]:
    evidence_ids: list[str] = []

    for experience in candidate.experiences:
        if not experience_supports_requirement(
            experience.skills,
            requirement.normalized_skills,
        ):
            continue

        for evidence_id in experience.evidence_ids:
            if evidence_id not in evidence_ids:
                evidence_ids.append(evidence_id)

    return evidence_ids


def match_requirement_years(
    candidate: CandidateProfile,
    requirement: JobRequirement,
) -> RequirementMatch:
    minimum_years = requirement.minimum_years

    if minimum_years is None:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
        )

    observed_years, has_unknown_years = (
        collect_relevant_experience_years(
            candidate,
            requirement,
        )
    )

    evidence_ids = collect_experience_evidence_ids(
        candidate,
        requirement,
    )

    if observed_years is None:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
            minimum_years=minimum_years,
            evidence_ids=evidence_ids,
        )

    if minimum_years == 0:
        score = 1.0
        status = "matched"

    elif observed_years >= minimum_years:
        score = 1.0
        status = "matched"

    elif has_unknown_years:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
            minimum_years=minimum_years,
            observed_years=observed_years,
            evidence_ids=evidence_ids,
        )

    else:
        score = observed_years / minimum_years

        status = (
            "partial"
            if observed_years > 0
            else "not_matched"
        )

    return RequirementMatch(
        requirement_id=requirement.requirement_id,
        category=requirement.category,
        importance=requirement.importance,
        status=status,
        score=score,
        minimum_years=minimum_years,
        observed_years=observed_years,
        evidence_ids=evidence_ids,
    )


def merge_evidence_ids(
    *evidence_groups: list[str],
) -> list[str]:
    merged: list[str] = []

    for evidence_group in evidence_groups:
        for evidence_id in evidence_group:
            if evidence_id not in merged:
                merged.append(evidence_id)

    return merged


def match_requirement(
    candidate: CandidateProfile,
    requirement: JobRequirement,
) -> RequirementMatch:
    skill_result = (
        match_requirement_skills(
            candidate,
            requirement,
        )
        if requirement.normalized_skills
        else None
    )

    years_result = (
        match_requirement_years(
            candidate,
            requirement,
        )
        if requirement.minimum_years is not None
        else None
    )

    education_result = (
        match_requirement_education(
            candidate,
            requirement,
        )
        if requirement.category == "education"
        else None
    )

    certification_result = (
        match_requirement_certification(
            candidate,
            requirement,
        )
        if requirement.category == "certification"
        else None
    )

    dimension_results = [
        result
        for result in (
            skill_result,
            years_result,
            education_result,
            certification_result,
        )
        if result is not None
    ]

    if not dimension_results:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
        )

    assessed_results = [
        result
        for result in dimension_results
        if result.score is not None
    ]

    if not assessed_results:
        score = None
        status = "unknown"
    else:
        score = sum(
            result.score
            for result in assessed_results
            if result.score is not None
        ) / len(assessed_results)

        has_unknown_dimension = (
            len(assessed_results)
            != len(dimension_results)
        )

        if has_unknown_dimension:
            status = "partial"
        elif score == 1.0:
            status = "matched"
        elif score == 0.0:
            status = "not_matched"
        else:
            status = "partial"

    skill_evidence = (
        skill_result.evidence_ids
        if skill_result is not None
        else []
    )

    years_evidence = (
        years_result.evidence_ids
        if years_result is not None
        else []
    )

    return RequirementMatch(
        requirement_id=requirement.requirement_id,
        category=requirement.category,
        importance=requirement.importance,
        status=status,
        score=score,
        matched_skills=(
            skill_result.matched_skills
            if skill_result is not None
            else []
        ),
        not_observed_skills=(
            skill_result.not_observed_skills
            if skill_result is not None
            else []
        ),
        matched_certifications=(
            certification_result.matched_certifications
            if certification_result is not None
            else []
        ),
        minimum_years=requirement.minimum_years,
        observed_years=(
            years_result.observed_years
            if years_result is not None
            else None
        ),
        required_degree_level=(
            education_result.required_degree_level
            if education_result is not None
            else None
        ),
        observed_degree_level=(
            education_result.observed_degree_level
            if education_result is not None
            else None
        ),
        evidence_ids=merge_evidence_ids(
            skill_evidence,
            years_evidence,
            (
                education_result.evidence_ids
                if education_result is not None
                else []
            ),
        ),
    )


def average_assessed_score(
    matches: list[RequirementMatch],
) -> float | None:
    scores = [
        match.score
        for match in matches
        if match.score is not None
    ]

    if not scores:
        return None

    return sum(scores) / len(scores)


def match_job(
    candidate: CandidateProfile,
    job: JobProfile,
) -> JobMatchResult:
    requirement_matches = [
        match_requirement(
            candidate,
            requirement,
        )
        for requirement in job.requirements
    ]

    required_matches = [
        match
        for match in requirement_matches
        if match.importance == "required"
    ]

    preferred_matches = [
        match
        for match in requirement_matches
        if match.importance == "preferred"
    ]

    required_score = average_assessed_score(
        required_matches
    )

    preferred_score = average_assessed_score(
        preferred_matches
    )

    overall_score = (
        required_score
        if required_score is not None
        else preferred_score
    )

    assessed_requirements = sum(
        match.score is not None
        for match in requirement_matches
    )

    unknown_requirements = sum(
        match.score is None
        for match in requirement_matches
    )

    return JobMatchResult(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        overall_score=overall_score,
        required_score=required_score,
        preferred_score=preferred_score,
        assessed_requirements=assessed_requirements,
        unknown_requirements=unknown_requirements,
        requirement_matches=requirement_matches,
    )


DEGREE_LEVEL_RANK: dict[DegreeLevel, int] = {
    "diploma": 1,
    "associate": 2,
    "bachelor": 3,
    "master": 4,
    "doctorate": 5,
}


def normalize_degree_text(text: str) -> str:
    return " ".join(
        re.sub(
            r"[^a-z0-9]+",
            " ",
            text.casefold(),
        ).split()
    )


def extract_degree_level(
    text: str,
) -> DegreeLevel | None:
    normalized = normalize_degree_text(text)

    patterns: tuple[
        tuple[DegreeLevel, str],
        ...
    ] = (
        (
            "doctorate",
            r"\b(?:ph d|phd|doctorate|doctoral)\b",
        ),
        (
            "master",
            r"\b(?:master(?: s)?|m sc|msc|m eng|meng|mba)\b",
        ),
        (
            "bachelor",
            r"\b(?:bachelor(?: s)?|b sc|bsc|b eng|beng)\b",
        ),
        (
            "associate",
            r"\bassociate(?: s)?\b",
        ),
        (
            "diploma",
            r"\bdiploma\b",
        ),
    )

    for level, pattern in patterns:
        if re.search(pattern, normalized):
            return level

    return None


def highest_candidate_degree_level(
    candidate: CandidateProfile,
) -> DegreeLevel | None:
    levels: list[DegreeLevel] = []

    for education in candidate.education:
        level = extract_degree_level(
            education.degree
        )

        if level is not None:
            levels.append(level)

    if not levels:
        return None

    return max(
        levels,
        key=lambda level: DEGREE_LEVEL_RANK[level],
    )


def collect_education_evidence_ids(
    candidate: CandidateProfile,
) -> list[str]:
    evidence_ids: list[str] = []

    for education in candidate.education:
        if extract_degree_level(
            education.degree
        ) is None:
            continue

        for evidence_id in education.evidence_ids:
            if evidence_id not in evidence_ids:
                evidence_ids.append(evidence_id)

    return evidence_ids


def match_requirement_education(
    candidate: CandidateProfile,
    requirement: JobRequirement,
) -> RequirementMatch:
    required_level = extract_degree_level(
        requirement.description
    )

    if required_level is None:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
        )

    observed_level = highest_candidate_degree_level(
        candidate
    )

    if observed_level is None:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
            required_degree_level=required_level,
        )

    matched = (
        DEGREE_LEVEL_RANK[observed_level]
        >= DEGREE_LEVEL_RANK[required_level]
    )

    return RequirementMatch(
        requirement_id=requirement.requirement_id,
        category=requirement.category,
        importance=requirement.importance,
        status=(
            "matched"
            if matched
            else "not_matched"
        ),
        score=1.0 if matched else 0.0,
        required_degree_level=required_level,
        observed_degree_level=observed_level,
        evidence_ids=collect_education_evidence_ids(
            candidate
        ),
    )


def normalize_certification_text(
    text: str,
) -> str:
    return " ".join(
        re.sub(
            r"[^a-z0-9]+",
            " ",
            text.casefold(),
        ).split()
    )


def match_requirement_certification(
    candidate: CandidateProfile,
    requirement: JobRequirement,
) -> RequirementMatch:
    if not candidate.certifications:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
        )

    normalized_requirement = (
        normalize_certification_text(
            requirement.description
        )
    )

    matched_certifications = [
        certification
        for certification in candidate.certifications
        if normalize_certification_text(
            certification
        )
        in normalized_requirement
    ]

    if not matched_certifications:
        return RequirementMatch(
            requirement_id=requirement.requirement_id,
            category=requirement.category,
            importance=requirement.importance,
            status="unknown",
        )

    return RequirementMatch(
        requirement_id=requirement.requirement_id,
        category=requirement.category,
        importance=requirement.importance,
        status="matched",
        score=1.0,
        matched_certifications=matched_certifications,
    )
