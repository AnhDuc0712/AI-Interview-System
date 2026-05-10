from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, ReturnDocument

from app.core.exceptions import AuthorizationError, ProcessingError
from app.db.client import db
from app.models.user import AuthenticatedPrincipal, User, UserProfile, UserRole
from app.utils.ids import generate_public_id


PROFILE_COMPLETION_FIELDS = (
    'headline',
    'biography',
    'timezone',
    'target_role',
    'years_of_experience',
    'skills',
)


class UserRepository:
    def __init__(self) -> None:
        self.collection = db['users']

    async def ensure_indexes(self) -> None:
        await self.collection.create_index(
            [('public_id', ASCENDING)],
            name='uq_users_public_id',
            unique=True
        )
        await self.collection.create_index(
            [('clerk.clerk_user_id', ASCENDING)],
            name='uq_users_clerk_user_id',
            unique=True
        )
        await self.collection.create_index(
            [('clerk.email', ASCENDING)],
            name='idx_users_clerk_email',
            sparse=True
        )
        await self.collection.create_index(
            [('role', ASCENDING), ('state.is_deleted', ASCENDING)],
            name='idx_users_role_deleted'
        )
        await self.collection.create_index(
            [('metadata.updated_at', ASCENDING)],
            name='idx_users_updated_at'
        )

    async def upsert_from_principal(self, principal: AuthenticatedPrincipal) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        completion = calculate_profile_completion({})

        update = {
            '$set': {
                'clerk.email': principal.email,
                'clerk.issuer': principal.issuer,
                'clerk.profile.first_name': principal.first_name,
                'clerk.profile.last_name': principal.last_name,
                'clerk.profile.full_name': principal.full_name,
                'clerk.profile.username': principal.username,
                'clerk.profile.image_url': principal.image_url,
                'metadata.updated_at': now,
                'metadata.last_sign_in_at': now,
                'metadata.clerk_synced_at': now
            },
            '$setOnInsert': {
                'public_id': generate_public_id(),
                'role': UserRole.candidate.value,
                'clerk.clerk_user_id': principal.clerk_user_id,
                'profile': UserProfile().model_dump(),
                'metadata.created_at': now,
                'metadata.last_profile_updated_at': None,
                'metadata.profile_completion_score': completion['score'],
                'metadata.profile_completion_fields_completed': completion['fields_completed'],
                'metadata.profile_completion_fields_total': completion['fields_total'],
                'metadata.profile_completed_at': None,
                'state.is_deleted': False,
                'state.deleted_at': None
            }
        }

        return await self.collection.find_one_and_update(
            {'clerk.clerk_user_id': principal.clerk_user_id},
            update,
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

    async def update_profile_by_public_id(
        self,
        public_id: str,
        profile_updates: dict[str, Any]
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        completion = calculate_profile_completion(profile_updates)

        set_operations = {
            'metadata.updated_at': now,
            'metadata.last_profile_updated_at': now,
            'metadata.profile_completion_score': completion['score'],
            'metadata.profile_completion_fields_completed': completion['fields_completed'],
            'metadata.profile_completion_fields_total': completion['fields_total'],
            'metadata.profile_completed_at': now if completion['score'] == 100 else None
        }
        for field, value in profile_updates.items():
            set_operations[f'profile.{field}'] = value

        document = await self.collection.find_one_and_update(
            {'public_id': public_id, 'state.is_deleted': False},
            {'$set': set_operations},
            return_document=ReturnDocument.AFTER
        )
        if document is None:
            raise AuthorizationError('User account is deactivated')
        return document

    def deserialize(self, document: dict[str, Any] | None) -> User:
        if document is None:
            raise ProcessingError('User not found')

        serialized = self._convert_object_ids(document)
        return User.model_validate(serialized)

    def _convert_object_ids(self, data: Any) -> Any:
        if isinstance(data, list):
            return [self._convert_object_ids(item) for item in data]
        if isinstance(data, dict):
            return {k: self._convert_object_ids(v) for k, v in data.items()}
        if isinstance(data, ObjectId):
            return str(data)
        return data


def calculate_profile_completion(profile: dict[str, Any]) -> dict[str, int]:
    completed = 0
    for field in PROFILE_COMPLETION_FIELDS:
        value = profile.get(field)
        if isinstance(value, list):
            if value:
                completed += 1
            continue
        if value is not None and value != '':
            completed += 1

    total = len(PROFILE_COMPLETION_FIELDS)
    score = int(round((completed / total) * 100)) if total else 100
    return {
        'score': score,
        'fields_completed': completed,
        'fields_total': total
    }
