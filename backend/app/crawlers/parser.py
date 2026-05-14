from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field


def clean_text(raw_text: str) -> str:
    return re.sub(r'\s+', ' ', raw_text or '').strip()


def merge_description_and_requirements(description: str, requirements: str | None) -> str:
    parts = [clean_text(description)]
    if requirements:
        parts.append(clean_text(requirements))
    return '\n\n'.join(part for part in parts if part)


def parse_experience_level(raw_text: str) -> str:
    if not raw_text:
        return ''

    normalized = raw_text.lower()
    patterns = [
        r'(?:exp(?:erience)?\s*(?:level)?)[\s:\-]+(junior|mid|senior|lead|principal)',
        r'\b(junior|mid|senior|lead|principal)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            return match.group(1).capitalize()
    return ''


class ParsedJobContent(BaseModel):
    title: str
    company: str
    location: str | None = None
    experience_level: str | None = None
    description: str
    requirements: str | None = None
    skills_raw: str | None = None
    source: str
    url: str
    raw_description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
