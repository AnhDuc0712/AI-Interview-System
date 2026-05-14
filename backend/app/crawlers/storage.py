from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.db.client import db
from app.models.crawled_job import CrawledJob

logger = logging.getLogger(__name__)


class JobStorage:
    def __init__(self, collection_name: str = 'crawled_jobs') -> None:
        self.collection = db[collection_name]

    async def ensure_ready(self) -> None:
        await self.collection.create_index(
            [('url', ASCENDING)],
            unique=True,
            name='uq_crawled_job_url'
        )
        await self.collection.create_index(
            [('source', ASCENDING), ('created_at', ASCENDING)],
            name='idx_crawled_job_source_created_at'
        )

    async def exists(self, url: str) -> bool:
        document = await self.collection.find_one({'url': url}, {'_id': 1})
        return document is not None

    async def save_job_if_new(self, job: CrawledJob) -> dict[str, Any]:
        document = job.model_dump()
        document['created_at'] = document.get('created_at', datetime.utcnow())

        try:
            result = await self.collection.insert_one(document)
            document['_id'] = result.inserted_id
            return document
        except DuplicateKeyError:
            existing = await self.collection.find_one({'url': job.url})
            return existing or document

    def deserialize(self, document: dict[str, Any] | None) -> CrawledJob:
        if document is None:
            raise ValueError('Job document not found')

        serialized = self._convert_object_ids(document)
        return CrawledJob.model_validate(serialized)

    def _convert_object_ids(self, data: Any) -> Any:
        if isinstance(data, list):
            return [self._convert_object_ids(item) for item in data]
        if isinstance(data, dict):
            return {k: self._convert_object_ids(v) for k, v in data.items()}
        if isinstance(data, ObjectId):
            return str(data)
        return data
