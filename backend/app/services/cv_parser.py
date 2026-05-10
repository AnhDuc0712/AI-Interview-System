import re
from datetime import datetime, timezone

from app.models.cv import (
    CVParserMetadata,
    StructuredCVData,
    StructuredCVEducationItem,
    StructuredCVExperienceItem,
    StructuredCVPersonalInfo,
    StructuredCVProjectItem,
)


SECTION_HEADERS = {
    'experience': {'experience', 'work experience', 'employment history'},
    'education': {'education', 'academic background'},
    'skills': {'skills', 'technical skills', 'core skills'},
    'projects': {'projects', 'personal projects', 'selected projects'},
    'certifications': {'certifications', 'licenses'},
    'languages': {'languages'},
    'summary': {'summary', 'professional summary', 'profile'},
}


class StructuredCVParserService:
    parser_name = 'rule-based-structured-cv-parser'
    parser_version = 'v1'

    def parse(self, normalized_text: str) -> tuple[StructuredCVData, CVParserMetadata]:
        lines = [line.strip() for line in normalized_text.split('\n') if line.strip()]
        sections = split_sections(lines)
        personal_info = extract_personal_info(lines, sections.get('summary', []))

        data = StructuredCVData(
            personal_info=personal_info,
            skills=extract_bulleted_values(sections.get('skills', [])),
            experience=extract_experience(sections.get('experience', [])),
            education=extract_education(sections.get('education', [])),
            projects=extract_projects(sections.get('projects', [])),
            certifications=extract_bulleted_values(sections.get('certifications', [])),
            languages=extract_bulleted_values(sections.get('languages', [])),
            raw_sections=sections
        )
        metadata = CVParserMetadata(
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            parsed_at=datetime.now(timezone.utc)
        )
        return data, metadata


def split_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section = 'general'
    sections[current_section] = []

    for line in lines:
        section_name = resolve_section_name(line)
        if section_name:
            current_section = section_name
            sections.setdefault(current_section, [])
            continue
        sections.setdefault(current_section, []).append(line)

    return sections


def resolve_section_name(line: str) -> str | None:
    normalized = line.lower().strip(': ')
    for section_name, headers in SECTION_HEADERS.items():
        if normalized in headers:
            return section_name
    return None


def extract_personal_info(lines: list[str], summary_lines: list[str]) -> StructuredCVPersonalInfo:
    email = None
    phone = None
    name = lines[0] if lines else None
    location = None

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', '\n'.join(lines[:8]))
    if email_match:
        email = email_match.group(0)

    phone_match = re.search(r'(\+?\d[\d\-\s\(\)]{7,}\d)', '\n'.join(lines[:8]))
    if phone_match:
        phone = phone_match.group(0).strip()

    for line in lines[:8]:
        if '@' in line or any(char.isdigit() for char in line):
            continue
        if ',' in line and len(line.split()) <= 6:
            location = line
            break

    return StructuredCVPersonalInfo(
        full_name=name,
        email=email,
        phone=phone,
        location=location,
        summary=' '.join(summary_lines) if summary_lines else None
    )


def extract_bulleted_values(lines: list[str]) -> list[str]:
    values: list[str] = []
    for line in lines:
        parts = re.split(r'[,\u2022|]', line)
        for part in parts:
            item = part.strip(' -')
            if item:
                values.append(item)
    return deduplicate(values)


def extract_experience(lines: list[str]) -> list[StructuredCVExperienceItem]:
    items: list[StructuredCVExperienceItem] = []
    for line in lines:
        segments = [segment.strip() for segment in re.split(r'[-|@]', line) if segment.strip()]
        if not segments:
            continue
        items.append(
            StructuredCVExperienceItem(
                title=segments[0],
                company=segments[1] if len(segments) > 1 else None,
                description=line
            )
        )
    return items[:10]


def extract_education(lines: list[str]) -> list[StructuredCVEducationItem]:
    items: list[StructuredCVEducationItem] = []
    for line in lines:
        segments = [segment.strip() for segment in re.split(r'[-|,]', line) if segment.strip()]
        if not segments:
            continue
        items.append(
            StructuredCVEducationItem(
                institution=segments[0],
                degree=segments[1] if len(segments) > 1 else None,
                field_of_study=segments[2] if len(segments) > 2 else None
            )
        )
    return items[:10]


def extract_projects(lines: list[str]) -> list[StructuredCVProjectItem]:
    items: list[StructuredCVProjectItem] = []
    for line in lines:
        segments = [segment.strip() for segment in re.split(r'[-|:]', line, maxsplit=1) if segment.strip()]
        if not segments:
            continue
        items.append(
            StructuredCVProjectItem(
                name=segments[0],
                description=segments[1] if len(segments) > 1 else None
            )
        )
    return items[:10]


def deduplicate(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(value)
    return deduped
