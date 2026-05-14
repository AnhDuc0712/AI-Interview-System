from __future__ import annotations

from app.ai.relationships.graph_builder import RelationshipGraphBuilder
from app.ai.relationships.models import SkillRelationship


class SkillRelationshipUpdater:
    def __init__(self, min_pair_count: int = 2) -> None:
        self.builder = RelationshipGraphBuilder(min_pair_count=min_pair_count)

    def rebuild(self, skill_sets: list[list[str]]) -> list[SkillRelationship]:
        return self.builder.build(skill_sets)
