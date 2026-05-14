from __future__ import annotations

from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from app.ai.relationships.graph_builder import RelationshipGraphBuilder
from app.ai.relationships.utils import extract_unknown_tokens
from app.ai.skills.extractor import SkillExtractionEngine
from app.db.client import db


class SkillRelationshipService:
    def __init__(
        self,
        relationship_collection: AsyncIOMotorCollection | None = None,
        observation_collection: AsyncIOMotorCollection | None = None,
        cv_collection: AsyncIOMotorCollection | None = None,
        job_collection: AsyncIOMotorCollection | None = None,
        skill_engine: SkillExtractionEngine | None = None,
        min_pair_count: int | None = None,
    ) -> None:
        self.relationship_collection = relationship_collection or db['skill_relationships']
        self.observation_collection = observation_collection or db['skill_observations']
        self.cv_collection = cv_collection or db['cv_records']
        self.job_collection = job_collection or db['crawled_jobs']
        self.skill_engine = skill_engine or SkillExtractionEngine()
        self.min_pair_count = min_pair_count if min_pair_count is not None else 1

    async def ensure_ready(self) -> None:
        await self.relationship_collection.create_index(
            [('skill', ASCENDING)],
            unique=True,
            name='uq_skill_relationship_skill'
        )
        await self.relationship_collection.create_index(
            [('updated_at', DESCENDING)],
            name='idx_skill_relationship_updated_at'
        )

        await self.observation_collection.create_index(
            [('token', ASCENDING), ('source', ASCENDING)],
            unique=True,
            name='uq_skill_observation_token_source'
        )
        await self.observation_collection.create_index(
            [('frequency', DESCENDING)],
            name='idx_skill_observation_frequency'
        )

    async def rebuild_graph(self) -> dict[str, int]:
        skill_sets: list[list[str]] = []
        cv_count = 0
        job_count = 0

        async for document in self.cv_collection.find({'normalized_content.skills': {'$exists': True}}):
            skills = document.get('normalized_content', {}).get('skills', [])
            if skills:
                skill_sets.append(skills)
                cv_count += 1

        async for document in self.job_collection.find({'skills': {'$exists': True}}):
            skills = document.get('skills', [])
            if skills:
                skill_sets.append(skills)
                job_count += 1

        builder = RelationshipGraphBuilder(min_pair_count=self.min_pair_count)
        relationship_documents = builder.build(skill_sets)

        await self.relationship_collection.delete_many({})
        if relationship_documents:
            await self.relationship_collection.insert_many([
                rel.model_dump() for rel in relationship_documents
            ])

        await self.rebuild_observations()

        return {
            'documents_processed': cv_count + job_count,
            'cv_documents': cv_count,
            'job_documents': job_count,
            'relationships_created': len(relationship_documents),
        }

    async def rebuild_observations(self) -> int:
        await self.observation_collection.delete_many({})
        observed = 0

        async for document in self.cv_collection.find({'normalized_content.skills': {'$exists': True}}):
            skills = document.get('normalized_content', {}).get('skills', [])
            raw_text = document.get('normalized_text', '')
            observed += await self._record_unknown_tokens(raw_text, skills, 'cv')

        async for document in self.job_collection.find({'skills': {'$exists': True}}):
            skills = document.get('skills', [])
            raw_text = document.get('raw_description', '')
            observed += await self._record_unknown_tokens(raw_text, skills, 'job')

        return observed

    async def update_from_document(
        self,
        skills: list[str],
        raw_text: str | None = None,
        source: str = 'unknown'
    ) -> None:
        unique_skills = self._normalize(skills)
        if unique_skills:
            await self._increment_cooccurrence_pairs(unique_skills)
        if raw_text:
            await self._record_unknown_tokens(raw_text, unique_skills, source)

    async def _increment_cooccurrence_pairs(self, skills: list[str]) -> None:
        unique_skills = list(dict.fromkeys(skill.strip() for skill in skills if skill and skill.strip()))
        if len(unique_skills) < 2:
            return

        pairs = []
        for i in range(len(unique_skills)):
            for j in range(i + 1, len(unique_skills)):
                pairs.append((unique_skills[i], unique_skills[j]))

        for skill_a, skill_b in pairs:
            await self._upsert_relationship(skill_a, skill_b)
            await self._upsert_relationship(skill_b, skill_a)

    async def _upsert_relationship(self, skill: str, related_skill: str) -> None:
        now = datetime.utcnow()
        result = await self.relationship_collection.find_one_and_update(
            {'skill': skill, 'related_skills.skill': related_skill},
            {
                '$inc': {
                    'related_skills.$.count': 1,
                    'total_cooccurrence_count': 1,
                },
                '$set': {'updated_at': now},
            },
            return_document=ReturnDocument.AFTER,
        )

        if result is None:
            await self.relationship_collection.update_one(
                {'skill': skill},
                {
                    '$inc': {'total_cooccurrence_count': 1},
                    '$setOnInsert': {'skill': skill, 'updated_at': now},
                    '$push': {
                        'related_skills': {
                            'skill': related_skill,
                            'count': 1,
                            'weight': 0.0,
                        }
                    },
                },
                upsert=True,
            )
            result = await self.relationship_collection.find_one({'skill': skill})

        await self._recalculate_weights(skill, result)

    async def _recalculate_weights(self, skill: str, document: dict[str, Any] | None = None) -> None:
        if document is None:
            document = await self.relationship_collection.find_one({'skill': skill})
        if not document:
            return

        total = document.get('total_cooccurrence_count', 0) or 1
        updates: dict[str, float] = {}

        for index, related in enumerate(document.get('related_skills', [])):
            weight = round(related.get('count', 0) / total, 4)
            updates[f'related_skills.{index}.weight'] = weight

        if updates:
            await self.relationship_collection.update_one(
                {'skill': skill},
                {'$set': updates},
            )

    async def _record_unknown_tokens(
        self,
        raw_text: str,
        known_skills: list[str],
        source: str,
    ) -> int:
        unknown_tokens = extract_unknown_tokens(raw_text, known_skills)
        if not unknown_tokens:
            return 0

        now = datetime.utcnow()
        recorded = 0
        for token in unknown_tokens:
            await self.observation_collection.update_one(
                {'token': token, 'source': source},
                {
                    '$inc': {'frequency': 1},
                    '$set': {'updated_at': now},
                    '$setOnInsert': {
                        'token': token,
                        'source': source,
                        'created_at': now,
                    },
                    '$addToSet': {'context_skills': {'$each': known_skills}},
                },
                upsert=True,
            )
            recorded += 1

        return recorded

    def _normalize(self, skills: list[str]) -> list[str]:
        return [skill.strip() for skill in skills if skill and skill.strip()]


def get_skill_relationship_service() -> SkillRelationshipService:
    return SkillRelationshipService()
