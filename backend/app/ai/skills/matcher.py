from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from app.ai.skills.normalizer import NORMALIZATION_MAP

DEFAULT_TAXONOMY_PATH = Path(__file__).parent / 'taxonomy.json'


def _load_taxonomy(path: Path | str | None = None) -> dict[str, list[str]]:
    taxonomy_path = Path(path or DEFAULT_TAXONOMY_PATH)
    with taxonomy_path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def _build_alias_map(taxonomy: dict[str, list[str]]) -> dict[str, str]:
    # Build a stable alias map from taxonomy labels and normalization aliases.
    # This enables case-insensitive, punctuation-insensitive matching across CV text.
    aliases: dict[str, str] = {}
    for category, skills in taxonomy.items():
        for skill in skills:
            normalized = skill.lower().strip()
            aliases[normalized] = skill
            compact = re.sub(r'[\s\.\-_]+', '', normalized)
            aliases[compact] = skill
            if normalized not in aliases:
                aliases[normalized] = skill
    for alias, canonical in NORMALIZATION_MAP.items():
        aliases[alias.lower().strip()] = canonical
    return aliases


def _build_patterns(alias_map: dict[str, str]) -> list[tuple[re.Pattern, str]]:
    patterns: list[tuple[re.Pattern, str]] = []
    for alias, canonical in alias_map.items():
        escaped = re.escape(alias)
        pattern = re.compile(rf'(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])', re.IGNORECASE)
        patterns.append((pattern, canonical))
    patterns.sort(key=lambda entry: -len(entry[0].pattern))
    return patterns


class SkillMatcher:
    def __init__(self, taxonomy: dict[str, list[str]] | str | None = None) -> None:
        if isinstance(taxonomy, str):
            self.taxonomy = _load_taxonomy(taxonomy)
        else:
            self.taxonomy = taxonomy or _load_taxonomy(None)
        self.alias_map = _build_alias_map(self.taxonomy)
        self.patterns = _build_patterns(self.alias_map)

    def match(self, text: str | Iterable[str]) -> list[str]:
        joined_text = '\n'.join(text) if isinstance(text, Iterable) and not isinstance(text, str) else str(text)
        hits: list[tuple[int, int, str]] = []

        for pattern, canonical in self.patterns:
            for match in pattern.finditer(joined_text):
                hits.append((match.start(), -len(match.group(0)), canonical, match.end()))

        hits.sort()
        found: list[str] = []
        seen: set[str] = set()
        taken_spans: list[tuple[int, int]] = []

        for start, neg_length, canonical, end in hits:
            lower_canonical = canonical.lower()
            if lower_canonical in seen:
                continue

            overlaps = any(start < occupied_end and end > occupied_start for occupied_start, occupied_end in taken_spans)
            if overlaps:
                continue

            seen.add(lower_canonical)
            taken_spans.append((start, end))
            found.append(canonical)

        return found
