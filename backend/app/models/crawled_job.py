from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CrawledJob(BaseModel):
    title: str
    company: str
    location: str | None = None
    experience_level: str | None = None
    description: str
    requirements: str | None = None
    skills_raw: str | None = None
    source: str
    url: str
    raw_description: str | None = None
    skills: list[str] = Field(default_factory=list)
    categorized_skills: dict[str, list[str]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
