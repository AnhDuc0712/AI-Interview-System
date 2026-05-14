from __future__ import annotations

from collections import Counter
from typing import Dict


class RelationshipScorer:
    @staticmethod
    def score_relationships(
        pair_counts: Counter[tuple[str, str]],
        skill_document_counts: Counter[str],
        min_pair_count: int = 2,
    ) -> dict[str, dict[str, float]]:
        relationship_scores: dict[str, dict[str, float]] = {}

        for (skill_a, skill_b), count in sorted(pair_counts.items()):
            if count < min_pair_count:
                continue

            total_a = skill_document_counts.get(skill_a, 0) or 1
            total_b = skill_document_counts.get(skill_b, 0) or 1

            score_a = round(count / total_a, 4)
            score_b = round(count / total_b, 4)

            relationship_scores.setdefault(skill_a, {})[skill_b] = score_a
            relationship_scores.setdefault(skill_b, {})[skill_a] = score_b

        return relationship_scores