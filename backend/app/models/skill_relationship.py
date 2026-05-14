from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SkillRelationshipEdge(BaseModel):
    skill: str
    count: int
    weight: float


class SkillRelationshipRecord(BaseModel):
    skill: str
    related_skills: list[SkillRelationshipEdge] = Field(default_factory=list)
    total_cooccurrence_count: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)
