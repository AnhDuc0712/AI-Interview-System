from fastapi.testclient import TestClient

from app.dependencies.auth import get_current_user
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


def _build_user() -> User:
    return User(
        _id='507f1f77bcf86cd799439011',
        public_id='usr_123',
        role=UserRole.candidate,
        clerk=ClerkManagedUserData(
            clerk_user_id='user_123',
            email='engineer@example.com',
            issuer='https://example.clerk.accounts.dev',
            profile=ClerkProfile(
                first_name='Senior',
                last_name='Engineer',
                full_name='Senior Engineer',
                username='senior.engineer',
                image_url='https://example.com/avatar.png'
            )
        ),
        profile=UserProfile(
            headline='Backend Engineer',
            biography='Builds scalable interview platforms',
            location='Ho Chi Minh City',
            timezone='Asia/Saigon',
            target_role='Senior Backend Engineer',
            years_of_experience=8,
            skills=['Python', 'FastAPI'],
            preferences={'interview_style': 'structured'}
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


async def _override_current_user() -> User:
    return _build_user()


def test_current_user_endpoint_requires_authentication():
    client = TestClient(app)
    response = client.get('/api/v1/auth/me')

    assert response.status_code == 401
    assert response.json()['detail'] == 'Authentication credentials were not provided'


def test_current_user_endpoint_returns_authenticated_user():
    app.dependency_overrides[get_current_user] = _override_current_user
    client = TestClient(app)

    response = client.get('/api/v1/auth/me')

    assert response.status_code == 200
    assert response.json()['user']['clerk']['clerk_user_id'] == 'user_123'
    assert response.json()['user']['public_id'] == 'usr_123'

    app.dependency_overrides.clear()


def test_protected_endpoint_returns_user_context():
    app.dependency_overrides[get_current_user] = _override_current_user
    client = TestClient(app)

    response = client.get('/api/v1/auth/protected')

    assert response.status_code == 200
    body = response.json()
    assert body['message'] == 'You have access to this protected resource'
    assert body['user']['clerk']['email'] == 'engineer@example.com'
    assert body['user']['clerk']['profile']['username'] == 'senior.engineer'

    app.dependency_overrides.clear()
