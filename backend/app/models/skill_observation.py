from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SkillObservationRecord(BaseModel):
    token: str
    source: str
    context_skills: list[str] = Field(default_factory=list)
    frequency: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
