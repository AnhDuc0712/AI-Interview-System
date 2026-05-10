from functools import lru_cache

from app.models.user import AuthenticatedPrincipal, User
from app.repositories.user_repository import UserRepository


class UserSyncService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    async def sync_authenticated_user(self, principal: AuthenticatedPrincipal) -> User:
        document = await self.repository.upsert_from_principal(principal)
        return self.repository.deserialize(document)

    async def ensure_indexes(self) -> None:
        await self.repository.ensure_indexes()


@lru_cache
def get_user_sync_service() -> UserSyncService:
    return UserSyncService()
