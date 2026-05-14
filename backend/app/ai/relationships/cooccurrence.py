from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Iterable, Sequence

from app.ai.relationships.utils import canonicalize_skill


class SkillCooccurrenceCounter:
    @staticmethod
    def count_pairs(skill_lists: Iterable[Sequence[str]]) -> tuple[Counter[tuple[str, str]], Counter[str]]:
        pair_counts: Counter[tuple[str, str]] = Counter()
        skill_document_counts: Counter[str] = Counter()

        for skills in skill_lists:
            normalized = [canonicalize_skill(skill) for skill in skills if skill and skill.strip()]
            unique_skills = list(dict.fromkeys(normalized))
            if not unique_skills:
                continue

            for skill in unique_skills:
                skill_document_counts[skill] += 1

            for a, b in combinations(unique_skills, 2):
                pair = tuple(sorted((a, b)))
                pair_counts[pair] += 1

        return pair_counts, skill_document_counts