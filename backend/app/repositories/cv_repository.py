from datetime import datetime, timezone
import logging
import traceback
from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, ReturnDocument

from app.core.exceptions import AuthorizationError, ProcessingError
from app.db.client import db
from app.models.cv import (
    CVExtractionMetadata,
    CVMetadata,
    CVOwnership,
    CVParserMetadata,
    CVProcessingStatus,
    CVRecord,
    OriginalFileMetadata,
    StoredFileMetadata,
    StructuredCVData,
)

logger = logging.getLogger(__name__)

class CVRepository:
    def __init__(self) -> None:
        self.collection = db['cv_records']

    async def ensure_indexes(self) -> None:
        await self.collection.create_index(
            [('public_id', ASCENDING)],
            name='uq_cv_public_id',
            unique=True
        )
        await self.collection.create_index(
            [('ownership.user_public_id', ASCENDING), ('metadata.created_at', DESCENDING)],
            name='idx_cv_owner_created_at'
        )
        await self.collection.create_index(
            [('status', ASCENDING), ('metadata.updated_at', DESCENDING)],
            name='idx_cv_status_updated_at'
        )
        await self.collection.create_index(
            [
                ('ownership.user_public_id', ASCENDING),
                ('status', ASCENDING),
                ('metadata.created_at', DESCENDING)
            ],
            name='idx_cv_owner_status_created_at'
        )
        await self.collection.create_index(
            [('stored_file.checksum_sha256', ASCENDING)],
            name='idx_cv_checksum'
        )

    async def create_pending(
        self,
        *,
        public_id: str,
        ownership: CVOwnership,
        original_file: OriginalFileMetadata,
        stored_file: StoredFileMetadata
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        document = {
            'public_id': public_id,
            'ownership': ownership.model_dump(),
            'status': CVProcessingStatus.pending.value,
            'original_file': original_file.model_dump(),
            'stored_file': stored_file.model_dump(),
            'extraction': CVExtractionMetadata(
                extractor_name='unknown',
                extractor_version='unknown'
            ).model_dump(),
            'parser': CVParserMetadata(
                parser_name='unknown',
                parser_version='unknown'
            ).model_dump(),
            'normalized_content': None,
            'normalized_text': None,
            'metadata': CVMetadata(
                created_at=now,
                updated_at=now
            ).model_dump()
        }
        result = await self.collection.insert_one(document)
        document['_id'] = result.inserted_id
        return document

    async def mark_processing(
        self,
        public_id: str
    ) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        return await self.collection.find_one_and_update(
            {'public_id': public_id},
            {
                '$set': {
                    'status': CVProcessingStatus.processing.value,
                    'metadata.updated_at': now,
                    'metadata.processing_started_at': now,
                    'metadata.last_error': None
                }
            },
            return_document=ReturnDocument.AFTER
        )

    async def mark_completed(
        self,
        *,
        public_id: str,
        extraction: CVExtractionMetadata,
        parser: CVParserMetadata,
        normalized_text: str,
        normalized_content: StructuredCVData
    ) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        return await self.collection.find_one_and_update(
            {'public_id': public_id},
            {
                '$set': {
                    'status': CVProcessingStatus.completed.value,
                    'extraction': extraction.model_dump(),
                    'parser': parser.model_dump(),
                    'normalized_text': normalized_text,
                    'normalized_content': normalized_content if isinstance(normalized_content, dict) else normalized_content.model_dump(),
                    'metadata.updated_at': now,
                    'metadata.processing_completed_at': now,
                    'metadata.failed_at': None,
                    'metadata.last_error': None
                }
            },
            return_document=ReturnDocument.AFTER
        )

    async def mark_failed(self, public_id: str, error_message: str) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        return await self.collection.find_one_and_update(
            {'public_id': public_id},
            {
                '$set': {
                    'status': CVProcessingStatus.failed.value,
                    'metadata.updated_at': now,
                    'metadata.failed_at': now,
                    'metadata.last_error': error_message
                }
            },
            return_document=ReturnDocument.AFTER
        )

    async def list_by_owner(
        self,
        *,
        user_public_id: str,
        page: int,
        limit: int,
        status: CVProcessingStatus | None = None
    ) -> tuple[list[dict[str, Any]], int]:
        filters: dict[str, Any] = {'ownership.user_public_id': user_public_id}
        if status is not None:
            filters['status'] = status.value

        skip = (page - 1) * limit
        logger.info(
            'Executing CV list query filters=%s skip=%s limit=%s',
            filters,
            skip,
            limit
        )
        cursor = (
            self.collection
            .find(filters)
            .sort('metadata.created_at', DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        items = await cursor.to_list(length=limit)
        total = await self.collection.count_documents(filters)
        logger.info(
            'CV list query result user_public_id=%s count=%s total=%s sample_public_ids=%s',
            user_public_id,
            len(items),
            total,
            [item.get('public_id') for item in items[:3]]
        )
        return items, total

    async def get_by_public_id_for_owner(
        self,
        *,
        public_id: str,
        user_public_id: str
    ) -> dict[str, Any]:
        document = await self.collection.find_one(
            {
                'public_id': public_id,
                'ownership.user_public_id': user_public_id
            }
        )
        if document is None:
            raise AuthorizationError('You do not have access to this CV record')
        return document

    def deserialize(self, document: dict[str, Any] | None) -> CVRecord:
        if document is None:
            raise ProcessingError('CV record not found')

        serialized = self._convert_object_ids(document)
        try:
            return CVRecord.model_validate(serialized)
        except Exception as exc:
            logger.error(
                'Failed to deserialize CV record public_id=%s keys=%s: %s\nDocument=%s\n%s',
                serialized.get('public_id'),
                sorted(serialized.keys()),
                exc,
                serialized,
                traceback.format_exc()
            )
            raise

    def _convert_object_ids(self, data: Any) -> Any:
        if isinstance(data, list):
            return [self._convert_object_ids(item) for item in data]
        if isinstance(data, dict):
            return {k: self._convert_object_ids(v) for k, v in data.items()}
        if isinstance(data, ObjectId):
            return str(data)
        return data
