from __future__ import annotations

import re
from typing import Optional

from app.ai.parser.patterns import SECTION_HEADERS


def normalize_header(line: str) -> str:
    normalized = line.lower().strip()
    normalized = re.sub(r'[\s:\-\|]+$', '', normalized)
    normalized = re.sub(r'[^a-z0-9 ]+', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def detect_section(line: str) -> Optional[str]:
    normalized = normalize_header(line)
    if not normalized or len(normalized) > 120:
        return None

    for section_name, labels in SECTION_HEADERS.items():
        for label in labels:
            if normalized == label or normalized.startswith(label) or label in normalized:
                return section_name
    return None


def split_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section = 'general'
    sections[current_section] = []

    for line in lines:
        section_name = detect_section(line)
        if section_name:
            current_section = section_name
            sections.setdefault(current_section, [])
            continue
        sections.setdefault(current_section, []).append(line.strip())

    return sections
