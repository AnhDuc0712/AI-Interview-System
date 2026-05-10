from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class UserRole(str, Enum):
    candidate = 'candidate'
    interviewer = 'interviewer'
    admin = 'admin'


class AuthenticatedPrincipal(BaseModel):
    clerk_user_id: str = Field(..., description='Clerk user identifier')
    session_id: str | None = Field(default=None, description='Clerk session identifier')
    email: str | None = Field(default=None, description='Primary email address')
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    username: str | None = None
    image_url: str | None = None
    issuer: str | None = None
    audience: str | list[str] | None = None


class ClerkProfile(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    username: str | None = None
    image_url: str | None = None


class ClerkManagedUserData(BaseModel):
    clerk_user_id: str
    email: str | None = None
    issuer: str | None = None
    profile: ClerkProfile


class UserProfile(BaseModel):
    headline: str | None = None
    biography: str | None = None
    location: str | None = None
    timezone: str | None = None
    target_role: str | None = None
    years_of_experience: int | None = None
    skills: list[str] = Field(default_factory=list)
    preferences: dict[str, str] = Field(default_factory=dict)


class UserMetadata(BaseModel):
    created_at: datetime
    updated_at: datetime
    last_sign_in_at: datetime
    last_profile_updated_at: datetime | None = None
    clerk_synced_at: datetime
    profile_completion_score: int = 0
    profile_completion_fields_completed: int = 0
    profile_completion_fields_total: int = 0
    profile_completed_at: datetime | None = None


class UserState(BaseModel):
    is_deleted: bool = False
    deleted_at: datetime | None = None


class User(BaseModel):
    id: str | None = Field(default=None, validation_alias='_id', serialization_alias='id')
    public_id: str
    role: UserRole
    clerk: ClerkManagedUserData
    profile: UserProfile
    metadata: UserMetadata
    state: UserState

    model_config = ConfigDict(populate_by_name=True)
