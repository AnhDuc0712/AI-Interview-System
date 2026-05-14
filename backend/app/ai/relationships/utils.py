from __future__ import annotations

import re
from typing import Iterable

from app.ai.skills.extractor import SkillExtractionEngine

STOPWORDS = {
    'and', 'or', 'with', 'for', 'to', 'of', 'in', 'the', 'a', 'an',
    'experience', 'years', 'skill', 'skills', 'knowledge', 'including',
    'including', 'preferred', 'required', 'team', 'work', 'working',
}


def canonicalize_skill(skill: str) -> str:
    return skill.strip()


def extract_unknown_tokens(raw_text: str, known_skills: Iterable[str]) -> list[str]:
    if not raw_text:
        return []

    known_lower = {skill.lower().strip() for skill in known_skills if skill}
    candidate_parts = re.split(r'[\n,;•\u2022/\\\|\[\]{}()]+', raw_text)
    engine = SkillExtractionEngine()
    candidates: list[str] = []

    for part in candidate_parts:
        token = part.strip()
        if not token or len(token) > 80:
            continue
        if token.lower() in STOPWORDS:
            continue
        if len(token.split()) > 4:
            continue

        if token.lower() in known_lower:
            continue

        if token.isdigit():
            continue

        if not re.search(r'[A-Za-z]', token):
            continue

        if token.lower() in known_lower:
            continue

        if engine.matcher.match([token]):
            continue

        uppercase_count = sum(1 for ch in token if ch.isupper())
        if uppercase_count == 0 and not re.search(r'\d', token) and not re.search(r'[\.#+-]', token):
            continue

        if ' ' in token and uppercase_count < 2 and not re.search(r'[\.#+\d-]', token):
            continue

        candidates.append(token)

    unique_tokens = []
    seen = set()
    for token in candidates:
        normalized = token.strip()
        if not normalized:
            continue
        lower = normalized.lower()
        if lower in seen:
            continue
        seen.add(lower)
        unique_tokens.append(normalized)

    return unique_tokens