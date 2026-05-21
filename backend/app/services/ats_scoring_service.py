from __future__ import annotations

import logging
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING

from app.ai.skills.normalizer import normalize_skill
from app.core.exceptions import ProcessingError, ValidationError
from app.db.client import db

logger = logging.getLogger(__name__)


class ATSScoringService:
    def __init__(
        self,
        job_collection: AsyncIOMotorCollection | None = None,
        taxonomy_collection: AsyncIOMotorCollection | None = None,
    ) -> None:
        self.job_collection = job_collection or db['crawled_jobs']
        self.taxonomy_collection = taxonomy_collection or db['skill_taxonomy']

    async def ensure_ready(self) -> None:
        await self.job_collection.create_index(
            [('skills', ASCENDING)],
            name='idx_crawled_jobs_skills',
        )
        await self.taxonomy_collection.create_index(
            [('skill', ASCENDING)],
            unique=True,
            name='uq_skill_taxonomy_skill',
        )
        await self.taxonomy_collection.create_index(
            [('demand_count', DESCENDING)],
            name='idx_skill_taxonomy_demand_count_desc',
        )

    async def score_cv_against_job(
        self,
        cv_skills: list[str],
        *,
        job_id: str | None = None,
        job_url: str | None = None,
    ) -> dict[str, Any]:
        if not job_id and not job_url:
            raise ValidationError('Either job_id or job_url must be provided')

        filters = self._build_job_filter(job_id=job_id, job_url=job_url)
        try:
            job_document = await self.job_collection.find_one(
                filters,
                {
                    'title': 1,
                    'company': 1,
                    'source': 1,
                    'url': 1,
                    'skills': 1,
                },
            )
            if not job_document:
                raise ValidationError('Job not found')

            normalized_cv_skills = self._normalize_skills(cv_skills)
            return await self._score_job_document(job_document, normalized_cv_skills)
        except ValidationError:
            raise
        except Exception as exc:
            logger.exception('Failed to score CV against job')
            raise ProcessingError('Unable to score CV against job requirements') from exc

    async def score_cv_against_jobs(
        self,
        cv_skills: list[str],
        *,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        normalized_cv_skills = self._normalize_skills(cv_skills)
        if not normalized_cv_skills:
            return []

        try:
            demand_map = await self._load_market_demand(normalized_cv_skills)
            cursor = self.job_collection.find(
                {'skills': {'$in': list(normalized_cv_skills)}},
                {
                    'title': 1,
                    'company': 1,
                    'source': 1,
                    'url': 1,
                    'skills': 1,
                },
            ).limit(max(limit * 5, limit))

            results: list[dict[str, Any]] = []
            async for document in cursor:
                scored = await self._score_job_document(document, normalized_cv_skills, demand_map=demand_map)
                results.append(scored)

            results.sort(key=lambda item: item['match_score'], reverse=True)
            return results[:limit]
        except Exception as exc:
            logger.exception('Failed to score CV against multiple jobs')
            raise ProcessingError('Unable to score CV against market jobs') from exc

    async def _load_market_demand(self, skills: set[str]) -> dict[str, int]:
        if not skills:
            return {}

        demand_map: dict[str, int] = {}
        cursor = self.taxonomy_collection.find(
            {'skill': {'$in': list(skills)}},
            {'skill': 1, 'demand_count': 1},
        )
        async for document in cursor:
            skill = document.get('skill')
            if isinstance(skill, str):
                demand_map[skill] = int(document.get('demand_count', 0) or 0)
        return demand_map

    async def _score_job_document(
        self,
        job_document: dict[str, Any],
        normalized_cv_skills: set[str],
        demand_map: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        normalized_job_skills = self._normalize_skills(job_document.get('skills'))
        merged_demand_map = dict(demand_map or {})
        missing_demand_skills = normalized_job_skills - set(merged_demand_map)
        if missing_demand_skills:
            merged_demand_map.update(await self._load_market_demand(missing_demand_skills))

        matched_skills = sorted(
            normalized_cv_skills & normalized_job_skills,
            key=lambda skill: (-merged_demand_map.get(skill, 0), skill),
        )
        missing_skills = sorted(
            normalized_job_skills - normalized_cv_skills,
            key=lambda skill: (-merged_demand_map.get(skill, 0), skill),
        )

        demand_weight_total = sum(max(merged_demand_map.get(skill, 0), 1) for skill in normalized_job_skills)
        matched_demand_weight = sum(max(merged_demand_map.get(skill, 0), 1) for skill in matched_skills)
        coverage_score = len(matched_skills) / len(normalized_job_skills) if normalized_job_skills else 0.0
        demand_score = matched_demand_weight / demand_weight_total if demand_weight_total else 0.0
        match_score = round(((coverage_score * 0.6) + (demand_score * 0.4)) * 100, 2)

        return {
            'job': {
                'id': str(job_document.get('_id')) if job_document.get('_id') else None,
                'title': job_document.get('title'),
                'company': job_document.get('company'),
                'source': job_document.get('source'),
                'url': job_document.get('url'),
            },
            'match_score': match_score,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'market_demand': {skill: merged_demand_map.get(skill, 0) for skill in normalized_job_skills},
        }

    def _normalize_skills(self, raw_skills: Any) -> set[str]:
        if not isinstance(raw_skills, list):
            return set()
        normalized: set[str] = set()
        for raw_skill in raw_skills:
            if not isinstance(raw_skill, str):
                continue
            value = normalize_skill(raw_skill).strip()
            if value:
                normalized.add(value)
        return normalized

    def _build_job_filter(self, *, job_id: str | None, job_url: str | None) -> dict[str, Any]:
        if job_id:
            try:
                return {'_id': ObjectId(job_id)}
            except Exception as exc:
                raise ValidationError('job_id is not a valid ObjectId') from exc
        return {'url': job_url}


def get_ats_scoring_service() -> ATSScoringService:
    return ATSScoringService()
