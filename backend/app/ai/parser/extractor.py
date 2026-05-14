from __future__ import annotations

import re
from typing import Iterable

from app.models.cv import (
    StructuredCVPersonalInfo,
    StructuredCVEducationItem,
    StructuredCVExperienceItem,
    StructuredCVProjectItem,
)
from app.ai.parser.patterns import (
    BULLET_SPLIT_PATTERN,
    DATE_RANGE_PATTERN,
    DATE_WORD_PATTERN,
    DATE_YEAR_PATTERN,
    EMAIL_PATTERN,
    GITHUB_PATTERN,
    LINKEDIN_PATTERN,
    PHONE_PATTERN,
    SECTION_SPLIT_PATTERN,
    URL_PATTERN,
    NOISE_NAME_LINES,
)


def extract_personal_info(
    lines: list[str],
    summary_lines: list[str],
) -> StructuredCVPersonalInfo:
    top_lines = [line for line in lines[:12] if line.strip()]
    email = _find_first_match(EMAIL_PATTERN, top_lines)
    phone = _find_first_match(PHONE_PATTERN, top_lines)
    github = _extract_github(lines)
    linkedin = _extract_linkedin(lines)
    full_name = _extract_full_name(top_lines, email=email, phone=phone)
    location = _extract_location(top_lines, email=email, phone=phone)
    summary = ' '.join(summary_lines).strip() if summary_lines else None

    return StructuredCVPersonalInfo(
        full_name=full_name,
        email=email,
        phone=phone,
        location=location,
        github=github,
        linkedin=linkedin,
        summary=summary,
    )


def extract_skills(lines: list[str]) -> list[str]:
    values: list[str] = []
    for line in lines:
        values.extend(_split_values(line))
    return _deduplicate(values)


def extract_experience(lines: list[str]) -> list[StructuredCVExperienceItem]:
    items: list[StructuredCVExperienceItem] = []
    for line in lines:
        if not line.strip():
            continue

        title, company = _split_title_company(line)
        start_date, end_date = _parse_date_range(line)
        items.append(
            StructuredCVExperienceItem(
                title=title,
                company=company,
                start_date=start_date,
                end_date=end_date,
                description=line.strip(),
            )
        )

    return items[:12]


def extract_education(lines: list[str]) -> list[StructuredCVEducationItem]:
    items: list[StructuredCVEducationItem] = []
    for line in lines:
        if not line.strip():
            continue

        segments = [segment.strip() for segment in re.split(r'\s*[-–—|,]\s*', line) if segment.strip()]
        institution = segments[0] if segments else line.strip()
        degree = segments[1] if len(segments) > 1 else None
        field_of_study = segments[2] if len(segments) > 2 else None
        graduation_date = _extract_year(line)

        items.append(
            StructuredCVEducationItem(
                institution=institution,
                degree=degree,
                field_of_study=field_of_study,
                graduation_date=graduation_date,
            )
        )

    return items[:10]


def extract_projects(lines: list[str]) -> list[StructuredCVProjectItem]:
    items: list[StructuredCVProjectItem] = []
    for line in lines:
        if not line.strip():
            continue

        fragments = [fragment.strip() for fragment in re.split(r'\s+[-–—:]\s+', line, maxsplit=1) if fragment.strip()]
        name = fragments[0]
        description = fragments[1] if len(fragments) > 1 else None

        items.append(
            StructuredCVProjectItem(
                name=name,
                description=description,
            )
        )

    return items[:12]


def extract_certifications(lines: list[str]) -> list[str]:
    values: list[str] = []
    for line in lines:
        values.extend(_split_values(line))
    return _deduplicate(values)


def _find_first_match(pattern: re.Pattern, lines: Iterable[str], group: str | int = 0) -> str | None:
    for line in lines:
        match = pattern.search(line)
        if match:
            return match.group(group) if group else match.group(0)
    return None


def _extract_github(lines: Iterable[str]) -> str | None:
    username = _find_first_match(GITHUB_PATTERN, lines, group='username')
    return f'https://github.com/{username}' if username else None


def _extract_linkedin(lines: Iterable[str]) -> str | None:
    identifier = _find_first_match(LINKEDIN_PATTERN, lines, group='identifier')
    return f'https://linkedin.com/in/{identifier}' if identifier else None


def _extract_full_name(lines: list[str], email: str | None, phone: str | None) -> str | None:
    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()
        if not stripped or lower in NOISE_NAME_LINES:
            continue
        if email and email in stripped:
            continue
        if phone and phone in stripped:
            continue
        if URL_PATTERN.search(stripped):
            continue
        if any(char.isdigit() for char in stripped):
            continue
        if len(stripped.split()) <= 6:
            return stripped

    return lines[0].strip() if lines else None


def _extract_location(lines: list[str], email: str | None, phone: str | None) -> str | None:
    for line in lines:
        stripped = line.strip()
        if email and email in stripped:
            continue
        if phone and phone in stripped:
            continue
        if URL_PATTERN.search(stripped):
            continue
        if ',' in stripped and len(stripped.split()) <= 10:
            return stripped

    return None


def _split_values(line: str, preserve_commas: bool = True) -> list[str]:
    cleaned = BULLET_SPLIT_PATTERN.sub(',', line)
    parts = [part.strip(' -•') for part in re.split(r'[\,;]|\s{2,}', cleaned) if part.strip()]
    values = [part for part in parts if part.lower() not in {'skills', 'experience', 'education', 'projects', 'certifications'}]
    if not preserve_commas:
        values = [re.sub(r'[\,;]+$', '', part).strip() for part in values]
    return values


def _split_title_company(line: str) -> tuple[str, str | None]:
    fragments = [fragment.strip() for fragment in SECTION_SPLIT_PATTERN.split(line) if fragment.strip()]
    if len(fragments) > 1:
        return fragments[0], fragments[1]
    return line.strip(), None


def _parse_date_range(line: str) -> tuple[str | None, str | None]:
    if not line:
        return None, None

    match = DATE_RANGE_PATTERN.search(line)
    if match:
        start = _safe_group(match, 'start', 1)
        end = _safe_group(match, 'end', 2)
        return _normalize_date_token(start), _normalize_date_token(end)

    keyword_match = DATE_WORD_PATTERN.search(line)
    if keyword_match:
        return None, _normalize_date_token(keyword_match.group(0))

    year = _extract_year(line)
    return (year, None) if year else (None, None)


def _extract_year(line: str) -> str | None:
    match = DATE_YEAR_PATTERN.search(line)
    if not match:
        return None
    year = _safe_group(match, 'year', 1)
    return year.strip() if year else None


def _safe_group(match: re.Match, name: str, fallback_index: int) -> str | None:
    if name in match.groupdict():
        return match.group(name)
    groups = match.groups()
    if groups and len(groups) >= fallback_index:
        return groups[fallback_index - 1]
    try:
        return match.group(fallback_index)
    except IndexError:
        return None


def _normalize_date_token(token: str | None) -> str | None:
    if not token:
        return None
    token = token.strip()
    lowered = token.lower()
    keyword_map = {
        'present': 'Present',
        'current': 'Current',
        'expected': 'Expected',
        'now': 'Now',
        'ongoing': 'Ongoing',
    }
    if lowered in keyword_map:
        return keyword_map[lowered]
    return token


def _deduplicate(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = value.lower().strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append(value)
    return deduped
