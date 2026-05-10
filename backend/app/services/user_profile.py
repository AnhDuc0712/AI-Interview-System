from functools import lru_cache

from app.core.exceptions import AuthorizationError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.users import ProfileCompletionSummary, UpdateMyProfileRequest


class UserProfileService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    async def get_my_profile(self, user: User) -> User:
        self._ensure_active_user(user)
        return user

    async def update_my_profile(
        self,
        user: User,
        payload: UpdateMyProfileRequest
    ) -> User:
        self._ensure_active_user(user)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return user

        merged_profile = user.profile.model_dump()
        merged_profile.update(updates)

        document = await self.repository.update_profile_by_public_id(
            public_id=user.public_id,
            profile_updates=merged_profile
        )
        return self.repository.deserialize(document)

    def build_profile_completion(self, user: User) -> ProfileCompletionSummary:
        return ProfileCompletionSummary(
            score=user.metadata.profile_completion_score,
            fields_completed=user.metadata.profile_completion_fields_completed,
            fields_total=user.metadata.profile_completion_fields_total,
            is_complete=user.metadata.profile_completion_score == 100
        )

    @staticmethod
    def _ensure_active_user(user: User) -> None:
        if user.state.is_deleted:
            raise AuthorizationError('User account is deactivated')


@lru_cache
def get_user_profile_service() -> UserProfileService:
    return UserProfileService()
