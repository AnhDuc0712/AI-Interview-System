from __future__ import annotations

from pydantic import BaseModel, Field

from app.ai.skills.categorizer import categorize_skills
from app.ai.skills.matcher import SkillMatcher
from app.ai.skills.normalizer import normalize_skills


# The SkillExtractionEngine is the reusable entrypoint for CV skill processing.
# It keeps extraction, normalization, and categorization separate to support
# future pipeline extensions such as AI-based skill scoring.


class SkillExtractionResult(BaseModel):
    skills: list[str] = Field(default_factory=list)
    categorized_skills: dict[str, list[str]] = Field(default_factory=dict)


class SkillExtractionEngine:
    def __init__(self, taxonomy_path: str | None = None) -> None:
        self.matcher = SkillMatcher(None if taxonomy_path is None else taxonomy_path)

    def extract(self, raw_text: str, section_lines: list[str] | None = None) -> SkillExtractionResult:
        matched_skills: list[str] = []

        if section_lines:
            matched_skills.extend(self.matcher.match(section_lines))
        else:
            matched_skills.extend(self.matcher.match(raw_text))

        skills = normalize_skills(matched_skills)
        categorized = categorize_skills(skills, self.matcher.taxonomy)

        return SkillExtractionResult(
            skills=skills,
            categorized_skills=categorized,
        )
