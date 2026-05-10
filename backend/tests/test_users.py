from fastapi.testclient import TestClient

from app.dependencies.auth import get_current_user
from app.dependencies.users import get_user_profile_dependency
from app.main import app
from app.models.user import (
    ClerkManagedUserData,
    ClerkProfile,
    User,
    UserMetadata,
    UserProfile,
    UserRole,
    UserState,
)
from app.schemas.users import UpdateMyProfileRequest
from app.services.user_profile import UserProfileService


def _build_user() -> User:
    return User(
        _id='507f1f77bcf86cd799439011',
        public_id='usr_profile_1',
        role=UserRole.candidate,
        clerk=ClerkManagedUserData(
            clerk_user_id='user_profile_1',
            email='profile@example.com',
            issuer='https://example.clerk.accounts.dev',
            profile=ClerkProfile(
                first_name='Profile',
                last_name='Owner',
                full_name='Profile Owner',
                username='profile.owner',
                image_url='https://example.com/profile.png'
            )
        ),
        profile=UserProfile(
            headline='AI Engineer',
            biography='Building adaptive interview experiences',
            location='Singapore',
            timezone='Asia/Singapore',
            target_role='ML Platform Engineer',
            years_of_experience=6,
            skills=['Python', 'LLMs'],
            preferences={'practice_mode': 'adaptive'}
        ),
        metadata=UserMetadata(
            created_at='2026-05-08T00:00:00Z',
            updated_at='2026-05-08T00:00:00Z',
            last_sign_in_at='2026-05-08T00:00:00Z',
            last_profile_updated_at='2026-05-08T00:00:00Z',
            clerk_synced_at='2026-05-08T00:00:00Z',
            profile_completion_score=100,
            profile_completion_fields_completed=6,
            profile_completion_fields_total=6,
            profile_completed_at='2026-05-08T00:00:00Z'
        ),
        state=UserState(is_deleted=False, deleted_at=None)
    )


class FakeUserProfileService(UserProfileService):
    async def get_my_profile(self, user: User) -> User:
        return user

    async def update_my_profile(
        self,
        user: User,
        payload: UpdateMyProfileRequest
    ) -> User:
        updated = user.model_copy(deep=True)
        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(updated.profile, field, value)
        updated.metadata.profile_completion_score = 83
        updated.metadata.profile_completion_fields_completed = 5
        updated.metadata.profile_completion_fields_total = 6
        return updated


async def _override_current_user() -> User:
    return _build_user()


def _override_user_profile_service() -> UserProfileService:
    return FakeUserProfileService()


def test_get_my_profile_returns_profile_snapshot():
    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_user_profile_dependency] = _override_user_profile_service
    client = TestClient(app)

    response = client.get('/api/v1/users/me/profile')

    assert response.status_code == 200
    body = response.json()
    assert body['user']['public_id'] == 'usr_profile_1'
    assert body['profile_completion']['score'] == 100
    assert body['user']['clerk']['profile']['full_name'] == 'Profile Owner'

    app.dependency_overrides.clear()


def test_patch_my_profile_updates_only_app_managed_fields():
    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_user_profile_dependency] = _override_user_profile_service
    client = TestClient(app)

    response = client.patch(
        '/api/v1/users/me',
        json={
            'headline': 'Staff AI Engineer',
            'skills': ['Python', 'FastAPI', 'Prompt Engineering'],
            'preferences': {'practice_mode': 'deep-dive'}
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body['user']['profile']['headline'] == 'Staff AI Engineer'
    assert body['user']['profile']['skills'] == ['Python', 'FastAPI', 'Prompt Engineering']
    assert body['user']['clerk']['email'] == 'profile@example.com'
    assert body['profile_completion']['score'] == 83

    app.dependency_overrides.clear()
