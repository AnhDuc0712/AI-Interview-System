from functools import lru_cache
import logging
import traceback

from app.models.user import User
from app.repositories.cv_repository import CVRepository
from app.schemas.cv import CVListResponse, PaginationMeta
from app.models.cv import CVProcessingStatus, CVRecord

logger = logging.getLogger(__name__)


class CVQueryService:
    def __init__(self, repository: CVRepository | None = None) -> None:
        self.repository = repository or CVRepository()

    async def list_my_cvs(
        self,
        *,
        user: User,
        page: int,
        limit: int,
        status: CVProcessingStatus | None = None
    ) -> CVListResponse:
        logger.info(
            'Listing CVs for user_public_id=%s page=%s limit=%s status=%s',
            user.public_id,
            page,
            limit,
            status.value if status else None
        )
        try:
            documents, total = await self.repository.list_by_owner(
                user_public_id=user.public_id,
                page=page,
                limit=limit,
                status=status
            )
            logger.info(
                'Mongo query returned %s items out of total=%s for user_public_id=%s',
                len(documents),
                total,
                user.public_id
            )
            items = [self.repository.deserialize(document) for document in documents]
            total_pages = max(1, (total + limit - 1) // limit) if total else 1
            return CVListResponse(
                items=items,
                pagination=PaginationMeta(
                    page=page,
                    limit=limit,
                    total=total,
                    total_pages=total_pages
                )
            )
        except Exception as exc:
            logger.error(
                'Failed to list CVs for user_public_id=%s page=%s limit=%s status=%s: %s\n%s',
                user.public_id,
                page,
                limit,
                status.value if status else None,
                exc,
                traceback.format_exc()
            )
            raise

    async def get_my_cv_detail(self, *, user: User, public_id: str) -> CVRecord:
        document = await self.repository.get_by_public_id_for_owner(
            public_id=public_id,
            user_public_id=user.public_id
        )
        return self.repository.deserialize(document)


@lru_cache
def get_cv_query_service() -> CVQueryService:
    return CVQueryService()
