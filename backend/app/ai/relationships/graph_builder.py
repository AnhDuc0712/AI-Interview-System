from __future__ import annotations

from datetime import datetime
from typing import Iterable, Sequence

from app.ai.relationships.cooccurrence import SkillCooccurrenceCounter
from app.ai.relationships.models import SkillRelationship
from app.ai.relationships.scoring import RelationshipScorer


class RelationshipGraphBuilder:
    def __init__(self, min_pair_count: int = 1) -> None:
        self.min_pair_count = min_pair_count

    def build(self, skill_sets: Iterable[Sequence[str]]) -> list[SkillRelationship]:
        pair_counts, skill_document_counts = SkillCooccurrenceCounter.count_pairs(skill_sets)
        relationship_scores = RelationshipScorer.score_relationships(
            pair_counts,
            skill_document_counts,
            min_pair_count=self.min_pair_count,
        )

        relationship_documents: list[SkillRelationship] = []
        now = datetime.utcnow()

        for skill, relations in sorted(relationship_scores.items()):
            related_skills = [
                {
                    'skill': related,
                    'count': pair_counts[tuple(sorted((skill, related)))],
                    'weight': relations[related],
                }
                for related in sorted(relations, key=lambda value: (-relations[value], value))
            ]
            total_count = sum(item['count'] for item in related_skills)

            relationship_documents.append(
                SkillRelationship(
                    skill=skill,
                    related_skills=related_skills,
                    total_cooccurrence_count=total_count,
                    updated_at=now,
                )
            )

        return relationship_documents