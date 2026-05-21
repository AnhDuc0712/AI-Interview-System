from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from app.ai.skills.categorizer import categorize_skills
from app.ai.skills.extractor import SkillExtractionEngine
from app.ai.skills.matcher import SkillMatcher
from app.ai.skills.normalizer import normalize_skills
from app.db.client import db
from app.models.cv import CVParserMetadata, StructuredCVData, StructuredCVPersonalInfo
from app.services.cv_parser import StructuredCVParserService
from app.services.hybrid_cv_parser import HybridCVParserService

logger = logging.getLogger(__name__)


class SmartCVParserService:
    parser_name = 'smart-cv-parser'
    parser_version = 'v1'

    def __init__(
        self,
        llm_parser: HybridCVParserService | None = None,
        rule_parser: StructuredCVParserService | None = None,
        job_collection: AsyncIOMotorCollection | None = None,
        skill_engine: SkillExtractionEngine | None = None,
        similar_job_limit: int = 5,
        similar_job_scan_limit: int = 200,
    ) -> None:
        self.llm_parser = llm_parser or HybridCVParserService()
        self.rule_parser = rule_parser or StructuredCVParserService()
        self.job_collection = job_collection or db['crawled_jobs']
        self.skill_engine = skill_engine or SkillExtractionEngine()
        self.skill_matcher = SkillMatcher()
        self.similar_job_limit = similar_job_limit
        self.similar_job_scan_limit = similar_job_scan_limit

    async def parse(self, normalized_text: str) -> tuple[StructuredCVData, CVParserMetadata]:
        llm_data = await self._parse_with_llm(normalized_text)
        rule_data, _ = self.rule_parser.parse(normalized_text)

        base_data = llm_data or rule_data
        merged_data = self._merge_structured_data(base_data, rule_data)

        raw_text_skills = self.skill_engine.extract(normalized_text).skills
        candidate_skills = normalize_skills(merged_data.skills + raw_text_skills)
        similar_jobs = await self._find_similar_jobs(candidate_skills)
        market_validated_skills = self._extract_market_validated_skills(normalized_text, similar_jobs)

        final_skills = normalize_skills(candidate_skills + market_validated_skills)
        merged_data.skills = final_skills
        merged_data.categorized_skills = categorize_skills(final_skills, self.skill_engine.matcher.taxonomy)
        merged_data.raw_sections = dict(merged_data.raw_sections)
        merged_data.raw_sections['similar_jobs'] = [
            f"{job['title']} | {job['company']} | score={job['similarity_score']:.3f}"
            for job in similar_jobs
        ]

        metadata = CVParserMetadata(
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            parsed_at=datetime.now(timezone.utc),
        )
        return merged_data, metadata

    async def _parse_with_llm(self, normalized_text: str) -> StructuredCVData | None:
        try:
            parsed_content, _ = await self.llm_parser.parse(normalized_text)
            if not parsed_content:
                return None
            if isinstance(parsed_content, StructuredCVData):
                return parsed_content
            if isinstance(parsed_content, dict):
                return StructuredCVData.model_validate(parsed_content)
            return None
        except Exception:
            logger.exception('SmartCVParserService failed to parse with LLM parser. Falling back to rule parser.')
            return None

    async def _find_similar_jobs(self, cv_skills: list[str]) -> list[dict[str, Any]]:
        normalized_cv_skills = {skill for skill in cv_skills if skill}
        if not normalized_cv_skills:
            return []

        cursor = self.job_collection.find(
            {'skills': {'$in': list(normalized_cv_skills)}},
            {
                'title': 1,
                'company': 1,
                'source': 1,
                'url': 1,
                'skills': 1,
            },
        ).limit(self.similar_job_scan_limit)

        scored_jobs: list[dict[str, Any]] = []
        async for document in cursor:
            job_skills = set(normalize_skills([skill for skill in document.get('skills', []) if isinstance(skill, str)]))
            if not job_skills:
                continue

            overlap = normalized_cv_skills & job_skills
            if not overlap:
                continue

            union = normalized_cv_skills | job_skills
            similarity_score = len(overlap) / len(union) if union else 0.0
            scored_jobs.append(
                {
                    'title': document.get('title') or 'Unknown title',
                    'company': document.get('company') or 'Unknown company',
                    'source': document.get('source'),
                    'url': document.get('url'),
                    'skills': sorted(job_skills),
                    'overlap_skills': sorted(overlap),
                    'similarity_score': similarity_score,
                }
            )

        scored_jobs.sort(
            key=lambda item: (item['similarity_score'], len(item['overlap_skills'])),
            reverse=True,
        )
        return scored_jobs[:self.similar_job_limit]

    def _extract_market_validated_skills(
        self,
        normalized_text: str,
        similar_jobs: list[dict[str, Any]],
    ) -> list[str]:
        if not similar_jobs:
            return []

        text_hits = set(self.skill_matcher.match(normalized_text))
        job_skills = [
            skill
            for job in similar_jobs
            for skill in job.get('skills', [])
            if isinstance(skill, str)
        ]
        confirmed_skills = [skill for skill in job_skills if skill in text_hits]
        return normalize_skills(confirmed_skills)

    def _merge_structured_data(
        self,
        primary: StructuredCVData,
        fallback: StructuredCVData,
    ) -> StructuredCVData:
        merged = StructuredCVData.model_validate(primary.model_dump())

        primary_personal = primary.personal_info.model_dump()
        fallback_personal = fallback.personal_info.model_dump()
        merged.personal_info = StructuredCVPersonalInfo.model_validate(
            {
                key: primary_personal.get(key) or fallback_personal.get(key)
                for key in set(primary_personal) | set(fallback_personal)
            }
        )

        merged.skills = normalize_skills(primary.skills + fallback.skills)
        merged.experience = primary.experience or fallback.experience
        merged.education = primary.education or fallback.education
        merged.projects = primary.projects or fallback.projects
        merged.certifications = primary.certifications or fallback.certifications
        merged.languages = primary.languages or fallback.languages

        merged.raw_sections = {
            **fallback.raw_sections,
            **primary.raw_sections,
        }
        return merged


def get_smart_cv_parser_service() -> SmartCVParserService:
    return SmartCVParserService()
