from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, UpdateOne

from app.ai.skills.normalizer import normalize_skill
from app.core.exceptions import ProcessingError
from app.db.client import db

logger = logging.getLogger(__name__)


class SkillTaxonomyBuilder:
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
        await self.taxonomy_collection.create_index(
            [('skill', ASCENDING)],
            unique=True,
            name='uq_skill_taxonomy_skill',
        )
        await self.taxonomy_collection.create_index(
            [('source', ASCENDING), ('demand_count', ASCENDING)],
            name='idx_skill_taxonomy_source_demand_count',
        )
        await self.taxonomy_collection.create_index(
            [('last_rebuilt_at', ASCENDING)],
            name='idx_skill_taxonomy_last_rebuilt_at',
        )

    async def rebuild(self) -> dict[str, int]:
        try:
            frequency_counter: Counter[str] = Counter()
            cooccurrence_counter: dict[str, Counter[str]] = defaultdict(Counter)
            processed_jobs = 0
            rebuild_started_at = datetime.now(timezone.utc)

            cursor = self.job_collection.find(
                {'skills': {'$exists': True, '$type': 'array'}},
                {'skills': 1},
            ).batch_size(self.batch_size)

            while True:
                batch = await cursor.to_list(length=self.batch_size)
                if not batch:
                    break

                for document in batch:
                    normalized_skills = self._normalize_skills(document.get('skills'))
                    if not normalized_skills:
                        continue

                    processed_jobs += 1
                    frequency_counter.update(normalized_skills)
                    self._update_cooccurrence_counts(normalized_skills, cooccurrence_counter)

            await self._persist_taxonomy(
                frequency_counter=frequency_counter,
                cooccurrence_counter=cooccurrence_counter,
                processed_jobs=processed_jobs,
                rebuilt_at=rebuild_started_at,
            )

            logger.info(
                'Skill taxonomy rebuilt from crawled jobs. processed_jobs=%s unique_skills=%s',
                processed_jobs,
                len(frequency_counter),
            )

            return {
                'processed_jobs': processed_jobs,
                'unique_skills': len(frequency_counter),
            }
        except Exception as exc:
            logger.exception('Failed to rebuild skill taxonomy')
            raise ProcessingError('Unable to rebuild skill taxonomy from crawled jobs') from exc

    async def _persist_taxonomy(
        self,
        *,
        frequency_counter: Counter[str],
        cooccurrence_counter: dict[str, Counter[str]],
        processed_jobs: int,
        rebuilt_at: datetime,
    ) -> None:
        operations: list[UpdateOne] = []

        for skill, demand_count in frequency_counter.items():
            related_skills = [
                {'skill': related_skill, 'count': count}
                for related_skill, count in cooccurrence_counter[skill].most_common()
            ]
            operations.append(
                UpdateOne(
                    {'skill': skill},
                    {
                        '$set': {
                            'skill': skill,
                            'source': 'crawled_jobs',
                            'demand_count': demand_count,
                            'job_document_count': processed_jobs,
                            'related_skills': related_skills,
                            'last_rebuilt_at': rebuilt_at,
                            'updated_at': rebuilt_at,
                        },
                        '$setOnInsert': {
                            'created_at': rebuilt_at,
                        },
                    },
                    upsert=True,
                )
            )

        if operations:
            await self.taxonomy_collection.bulk_write(operations, ordered=False)

        await self.taxonomy_collection.delete_many(
            {
                'source': 'crawled_jobs',
                'last_rebuilt_at': {'$lt': rebuilt_at},
            }
        )

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

    def _update_cooccurrence_counts(
        self,
        skills: list[str],
        cooccurrence_counter: dict[str, Counter[str]],
    ) -> None:
        if len(skills) < 2:
            return

        for skill_a, skill_b in combinations(sorted(skills), 2):
            cooccurrence_counter[skill_a][skill_b] += 1
            cooccurrence_counter[skill_b][skill_a] += 1


def get_skill_taxonomy_builder() -> SkillTaxonomyBuilder:
    return SkillTaxonomyBuilder()
