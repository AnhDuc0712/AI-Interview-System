from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING

from app.ai.skills.normalizer import normalize_skill
from app.core.exceptions import ProcessingError
from app.db.client import db

logger = logging.getLogger(__name__)


class SkillSuggestionService:
    def __init__(
        self,
        job_collection: AsyncIOMotorCollection | None = None,
        taxonomy_collection: AsyncIOMotorCollection | None = None,
        batch_size: int = 500,
    ) -> None:
        if batch_size <= 0:
            raise ValueError('batch_size must be greater than 0')

        self.job_collection = job_collection or db['crawled_jobs']
        self.taxonomy_collection = taxonomy_collection or db['skill_taxonomy']
        self.batch_size = batch_size

    async def ensure_ready(self) -> None:
        await self.job_collection.create_index(
            [('created_at', DESCENDING)],
            name='idx_crawled_jobs_created_at_desc',
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

    async def suggest_hot_skills(self, *, limit: int = 10, days: int = 30) -> list[dict[str, Any]]:
        try:
            counts = await self._count_recent_skills(days=days)
            if not counts:
                return await self._load_taxonomy_hot_skills(limit=limit)
            return [
                {
                    'skill': skill,
                    'demand_count': demand_count,
                    'reason': f'Appears in {demand_count} recent job postings',
                }
                for skill, demand_count in counts.most_common(limit)
            ]
        except Exception as exc:
            logger.exception('Failed to compute hot skills')
            raise ProcessingError('Unable to compute hot skill suggestions') from exc

    async def suggest_for_cv(
        self,
        cv_skills: list[str],
        *,
        limit: int = 10,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        normalized_cv_skills = self._normalize_skills(cv_skills)
        if not normalized_cv_skills:
            return await self.suggest_hot_skills(limit=limit, days=days)

        try:
            recent_counts = await self._count_recent_skills(days=days)
            suggestion_scores: dict[str, float] = defaultdict(float)
            source_skill_map: dict[str, set[str]] = defaultdict(set)

            cursor = self.taxonomy_collection.find(
                {'skill': {'$in': list(normalized_cv_skills)}},
                {'skill': 1, 'related_skills': 1},
            )
            async for document in cursor:
                source_skill = document.get('skill')
                if not isinstance(source_skill, str):
                    continue
                for related in document.get('related_skills', []):
                    related_skill = related.get('skill')
                    if not isinstance(related_skill, str) or related_skill in normalized_cv_skills:
                        continue

                    cooccurrence_count = int(related.get('count', 0) or 0)
                    market_count = recent_counts.get(related_skill, 0)
                    score = (cooccurrence_count * 2.0) + float(market_count)
                    if score <= 0:
                        continue

                    suggestion_scores[related_skill] += score
                    source_skill_map[related_skill].add(source_skill)

            ranked_skills = sorted(
                suggestion_scores.items(),
                key=lambda item: (-item[1], -recent_counts.get(item[0], 0), item[0]),
            )

            suggestions = [
                {
                    'skill': skill,
                    'score': round(score, 2),
                    'market_demand': recent_counts.get(skill, 0),
                    'based_on_skills': sorted(source_skill_map.get(skill, set())),
                    'reason': self._build_reason(
                        skill=skill,
                        market_demand=recent_counts.get(skill, 0),
                        source_skills=source_skill_map.get(skill, set()),
                    ),
                }
                for skill, score in ranked_skills[:limit]
            ]

            if suggestions:
                return suggestions
            return await self.suggest_hot_skills(limit=limit, days=days)
        except Exception as exc:
            logger.exception('Failed to compute personalized skill suggestions')
            raise ProcessingError('Unable to compute personalized skill suggestions') from exc

    async def _count_recent_skills(self, *, days: int) -> Counter[str]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=max(days, 1))
        counter: Counter[str] = Counter()

        cursor = self.job_collection.find(
            {
                'skills': {'$exists': True, '$type': 'array'},
                'created_at': {'$gte': cutoff},
            },
            {'skills': 1},
        ).batch_size(self.batch_size)

        while True:
            batch = await cursor.to_list(length=self.batch_size)
            if not batch:
                break
            for document in batch:
                counter.update(self._normalize_skills(document.get('skills')))

        return counter

    async def _load_taxonomy_hot_skills(self, *, limit: int) -> list[dict[str, Any]]:
        suggestions: list[dict[str, Any]] = []
        cursor = self.taxonomy_collection.find(
            {'source': 'crawled_jobs'},
            {'skill': 1, 'demand_count': 1},
        ).sort('demand_count', DESCENDING).limit(limit)

        async for document in cursor:
            skill = document.get('skill')
            if not isinstance(skill, str):
                continue
            demand_count = int(document.get('demand_count', 0) or 0)
            suggestions.append(
                {
                    'skill': skill,
                    'demand_count': demand_count,
                    'reason': f'Appears in {demand_count} job postings in the taxonomy',
                }
            )
        return suggestions

    def _normalize_skills(self, raw_skills: Any) -> list[str]:
        if not isinstance(raw_skills, list):
            return []

        normalized: list[str] = []
        seen: set[str] = set()
        for raw_skill in raw_skills:
            if not isinstance(raw_skill, str):
                continue
            skill = normalize_skill(raw_skill).strip()
            normalized_key = skill.lower()
            if not normalized_key or normalized_key in seen:
                continue
            seen.add(normalized_key)
            normalized.append(skill)
        return normalized

    def _build_reason(self, *, skill: str, market_demand: int, source_skills: set[str]) -> str:
        if source_skills:
            source_list = ', '.join(sorted(source_skills))
            return f'Pairs well with {source_list} and appears in {market_demand} recent jobs'
        return f'Appears in {market_demand} recent job postings'


def get_skill_suggestion_service() -> SkillSuggestionService:
    return SkillSuggestionService()
