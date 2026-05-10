import asyncio
from datetime import datetime, timezone

from app.models.user import AuthenticatedPrincipal
from app.services.user_sync import UserSyncService


class FakeUserRepository:
    def __init__(self) -> None:
        self.indexes_ensured = False

    async def ensure_indexes(self) -> None:
        self.indexes_ensured = True

    async def upsert_from_principal(self, principal: AuthenticatedPrincipal) -> dict:
        now = datetime.now(timezone.utc)
        return {
            '_id': '507f1f77bcf86cd799439011',
            'public_id': 'usr_abc',
            'role': 'candidate',
            'clerk': {
                'clerk_user_id': principal.clerk_user_id,
                'email': principal.email,
                'issuer': principal.issuer,
                'profile': {
                    'first_name': principal.first_name,
                    'last_name': principal.last_name,
                    'full_name': principal.full_name,
                    'username': principal.username,
                    'image_url': principal.image_url
                }
            },
            'profile': {
                'headline': None,
                'biography': None,
                'location': None,
                'timezone': None,
                'target_role': None,
                'years_of_experience': None,
                'skills': [],
                'preferences': {}
            },
            'metadata': {
                'created_at': now,
                'updated_at': now,
                'last_sign_in_at': now,
                'last_profile_updated_at': None,
                'clerk_synced_at': now,
                'profile_completion_score': 0,
                'profile_completion_fields_completed': 0,
                'profile_completion_fields_total': 6,
                'profile_completed_at': None
            },
            'state': {
                'is_deleted': False,
                'deleted_at': None
            }
        }

    def deserialize(self, document: dict):
        from app.repositories.user_repository import UserRepository
        return UserRepository().deserialize(document)


def test_user_sync_service_creates_user_document():
    repository = FakeUserRepository()
    service = UserSyncService(repository=repository)
    principal = AuthenticatedPrincipal(
        clerk_user_id='user_abc',
        session_id='sess_abc',
        email='candidate@example.com',
        first_name='Ada',
        last_name='Lovelace',
        full_name='Ada Lovelace',
        username='ada',
        image_url='https://example.com/ada.png'
    )

    user = asyncio.run(service.sync_authenticated_user(principal))

    assert user.id == '507f1f77bcf86cd799439011'
    assert user.clerk.clerk_user_id == 'user_abc'
    assert user.clerk.profile.full_name == 'Ada Lovelace'
    assert user.public_id == 'usr_abc'


def test_user_sync_service_ensures_indexes():
    repository = FakeUserRepository()
    service = UserSyncService(repository=repository)

    asyncio.run(service.ensure_indexes())

    assert repository.indexes_ensured is True
